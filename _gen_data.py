# -*- coding: utf-8 -*-
"""Generate default data.js for H-120..H+14 wedding planner."""
import json
from pathlib import Path

# Same tasks as Excel (id, wbs, name, phase, start_week, dur_week, deps, owner, vendor, cp)
TASKS = [
    ("A01", "1.1", "Kickoff keluarga inti + visi pasangan", "P0", 0, 1, [], "Pasangan", "Internal", True),
    ("A02", "1.2", "Definisikan scope acara (akad/resepsi/pre-event)", "P0", 1, 1, ["A01"], "Pasangan", "Internal", True),
    ("A03", "1.3", "Susun RACI keluarga (siapa putuskan apa)", "P0", 1, 1, ["A01"], "PM Keluarga", "Internal", False),
    ("A04", "1.4", "Buat project charter & decision log", "P0", 2, 1, ["A02", "A03"], "PM Keluarga", "Internal", True),
    ("A05", "1.5", "Setup tools (drive, WA grup, sheet master)", "P0", 2, 1, ["A01"], "PM Keluarga", "Internal", False),
    ("A06", "1.6", "Risk register awal + assumptions log", "P0", 3, 1, ["A04"], "PM Keluarga", "Internal", False),
    ("A07", "1.7", "Stakeholder map (kedua keluarga + tokoh)", "P0", 3, 1, ["A03"], "PM Keluarga", "Internal", False),
    ("A08", "1.8", "Gate review: go/no-go planning formal", "P0", 4, 1, ["A04", "A06"], "Pasangan", "Internal", True),
    ("B01", "2.1", "Kumpulkan target budget kedua keluarga", "P1", 2, 2, ["A02"], "Finance Lead", "Internal", True),
    ("B02", "2.2", "Benchmark harga vendor lokal (survey kasar)", "P1", 3, 2, ["B01"], "Finance Lead", "Internal", False),
    ("B03", "2.3", "WBS cost breakdown (CAPEX acara)", "P1", 5, 2, ["B01", "B02", "A08"], "Finance Lead", "Internal", True),
    ("B04", "2.4", "Alokasi contingency 10–15%", "P1", 6, 1, ["B03"], "Finance Lead", "Internal", True),
    ("B05", "2.5", "Cashflow plan (DP / termin / pelunasan)", "P1", 7, 1, ["B03"], "Finance Lead", "Internal", True),
    ("B06", "2.6", "Buka rekening / wallet khusus wedding", "P1", 5, 1, ["B01"], "Finance Lead", "Bank", False),
    ("B07", "2.7", "Approval budget baseline (Gate B)", "P1", 8, 1, ["B04", "B05"], "Pasangan", "Internal", True),
    ("B08", "2.8", "Setup tracking actual vs budget (mingguan)", "P1", 8, 1, ["B07"], "Finance Lead", "Internal", False),
    ("C01", "3.1", "Moodboard tema & palet warna", "P2", 4, 2, ["A02"], "Creative Lead", "Internal", False),
    ("C02", "3.2", "Pilih tone acara (formal/intimate/garden)", "P2", 5, 1, ["C01", "A08"], "Pasangan", "Internal", True),
    ("C03", "3.3", "Draft rundown high-level (pre→akad→resepsi)", "P2", 6, 1, ["C02"], "PM Keluarga", "Internal", True),
    ("C04", "3.4", "Estimate kapasitas tamu (VIP / umum)", "P2", 6, 1, ["A02", "B01"], "Guest Lead", "Internal", True),
    ("C05", "3.5", "Design brief untuk WO & vendor kreatif", "P2", 7, 1, ["C02", "C03"], "Creative Lead", "Internal", True),
    ("C06", "3.6", "Gate design direction approved", "P2", 8, 1, ["C05", "B07"], "Pasangan", "Internal", True),
    ("D01", "4.1", "Shortlist 3–5 tanggal kandidat", "P3", 5, 1, ["A08"], "Pasangan", "Internal", True),
    ("D02", "4.2", "Cek kalender keluarga besar & tokoh", "P3", 5, 1, ["D01", "A07"], "PM Keluarga", "Internal", False),
    ("D03", "4.3", "Survey venue longlist (8–12 lokasi)", "P3", 6, 2, ["C02", "C04"], "Venue Lead", "Venue", True),
    ("D04", "4.4", "Site visit shortlist (3–4 venue)", "P3", 8, 2, ["D03", "B07"], "Venue Lead", "Venue", True),
    ("D05", "4.5", "Bandingkan proposal venue (scorecard)", "P3", 9, 1, ["D04"], "Venue Lead", "Internal", True),
    ("D06", "4.6", "Lock tanggal + booking venue (DP)", "P3", 10, 1, ["D01", "D02", "D05", "C06"], "Pasangan", "Venue", True),
    ("D07", "4.7", "Review & tandatangan kontrak venue", "P3", 10, 1, ["D06"], "Legal Lead", "Venue", True),
    ("D08", "4.8", "Ambil denah venue + power/load-in rule", "P3", 11, 1, ["D07"], "Venue Lead", "Venue", True),
    ("D09", "4.9", "Cek persyaratan KUA / catatan sipil", "P3", 8, 2, ["A08"], "Admin Lead", "KUA", True),
    ("D10", "4.10", "Kumpulkan dokumen N1–N5 / kelengkapan", "P3", 10, 3, ["D09"], "Admin Lead", "Kelurahan", True),
    ("D11", "4.11", "Daftar & jadwalkan akad di KUA/penghulu", "P3", 13, 2, ["D06", "D10"], "Admin Lead", "KUA", True),
    ("D12", "4.12", "Asuransi acara / force majeure (opsional)", "P3", 12, 1, ["D07"], "Finance Lead", "Asuransi", False),
    ("E01", "5.1", "RFI Wedding Organizer (3–5 WO)", "P4", 8, 2, ["C06", "B07"], "WO Lead", "WO", True),
    ("E02", "5.2", "Interview & pitch WO + portfolio review", "P4", 10, 1, ["E01", "D06"], "WO Lead", "WO", True),
    ("E03", "5.3", "Negosiasi & kontrak WO (scope RACI)", "P4", 11, 1, ["E02"], "Legal Lead", "WO", True),
    ("E04", "5.4", "Kickoff WO: timeline master sync", "P4", 12, 1, ["E03", "D08"], "WO", "WO", True),
    ("E05", "5.5", "RFP Catering (menu + porsi + tasting)", "P4", 12, 2, ["E04", "C04"], "F&B Lead", "Catering", True),
    ("E06", "5.6", "Food tasting & finalisasi menu", "P4", 14, 1, ["E05"], "Pasangan", "Catering", True),
    ("E07", "5.7", "Kontrak catering + deposit", "P4", 15, 1, ["E06"], "Legal Lead", "Catering", True),
    ("E08", "5.8", "RFP Dekorasi / florist / styling", "P4", 12, 2, ["E04", "C05"], "Deco Lead", "Dekorasi", True),
    ("E09", "5.9", "Presentasi konsep deco + 3D/layout", "P4", 14, 2, ["E08", "D08"], "Deco Lead", "Dekorasi", True),
    ("E10", "5.10", "Kontrak dekorasi + material lead time", "P4", 16, 1, ["E09"], "Legal Lead", "Dekorasi", True),
    ("E11", "5.11", "RFP Foto & video (prewed + H-day)", "P4", 12, 2, ["E04"], "Media Lead", "Fotografer", False),
    ("E12", "5.12", "Kontrak foto/video + shot list draft", "P4", 14, 1, ["E11"], "Legal Lead", "Fotografer", True),
    ("E13", "5.13", "RFP MUA & hair (trial schedule)", "P4", 13, 2, ["E04"], "Beauty Lead", "MUA", False),
    ("E14", "5.14", "Kontrak MUA + booking trial", "P4", 15, 1, ["E13"], "Legal Lead", "MUA", True),
    ("E15", "5.15", "RFP Entertainment (MC/band/DJ/qori)", "P4", 14, 2, ["E04", "C03"], "Program Lead", "Entertainment", False),
    ("E16", "5.16", "Kontrak entertainment + tech rider", "P4", 16, 1, ["E15"], "Legal Lead", "Entertainment", False),
    ("E17", "5.17", "RFP Sound/lighting/LED (jika terpisah)", "P4", 14, 2, ["E04", "D08"], "Tech Lead", "AVL", False),
    ("E18", "5.18", "Kontrak AVL + power audit venue", "P4", 16, 1, ["E17", "D08"], "Tech Lead", "AVL", True),
    ("E19", "5.19", "RFP Undangan cetak + digital + website", "P4", 13, 2, ["E04", "C05"], "Invite Lead", "Stationery", False),
    ("E20", "5.20", "Kontrak stationery & invitation site", "P4", 15, 1, ["E19"], "Legal Lead", "Stationery", True),
    ("E21", "5.21", "RFP Souvenir / welcome gift", "P4", 16, 2, ["E04"], "Guest Lead", "Souvenir", False),
    ("E22", "5.22", "Kontrak souvenir + production lead time", "P4", 18, 1, ["E21"], "Legal Lead", "Souvenir", False),
    ("E23", "5.23", "RFP Transport (bridal car / shuttle)", "P4", 18, 2, ["E04"], "Logistik Lead", "Transport", False),
    ("E24", "5.24", "Kontrak transport + route plan", "P4", 20, 1, ["E23"], "Logistik Lead", "Transport", False),
    ("E25", "5.25", "Vendor master register + SLA matrix", "P4", 20, 1, ["E07", "E10", "E12", "E14", "E18", "E20"], "WO", "WO", True),
    ("E26", "5.26", "Kalender termin pembayaran vendor", "P4", 20, 1, ["E25", "B05"], "Finance Lead", "Internal", True),
    ("F01", "6.1", "Draft guest list v1 (kedua keluarga)", "P5", 10, 2, ["C04"], "Guest Lead", "Internal", True),
    ("F02", "6.2", "Kategorisasi VIP / keluarga / umum", "P5", 12, 1, ["F01"], "Guest Lead", "Internal", False),
    ("F03", "6.3", "Validasi kapasitas vs venue seating", "P5", 13, 1, ["F01", "D08"], "WO", "WO", True),
    ("F04", "6.4", "Finalize copy undangan + QR RSVP", "P5", 16, 1, ["E20", "D06"], "Invite Lead", "Stationery", True),
    ("F05", "6.5", "Desain undangan (revisi max 3×)", "P5", 17, 2, ["F04", "C06"], "Creative Lead", "Stationery", True),
    ("F06", "6.6", "Approve final artwork undangan", "P5", 19, 1, ["F05"], "Pasangan", "Stationery", True),
    ("F07", "6.7", "Cetak undangan fisik + QC batch", "P5", 20, 2, ["F06", "F03"], "Invite Lead", "Stationery", True),
    ("F08", "6.8", "Launch website / e-invite + RSVP form", "P5", 20, 1, ["F06"], "Invite Lead", "Stationery", False),
    ("F09", "6.9", "Save-the-date (digital) ke VIP", "P5", 14, 1, ["D06", "F02"], "Guest Lead", "Internal", False),
    ("F10", "6.10", "Distribusi undangan gelombang 1 (VIP)", "P5", 24, 2, ["F07", "F09"], "Guest Lead", "Internal", True),
    ("F11", "6.11", "Distribusi undangan gelombang 2", "P5", 28, 2, ["F10"], "Guest Lead", "Internal", True),
    ("F12", "6.12", "Follow-up RSVP mingguan", "P5", 26, 16, ["F08", "F10"], "Guest Lead", "Internal", True),
    ("F13", "6.13", "Guest list freeze v2 (H-21)", "P5", 45, 1, ["F12"], "Guest Lead", "Internal", True),
    ("F14", "6.14", "Final headcount ke catering (H-14)", "P5", 46, 1, ["F13", "E07"], "F&B Lead", "Catering", True),
    ("F15", "6.15", "Seating chart + place card", "P5", 46, 1, ["F13", "D08"], "WO", "WO", True),
    ("F16", "6.16", "Hotel block / akomodasi tamu luar kota", "P5", 22, 4, ["F02", "D06"], "Guest Lead", "Hotel", False),
    ("G01", "7.1", "Moodboard busana pengantin (3 look)", "P6", 12, 2, ["C06"], "Fashion Lead", "Bridal", False),
    ("G02", "7.2", "Fitting / booking bridal & beskap", "P6", 14, 2, ["G01", "B07"], "Fashion Lead", "Bridal", True),
    ("G03", "7.3", "Kontrak jahit / sewa gaun + DP", "P6", 16, 1, ["G02"], "Legal Lead", "Bridal", True),
    ("G04", "7.4", "Fitting 1 (ukuran dasar)", "P6", 24, 1, ["G03"], "Pasangan", "Bridal", True),
    ("G05", "7.5", "Fitting 2 (penyesuaian)", "P6", 36, 1, ["G04"], "Pasangan", "Bridal", True),
    ("G06", "7.6", "Fitting final + aksesoris (H-14)", "P6", 46, 1, ["G05"], "Pasangan", "Bridal", True),
    ("G07", "7.7", "Busana keluarga inti & bridesmaid", "P6", 20, 4, ["G01"], "Fashion Lead", "Tailor", False),
    ("G08", "7.8", "Trial makeup & hair #1", "P6", 28, 1, ["E14"], "Pasangan", "MUA", True),
    ("G09", "7.9", "Trial makeup #2 + foto test", "P6", 36, 1, ["G08", "E12"], "Pasangan", "MUA", False),
    ("G10", "7.10", "Skincare / treatment schedule H-90", "P6", 35, 6, ["E14"], "Beauty Lead", "Klinik", False),
    ("G11", "7.11", "Prewedding shoot planning", "P6", 18, 2, ["E12", "G03"], "Media Lead", "Fotografer", False),
    ("G12", "7.12", "Prewedding shoot execution", "P6", 22, 1, ["G11", "G04"], "Pasangan", "Fotografer", False),
    ("G13", "7.13", "Select foto prewed untuk undangan/LED", "P6", 24, 2, ["G12"], "Creative Lead", "Fotografer", False),
    ("H01", "8.1", "Layout floorplan final (aisle/VIP/buffet)", "P7", 18, 2, ["E10", "D08", "F03"], "WO", "Dekorasi", True),
    ("H02", "8.2", "Material board & sample bunga", "P7", 20, 2, ["H01"], "Deco Lead", "Dekorasi", False),
    ("H03", "8.3", "Approve final deco package", "P7", 22, 1, ["H02"], "Pasangan", "Dekorasi", True),
    ("H04", "8.4", "Order bunga impor / non-seasonal", "P7", 36, 2, ["H03"], "Deco Lead", "Florist", True),
    ("H05", "8.5", "Menu dietary matrix (halal/alergi/VIP)", "P7", 20, 2, ["E07", "F02"], "F&B Lead", "Catering", False),
    ("H06", "8.6", "Cake / dessert table design & order", "P7", 30, 2, ["E07", "C06"], "F&B Lead", "Cake", False),
    ("H07", "8.7", "Bar / soft drink / coffee station plan", "P7", 28, 2, ["E07"], "F&B Lead", "Catering", False),
    ("H08", "8.8", "Staffing F&B (waiter/usher ratio)", "P7", 40, 1, ["F14"], "F&B Lead", "Catering", True),
    ("H09", "8.9", "Lighting plot & LED content slots", "P7", 24, 2, ["E18", "H01"], "Tech Lead", "AVL", True),
    ("H10", "8.10", "Soundcheck plan + mic allocation", "P7", 30, 1, ["E18", "E16"], "Tech Lead", "AVL", False),
    ("H11", "8.11", "Backup power / genset decision", "P7", 26, 1, ["E18", "D08"], "Tech Lead", "AVL", True),
    ("H12", "8.12", "Load-in / load-out schedule dengan venue", "P7", 40, 1, ["H01", "H09", "E25"], "WO", "Venue", True),
    ("I01", "9.1", "Rundown detail menit-per-menit v1", "P8", 20, 2, ["E04", "C03"], "WO", "WO", True),
    ("I02", "9.2", "Script MC + cue sheet", "P8", 28, 2, ["I01", "E16"], "Program Lead", "MC", False),
    ("I03", "9.3", "Playlist / setlist musik", "P8", 30, 2, ["E16", "I01"], "Program Lead", "Entertainment", False),
    ("I04", "9.4", "Urutan prosesi & petugas (wali, saksi)", "P8", 24, 2, ["D11", "I01"], "Admin Lead", "KUA", True),
    ("I05", "9.5", "Produksi video cinematic / teaser", "P8", 26, 4, ["G13"], "Media Lead", "Fotografer", False),
    ("I06", "9.6", "Konten LED: slideshow + ucapan", "P8", 36, 2, ["H09", "G13", "I05"], "Creative Lead", "AVL", False),
    ("I07", "9.7", "Kartu ucapan / guestbook / angpao flow", "P8", 32, 2, ["F02"], "Guest Lead", "Internal", False),
    ("I08", "9.8", "Brief usher & family coordinator", "P8", 42, 1, ["I01", "F15"], "WO", "WO", True),
    ("I09", "9.9", "Approve rundown final (Gate Program)", "P8", 44, 1, ["I01", "I02", "I04", "F13"], "Pasangan", "WO", True),
    ("J01", "10.1", "Transport plan pengantin H-day", "P9", 30, 2, ["E24", "I01"], "Logistik Lead", "Transport", True),
    ("J02", "10.2", "Parking & wayfinding signage", "P9", 36, 2, ["D08", "F13"], "Logistik Lead", "Venue", False),
    ("J03", "10.3", "Security & crowd control brief", "P9", 40, 1, ["F13"], "WO", "Security", False),
    ("J04", "10.4", "Medical standby / P3K plan", "P9", 42, 1, ["E04"], "WO", "Medis", False),
    ("J05", "10.5", "Weather contingency (outdoor elements)", "P9", 38, 1, ["H03", "A06"], "WO", "WO", False),
    ("J06", "10.6", "Vendor meal & crew holding area", "P9", 42, 1, ["E07", "H12"], "F&B Lead", "Catering", False),
    ("J07", "10.7", "Asset inventory (barang sewa/beli)", "P9", 34, 2, ["E25"], "WO", "Internal", False),
    ("J08", "10.8", "Komunikasi protokol VIP / pejabat", "P9", 40, 2, ["F02", "I01"], "Guest Lead", "Internal", False),
    ("J09", "10.9", "Runbook H-day (kontak darurat 1 halaman)", "P9", 44, 1, ["E25", "I09", "J01"], "WO", "WO", True),
    ("J10", "10.10", "Rehearsal plan & call sheet", "P9", 45, 1, ["I09", "J09"], "WO", "WO", True),
    ("K01", "11.1", "Vendor sync meeting #1 (H-60)", "P10", 40, 1, ["E25", "H03", "I01"], "WO", "All Vendors", True),
    ("K02", "11.2", "Payment checkpoint termin tengah", "P10", 40, 1, ["E26", "B08"], "Finance Lead", "Internal", True),
    ("K03", "11.3", "Confirm all vendor call times", "P10", 42, 1, ["K01", "H12"], "WO", "All Vendors", True),
    ("K04", "11.4", "Print place cards / name tags / signage", "P10", 45, 1, ["F15"], "Invite Lead", "Stationery", True),
    ("K05", "11.5", "Souvenir packing & QC", "P10", 44, 2, ["E22", "F13"], "Guest Lead", "Souvenir", False),
    ("K06", "11.6", "Final legal docs check (KUA ready)", "P10", 44, 1, ["D11", "I04"], "Admin Lead", "KUA", True),
    ("K07", "11.7", "Vendor sync meeting #2 (H-30)", "P10", 44, 1, ["K01", "F13"], "WO", "All Vendors", True),
    ("K08", "11.8", "Change freeze (no major scope change)", "P10", 45, 1, ["K07", "I09"], "Pasangan", "WO", True),
    ("L01", "12.1", "Final headcount lock & PO catering", "P11", 46, 1, ["F14", "K08"], "F&B Lead", "Catering", True),
    ("L02", "12.2", "Fitting final busana + steam plan", "P11", 46, 1, ["G06"], "Fashion Lead", "Bridal", True),
    ("L03", "12.3", "Rehearsal on-site (prosesi + cue)", "P11", 47, 1, ["J10", "L01", "H12"], "WO", "All Vendors", True),
    ("L04", "12.4", "Tech rehearsal sound/LED", "P11", 47, 1, ["H10", "I06", "L03"], "Tech Lead", "AVL", True),
    ("L05", "12.5", "Brief keluarga & petugas inti", "P11", 47, 1, ["I08", "L03"], "PM Keluarga", "Internal", True),
    ("L06", "12.6", "Confirm weather & contingency trigger", "P11", 47, 1, ["J05"], "WO", "WO", False),
    ("L07", "12.7", "Pack emergency kit pengantin", "P11", 47, 1, ["L02"], "Beauty Lead", "Internal", False),
    ("L08", "12.8", "Pelunasan vendor sesuai kontrak (pre H)", "P11", 47, 1, ["K02", "L01"], "Finance Lead", "Internal", True),
    ("M01", "13.1", "H-1: load-in deco & AVL start", "P12", 47, 1, ["H12", "L03"], "WO", "Dekorasi", True),
    ("M02", "13.2", "H-1: QC venue (AC, toilet, power, WIFI)", "P12", 47, 1, ["M01"], "Venue Lead", "Venue", True),
    ("M03", "13.3", "H-1: set seating, signage, souvenir", "P12", 47, 1, ["K04", "K05", "F15"], "WO", "WO", True),
    ("M04", "13.4", "H-1: overnight security / lockup", "P12", 47, 1, ["M01", "J03"], "WO", "Security", False),
    ("M05", "13.5", "H0 AM: MUA call time & getting ready", "P12", 48, 1, ["E14", "L02", "L07"], "Beauty Lead", "MUA", True),
    ("M06", "13.6", "H0 AM: foto getting ready", "P12", 48, 1, ["M05", "E12"], "Media Lead", "Fotografer", True),
    ("M07", "13.7", "H0: transport ke lokasi akad", "P12", 48, 1, ["J01", "M05"], "Logistik Lead", "Transport", True),
    ("M08", "13.8", "H0: pelaksanaan akad + dokumen", "P12", 48, 1, ["K06", "I04", "M07"], "Admin Lead", "KUA", True),
    ("M09", "13.9", "H0: resepsi — doors open & receiving", "P12", 48, 1, ["M02", "M03", "M08"], "WO", "All Vendors", True),
    ("M10", "13.10", "H0: program on-stage per rundown", "P12", 48, 1, ["M09", "I09", "L04"], "Program Lead", "MC", True),
    ("M11", "13.11", "H0: F&B service monitoring", "P12", 48, 1, ["L01", "M09"], "F&B Lead", "Catering", True),
    ("M12", "13.12", "H0: real-time issue log & escalation", "P12", 48, 1, ["J09", "M09"], "WO", "WO", True),
    ("M13", "13.13", "H0 PM: load-out & handback venue", "P12", 48, 1, ["M10", "M11"], "WO", "Venue", True),
    ("N01", "14.1", "Hot wash / debrief H+1 dengan WO", "P13", 49, 1, ["M13"], "WO", "WO", True),
    ("N02", "14.2", "Return barang sewa & checklist aset", "P13", 49, 1, ["M13", "J07"], "Logistik Lead", "Vendors", False),
    ("N03", "14.3", "Final invoice reconciliation semua vendor", "P13", 49, 2, ["M13", "L08"], "Finance Lead", "Internal", True),
    ("N04", "14.4", "Bayar retensi / pelunasan sisa", "P13", 51, 1, ["N03"], "Finance Lead", "Internal", True),
    ("N05", "14.5", "Terima raw foto/video + QC seleksi", "P13", 50, 3, ["M06", "M10"], "Media Lead", "Fotografer", False),
    ("N06", "14.6", "Edit final album / highlight film", "P13", 53, 2, ["N05"], "Media Lead", "Fotografer", False),
    ("N07", "14.7", "Thank-you note / gift ke keluarga & VIP", "P13", 50, 2, ["N01"], "Guest Lead", "Internal", False),
    ("N08", "14.8", "Urus dokumen pasca-nikah (buku nikah dll)", "P13", 49, 2, ["M08"], "Admin Lead", "KUA", True),
    ("N09", "14.9", "Update dokumen sipil / KK / rekening", "P13", 51, 3, ["N08"], "Admin Lead", "Dukcapil", False),
    ("N10", "14.10", "Archive project (kontrak, foto, laporan)", "P13", 54, 1, ["N04", "N06"], "PM Keluarga", "Internal", True),
    ("N11", "14.11", "Lessons learned & close project", "P13", 55, 1, ["N10", "N01"], "Pasangan", "Internal", True),
]

