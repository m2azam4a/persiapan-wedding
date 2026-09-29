# -*- coding: utf-8 -*-
"""Generate micromanage-level step-by-step definitions (bahasa mudah)."""
import json
from pathlib import Path

ROOT = Path(r"D:\Isi Otak Azam\Persiapan Wedding\wedding-planner-html")
text = (ROOT / "js" / "data.js").read_text(encoding="utf-8")
payload = json.loads(text.replace("window.WP_DEFAULT = ", "", 1).rstrip().rstrip(";"))

PHASES_SIMPLE = {
    "P0": "Awal: sepakat dulu mau seperti apa",
    "P1": "Uang: tentukan budget",
    "P2": "Konsep: tentukan tema & suasana",
    "P3": "Tanggal, tempat, & surat-surat",
    "P4": "Cari & kontrak vendor",
    "P5": "Tamu & undangan",
    "P6": "Baju & makeup",
    "P7": "Dekor, makanan, suara/lampu",
    "P8": "Susunan acara",
    "P9": "Transport, parkir, keamanan",
    "P10": "60 hari sebelum: rapat intensif",
    "P11": "Minggu pernikahan",
    "P12": "H-1 & hari pernikahan",
    "P13": "Setelah acara selesai",
}

PHASE_CONTEXT = {
    "P0": "Bagian paling awal. Tujuannya supaya pasangan dan keluarga sepakat dulu, sebelum banyak belanja.",
    "P1": "Bagian soal uang: berapa maksimal yang boleh dikeluarkan, dan kapan bayar apa.",
    "P2": "Bagian menentukan tema dan suasana acara biar semua orang bayangannya sama.",
    "P3": "Bagian mengunci tanggal, menyewa tempat, dan urus surat nikah.",
    "P4": "Bagian mencari jasa (WO, katering, dekor, dll), bandingkan harga, lalu tanda tangan kontrak.",
    "P5": "Bagian daftar tamu, undangan, dan konfirmasi siapa yang datang.",
    "P6": "Bagian baju pengantin, fitting, trial makeup, dan foto prewedding.",
    "P7": "Bagian detail dekorasi, makanan, suara, lampu, dan jadwal bongkar-pasang di lokasi.",
    "P8": "Bagian menyusun urutan acara dari menit ke menit.",
    "P9": "Bagian mobil, parkir, satpam, dan rencana kalau ada masalah mendadak.",
    "P10": "Sekitar 2 bulan sebelum hari-H: rapat vendor, bayar cicilan, stop perubahan besar.",
    "P11": "Seminggu sebelum: jumlah tamu final, latihan, briefing keluarga, pelunasan.",
    "P12": "Sehari sebelum dan hari pernikahan: pasang, akad, resepsi, beres-beres.",
    "P13": "Setelah acara: evaluasi, bayar sisa tagihan, ambil dokumen, simpan arsip.",
}


def base_open(t):
    owner, vendor = t["owner"], t["vendor"]
    deps = t.get("deps") or []
    steps = [
        f"Buka halaman Jadwal, cari pekerjaan “{t['name']}” (kode {t['id']} / {t['wbs']}).",
        f"Ubah status “{t['name']}” menjadi Sedang dikerjakan.",
        f"Konfirmasi PIC untuk “{t['name']}”: {owner}. Jika bukan Anda, hubungi dulu sebelum lanjut.",
        f"Siapkan kontak kerja sama untuk tugas ini: {vendor}.",
    ]
    if deps:
        steps.append(
            f"Untuk “{t['name']}”, cek dulu syarat selesai: "
            + ", ".join(deps)
            + ". Jika belum Selesai, tanya boleh mulai paralel atau tidak."
        )
        steps.append(
            f"Jika “{t['name']}” tetap dimulai sebelum syarat beres, tulis alasan di Catatan Jadwal."
        )
    else:
        steps.append(f"“{t['name']}” tidak menunggu pekerjaan lain — boleh langsung mulai.")
    return steps


def base_close(t):
    return [
        f"Simpan bukti “{t['name']}” di folder bersama (foto/chat/file/kontrak/kwitansi).",
        f"Tulis di Catatan Jadwal ringkasan hasil “{t['name']}” + link bukti.",
        f"Jika “{t['name']}” belum beres, status = Terhambat + penyebabnya.",
        f"Jika “{t['name']}” beres, status = Selesai dan persen 100.",
        f"Kabari pihak yang menunggu hasil “{t['name']}” (lihat Pekerjaan berikutnya di panel kanan).",
    ]


def steps_rfi_rfp(t, kind):
    label = "permintaan informasi (RFI)" if "rfi" in kind else "permintaan penawaran (RFP)"
    return base_open(t) + [
        f"Buat dokumen singkat {label} di Google Docs / Word (1–2 halaman).",
        "Isi: tanggal acara, tempat (kalau sudah), jumlah tamu perkiraan, gaya acara, budget kisaran, dan tenggat jawab.",
        "Buat daftar minimal 3 calon vendor (nama + nomor WA + link Instagram/website).",
        "Kirim brief yang sama ke semua calon (supaya adil & gampang dibanding).",
        "Catat tanggal kirim dan tanggal janji balasan di Excel/Sheet.",
        "Follow-up WA di hari ke-2 jika belum dibalas.",
        "Kumpulkan semua penawaran ke 1 folder, beri nama file: NamaVendor_Tanggal.pdf.",
        "Buat tabel banding: harga | apa saja yang termasuk | apa yang tidak termasuk | kelemahan.",
        "Pilih 2–3 finalis untuk diwawancara / diminta presentasi.",
        "Jadwalkan meeting (online/offline), siapkan 5 pertanyaan wajib (harga, overtime, pembatalan, personel, contoh kerja).",
        "Setelah meeting, update tabel banding dengan skor 1–5.",
        "Tulis rekomendasi singkat: vendor A karena … (boleh dibaca orang tua).",
    ] + base_close(t)


def steps_kontrak(t):
    return base_open(t) + [
        "Minta draft kontrak dari vendor (PDF).",
        "Print atau buka di laptop, highlight bagian: harga total, jadwal bayar, apa yang termasuk, aturan batal, keterlambatan, lembur.",
        "Cocokkan dengan penawaran terakhir — kalau beda, tanya vendor sebelum tanda tangan.",
        "Pastikan lampiran ada: menu / denah / daftar foto / jumlah personel (sesuai jenis vendor).",
        "Tulis rekening resmi vendor (bukan rekening pribadi tanpa surat kuasa).",
        "Minta pasangan/orang yang berwenang baca & setuju.",
        "Tanda tangan (basah atau digital) kedua belah pihak.",
        "Scan/foto kontrak, simpan di folder Kontrak/{NamaVendor}.",
        "Bayar DP sesuai kontrak, minta kwitansi resmi.",
        "Catat di kalender HP: tanggal termin bayar berikutnya + pengingat H-3.",
        "Kirim salinan kontrak ke WO / Finance Lead.",
    ] + base_close(t)


def steps_meeting(t):
    return base_open(t) + [
        "Tentukan tanggal & jam meeting (cek dulu kesediaan orang penting).",
        "Buat undangan WA/kalender berisi: link Zoom/lokasi, durasi, siapa yang wajib hadir.",
        "Siapkan agenda tertulis (poin 1, 2, 3…) dan kirim H-1 sebelum meeting.",
        "Siapkan bahan: file terkait, foto, tabel status, pertanyaan terbuka.",
        "Di meeting: mulai tepat waktu, sebutkan tujuan 1 kalimat.",
        "Bahas tiap poin agenda; catat keputusan & siapa yang mengerjakan.",
        "Kalau ada perdebatan, catat opsi A/B lalu minta penentu final memilih.",
        "Akhiri dengan ringkas ulang keputusan (baca keras biar semua dengar).",
        "Maksimal 24 jam setelah meeting: kirim notulen + daftar tugas (nama | tugas | tenggat).",
        "Follow-up tugas di H+3 kalau belum bergerak.",
    ] + base_close(t)


def steps_fitting(t):
    return base_open(t) + [
        "Hubungi bridal/penjahit, konfirmasi jam fitting & alamat.",
        "Siapkan sepatu, bra/dalaman, dan aksesoris yang akan dipakai di hari-H.",
        "Datang 10 menit lebih awal, bawa botol air & tisu.",
        "Pakai baju lengkap, coba duduk, jalan, angkat tangan, (kalau relevan) gerakan ibadah.",
        "Cek: longgar/sempit di mana, panjang rok, lengan, kenyamanan napas.",
        "Foto depan-samping-belakang (boleh minta dibantu keluarga).",
        "Tulis daftar perbaikan di notes HP: “pinggang longgarkan 1 cm”, dll.",
        "Konfirmasi ke penjahit: apa yang diganti + tanggal fitting berikutnya.",
        "Bayar biaya tambahan jika ada, minta kwitansi.",
        "Update status di Jadwal + unggah foto fitting ke folder bersama.",
    ] + base_close(t)


def steps_trial_mua(t):
    return base_open(t) + [
        "Kirim 3–5 foto referensi ke MUA (selfie + foto yang disukai).",
        "Kabari warna baju / kain sample yang akan dipakai.",
        "Konfirmasi jam trial, apakah include hair, dan berapa lama.",
        "Cuci muka bersih, jangan makeup tebal sebelum datang.",
        "Saat trial: minta foto di jendela (cahaya natural) dan di dalam ruangan.",
        "Coba ekspresi: senyum, serius, menunduk — cek apakah makeup “pecah”.",
        "Catat yang kurang: terlalu gelap, terlalu glitter, rambut kurang volume, dll.",
        "Putuskan look final atau jadwalkan trial ke-2 kalau belum pas.",
        "Simpan foto referensi final di folder Makeup.",
        "Konfirmasi call time MUA di hari-H (jam datang ke rumah/hotel).",
    ] + base_close(t)


def steps_undangan(t):
    return base_open(t) + [
        "Kumpulkan data final: nama lengkap pasangan, nama orang tua, waktu, alamat, maps, dress code, kontak RSVP.",
        "Tulis teks undangan di Docs, minta 2 orang baca ulang (cari typo nama & tanggal).",
        "Kirim teks + referensi desain ke vendor undangan.",
        "Minta 1–2 draft desain, beri feedback spesifik (“logo lebih kecil”, “jam diganti”).",
        "Approve file final tertulis (“OK cetak versi ini”).",
        "Minta sampel cetak / PDF final sebelum mass production.",
        "Cek sampel: warna, potongan, QR RSVP bisa dibuka, ejaan.",
        "Hitung jumlah cetak = tamu + cadangan 10%.",
        "Terima barang, hitung fisik vs invoice, foto box sebagai bukti.",
        "Pisahkan undangan VIP vs umum, siapkan daftar kirim.",
    ] + base_close(t)


