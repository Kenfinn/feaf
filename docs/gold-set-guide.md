# Gold set guide

The version for the finance team is internal team material, not published. It is sent together with [`gold-set/gold-set-labelling-sheet.xlsx`](./gold-set/gold-set-labelling-sheet.xlsx).
It covers: the columns to fill in, the agreed rules per announcement type, unit conversions,
examples, and the `menit` (minutes) column for the manual-work baseline.

This file is a technical note for the team.

## Building the package

The Excel file holds 46 real announcements from 9 Nov, about 7 per path, with an "Isi pengumuman" (announcement content)
sheet so labellers do not need MOPS or an access code. Person names are not included: items labelled 姓名 (name)
are dropped, and for articles 1/6/7/8 only items from the allow-list (`app/gold.py`,
`LABEL_AMAN_ORANG`) are taken.

```bash
SENTINEL_DATA_DIR=<data folder> python3 scripts/buat_paket_gold.py --keluar docs/gold-set/gold-set-labelling-sheet.xlsx
```

## After the Excel file comes back

```bash
python3 scripts/buat_paket_gold.py --ke-csv <filled-in excel> --keluar eval/gold.csv
python3 scripts/evaluasi.py --menit-manual <average of the menit column> --simpan
```

Rows without `keputusan` (decision) are skipped. The `keputusan` column (`terbit`/`tahan`/`arsip`, i.e. publish/hold/archive) and `tingkat` (level) are read
by `scripts/evaluasi.py` in gold mode. The old `harus_terbit` column is still accepted (`ya` = `terbit`,
`tidak` = `arsip`).

Candidates can also be downloaded from the server: `/ekspor/kandidat-gold.csv` (needs an access code).