PHASES = {
    "P0": "Initiation & Governance",
    "P1": "Budget & Cashflow",
    "P2": "Concept & Design",
    "P3": "Date / Venue / Legal",
    "P4": "Vendor Procurement",
    "P5": "Guest & Invitation",
    "P6": "Attire & Beauty",
    "P7": "Deco / F&B / Tech",
    "P8": "Program & Content",
    "P9": "Logistics & Ops",
    "P10": "H-60 Intensive",
    "P11": "Wedding Week",
    "P12": "H-1 & Hari-H",
    "P13": "Post-Event Closeout",
}

HARI_H_WEEK = 48
# Compress 48 weeks before H into 120 days: factor = 120/48 = 2.5 days per week-unit
SCALE = 2.5


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def to_days(week, dur):
    start = round((week - HARI_H_WEEK) * SCALE)
    end = round((week + dur - HARI_H_WEEK) * SCALE)
    start = clamp(start, -120, 14)
    end = clamp(end, -119, 15)
    if end <= start:
        end = min(14, start + 1)
    return start, end


out_tasks = []
for tid, wbs, name, phase, start, dur, deps, owner, vendor, cp in TASKS:
    s, e = to_days(start, dur)
    out_tasks.append({
        "id": tid,
        "wbs": wbs,
        "name": name,
        "phase": phase,
        "start": s,
        "end": e,
        "deps": deps,
        "owner": owner,
        "vendor": vendor,
        "cp": cp,
        "status": "todo",
        "progress": 0,
        "notes": "",
    })