def steps_guest_rsvp(t):
    return base_open(t) + [
        "Buka 1 file master daftar tamu (jangan copy ke banyak file).",
        "Pastikan kolom ada: nama, kategori (VIP/keluarga/umum), jumlah orang, status undangan, status RSVP, catatan alergi.",
        "Update data dari WA/telepon setiap kali ada balasan.",
        "Tandai warna: hijau=hadir, merah=tidak, kuning=belum jawab.",
        "Setiap minggu: filter yang masih kuning, hubungi ulang (WA singkat sopan).",
        "Untuk luar kota: tanya butuh hotel/antar-jemput atau tidak.",
        "Sinkronkan angka hadir sementara ke katering/WO kalau diminta.",
        "Sebelum freeze: export PDF/Excel bertanggal sebagai arsip.",
    ] + base_close(t)


def steps_load(t):
    return base_open(t) + [
        "Minta aturan loading dari pihak tempat (jam buka, lift, parkir truk, listrik).",
        "Buat tabel: vendor | jam datang | apa yang dibawa | butuh berapa orang bantu.",
        "Urutkan: suara/lampu dulu → dekor besar → meja/kursi → finishing bunga.",
        "Tunjuk 1 orang “penjaga pintu” di lokasi dengan daftar checklist.",
        "Siapkan air minum & tempat istirahat singkat untuk crew.",
        "Di hari loading: centang tiap vendor yang datang & selesai setup.",
        "Foto kondisi ruangan sebelum & sesudah (buat bukti).",
        "Untuk load-out: pastikan semua barang vendor kembali, spot cek barang sewa keluarga.",
        "Serahkan ruangan ke pihak tempat, minta konfirmasi tidak ada kerusakan.",
    ] + base_close(t)


def steps_rehearsal(t):
    return base_open(t) + [
        "Buat undangan latihan: jam, lokasi, siapa wajib datang.",
        "Cetak/share susunan acara versi terbaru ke semua peserta.",
        "Siapkan mic, musik, dan orang yang akan jadi “pengganti” kalau ada yang absen.",
        "Latih dari awal: masuk, posisi akad, salam, keluar, jalur foto.",
        "Stop di tiap masalah, catat: apa masalahnya + siapa perbaiki + kapan.",
        "Tes volume mic & musik di posisi tamu duduk (bukan cuma di panggung).",
        "Pastikan petugas tahu kode isyarat (contoh: anggukan = mulai musik).",
        "Akhiri dengan ringkas: 3 hal yang wajib diingat di hari-H.",
        "Update susunan acara kalau ada perubahan kecil hasil latihan.",
    ] + base_close(t)


def steps_bayar(t):
    return base_open(t) + [
        "Buka kontrak, cari jadwal bayar yang relevan dengan pekerjaan ini.",
        "Cek nomor rekening resmi vendor (cocokkan dengan kontrak).",
        "Siapkan nominal pas (termasuk PPN kalau ada).",
        "Transfer, simpan bukti (screenshot + PDF bank).",
        "Kirim bukti ke vendor, minta kwitansi/invoice resmi.",
        "Update tabel keuangan: tanggal | vendor | nominal | sisa.",
        "Kalau ada selisih, tulis penjelasan di catatan (overtime, tambahan porsi, dll).",
        "Kabari Finance Lead / pasangan bahwa pembayaran sudah masuk.",
    ] + base_close(t)


def steps_dokumen(t):
    return base_open(t) + [
        "Tulis daftar dokumen resmi dari KUA/kelurahan/catatan sipil (jangan hafalan).",
        "Siapkan map fisik + folder digital “Dokumen Nikah”.",
        "Fotokopi & scan tiap dokumen (nama file jelas).",
        "Cek masa berlaku / stempel / tanda tangan masih valid.",
        "Buat janji ke kelurahan/KUA, catat jam & nama petugas.",
        "Datang bawa dokumen asli + fotokopi + pulpen + map.",
        "Catat nomor antrean / bukti serah berkas.",
        "Tanyakan kapan boleh diambil & syarat pengambilan.",
        "Setelah selesai, foto hasil akhir (buku nikah/akta) untuk arsip.",
    ] + base_close(t)


def steps_gate(t):
    return base_open(t) + [
        "Kumpulkan bahan keputusan ke 1 folder (harga, desain, risiko, opsi A/B).",
        "Buat ringkasan 5–10 baris: apa yang diputuskan hari ini.",
        "Undang hanya orang yang berhak memutuskan (jangan terlalu ramai).",
        "Presentasikan opsi dengan plus-minus, jangan cuma “saya suka ini”.",
        "Minta keputusan jelas: Lanjut / Revisi / Tunda — tulis di notes.",
        "Kalau Revisi: tulis apa yang harus diubah + tenggat.",
        "Kalau Lanjut: catat syarat (budget max, vendor terpilih, dll).",
        "Kirim keputusan tertulis ke grup terkait di hari yang sama.",
    ] + base_close(t)


def steps_generic(t):
    name = t["name"]
    return base_open(t) + [
        f"Tulis di notes HP tujuan spesifik: menyelesaikan “{name}”.",
        f"Buat checklist unik untuk “{name}” (minimal 5 poin konkret, jangan generik).",
        "Siapkan alat yang dibutuhkan: HP, laptop, folder, pulpen, kontak terkait.",
        "Kerjakan poin checklist berurutan; centang setelah ada bukti.",
        "Setiap selesai 1 poin, foto/screenshot bukti dan simpan dengan nama file jelas.",
        "Kalau stuck lebih dari 1 hari, tulis di Catatan Jadwal & minta bantuan orang yang tepat.",
        "Review hasil dengan pasangan/keluarga inti (kalau keputusan menyentuh mereka).",
        "Rapikan file/barang hasil kerja supaya orang lain bisa menemukan.",
    ] + base_close(t)


