# Paito Live

Situs statis berbahasa Indonesia untuk tampilan Paito SDY.

## Pembaruan otomatis

GitHub Actions mengambil tabel Paito Sydney dari endpoint publik yang dipakai halaman [Paito Warna Sydney Angkanet](https://angkanet.college/paito-warna-sydney-pools/), memvalidasi formatnya, lalu memperbarui `data/paito-sdy.json` jika datanya berubah. Proses berjalan setiap hari pukul **22.00 WIB** dan dapat dijalankan manual dari tab **Actions**.

Situs menampilkan waktu pengambilan terakhir dan tautan ke sumber. Data ini mengikuti ketersediaan dan format sumber; jika sumber berubah atau tidak dapat diakses, workflow akan gagal dengan aman dan file terakhir yang berhasil tetap tersimpan.

## Menjalankan secara lokal

Diperlukan Python 3.9+ untuk scraper. Jalankan pembaruan dengan:

```bash
python3 scripts/update_paito.py
```

Untuk membuka situs, jalankan server statis dari folder repository, misalnya:

```bash
python3 -m http.server 8000
```

Kemudian kunjungi `http://localhost:8000`.

## Struktur berkas

- `index.html` — struktur halaman.
- `styles.css` — tampilan responsif.
- `script.js` — pemuatan dan rendering dataset.
- `data/paito-sdy.json` — data Paito terakhir yang berhasil diambil.
- `scripts/update_paito.py` — pengambil dan validator data.
- `.github/workflows/update-paito.yml` — jadwal harian GitHub Actions.