# Daily focus templates by day bands
DAILY_EXTRA = {
    -120: ["Kickoff resmi H-4 bulan", "Share folder & grup WA aktif"],
    -90: ["Review budget mid-point", "Cek status kontrak vendor utama"],
    -60: ["Vendor sync #1", "Freeze konsep deco"],
    -30: ["Vendor sync #2", "RSVP push intensif"],
    -21: ["Guest list freeze", "Change freeze scope"],
    -14: ["Headcount ke catering", "Fitting final"],
    -7: ["Rehearsal plan lock", "Pelunasan pre-H"],
    -3: ["Tech rehearsal", "Brief keluarga"],
    -1: ["Load-in deco & AVL", "QC venue + overnight security"],
    0: ["Akad + resepsi execution", "Issue log real-time"],
    1: ["Debrief WO", "Return aset sewa"],
    3: ["Invoice recon", "Dokumen pasca-nikah"],
    7: ["Thank-you VIP", "Seleksi foto raw"],
    14: ["Archive project", "Lessons learned"],
}

daily = []
for d in range(-120, 15):
    active = [t for t in out_tasks if t["start"] <= d < t["end"]]
    items = []
    for t in active[:6]:
        items.append({
            "id": f"D{d}_{t['id']}",
            "text": f"Kerjakan / pantau: {t['name']}",
            "taskId": t["id"],
            "done": False,
        })
    for i, extra in enumerate(DAILY_EXTRA.get(d, [])):
        items.append({
            "id": f"D{d}_X{i}",
            "text": extra,
            "taskId": None,
            "done": False,
        })
    if not items:
        items.append({
            "id": f"D{d}_IDLE",
            "text": "Buffer / follow-up vendor & admin harian",
            "taskId": None,
            "done": False,
        })
    daily.append({"day": d, "items": items})

payload = {
    "version": 1,
    "settings": {
        "coupleNames": "Azam & Pasangan",
        "weddingDate": "",  # ISO date = Hari-H; empty = relative only
        "dayMin": -120,
        "dayMax": 14,
        "autoReschedule": True,
        "showDeps": True,
        "showCriticalOnly": False,
    },
    "phases": PHASES,
    "tasks": out_tasks,
    "daily": daily,
}

out = Path(r"D:\Isi Otak Azam\Persiapan Wedding\wedding-planner-html\js\data.js")
js = "window.WP_DEFAULT = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
out.write_text(js, encoding="utf-8")
print(f"Wrote {out} tasks={len(out_tasks)} daily={len(daily)}")