# Langkah tengah unik untuk task yang sebelumnya jatuh ke template generik
SPECIFIC = {
    "A02": [
        "Buka notes baru berjudul “Daftar acara yang dikelola”.",
        "Tulis satu per satu: lamaran? pengajian? akad? resepsi? after-party? seserahan?",
        "Untuk tiap acara, isi: wajib/opsional | perkiraan tamu | lokasi ide | siapa biayain.",
        "Hapus atau tandai “di luar proyek” untuk acara yang tidak akan diurus bersama.",
        "Catat asumsi tetap: 1 hari atau lebih? indoor/outdoor? kisaran jumlah tamu.",
        "Kirim daftar ke pasangan + 1 penentu tiap keluarga, minta balasan “setuju/ubah”.",
        "Revisi 1x berdasarkan feedback, simpan sebagai Scope v1.pdf.",
    ],
    "A03": [
        "Buat tabel 4 kolom: Keputusan | Yang kerjakan | Yang putuskan final | Yang dikabari.",
        "Isi baris wajib: budget, tempat, tema, daftar tamu VIP, vendor utama, perubahan mendadak.",
        "Contoh isi: “Budget final” → Finance Lead kerjakan, Orang tua A putuskan, pasangan dikabari.",
        "Isi “Desain dekor” → Creative/pasangan kerjakan, pasangan putuskan, WO dikabari.",
        "Baca keras tabel di meeting singkat 15 menit, pastikan tidak ada 2 penentu final bentrok.",
        "Simpan sebagai RACI-keluarga.xlsx dan pin di grup WA inti.",
    ],
    "A04": [
        "Buat dokumen “Project Charter” 1–2 halaman.",
        "Isi: tujuan acara, apa yang termasuk/tidak, tanggal target, budget plafon, risiko utama.",
        "Buat sheet “Decision Log”: tanggal | keputusan | siapa putuskan | dampak.",
        "Masukkan 3 keputusan awal dari kickoff ke Decision Log.",
        "Share link dokumen ke semua penentu final, minta mereka baca.",
        "Setelah disetujui, kunci file jadi Charter-v1 (jangan diedit sembarangan).",
    ],
    "A05": [
        "Buat folder Drive: 00-Charter, 01-Budget, 02-Vendor, 03-Tamu, 04-Desain, 05-HariH, 06-Arsip.",
        "Buat grup WA: “Wedding Inti” (keputusan) dan “Wedding Vendor” (opsional terpisah).",
        "Buat Sheet master: Dashboard status pekerjaan (boleh mirror dari aplikasi ini).",
        "Atur izin folder: penentu final = editor, lainnya = viewer jika perlu.",
        "Tulis aturan singkat di chat: “keputusan penting dicatat di Decision Log”.",
        "Uji: unggah 1 file contoh, pastikan semua bisa buka.",
    ],
    "A06": [
        "Buat tabel Risiko: Risiko | Kemungkinan (L/S/T) | Dampak | Cara cegah | Cadangan | PIC.",
        "Isi minimal 8 risiko: hujan, vendor batal, listrik padam, sakit, undangan typo, overbudget, tamu melebihi kapasitas, dokumen KUA telat.",
        "Untuk tiap risiko tulis cadangan konkret (contoh: tenda cadangan / genset / vendor backup).",
        "Buat juga daftar Asumsi (hal yang kita anggap benar tapi belum pasti).",
        "Review dengan pasangan 20 menit, tandai risiko “merah” yang wajib dipantau.",
        "Simpan Risk-Register-v1.xlsx di folder Charter.",
    ],
    "A07": [
        "Buat daftar nama: keluarga inti A, keluarga inti B, tokoh yang harus dihormati, VIP.",
        "Untuk tiap nama isi: pengaruh (tinggi/sedang/rendah) | sikap (dukung/netral/khawatir) | apa yang mereka peduli.",
        "Tandai siapa wajib diundang ke keputusan besar vs cukup dikabari hasilnya.",
        "Catat “cara komunikasi terbaik” (telepon orang tua dulu, jangan WA grup, dll).",
        "Susun urutan sosialisasi: siapa dikabari lebih dulu soal tanggal & tempat.",
        "Simpan Stakeholder-Map.pdf dan update kalau ada tokoh baru.",
    ],
    "B01": [
        "Siapkan meeting uang terpisah (jangan campur bahas dekor).",
        "Minta tiap pihak sebutkan kisaran kontribusi (min–max), tulis di sheet.",
        "Pisahkan kantong: biaya acara | mahar/hantaran | honeymoon | darurat.",
        "Jumlahkan angka realistis (pakai nilai tengah kalau masih range).",
        "Catat kapan uang cair (bulan ini / H-60 / H-30).",
        "Sepakati plafon sementara tertulis, meski nanti bisa direvisi 1x.",
    ],
    "B03": [
        "Buat sheet pos biaya: tempat, katering, dekor, WO, foto/video, MUA, baju, undangan, hiburan, suara/lampu, transport, souvenir, lain-lain, darurat.",
        "Isi estimasi tiap pos dari chat vendor / pengalaman saudara / survey kasar.",
        "Hitung total; bandingkan dengan plafon B01.",
        "Kalau total > plafon: tandai pos yang bisa dipotong (bukan potong sembarang).",
        "Tandai 3 pos paling rawan naik harga.",
        "Simpan Cost-Breakdown-v1 dan share ke Finance Lead + pasangan.",
    ],
    "B06": [
        "Pilih bank/e-wallet yang disepakati untuk khusus wedding.",
        "Buka rekening/wahana baru (atau sub-account) — jangan campur belanja harian.",
        "Catat nomor rekening, atas nama, dan siapa yang pegang akses.",
        "Buat aturan: setiap transfer wajib ada catatan “untuk apa”.",
        "Uji transfer Rp10.000 antar akun, pastikan notifikasi masuk.",
        "Simpan foto buku tabungan/screenshot di folder Budget.",
    ],
    "B08": [
        "Buat sheet: Minggu | Rencana keluar | Aktual keluar | Selisih | Catatan.",
        "Masukkan semua DP yang sudah dibayar sebagai aktual minggu ini.",
        "Set pengingat kalender tiap Minggu malam: “isi tracking budget”.",
        "Setiap update, warnai merah jika selisih > 10% dari rencana.",
        "Kalau merah: tulis usulan potongan di baris catatan.",
        "Share sheet ke pasangan + orang yang biayain.",
    ],
    "D01": [
        "Tulis 5 tanggal kandidat di kalender (termasuk cadangan).",
        "Cek bentrok dengan ujian/kerja/libur panjang/acara keluarga besar yang sudah pasti.",
        "Cek kasar musim hujan / hari baik menurut keluarga (kalau dipakai).",
        "Hapus tanggal yang jelas mustahil, sisakan 3–5.",
        "Urutkan prioritas 1–5 dengan alasan singkat.",
        "Kirim daftar ke pasangan & orang tua untuk komentar awal (belum final).",
    ],
    "D02": [
        "Salin shortlist tanggal ke chat keluarga besar / tokoh kunci.",
        "Tanya satu per satu (jangan cuma di grup ramai): “tanggal ini bentrok tidak?”.",
        "Catat jawaban di tabel: Nama | Tanggal OK? | Catatan.",
        "Kalau ada tokoh wajib hadir tapi bentrok, tandai tanggal itu sebagai berisiko.",
        "Revisi prioritas tanggal berdasarkan jawaban.",
        "Laporkan hasil ke pasangan dalam 1 ringkasan singkat.",
    ],
    "D12": [
        "Cari tahu opsi asuransi acara / pembatalan (broker atau bank).",
        "Tanya apa yang ditanggung: hujan, sakit, force majeure, vendor batal.",
        "Bandingkan premi vs manfaat; tulis di notes plus-minus.",
        "Kalau diambil: isi formulir, bayar, simpan polis PDF.",
        "Kalau tidak diambil: tulis keputusan “tidak asuransi” + alasan di Decision Log.",
        "Kabari Finance Lead hasil keputusan.",
    ],
    "E02": [
        "Siapkan daftar pertanyaan WO: pengalaman, jumlah crew H-day, overtime, contoh rundown, cara eskalasi.",
        "Minta tiap WO bawa portfolio + 1 contoh timeline proyek mirip.",
        "Jadwalkan interview 45–60 menit per WO (jangan digabung semua).",
        "Isi skor 1–5 segera setelah tiap interview (masih segar).",
        "Cek testimonial / tanya klien lama bila memungkinkan.",
        "Pilih juara 1 + cadangan, tulis alasan 5 baris.",
    ],
    "E09": [
        "Minta dekor mengirim konsep + denah kasar sesuai tempat.",
        "Siapkan layar besar untuk presentasi; undang pasangan + 1 penentu desain.",
        "Catat feedback spesifik: “panggung terlalu ramai”, “warna kurang hangat”, dll.",
        "Minta revisi maksimal 2 putaran dengan tenggat jelas.",
        "Pastikan file 3D/layout punya versi tanggal.",
        "Setelah disukai, minta quotation final mengikuti konsep itu.",
    ],
    "E25": [
        "Buat sheet Vendor Master: Nama | PIC | WA | Email | Nilai kontrak | Termin bayar | Deliverable | Status | Risiko.",
        "Masukkan semua vendor yang sudah kontrak (satu baris satu vendor).",
        "Isi SLA singkat: jam setup selesai, jam load-out, jumlah personel.",
        "Tandai merah vendor yang belum lengkap kontraknya.",
        "Share ke WO; minta mereka konfirmasi datanya benar.",
        "Update tiap kali ada vendor baru atau ubah PIC.",
    ],
    "F02": [
        "Buka guest list v1, tambah kolom Kategori: VIP / Keluarga A / Keluarga B / Umum / Anak.",
        "Isi kategori satu per satu (jangan biarkan kosong).",
        "Hitung subtotal per kategori.",
        "Tandai VIP yang wajib seating khusus / pickup.",
        "Kirim ringkasan jumlah per kategori ke pasangan untuk dicek.",
        "Kunci pengategorian v1 sebelum undangan massal.",
    ],
    "F09": [
        "Buat teks save-the-date singkat (tanggal, kota, “undangan menyusul”).",
        "Siapkan daftar VIP + keluarga luar kota saja (bukan semua tamu).",
        "Kirim via WA/email dengan foto pasangan opsional.",
        "Catat siapa sudah dikirim di sheet (centang).",
        "Follow-up yang tidak membalas dalam 5 hari.",
        "Simpan screenshot contoh pengiriman untuk arsip.",
    ],
    "G07": [
        "List orang yang perlu seragam: orang tua, saudara inti, bridesmaid/groomsmen.",
        "Tentukan kode warna + tingkat formalitas per kelompok.",
        "Kumpulkan ukuran tubuh (jangan menebak).",
        "Pilih opsi: sewa / beli / jahit; catat deadline fitting masing-masing.",
        "Buat jadwal fitting kolektif biar warna/ kain konsisten.",
        "Foto hasil akhir tiap orang untuk cek keseragaman.",
    ],
    "G10": [
        "Pilih klinik/beautician terpercaya; jangan eksperimen baru mepet hari-H.",
        "Buat jadwal treatment dari H-90 mundur (facial, dll) di kalender.",
        "Catat produk yang dipakai + reaksi alergi jika ada.",
        "Stop treatment agresif di H-14 kecuali disarankan ahli.",
        "Siapkan skincare harian sederhana yang sudah biasa dipakai.",
        "Kabari MUA soal kulit sensitif / treatment terakhir.",
    ],
    "H02": [
        "Minta dekor bawa sample kain, bunga, lighting swatch ke meeting.",
        "Foto tiap sample dengan label nama material.",
        "Bandingkan dengan design brief (warna & suasana).",
        "Pilih kombinasi final; tolak yang “hampir mirip” tapi beda jauh di foto.",
        "Catat vendor suplai bunga/kain kalau terpisah.",
        "Simpan Material-Board.pdf yang disetujui pasangan.",
    ],
    "H04": [
        "Konfirmasi jenis bunga impor yang dipakai di konsep final.",
        "Tanyakan lead time order & risiko keterlambatan ke florist.",
        "Lock jumlah & jenis tertulis (bukan chat ambigu).",
        "Bayar DP order sesuai jadwal supplier.",
        "Catat tanggal kedatangan bunga + PIC penerima di kota Anda.",
        "Siapkan rencana cadangan bunga lokal kalau impor gagal.",
    ],
    "H05": [
        "Kumpulkan data alergi/pantangan dari VIP & keluarga (WA form singkat).",
        "Buat tabel: Nama | Pantangan | Menu pengganti.",
        "Kirim tabel ke katering; minta konfirmasi bisa disediakan.",
        "Pastikan area penyajian tidak mencampur alat alergi parah (jika relevan).",
        "Brief waiter/usher soal meja mana yang pantangan.",
        "Simpan Dietary-Matrix final di folder F&B.",
    ],
    "H06": [
        "Tentukan: wedding cake hanya simbolik atau untuk disajikan tamu.",
        "Pilih desain sesuai tema; kirim referensi ke cake vendor.",
        "Konfirmasi rasa, jumlah tier, waktu antar ke venue.",
        "Cek apakah butuh meja khusus + lampu/outlet.",
        "Order tertulis + DP; catat jam delivery H-day.",
        "Tunjuk PIC yang terima cake di lokasi.",
    ],
    "H07": [
        "Putuskan stasiun: soft drink / kopi / air mineral / lainnya (sesuai adat).",
        "Tanyakan ke katering paket siap vs self-manage.",
        "Hitung kasar konsumsi berdasarkan jumlah tamu.",
        "Susun lokasi stasiun di denah (jangan tutup jalur tamu).",
        "Konfirmasi jumlah crew yang jaga stasiun.",
        "Masukkan ke kontrak F&B atau addendum.",
    ],
    "H08": [
        "Minta standar rasio waiter:jumlah tamu dari katering/WO.",
        "Hitung kebutuhan berdasarkan headcount final + VIP service.",
        "Tambah usher untuk arah duduk & angpao bila perlu.",
        "Tulis jumlah crew final di PO katering.",
        "Minta daftar nama/shift crew H-1.",
        "Brief singkat: prioritas meja VIP & pantangan makanan.",
    ],
    "H11": [
        "Minta data daya listrik venue (kW) + titik stop kontak.",
        "Bandingkan dengan kebutuhan AVL + dapur + AC tambahan.",
        "Kalau kurang: minta penawaran genset (kapasitas, BBM, operator).",
        "Putuskan sewa genset atau tidak; tulis di Decision Log.",
        "Jika sewa: kunci posisi genset + kabel supaya aman & tidak berisik ke tamu.",
        "Uji singkat di H-1 bersama teknisi.",
    ],
    "I07": [
        "Tentukan alur: tamu datang → salam → isi guestbook? → taruh angpao di mana.",
        "Siapkan alat: buku/frame guestbook, pulpen bagus, kotak angpao, penanggung jawab.",
        "Susun posisi meja agar tidak macet di pintu.",
        "Tunjuk 2 orang jaga kotak angpao bergantian.",
        "Brief sopan cara menyapa + jangan memaksa isi buku.",
        "Siapkan kantong/amplop rekap di akhir acara.",
    ],
    "J01": [
        "Tulis timeline mobil: jam makeup selesai → jam harus tiba di lokasi akad.",
        "Pilih tipe mobil + dekor sederhana (kalau ada).",
        "Petakan rute utama + rute cadangan (cek macet khas hari/jam itu).",
        "Tentukan driver + nomor WA + nomor cadangan.",
        "Siapkan di mobil: air, tisu, payung, charger, kitsi kecil.",
        "Share timeline ke WO, MUA, dan keluarga yang ikut konvoi.",
    ],
    "J02": [
        "Minta denah parkir resmi dari venue.",
        "Tandai zona: VIP, umum, vendor/loading.",
        "Desain papan penunjuk sederhana (panah + tulisan besar).",
        "Tentukan berapa petugas parkir & jam standby.",
        "Cetak/produksi signage; uji keterbacaan malam hari kalau resepsi malam.",
        "Brief petugas: prioritas VIP & jangan blokir jalur darurat.",
    ],
    "J06": [
        "Hitung jumlah crew vendor yang makan (tanya WO).",
        "Tentukan lokasi holding/makan crew jauh dari area tamu.",
        "Pesan menu crew ke katering (biasanya beda dari menu tamu).",
        "Jadwalkan jam makan supaya tidak bentrok saat service puncak.",
        "Siapkan air minum & tempat duduk sederhana.",
        "Tunjuk PIC yang arahkan crew ke area holding.",
    ],
    "J07": [
        "Buat daftar aset: milik sendiri / sewa vendor / pinjam keluarga.",
        "Isi kolom: barang | jumlah | pemilik | di mana disimpan | PIC kembali.",
        "Foto barang berharga sebelum dibawa ke venue.",
        "Cetak checklist untuk H-1 dan H+1.",
        "Saat load-out, centang satu per satu; tulis yang hilang/rusak.",
        "Update inventory final setelah semua kembali.",
    ],
    "J08": [
        "List VIP/pejabat yang butuh protokol khusus.",
        "Tulis: jam tiba perkiraan | dijemput siapa | duduk di mana | siapa dampingi.",
        "Siapkan parkir & jalur masuk khusus bila perlu.",
        "Brief usher: sapaan, gelar, jangan memfoto sembarangan jika ada aturan.",
        "Koordinasi dengan security untuk pengawalan ringan.",
        "Siapkan kontak aide/asisten VIP.",
    ],
    "K03": [
        "Buka Vendor Master, buat kolom “Call time H-1/H0”.",
        "Isi jam wajib datang tiap vendor (dekor, AVL, katering, MUA, foto, MC).",
        "Kirim broadcast WA personal (bukan hanya grup) berisi jam + lokasi + PIC.",
        "Minta balasan “OK” dari tiap PIC; centang di sheet.",
        "Yang belum balas dalam 24 jam: telepon langsung.",
        "Cetak call sheet final untuk WO di lokasi.",
    ],
    "K04": [
        "Export seating chart final ke PDF.",
        "Siapkan daftar nama place card (ejaan dicek 2 orang).",
        "Kirim file ke percetakan/stationery; minta sampel 1 lembar.",
        "Cetak semua + cadangan 10% nama kosong/salinan.",
        "Sortir place card per meja dalam amplop berlabel nomor meja.",
        "Pack signage arah (toilet, resepsi, photobooth) bersama.",
    ],
    "K05": [
        "Konfirmasi jumlah souvenir = headcount final + cadangan.",
        "Siapkan area packing bersih + tabel checklist.",
        "Pack per batch 20/50; timbang/hitung ulang tiap batch.",
        "Label box: isi berapa + untuk zona tamu mana.",
        "Sisihkan paket VIP terpisah jika beda isi.",
        "Foto box tertutup sebelum dimuat ke mobil.",
    ],
    "M02": [
        "Bawa checklist QC: AC dingin? toilet bersih/sabun/tisu? lampu? WIFI? jalur darurat?",
        "Cek power: stop kontak area panggung & dapur hidup.",
        "Cek kebersihan kaca, karpet, bau ruangan.",
        "Catat temuan + foto; langsung eskalasi ke PIC venue.",
        "Jangan anggap selesai sebelum temuan kritis ditutup atau ada workaround.",
        "Tanda tangan berita acara QC singkat dengan pihak venue.",
    ],
    "M05": [
        "Konfirmasi jam MUA datang & alamat lengkap semalam sebelumnya.",
        "Siapkan ruangan terang, stop kontak, gantungan baju, air minum.",
        "Urutkan wardrobe + aksesoris sesuai rundown (baju akad vs resepsi).",
        "Set alarm buffer 30 menit untuk keterlambatan.",
        "Dokumentasikan getting ready sesuai brief fotografer (jangan ganggu MUA).",
        "Sebelum berangkat: cek daftar barang wajib (cincin, surat, HP, powerbank).",
    ],
    "M07": [
        "Konfirmasi driver siap 30 menit sebelum call time.",
        "Masukkan barang emergency kit ke mobil.",
        "Update ETA ke WO saat berangkat dan saat 10 menit sebelum tiba.",
        "Pilih rute yang sudah direncanakan; jangan eksperimen jalan baru.",
        "Saat tiba: turun di titik yang sudah diarahkan usher.",
        "Kabari fotografer/WO “pengantin on site”.",
    ],
    "M09": [
        "Pastikan pintu dibuka sesuai jam rundown (tidak terlalu awal tanpa siap).",
        "Brief usher: alur salam, arah seating, posisi angpao.",
        "Cek musik/ambient menyala & volume nyaman.",
        "Pantau antrean 15 menit pertama; tambah petugas jika macet.",
        "Laporkan ke WO jika VIP belum datang mendekati momen penting.",
        "Jaga pintu tetap longgar untuk jalur darurat.",
    ],
    "M11": [
        "Dapatkan kontak PIC katering di lokasi.",
        "Cek 30 menit sebelum service: makanan siap, alat makan cukup, air tersedia.",
        "Pantau antrean buffet; minta buka line tambahan jika perlu.",
        "Prioritaskan meja VIP / orang tua jika ada service ke meja.",
        "Catat komplain makanan (habis/dingin) + jam kejadian.",
        "Eskalasi ke WO hanya untuk isu yang berdampak tamu luas.",
    ],
    "M12": [
        "Buat chat khusus “Issue H-day” berisi WO + PIC inti saja.",
        "Setiap isu tulis: jam | masalah | lokasi | siapa handle | status.",
        "Pisahkan isu kritis (keamanan/listrik/dokumen) vs isu kecil.",
        "Jangan terusik pasangan untuk isu operasional kecil.",
        "Update status isu sampai closed atau diwariskan ke H+1.",
        "Export chat/log di malam hari sebagai arsip.",
    ],
    "N02": [
        "Buka inventory aset J07.",
        "Cek tiap barang sewa/pinjam: ada? rusak? lengkap?",
        "Foto kondisi pengembalian.",
        "Hubungi pemilik/vendor untuk jadwal return.",
        "Minta surat/chat konfirmasi barang sudah diterima.",
        "Tandai di inventory: RETURNED + tanggal.",
    ],
    "N07": [
        "Buat daftar penerima thank-you: orang tua, VIP, petugas kunci, vendor berjasa.",
        "Tentukan bentuk: chat personal / kartu / oleh-oleh kecil.",
        "Tulis template ucapan, lalu personalisasi 1 kalimat per orang.",
        "Kirim dalam H+7 agar masih hangat.",
        "Centang sheet penerima yang sudah dikirimi.",
        "Simpan bukti pengiriman jika berupa paket.",
    ],
    "N11": [
        "Jadwalkan meeting singkat 30–45 menit (pasangan + PIC inti).",
        "Tiap orang sebut 2 hal bagus + 2 hal perlu diperbaiki.",
        "Catat pelajaran di Docs: orang | pelajaran | saran masa depan.",
        "Pastikan open item uang & dokumen sudah berstatus jelas.",
        "Tandai semua pekerjaan tersisa di Jadwal (Selesai/Terhambat beralasan).",
        "Ubah status proyek mental menjadi Closed; arsipkan folder induk.",
    ],
    # --- perbaikan audit: sebelumnya kena template salah ---
    "B02": [
        "Buat sheet: Jenis jasa | Vendor contoh | Harga rendah | Harga umum | Harga tinggi | Sumber info.",
        "Isi minimal: tempat, katering, dekor, WO, foto/video, MUA, hiburan, suara/lampu.",
        "Cari harga dari IG/WA saudara/teman yang baru menikah + 1–2 chat vendor (jangan minta proposal lengkap dulu).",
        "Catat satuan harga (per pax / paket / sewa hari) supaya bisa dibanding.",
        "Hitung kisaran total acara pakai harga “umum”, bandingkan dengan plafon kasar.",
        "Tandai 3 pos yang paling mahal / paling rawan naik.",
        "Simpan sebagai Benchmark-Harga-v1.xlsx (bukan angka final budget).",
    ],
    "B04": [
        "Ambil total rencana biaya dari pecahan budget (setelah B03).",
        "Hitung 10% dan 15% dari total itu — tulis dua opsi cadangan.",
        "Sepakati angka cadangan yang dipakai (misalnya 12%) dengan yang biayain.",
        "Taruh dana cadangan di baris terpisah di sheet budget (jangan “dimakan” pos lain).",
        "Tulis aturan: kapan boleh pakai cadangan (naik harga, perubahan wajib, bukan wishlist).",
        "Catat siapa yang boleh menyetujui pemakaian cadangan.",
        "Update plafon total = biaya rencana + cadangan.",
    ],
    "B05": [
        "Buat tabel: Tanggal perkiraan | Vendor/pos | Jenis bayar (DP/cicilan/lunas) | Nominal | Sumber uang.",
        "Isi dari kontrak yang sudah ada + rencana vendor yang belum dikontrak (perkiraan).",
        "Urutkan dari yang paling dekat bayarnya.",
        "Cek tiap bulan: apakah saldo rekening wedding cukup sebelum tanggal bayar?",
        "Kalau kurang: tulis opsi (undur non-kritis / tambah setoran / potong pos).",
        "Set pengingat HP H-7 sebelum tiap tanggal bayar besar.",
        "Simpan Cashflow-Wedding-v1 dan share ke Finance Lead + pasangan.",
    ],
    "C02": [
        "Tulis 3 opsi tone di notes: contoh formal khidmat / intimate hangat / garden cerah.",
        "Untuk tiap opsi isi: suasana 1 kalimat | contoh foto | pantangan (yang tidak diinginkan).",
        "Diskusi singkat dengan pasangan (15–20 menit), pilih 1 tone utama + 1 cadangan.",
        "Cek dengan 1 penentu keluarga apakah tone itu acceptable.",
        "Tulis keputusan final di satu baris: “Tone acara = …”.",
        "Simpan di folder Desain sebagai Tone-v1.pdf (bisa digabung moodboard).",
    ],
    "C03": [
        "Buat garis waktu kasar 1 halaman (bukan menit-per-menit): blok Pre → Akad → Resepsi → Selesai.",
        "Isi perkiraan jam mulai/selesai tiap blok (boleh ±30 menit).",
        "Tandai momen wajib di tiap blok (contoh akad: ijab, doa; resepsi: sambutan, makan).",
        "Catat asumsi lokasi (satu venue atau pindah lokasi).",
        "Kirim ke pasangan + WO (kalau sudah ada) untuk komentar “masuk akal/tidak”.",
        "Simpan Rundown-HighLevel-v1 — detail menit belakangan di fase susunan acara.",
    ],
    "C04": [
        "Buat tabel kasar: Kategori (VIP / keluarga / umum) | Perkiraan orang | Catatan.",
        "Isi angka dari pembicaraan kedua keluarga (bukan dari daftar nama lengkap dulu).",
        "Jumlahkan total perkiraan; bandingkan dengan kapasitas venue ide / plafon budget makan.",
        "Kalau total kebesaran: tulis opsi potong (kurangi umum / sesi terpisah / venue lebih besar).",
        "Sepakati “angka kerja” sementara (misalnya 400 pax) untuk brief vendor.",
        "Simpan Estimate-Tamu-v1 — ini bukan daftar tamu final.",
    ],
    "C05": [
        "Buka 1 dokumen “Design Brief” (1–2 halaman).",
        "Salin tone + warna dari moodboard; tulis suasana dalam 2–3 kalimat.",
        "Tambah: referensi foto (link/album), yang wajib ada, yang tidak diinginkan.",
        "Tambah teknis singkat: indoor/outdoor, jumlah tamu kasar, area prioritas (pelaminan/meja VIP).",
        "Baca ulang: pastikan orang awam (WO/dekor) langsung paham tanpa tanya berkali-kali.",
        "Kirim ke WO & vendor kreatif, minta konfirmasi “brief diterima”.",
        "Simpan Design-Brief-v1.pdf di folder Desain.",
    ],
    "D08": [
        "Minta ke venue: denah PDF/DWG + aturan listrik + jam load-in/out + akses lift/tangga.",
        "Simpan semua file di folder Venue/Teknis.",
        "Catat di notes: berapa kW tersedia, titik power, larangan (paku, open flame, dll).",
        "Forward paket teknis ke WO + dekor + suara/lampu.",
        "Tanya balik vendor: “ada yang kurang jelas?” — catat jawaban.",
        "Update sheet venue: “paket teknis lengkap = ya/tidak”.",
    ],
    "E26": [
        "Buat kalender/sheet: Tanggal bayar | Vendor | Nominal | Status | Bukti | PIC.",
        "Ambil tanggal dari semua kontrak yang sudah ditandatangani (DP, termin, pelunasan).",
        "Tambah perkiraan untuk vendor yang belum kontrak (beri warna beda = belum pasti).",
        "Sortir dari tanggal terdekat; set reminder HP untuk 5 pembayaran terbesar.",
        "Tiap kali bayar: update status + tempel link bukti di baris yang sama.",
        "Review mingguan 10 menit: ada yang jatuh tempo minggu ini?",
        "Share sheet ke Finance Lead + pasangan.",
    ],
    "F03": [
        "Ambil angka kapasitas duduk resmi dari venue (bukan kira-kira).",
        "Ambil total tamu rencana dari daftar/estimasi terkini.",
        "Hitung: tamu vs kursi/meja — sisakan buffer 5–10% kalau memungkinkan.",
        "Kalau overflow: tulis opsi (kurangi undangan / tambah sesi / ubah layout).",
        "Diskusikan opsi dengan pasangan + WO sebelum menambah undangan baru.",
        "Catat keputusan kapasitas kerja di sheet Tamu.",
    ],
    "F15": [
        "Export daftar tamu hadir (setelah RSVP memadai) ke sheet seating.",
        "Tandai meja VIP / keluarga inti / umum; patuhi pantangan duduk (yang tidak boleh berdekatan).",
        "Susun draft denah meja; minta cek 1 orang tiap keluarga.",
        "Revisi 1–2 putaran, lalu kunci versi seating.",
        "Buat daftar place card (nama sesuai undangan).",
        "Cetak/siapkan place card + denah untuk usher di hari-H.",
    ],
    "F16": [
        "Hitung tamu luar kota yang kemungkinan butuh hotel (dari daftar + RSVP).",
        "Shortlist 2–3 hotel dekat venue; cek harga & kuota.",
        "Negosiasi hotel block (kuota kamar + cutoff date).",
        "Buat info singkat untuk tamu: nama hotel, cara booking, siapa kontak.",
        "Kirim info ke VIP luar kota; catat siapa sudah booking.",
        "H-7: konfirmasi sisa kuota ke hotel.",
    ],
    "H01": [
        "Buka denah venue kosong; gambar area: pelaminan/aisle, VIP, buffet, panggung, FOOH, jalur tamu.",
        "Cek dengan aturan venue (larangan, lebar jalur, exit).",
        "Minta input WO + dekor + katering: apakah sirkulasi masuk akal.",
        "Revisi layout sampai tidak ada bottleneck (antrian makan/foto).",
        "Kunci Floorplan-Final.pdf dan share ke semua vendor terkait.",
        "Cetak 2–3 salinan untuk hari load-in.",
    ],
    "H09": [
        "Minta draft lighting plot dari vendor suara/lampu (area mana terang/redup).",
        "Susun daftar slot konten LED: jam | isi (slideshow, ucapan, logo, live).",
        "Cocokkan slot LED dengan rundown kasar.",
        "Approve plot + slot tertulis ke vendor AVL.",
        "Simpan file di folder Teknis/AVL.",
        "Pastikan ada cadangan konten kalau file gagal diputar.",
    ],
    "H10": [
        "Buat tabel mic: Siapa (MC, pengantin, wali, penyanyi) | Jenis mic | Kapan dipakai.",
        "Jadwalkan soundcheck: jam, siapa wajib hadir, lagu/tes ucapan.",
        "Konfirmasi ke AVL & hiburan: tech rider sudah cocok dengan listrik venue.",
        "Siapkan cadangan mic + batteries di notes PIC panggung.",
        "Setelah rencana OK, masukkan jam soundcheck ke rundown/call sheet.",
    ],
    "I02": [
        "Ambil rundown menit-per-menit sebagai tulang punggung.",
        "Tulis script MC: kalimat buka, transisi, undangan ke panggung, penutup (boleh singkat).",
        "Buat cue sheet: menit | apa yang terjadi | sinyal ke musik/LED | siapa di mic.",
        "Baca keras script 1x — potong kalimat yang terlalu panjang.",
        "Kirim ke MC & WO, minta koreksi factual (nama/gelar).",
        "Kunci Script-MC-vFinal.pdf.",
    ],
    "I03": [
        "Susun daftar lagu/instrumen per segmen: tamu datang, prosesi, makan, hiburan, penutup.",
        "Tandai lagu wajib keluarga vs freestyle DJ/band.",
        "Cek pantangan (lagu yang tidak diinginkan).",
        "Kirim setlist ke hiburan + AVL; minta konfirmasi bisa dimainkan.",
        "Simpan Playlist-v1 dan backup offline di USB/HP PIC.",
    ],
    "I04": [
        "Tulis urutan prosesi langkah demi langkah (siapa jalan kapan).",
        "Isi nama petugas nyata: wali, saksi, penjaga cincin, usher prosesi.",
        "Konfirmasi kesediaan + nomor WA tiap petugas.",
        "Latihan singkat di rumah/venue kalau perlu (terutama anak-anak).",
        "Masukkan urutan prosesi ke rundown & brief keluarga.",
        "Cetak 1 lembar ringkas untuk koordinator prosesi.",
    ],
    "I05": [
        "Sepakati deliverable: teaser berapa detik / cinematic berapa menit / kapan jadi.",
        "Kirim brief & referensi ke videografer.",
        "Jadwalkan syuting tambahan jika perlu (bukan hanya hari-H).",
        "Review draft 1x, beri catatan timestamp yang diganti.",
        "Approve final; simpan file master + versi LED/HP.",
    ],
    "I06": [
        "Kumpulkan foto yang akan tampil di LED (prewed, keluarga) + teks ucapan.",
        "Susun urutan slideshow; cek typo nama.",
        "Export resolusi sesuai permintaan vendor LED.",
        "Uji putar 1x di laptop; minta vendor konfirmasi format OK.",
        "Serahkan file + cadangan USB ke AVL sebelum H-1.",
    ],
    "J04": [
        "Putuskan: pakai petugas medis sewaan / dokter kenalan / P3K mandiri + ambulance on-call.",
        "Catat kontak darurat: nama | nomor | lokasi standby | jam tugas.",
        "Siapkan kotak P3K isi standar + obat pribadi pengantin jika perlu.",
        "Tentukan titik “pos medis” di venue (dekat toilet/parkir).",
        "Brief WO & security: kalau ada yang sakit, hubungi siapa dulu.",
        "Cetak kartu kontak medis untuk panitia inti.",
    ],
    "J05": [
        "List elemen outdoor yang rentan hujan/panas (dekor, prosesi, foto).",
        "Untuk tiap elemen tulis cadangan: pindah indoor / tenda / jadwal geser / cover.",
        "Tentukan “trigger”: jam berapa / kondisi apa keputusan diambil, siapa yang putuskan.",
        "Kabari vendor terkait soal kemungkinan ubah layout.",
        "Simpan Weather-Plan-1halaman.pdf di runbook.",
    ],
    "L06": [
        "Cek prakiraan cuaca H-3, H-1, dan pagi H0 (screenshot simpan).",
        "Bandingkan dengan trigger di rencana cuaca (J05).",
        "Jika mendekati trigger: rapat cepat WO + pasangan, putuskan opsi A/B.",
        "Kabari vendor yang terdampak dalam 1 pesan berantai.",
        "Update rundown singkat jika ada perubahan lokasi/jam.",
        "Dokumentasikan keputusan di Decision Log.",
    ],
    "L07": [
        "Siapkan pouchtas kecil: jarum-benang, double tape, plester, tisu, hand sanitizer, permen, obat pribadi, powerbank, uang cash kecil.",
        "Tambah item khusus: pods kontak lensa, hairpin, blotting paper (sesuai kebutuhan).",
        "Serahkan ke 1 orang pegang kit (bukan pengantin).",
        "Foto isi kit sebagai checklist; isi ulang yang habis setelah trial.",
        "Pastikan kit ikut di mobil menuju venue.",
    ],
    "M04": [
        "Konfirmasi dengan venue: boleh overnight? jam tutup? siapa kunci?",
        "Atur petugas jaga / security malam + kontak PIC.",
        "Catat barang berharga yang wajib dikunci / dibawa pulang sementara.",
        "Brief jaga: area patroli, larangan masuk orang asing, nomor darurat.",
        "Pagi H0: serah terima dari petugas malam ke WO (kondisi OK/ada isu).",
    ],
    "M10": [
        "Cetak rundown final + script MC untuk PIC panggung.",
        "Sebelum doors open: cek mic, LED, lineup hiburan siap.",
        "Jalankan acara sesuai cue; catat delay di notes (menit).",
        "Kalau molor >10 menit: potong segmen non-wajib bersama WO/MC.",
        "Pastikan momen wajib (sambutan/doa/hiburan utama) tetap jalan.",
        "Setelah program inti: konfirmasi ke WO “panggung clear”.",
    ],
}


