"""FCFF tidak positif dan galat per pengumuman (insiden feaf.web.id 18 Nov 2026, setelah v1.3.2).

Skenario pasal 20 mengganti capex tahun terakhir dengan angka dari pengumuman. Bila capex itu
melebihi arus kas operasi, FCFF0 <= 0 dan reverse DCF tidak terdefinisi: g hasil baliknya
>= WACC, `ev_from_growth` mengembalikan None, dan pemeriksaan sirkularitas di `dcf.compute`
menghitung `None - float`. TypeError itu menghentikan `pipeline.jalankan_semua()`, dan karena
setiap halaman membutuhkan hasilnya, seluruh situs 500.

Tanpa jaringan: jejak ditulis ke folder sementara, keputusan review di-patch.
"""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import dcf  # noqa: E402

from app import config, i18n  # noqa: E402
from app.agent import pipeline, recompute, verify  # noqa: E402


def _valuasi() -> dict:
    with open(os.path.join(ROOT, "valuation", "inputs", "2330.json"), encoding="utf-8") as f:
        return json.load(f)


def _fixture(nama: str) -> dict:
    with open(os.path.join(ROOT, "data", "fixtures", "details.json"), encoding="utf-8") as f:
        return next(r for r in json.load(f) if r["_fixture"] == nama)


def _fcff_negatif(d: dict) -> dict:
    """Arus kas operasi tahun terakhir di bawah capex: FCFF0 < 0."""
    d = copy.deepcopy(d)
    cf = d["cash_flow"]
    th = max(cf["capex_by_year"])
    cf["cfo_by_year"][th] = cf["capex_by_year"][th] * 0.5
    return d


class TestDcfFcffTidakPositif(unittest.TestCase):
    def test_reverse_dcf_tidak_terdefinisi_tanpa_galat(self):
        d = _fcff_negatif(_valuasi())
        r = dcf.compute(d)
        self.assertLess(r["fcff0"], 0)
        self.assertIsNone(r["implied_growth"])
        self.assertEqual(r["circularity"], {"ev_back": None, "drift_pct": None, "price_back": None})
        self.assertFalse(r["exceeds_ceiling"])
        self.assertEqual(r["sensitivity"], {"g_axis": [], "wacc_axis": [], "grid": []})

    def test_skenario_forward_tetap_dihitung(self):
        d = _fcff_negatif(_valuasi())
        g = d["assumptions"]["terminal_growth_ceiling"]
        r = dcf.compute(d, forward_g=g)
        self.assertIsNotNone(r["forward"]["fair_value"])
        self.assertEqual(len(r["sensitivity"]["grid"]), 5)

    def test_fcff_positif_tidak_berubah(self):
        r = dcf.compute(_valuasi())
        self.assertIsNotNone(r["implied_growth"])
        self.assertLess(r["circularity"]["drift_pct"], 1e-6)

    def test_cli_mencetak_tanpa_galat(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "v.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(_fcff_negatif(_valuasi()), f)
            out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "dcf.py"), p],
                                 capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("tidak terdefinisi", out.stdout)


class TestSkenarioCapexMelebihiArusKas(unittest.TestCase):
    def setUp(self):
        d = _valuasi()
        cf = d["cash_flow"]
        th = max(cf["capex_by_year"])
        self.d = d
        self.capex_besar = cf["cfo_by_year"][th] * 1.5        # FCFF0 sesudah skenario < 0

    def test_hitung_ulang_tanpa_galat(self):
        h = recompute.hitung_ulang(self.d, "capex", self.capex_besar)
        self.assertIsNotNone(h["sebelum"]["implied_growth"])
        self.assertIsNone(h["sesudah"]["implied_growth"])
        self.assertIsNone(h["delta"]["g_tersirat"])

    def test_pemeriksa_menahan_bukan_meloloskan(self):
        h = recompute.hitung_ulang(self.d, "capex", self.capex_besar)
        cek = verify.periksa_hasil(h)
        self.assertFalse(verify.vonis(cek)["lolos"])
        self.assertEqual(cek[0]["alasan_i18n"]["kode"], "cek.sirkular.tak_terdefinisi")


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._patch = [mock.patch.object(config, "TRACE_DIR", self._tmp.name),
                       mock.patch("app.review.untuk", return_value=None)]
        for p in self._patch:
            p.start()

    def tearDown(self):
        for p in self._patch:
            p.stop()
        self._tmp.cleanup()

    def test_pengumuman_capex_dengan_fcff_negatif_ditahan(self):
        h = pipeline.jalankan(_fixture("kasus-1-capex-bersih"), _fcff_negatif(_valuasi()))
        self.assertEqual(h["status"], "ditahan")

    def test_satu_pengumuman_galat_tidak_menghentikan_semuanya(self):
        baik = _fixture("kasus-3-rutin-tersaring")
        rusak = _fixture("kasus-1-capex-bersih")
        asli = pipeline.jalankan

        def jalankan(d, v):
            if d is rusak:
                raise TypeError("unsupported operand type(s) for -: 'NoneType' and 'float'")
            return asli(d, v)

        with mock.patch.object(pipeline.store, "muat_detail", return_value=([rusak, baik], "nyata")), \
             mock.patch.object(pipeline, "jalankan", side_effect=jalankan), \
             mock.patch("builtins.print"):
            hasil = pipeline.jalankan_semua()

        self.assertEqual(len(hasil), 2)
        gagal = hasil[0]
        self.assertEqual(gagal["status"], "ditahan")
        self.assertEqual(gagal["muatan"]["tahan"]["jenis"], "galat_proses")
        self.assertFalse(gagal["muatan"]["tahan"]["boleh_setujui"])
        self.assertIn("TypeError", gagal["alasan"])
        self.assertEqual(hasil[1]["status"], "dilewati")
        self.assertTrue(os.path.exists(os.path.join(self._tmp.name, f"{gagal['id']}.json")))


class TestTeks(unittest.TestCase):
    def test_kunci_baru_tiga_bahasa(self):
        for k in ("cek.sirkular.tak_terdefinisi", "tahap.galat_proses", "akhir.galat_proses",
                  "rv.jenis.galat_proses", "ui.alasan_polos.akhir.galat_proses",
                  "ui.alasan_polos.tahan.galat_proses"):
            for b in ("en", "zh", "id"):
                with self.subTest(kunci=k, bahasa=b):
                    teks = i18n.t(k, b, galat="X")
                    self.assertTrue(teks)
                    self.assertFalse(teks.startswith("⟦"))


if __name__ == "__main__":
    unittest.main()
