"""Teks untuk penanganan galat pipeline dan reverse DCF yang tidak terdefinisi (v1.3.3)."""

from __future__ import annotations

T: dict[str, tuple[str, str, str]] = {
    # Pemeriksa pasca-hitung: FCFF sesudah skenario <= 0, reverse DCF tidak terdefinisi.
    "cek.sirkular.tak_terdefinisi": (
        "Free cash flow after this scenario is not positive, so the implied growth is undefined and "
        "the result cannot be checked",
        "此情境下自由現金流量非正值，隱含成長率無法定義，結果無法驗證",
        "Arus kas bebas sesudah skenario ini tidak positif, jadi pertumbuhan tersirat tidak terdefinisi "
        "dan hasilnya tidak bisa diperiksa",
    ),
    # Satu pengumuman gagal diproses: ditahan, situs tetap jalan.
    "tahap.galat_proses": ("Processing error", "處理錯誤", "Galat pemrosesan"),
    "akhir.galat_proses": (
        "Held for review: an unexpected error occurred while processing this filing ({galat}).",
        "待人工審查：處理此公告時發生非預期錯誤（{galat}）。",
        "Ditahan untuk review: terjadi galat tak terduga saat memproses pengumuman ini ({galat}).",
    ),
    "rv.jenis.galat_proses": ("Processing error", "處理錯誤", "Galat pemrosesan"),
    "ui.alasan_polos.akhir.galat_proses": (
        "Held for review: this filing could not be processed automatically.",
        "待人工審查：此公告無法自動處理。",
        "Ditahan untuk review: pengumuman ini tidak bisa diproses otomatis.",
    ),
    "ui.alasan_polos.tahan.galat_proses": (
        "Held for review: this filing could not be processed automatically.",
        "待人工審查：此公告無法自動處理。",
        "Ditahan untuk review: pengumuman ini tidak bisa diproses otomatis.",
    ),
}