def pick_steps(t):
    if t["id"] in SPECIFIC:
        return base_open(t) + SPECIFIC[t["id"]] + base_close(t)
    low = t["name"].lower()
    if "rfi" in low:
        return steps_rfi_rfp(t, "rfi")
    if "rfp" in low:
        return steps_rfi_rfp(t, "rfp")
    if "kontrak" in low or "tandatangan" in low:
        return steps_kontrak(t)
    if "fitting" in low:
        return steps_fitting(t)
    if "trial" in low and ("makeup" in low or "mua" in low or "hair" in low):
        return steps_trial_mua(t)
    # design brief sebelum "brief" meeting
    if "design brief" in low or (low.startswith("design") and "brief" in low):
        return base_open(t) + SPECIFIC.get("C05", [
            "Tulis brief desain 1–2 halaman: suasana, warna, referensi, pantangan.",
            "Kirim ke WO/vendor kreatif dan minta konfirmasi diterima.",
        ]) + base_close(t)
    if "undangan" in low or "cetak" in low or ("stationery" in low) or ("e-invite" in low) or ("launch website" in low):
        return steps_undangan(t)
    # jangan pakai kata "tamu" sendirian (banyak false positive)
    if "rsvp" in low or "guest list" in low or "seating" in low or "headcount" in low or "daftar tamu" in low:
        return steps_guest_rsvp(t)
    if "load-in" in low or "load-out" in low:
        return steps_load(t)
    if "rehearsal" in low or "soundcheck" in low or "latihan" in low:
        return steps_rehearsal(t)
    # cashflow / kalender termin bukan template "bayar sekarang"
    if "kalender termin" in low or "cashflow" in low:
        pass  # pakai SPECIFIC (E26/B05) — sudah di atas jika id match; else generic di akhir
    elif any(k in low for k in ["pembayaran", "pelunasan", "invoice", "retensi", "bayar"]) or (
        "termin" in low and "kalender" not in low
    ):
        return steps_bayar(t)
    if any(k in low for k in ["dokumen", "kua", "n1", "sipil", "kk", "buku nikah"]):
        return steps_dokumen(t)
    if "gate" in low or "approval" in low or "approve" in low:
        return steps_gate(t)
    if any(k in low for k in ["meeting", "sync", "kickoff", "debrief", "hot wash"]) or (
        "brief" in low and "design brief" not in low and "tech" not in low
    ):
        # "brief usher" dll tetap meeting-like OK; design brief sudah di atas
        if "design brief" not in low:
            return steps_meeting(t)
    if "tasting" in low or ("menu" in low and "matrix" not in low and "finalisasi" in low):
        return base_open(t) + [
            "Konfirmasi jam & lokasi tasting ke katering.",
            "Bawa maksimal 3–4 pengambil keputusan (jangan rombongan besar).",
            "Siapkan form skor sederhana: rasa 1–5, tampilan 1–5, porsi 1–5.",
            "Cicip tiap menu, tulis catatan jujur (terlalu asin, kurang hangat, dll).",
            "Tanyakan opsi alergi / vegetarian / anak-anak.",
            "Minta daftar final menu tertulis sebelum pulang.",
            "Di rumah: diskusikan 1 pilihan final, hubungi katering untuk mengunci.",
            "Pastikan menu final masuk kontrak atau addendum bertanda tangan.",
        ] + base_close(t)
    if "tasting" in low:
        return base_open(t) + [
            "Konfirmasi jam & lokasi tasting ke katering.",
            "Bawa maksimal 3–4 pengambil keputusan (jangan rombongan besar).",
            "Siapkan form skor sederhana: rasa 1–5, tampilan 1–5, porsi 1–5.",
            "Cicip tiap menu, tulis catatan jujur (terlalu asin, kurang hangat, dll).",
            "Tanyakan opsi alergi / vegetarian / anak-anak.",
            "Minta daftar final menu tertulis sebelum pulang.",
            "Di rumah: diskusikan 1 pilihan final, hubungi katering untuk mengunci.",
            "Pastikan menu final masuk kontrak atau addendum bertanda tangan.",
        ] + base_close(t)
    # survey harga ≠ survey venue
    if "benchmark" in low or ("harga" in low and "survey" in low):
        return base_open(t) + SPECIFIC["B02"] + base_close(t)
    if "site visit" in low or ("venue" in low and ("survey" in low or "visit" in low or "shortlist" in low or "bandingkan" in low)) or (
        "survey venue" in low or "survey lokasi" in low
    ):
        return base_open(t) + [
            "Buat daftar lokasi kandidat (nama, alamat, kontak, kapasitas, harga sewa kasar).",
            "Telepon/WA dulu: cek ketersediaan tanggal & jam buka untuk survey.",
            "Siapkan checklist survey: AC, toilet, parkir, listrik, dapur, akses difabel, aturan musik.",
            "Datang ke lokasi, foto sudut ruangan (jangan cuma foto estetik).",
            "Tanya biaya tersembunyi: overtime, cleaning, deposit, parkir tamu.",
            "Isi skor 1–5 per lokasi di sheet yang sama.",
            "Diskusikan shortlist 3–4 lokasi dengan keluarga inti.",
            "Untuk site visit final: bawa WO/pasangan, ukur ulang kapasitas duduk.",
        ] + base_close(t)
    if "moodboard" in low or (("tema" in low or "tone" in low) and "busana" not in low and "rundown" not in low):
        return base_open(t) + [
            "Kumpulkan 15–30 foto referensi (Pinterest/IG) ke 1 album.",
            "Pilih 1 kata suasana: khidmat / hangat / garden / modern, dll.",
            "Pilih 3–4 warna utama (contoh swatch).",
            "Buat 1 halaman ringkas: suasana + warna + contoh foto + yang tidak diinginkan.",
            "Tunjukkan ke pasangan & 1 orang keluarga penentu, minta setuju/tolak.",
            "Simpan file final sebagai “Design Brief v1” untuk dikirim ke vendor.",
        ] + base_close(t)
    if "rundown" in low or "script" in low or "playlist" in low or "prosesi" in low:
        return base_open(t) + [
            "Buka template tabel: Jam | Kegiatan | Siapa pegang | Butuh mic/musik | Catatan.",
            "Isi dari paling pagi (bersiap) sampai acara selesai.",
            "Tandai momen wajib: akad, salam, makan, hiburan, penutup.",
            "Isi nama petugas nyata (bukan “panitia”), dual-check nomor WA mereka.",
            "Kirim draft ke WO & MC, minta koreksi dalam 48 jam.",
            "Update versi (v1 → v2), jangan timpa file lama tanpa ganti nama.",
            "Setelah disetujui, export PDF dan share ke semua petugas.",
        ] + base_close(t)
    # contingency budget ≠ rencana darurat; medical/weather/security/runbook tetap
    if "runbook" in low or "emergency kit" in low or (
        "weather" in low and "contingency" in low
    ) or ("security" in low and "crowd" in low) or "medical" in low or "p3k" in low:
        return base_open(t) + [
            "Buat dokumen 1 halaman: judul “Kalau terjadi masalah”.",
            "Isi tabel kontak: nama | peran | nomor | cadangan.",
            "Tulis 4–6 skenario relevan untuk pekerjaan ini.",
            "Untuk tiap skenario tulis: siapa bertindak + langkah 1-2-3.",
            "Cetak beberapa lembar / simpan PDF di HP PIC.",
            "Brief singkat orang terkait: “kalau X, hubungi Y”.",
        ] + base_close(t)
    if "alokasi contingency" in low or (low.startswith("alokasi") and "contingency" in low):
        return base_open(t) + SPECIFIC["B04"] + base_close(t)
    if "prewedding" in low or "shot list" in low or "album" in low or "cinematic" in low or "teaser" in low or ("led" in low and "konten" in low) or ("foto" in low and "prewed" in low):
        return base_open(t) + [
            "Tulis daftar momen/foto yang wajib (daftar shot) di notes.",
            "Kirim daftar itu ke fotografer/videografer, minta konfirmasi bisa/tidak.",
            "Siapkan wardrobe, lokasi, izin lokasi, dan jadwal makeup kalau perlu.",
            "Di hari syuting: datang tepat waktu, bawa air & snack kecil.",
            "Review hasil kasar di kamera sebelum pulang (kalau memungkinkan).",
            "Saat menerima file: cek kelengkapan folder & backup ke Drive + HDD.",
            "Pilih foto/video final, beri batas waktu revisi tertulis.",
            "Simpan versi final dengan nama jelas untuk undangan/LED/album.",
        ] + base_close(t)
    if "freeze" in low or (("final" in low or "lock" in low) and ("guest" in low or "headcount" in low or "change" in low or "rundown" in low)):
        return base_open(t) + [
            "Umumkan ke grup: mulai sekarang perubahan besar harus lewat izin.",
            "Tulis apa yang dikunci (tamu / menu / desain / rundown).",
            "Simpan file bertanggal sebagai versi final.",
            "Tolak permintaan perubahan yang tidak darurat dengan sopan + alasan.",
            "Catat exception (kalau ada) di decision log: siapa setuju.",
        ] + base_close(t)
    return steps_generic(t)


# Esensi singkat per pekerjaan (bukan ulang penjelasan fase)
ESENSI = {
    "A01": "Rapat pertama keluarga inti: sepakati visi acara, gaya kasar, dan siapa yang ikut putuskan.",
    "A02": "Tulis daftar acara yang benar-benar diurus (akad, resepsi, pre-event, dll) supaya scope jelas.",
    "A03": "Buat tabel siapa mengerjakan, siapa putuskan final, dan siapa hanya dikabari — biar tidak bentrok.",
    "A04": "Ringkas aturan proyek + catatan keputusan penting di satu tempat yang semua bisa baca.",
    "A05": "Siapkan folder Drive, grup WA, dan sheet master supaya semua file/kontak tidak berceceran.",
    "A06": "Catat risiko & asumsi awal (misalnya hujan, budget molor) supaya bisa diantisipasi.",
    "A07": "Petakan orang penting di kedua keluarga + tokoh yang harus dilibatkan/diberi kabar.",
    "A08": "Cek apakah perencanaan awal sudah cukup untuk lanjut ke tahap budget (go/no-go).",
    "B01": "Kumpulkan angka plafon dari kedua keluarga: berapa maksimal yang boleh dikeluarkan.",
    "B02": "Survey kasar harga pasar lokal (venue, katering, dll) supaya budget tidak mengarang.",
    "B03": "Pecah budget ke pos-pos biaya (venue, makan, dekor, dll) biar terlihat ke mana uangnya.",
    "B04": "Sisihkan dana cadangan 10–15% untuk kejutan harga atau perubahan mendadak.",
    "B05": "Susun jadwal kapan bayar DP, cicilan, dan pelunasan supaya uang tidak macet.",
    "B06": "Buka rekening/wallet khusus wedding agar uang acara tidak tercampur uang harian.",
    "B07": "Minta persetujuan resmi budget dasar dari penentu final sebelum belanja besar.",
    "B08": "Siapkan cara cek mingguan: rencana vs pengeluaran aktual.",
    "C01": "Kumpulkan referensi visual + palet warna supaya semua bayangan acaranya sama.",
    "C02": "Pilih tone acara (formal / intimate / garden, dll) sebagai panduan vendor.",
    "C03": "Buat alur kasar: sebelum akad → akad → resepsi, tanpa detail menit dulu.",
    "C04": "Perkirakan jumlah tamu VIP vs umum supaya kapasitas & budget masuk akal.",
    "C05": "Tulis brief desain singkat untuk WO & vendor kreatif (warna, suasana, pantangan).",
    "C06": "Kunci arah desain yang disetujui keluarga sebelum vendor mulai produksi.",
    "D01": "Pilih 3–5 kandidat tanggal acara untuk dibahas keluarga.",
    "D02": "Cek tanggal itu tidak bentrok dengan keluarga besar / tokoh penting.",
    "D03": "Cari banyak lokasi kandidat (longlist) sebelum menyaring.",
    "D04": "Kunjungi 3–4 venue terbaik untuk melihat kondisi nyata.",
    "D05": "Bandingkan proposal tempat dengan skor (harga, kapasitas, fasilitas, aturan).",
    "D06": "Kunci tanggal & bayar DP venue supaya slot tidak diambil orang lain.",
    "D07": "Baca & tanda tangan kontrak venue setelah syaratnya cocok.",
    "D08": "Ambil denah + aturan listrik/loading dari venue untuk vendor teknis.",
    "D09": "Cek syarat resmi KUA / catatan sipil di wilayah Anda.",
    "D10": "Kumpulkan surat/dokumen (sering disebut N1–N5 atau setara) sampai lengkap.",
    "D11": "Daftar dan kunci jadwal akad dengan KUA/penghulu.",
    "D12": "Pertimbangkan asuransi acara (opsional) kalau risikonya besar.",
    "E01": "Minta info/penawaran dari beberapa Wedding Organizer.",
    "E02": "Wawancara WO, cek portfolio, dan rasa kerja sama.",
    "E03": "Negosiasi lingkup kerja & siapa kerjakan apa, lalu kontrak WO.",
    "E04": "Kickoff dengan WO: samakan timeline master semua pihak.",
    "E05": "Kirim brief katering (menu, porsi, tasting) ke beberapa calon.",
    "E06": "Cicip makanan dan kunci menu final.",
    "E07": "Tanda tangan kontrak katering + bayar deposit.",
    "E08": "Minta penawaran dekorasi/florist/styling dari beberapa calon.",
    "E09": "Lihat presentasi konsep dekor (layout/3D) lalu pilih arah.",
    "E10": "Kontrak dekorasi dan catat lead time bahan/bunga.",
    "E11": "Minta penawaran foto & video (prewed + hari-H).",
    "E12": "Kontrak foto/video dan draft daftar momen wajib yang harus difoto/direkam.",
    "E13": "Minta penawaran MUA/hair termasuk jadwal trial.",
    "E14": "Kontrak MUA dan booking slot trial.",
    "E15": "Minta penawaran hiburan (MC/band/DJ/qori).",
    "E16": "Kontrak hiburan + daftar kebutuhan suara/lampu dari mereka.",
    "E17": "Minta penawaran sound/lighting/LED jika terpisah dari hiburan.",
    "E18": "Kontrak suara/lampu/LED dan cek daya listrik di tempat acara.",
    "E19": "Minta penawaran undangan cetak, digital, dan website.",
    "E20": "Kontrak undangan & situs undangan.",
    "E21": "Minta penawaran souvenir / welcome gift.",
    "E22": "Kontrak souvenir dan catat lama produksi.",
    "E23": "Minta penawaran mobil pengantin / shuttle.",
    "E24": "Kontrak transport + rencana rute hari-H.",
    "E25": "Buat daftar master semua vendor + janji layanan yang disepakati.",
    "E26": "Kalenderkan semua tanggal bayar ke vendor supaya tidak kelewatan.",
    "F01": "Buat draft pertama daftar tamu dari kedua keluarga.",
    "F02": "Pisahkan VIP, keluarga, dan tamu umum.",
    "F03": "Cek jumlah tamu masih muat di kapasitas tempat duduk venue.",
    "F04": "Kunci teks undangan + sistem QR RSVP.",
    "F05": "Desain undangan (revisi terbatas) sampai mendekati final.",
    "F06": "Approve artwork final sebelum dicetak massal.",
    "F07": "Cetak undangan fisik dan cek kualitas batch.",
    "F08": "Publish website/e-invite + form RSVP.",
    "F09": "Kirim save-the-date digital ke VIP lebih dulu.",
    "F10": "Bagikan undangan gelombang 1 (VIP).",
    "F11": "Bagikan undangan gelombang 2 (umum).",
    "F12": "Follow-up RSVP tiap minggu untuk yang belum jawab.",
    "F13": "Kunci daftar tamu v2 sekitar H-21 (freeze).",
    "F14": "Kirim angka final ke katering sekitar H-14.",
    "F15": "Susun seating chart + place card.",
    "F16": "Atur hotel block / akomodasi untuk tamu luar kota.",
    "G01": "Kumpulkan 3 look referensi busana pengantin.",
    "G02": "Booking bridal/beskap dan jadwal fitting.",
    "G03": "Kontrak jahit/sewa + bayar DP.",
    "G04": "Fitting 1: ukur dasar dan catat perbaikan.",
    "G05": "Fitting 2: sesuaikan hasil perbaikan.",
    "G06": "Fitting final + cek aksesoris sekitar H-14.",
    "G07": "Urus busana keluarga inti & bridesmaid.",
    "G08": "Trial makeup & hair pertama.",
    "G09": "Trial makeup kedua + foto test look final.",
    "G10": "Jadwalkan skincare/treatment jauh-jauh hari (hindari eksperimen mepet).",
    "G11": "Rencana prewedding: lokasi, baju, daftar foto, izin.",
    "G12": "Eksekusi hari syuting prewedding.",
    "G13": "Pilih foto prewed untuk undangan/layar.",
    "H01": "Kunci denah lantai final (lorong, VIP, buffet, panggung).",
    "H02": "Lihat sample bahan & bunga sebelum produksi massal.",
    "H03": "Setujui paket dekor final yang akan dipasang.",
    "H04": "Pesan bunga impor/non-seasonal lebih awal (lead time panjang).",
    "H05": "Catat pantangan makan (halal/alergi/VIP) per meja/tamu.",
    "H06": "Desain & pesan cake / dessert table.",
    "H07": "Rencana bar / soft drink / coffee station.",
    "H08": "Hitung rasio waiter/usher vs jumlah tamu.",
    "H09": "Susun lighting plot & slot konten LED.",
    "H10": "Rencana soundcheck + alokasi mic (MC, pengantin, tokoh).",
    "H11": "Putuskan perlu genset/backup power atau tidak.",
    "H12": "Susun jadwal load-in/load-out bersama aturan venue.",
    "I01": "Buat rundown detail menit-per-menit versi 1.",
    "I02": "Tulis script MC + cue sheet (kapan bicara/musik).",
    "I03": "Susun playlist/setlist musik sepanjang acara.",
    "I04": "Urutkan prosesi & petugas (wali, saksi, dll).",
    "I05": "Produksi video cinematic/teaser (jika ada).",
    "I06": "Siapkan konten LED: slideshow + ucapan.",
    "I07": "Atur alur kartu ucapan / guestbook / angpao.",
    "I08": "Brief usher & koordinator keluarga soal tugas hari-H.",
    "I09": "Kunci rundown final (titik persetujuan program) yang disetujui.",
    "J01": "Rencana transport pengantin di hari-H (rute & jam).",
    "J02": "Atur parkir + penunjuk arah supaya tamu tidak bingung.",
    "J03": "Brief keamanan & pengaturan kerumunan.",
    "J04": "Rencana medis/P3K standby di lokasi.",
    "J05": "Rencana cadangan cuaca (jika ada elemen outdoor).",
    "J06": "Siapkan makan crew & area tunggu vendor.",
    "J07": "Inventaris barang sewa/beli supaya tidak hilang.",
    "J08": "Protokol komunikasi jika ada VIP/pejabat.",
    "J09": "Buat lembar 1 halaman: kontak darurat + skenario masalah.",
    "J10": "Rencana latihan + daftar jam datang petugas.",
    "K01": "Rapat sync vendor #1 sekitar H-60.",
    "K02": "Cek & bayar cicilan tengah sesuai kontrak.",
    "K03": "Konfirmasi jam datang semua vendor di hari-H.",
    "K04": "Cetak place card, name tag, dan signage.",
    "K05": "Packing souvenir + quality check.",
    "K06": "Cek ulang dokumen legal/KUA sudah siap.",
    "K07": "Rapat sync vendor #2 sekitar H-30.",
    "K08": "Freeze perubahan besar: scope tidak diubah-ubah lagi.",
    "L01": "Kunci jumlah tamu final & surat pesanan ke katering.",
    "L02": "Fitting final busana + rencana setrika/steam.",
    "L03": "Latihan on-site prosesi + cue.",
    "L04": "Latihan teknis suara/layar.",
    "L05": "Brief singkat keluarga & petugas inti.",
    "L06": "Konfirmasi cuaca & kapan trigger rencana cadangan.",
    "L07": "Pack emergency kit pengantin (bantalan, jarum, obat, dll).",
    "L08": "Pelunasan vendor sesuai kontrak sebelum hari-H.",
    "M01": "H-1: mulai pasang dekor & suara/lampu/LED.",
    "M02": "H-1: cek venue (AC, toilet, listrik, WIFI).",
    "M03": "H-1: pasang seating, signage, souvenir.",
    "M04": "H-1: amankan lokasi semalaman (satpam/kunci).",
    "M05": "H0 pagi: MUA datang & sesi bersiap pengantin.",
    "M06": "H0 pagi: foto sesi bersiap.",
    "M07": "H0: antar pengantin ke lokasi akad tepat waktu.",
    "M08": "H0: pelaksanaan akad + dokumen resmi.",
    "M09": "H0: buka pintu & menyambut tamu resepsi.",
    "M10": "H0: jalankan program panggung sesuai rundown.",
    "M11": "H0: pantau layanan makanan & minuman.",
    "M12": "H0: catat isu real-time & eskalasi ke orang yang tepat.",
    "M13": "H0 sore/malam: bongkar barang & serah terima venue.",
    "N01": "H+1: evaluasi singkat dengan WO (apa yang bagus/buruk).",
    "N02": "Kembalikan barang sewa + centang inventaris.",
    "N03": "Cocokkan semua tagihan vendor vs kontrak.",
    "N04": "Bayar sisa tagihan / dana ditahan yang belum lunas.",
    "N05": "Terima raw foto/video + cek kelengkapan.",
    "N06": "Edit final album / highlight film.",
    "N07": "Kirim ucapan terima kasih / gift ke keluarga & VIP.",
    "N08": "Urus dokumen pasca-nikah (buku nikah, dll).",
    "N09": "Update data sipil / KK / rekening jika perlu.",
    "N10": "Arsipkan kontrak, foto, laporan ke folder induk.",
    "N11": "Catat pelajaran + tutup proyek secara resmi.",
}


def tujuan_of(t):
    e = ESENSI.get(t["id"])
    if e:
        return e
    return (
        f"Garis besarnya: menyelesaikan “{t['name']}” sampai hasilnya jelas dan bisa dipakai langkah berikutnya."
    )


def hasil_of(t):
    """Deliverable konkret per task (fallback per pola jika belum ada)."""
    HASIL = {
        "A01": "Notulen kickoff + daftar tugas (nama | tugas | tenggat) terkirim ke grup inti.",
        "A02": "Dokumen Scope v1: daftar acara yang diurus / tidak diurus, disetujui pasangan.",
        "A03": "Tabel RACI keluarga (siapa kerjakan/putuskan/dikabari) tersimpan & dipin di grup.",
        "A04": "Project Charter + Decision Log v1 dibagikan ke penentu final.",
        "A05": "Folder Drive + grup WA + sheet master hidup dan bisa diakses orang inti.",
        "A06": "Risk register + daftar asumsi v1 (minimal 8 risiko) di folder bersama.",
        "A07": "Peta stakeholder (nama, pengaruh, cara komunikasi) dalam PDF/sheet.",
        "A08": "Keputusan go/no-go tertulis + alasan, dicatat di Decision Log.",
        "B01": "Angka plafon kontribusi kedua keluarga tertulis (min–max atau angka tengah).",
        "B02": "Sheet benchmark harga lokal per jenis jasa (bukan kontrak).",
        "B03": "Pecahan biaya per pos (cost breakdown) vs plafon.",
        "B04": "Baris dana cadangan 10–15% + aturan pemakaian di sheet budget.",
        "B05": "Tabel jadwal bayar (tanggal | pos | nominal | sumber uang).",
        "B06": "Rekening/wallet khusus wedding aktif + bukti uji transfer.",
        "B07": "Persetujuan budget dasar dari penentu final (chat/tanda tangan).",
        "B08": "Sheet tracking mingguan rencana vs aktual siap dipakai.",
        "C01": "Moodboard + palet warna disetujui pasangan.",
        "C02": "Keputusan tone acara 1 kalimat tertulis.",
        "C03": "Rundown high-level Pre→Akad→Resepsi (jam kasar).",
        "C04": "Estimate jumlah VIP/umum + angka kerja untuk brief vendor.",
        "C05": "Design Brief 1–2 halaman terkirim ke WO/vendor kreatif.",
        "C06": "Persetujuan arah desain (approval) tercatat.",
        "D01": "Shortlist 3–5 tanggal berprioritas.",
        "D02": "Tabel cek bentrok tokoh/keluarga besar.",
        "D03": "Longlist 8–12 lokasi + kontak.",
        "D04": "Catatan site visit 3–4 venue + foto.",
        "D05": "Scorecard banding venue + rekomendasi pemenang.",
        "D06": "Bukti booking/DP venue + tanggal terkunci.",
        "D07": "Kontrak venue bertanda tangan + file tersimpan.",
        "D08": "Paket denah + aturan listrik/loading di folder Venue/Teknis.",
        "D09": "Checklist syarat KUA/sipil sesuai wilayah.",
        "D10": "Paket dokumen N1–N5/setara lengkap (scan).",
        "D11": "Jadwal akad resmi dari KUA/penghulu.",
        "D12": "Keputusan asuransi (ambil/tidak) + alasan tertulis.",
        "E25": "Vendor master register + janji layanan per vendor.",
        "E26": "Kalender semua tanggal bayar vendor + reminder.",
        "F01": "Draft guest list v1 gabungan kedua keluarga.",
        "F02": "Guest list terbagi VIP / keluarga / umum.",
        "F03": "Catatan kapasitas venue vs jumlah tamu + keputusan jika overflow.",
        "F13": "Guest list freeze v2 bertanggal.",
        "F14": "Angka final terkirim ke katering (bukti chat/email).",
        "F15": "Seating chart + place card siap cetak.",
        "F16": "Info hotel block + daftar tamu yang sudah booking.",
        "H01": "Floorplan final PDF tershare ke vendor terkait.",
        "J04": "Kontak medis/P3K + titik pos medis tertulis.",
        "J05": "Rencana cuaca 1 halaman + trigger keputusan.",
        "J09": "Runbook H-day 1 halaman (kontak + skenario).",
        "L07": "Emergency kit terisi + PIC pemegang kit.",
        "N03": "Rekonsiliasi invoice vs kontrak (sheet berstatus lunas/sisa).",
        "N10": "Folder arsip proyek lengkap (kontrak, foto, laporan).",
        "N11": "Dokumen lessons learned + status proyek ditutup.",
    }
    if t["id"] in HASIL:
        return HASIL[t["id"]]
    low = t["name"].lower()
    if "kontrak" in low or "tandatangan" in low:
        return "Kontrak bertanda tangan + bukti DP/kwitansi + file di folder Kontrak."
    if "rfi" in low or "rfp" in low:
        return "Folder penawaran + tabel banding + rekomendasi vendor tertulis."
    if "undangan" in low or "cetak" in low or "e-invite" in low or "website" in low:
        return "File/undangan final tanpa typo penting + siap distribusi."
    if "meeting" in low or "sync" in low or "kickoff" in low or "debrief" in low or "hot wash" in low:
        return "Notulen + daftar tugas (nama, tugas, tenggat) yang sudah dikirim."
    if "fitting" in low or "trial" in low:
        return "Catatan hasil + foto + jadwal perbaikan/trial berikutnya (kalau ada)."
    if "gate" in low or "approve" in low or "approval" in low:
        return "Keputusan setuju/tolak tertulis + versi file yang dikunci."
    if "pembayaran" in low or "pelunasan" in low or "bayar" in low or "termin" in low or "invoice" in low:
        return "Bukti transfer + kwitansi + baris kalender bayar ter-update."
    if "load-in" in low or "load-out" in low:
        return "Checklist loading tercentang + foto kondisi + serah terima (kalau ada)."
    return f"Bukti konkret untuk “{t['name']}” (file/foto/chat) tersimpan + orang terkait dikabari."


def selesai_of(t):
    SELESAI = {
        "A01": "Semua peserta kunci sudah dapat notulen & tugas, tidak ada keputusan mengambang.",
        "A02": "Pasangan + penentu setuju daftar acara Scope v1.",
        "A03": "Tidak ada 2 penentu final bentrok untuk keputusan kritis.",
        "A08": "Ada keputusan tegas lanjut/ berhenti/ revisi sebelum fase budget.",
        "B04": "Angka cadangan & aturan pakai disetujui yang biayain.",
        "B05": "Semua tanggal bayar besar punya sumber uang yang masuk akal.",
        "B07": "Penentu final bilang “budget dasar OK” secara tertulis.",
        "C05": "WO/vendor kreatif konfirmasi brief diterima.",
        "C06": "Arah desain dikunci; perubahan besar harus lewat izin.",
        "D06": "Tanggal & venue terkunci dengan bukti DP.",
        "E26": "Semua kontrak aktif masuk kalender bayar + reminder hidup.",
        "F13": "Daftar tamu diumumkan freeze; perubahan hanya exception.",
        "F14": "Katering acknowledge angka final.",
        "H01": "WO+dekor+katering setuju floorplan final.",
        "I09": "Rundown final disetujui WO+pasangan (+MC jika perlu).",
        "L01": "PO/angka katering terkunci sesuai headcount.",
        "N11": "Tidak ada open item kritis uang/dokumen; folder diarsipkan.",
    }
    if t["id"] in SELESAI:
        return SELESAI[t["id"]]
    return (
        f"“{t['name']}” dianggap selesai jika hasil di atas ada, bukti tersimpan, "
        "status Jadwal = Selesai (atau Terhambat dengan alasan jelas), dan pihak terkait sudah dikabari."
    )


def hindari_of(t):
    low = t["name"].lower()
    base = "Menandai Selesai tanpa bukti; mengerjakan sendirian tanpa kabari penanggung jawab; melewatkan syarat sebelumnya tanpa izin."
    if "kontrak" in low:
        return base + " Jangan tanda tangan jika lampiran (menu/denah/harga) belum cocok."
    if "bayar" in low or "pelunasan" in low or "termin" in low or "invoice" in low:
        return base + " Jangan transfer ke rekening yang tidak tertulis di kontrak."
    if "gate" in low or "approve" in low:
        return base + " Jangan “approve lisan saja” tanpa catatan keputusan."
    if "undangan" in low or "cetak" in low:
        return base + " Jangan cetak massal sebelum nama/tanggal/jam dicek 2 orang."
    if "contingency" in low and "alokasi" in low:
        return base + " Jangan pakai dana cadangan untuk wishlist non-darurat."
    return base


defs = {}
for t in payload["tasks"]:
    steps = pick_steps(t)
    cleaned = []
    for s in steps:
        if not cleaned or cleaned[-1] != s:
            cleaned.append(s)
    defs[t["id"]] = {
        "nama": t["name"],
        "wbs": t["wbs"],
        "phase": t["phase"],
        "phase_nama": PHASES_SIMPLE.get(t["phase"], t["phase"]),
        "deps": t.get("deps") or [],
        "cp": bool(t.get("cp")),
        "pic": t["owner"],
        "vendor": t["vendor"],
        "konteks_fase": PHASE_CONTEXT.get(t["phase"], ""),
        "esensi": tujuan_of(t),
        "tujuan": tujuan_of(t),
        "langkah": cleaned,
        "hasil": hasil_of(t),
        "selesai_bila": selesai_of(t),
        "hindari": hindari_of(t),
    }

payload["phases"] = PHASES_SIMPLE
(ROOT / "js" / "data.js").write_text(
    "window.WP_DEFAULT = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
(ROOT / "js" / "definitions.js").write_text(
    "window.WP_DEFINITIONS = " + json.dumps(defs, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
avg = sum(len(d["langkah"]) for d in defs.values()) / len(defs)
print(f"Wrote {len(defs)} defs, avg steps={avg:.1f}")
# sanity: mismatched ids must not share emergency/venue opening
bad = []
checks = {
    "B02": "Benchmark-Harga",
    "B04": "dana cadangan",
    "B05": "Cashflow-Wedding",
    "C04": "Estimate-Tamu",
    "C05": "Design Brief",
    "E26": "Kalender semua tanggal",
}
for tid, needle in checks.items():
    blob = " ".join(defs[tid]["langkah"])
    if needle.lower() not in blob.lower() and needle not in blob:
        # softer contains
        if not any(n.lower() in blob.lower() for n in needle.split()):
            bad.append(tid + " missing " + needle)
    if "Kalau terjadi masalah" in blob and tid in ("B02", "B04", "B05", "C04", "C05", "E26"):
        bad.append(tid + " still emergency template")
    if "daftar lokasi kandidat" in blob and tid == "B02":
        bad.append("B02 still venue survey")
print("sanity_bad", bad or "OK")