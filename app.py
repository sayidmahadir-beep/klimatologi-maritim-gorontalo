import streamlit as st
import os
import time

st.set_page_config(page_title="MARITIM GORONTALO - BMKG", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# INISIALISASI SESSION STATE
if "nav_menu" not in st.session_state:
    st.session_state.nav_menu = "Beranda"
if "idx_bulan" not in st.session_state:
    st.session_state.idx_bulan = 0
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False

# DATA TERPUSAT
PARAMS = [
    ("🌊", "Tinggi Gelombang", "Significant Wave Height (m)", "#0284C7", "Tinggi Gelombang", "SWH", "Analisis Significant Wave Height (m) bulanan perairan Gorontalo"),
    ("🧭", "Arus Laut", "Current Speed & Dir (cm/s)", "#0D9488", "Arus Laut", "CSD", "Distribusi kecepatan dan arah arus permukaan laut (cm/s)"),
    ("⏱️", "Periode Gelombang", "Peak Wave Period (s)", "#6366F1", "Periode Gelombang", "WavePeriod", "Karakteristik spektrum periode gelombang laut (detik)"),
    ("💨", "Angin Permukaan", "Wind Speed & Dir (knot)", "#059669", "Angin", "WSD", "Pola kecepatan dan arah angin permukaan maritim (knot)")
]

PARAM_MAP = {p[4]: {"folder": p[5], "caption": p[6], "satuan": p[2]} for p in PARAMS}
BULAN_LIST = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

MUSIM_MAP = {
    "Monsun Baratan (DJF)": ["Desember", "Januari", "Februari"],
    "Peralihan I (MAM)": ["Maret", "April", "Mei"],
    "Monsun Timuran (JJA)": ["Juni", "Juli", "Agustus"],
    "Peralihan II (SON)": ["September", "Oktober", "November"]
}

ANALISIS_DATA = {
    "Tinggi Gelombang": {
        "Monsun Baratan (DJF)": "Pada periode Monsun Baratan (DJF), tinggi gelombang signifikan di perairan Laut Sulawesi (utara Gorontalo) cenderung meningkat akibat dorongan angin baratan yang persisten. Sementara itu, wilayah Teluk Tomini di bagian selatan relatif lebih terlindungi dengan kondisi gelombang kategori tenang hingga rendah.",
        "Peralihan I (MAM)"   : "Memasuki periode Peralihan I (MAM), tinggi gelombang di perairan utara Gorontalo mulai berangsur melandai seiring melemahnya aliran angin baratan. Kondisi perairan Teluk Tomini tetap didominasi gelombang rendah.",
        "Monsun Timuran (JJA)": "Pada periode Monsun Timuran (JJA), area pembangkitan gelombang tinggi bergeser mengikuti dominasi angin timuran hingga tenggara, memengaruhi perairan terbuka di bagian terluar Teluk Tomini sebelah timur dan Laut Sulawesi.",
        "Peralihan II (SON)"  : "Pada periode Peralihan II (SON), variasi tinggi gelombang cenderung stabil pada kategori rendah baik di perairan utara Gorontalo maupun di dalam Teluk Tomini sebelum kembali meningkat menjelang Desember."
    },
    "Arus Laut": {
        "Monsun Baratan (DJF)": "Sirkulasi arus permukaan pada periode DJF dipengaruhi oleh dorongan massa air dari Laut Sulawesi menuju timur serta pola sirkulasi lokal di dalam Teluk Tomini yang dipicu oleh angin baratan.",
        "Peralihan I (MAM)"   : "Pada periode MAM, kecepatan arus permukaan umumnya melemah dan menunjukkan pola transisi arah seiring berkurangnya tekanan angin monsunal.",
        "Monsun Timuran (JJA)": "Pada periode Monsun Timuran (JJA), aliran arus permukaan di perairan terbuka bergerak dominan ke arah barat hingga barat laut, dengan penguatan kecepatan arus yang terpusat di area selat dan bagian terluar teluk.",
        "Peralihan II (SON)"  : "Periode SON ditandai dengan kembali melemahnya intensitas arus permukaan serta pembentukan pusaran (eddy) skala lokal di perairan Teluk Tomini."
    },
    "Periode Gelombang": {
        "Monsun Baratan (DJF)": "Periode puncak gelombang pada musim DJF menunjukkan dominasi gelombang alun (swell) yang menjalar dari perairan terbuka Laut Sulawesi ke pesisir utara Gorontalo.",
        "Peralihan I (MAM)"   : "Pada musim MAM, spektrum periode gelombang didominasi oleh gelombang lokal (wind sea) berperiode pendek hingga menengah akibat melemahnya penjalaran alun jarak jauh.",
        "Monsun Timuran (JJA)": "Periode JJA memperlihatkan peningkatan periode gelombang di sektor timur dan selatan (Teluk Tomini) akibat penjalaran energi gelombang dari Laut Maluku.",
        "Peralihan II (SON)"  : "Pada periode SON, karakteristik periode gelombang kembali seragam pada rentang pendek hingga menengah di hampir seluruh perairan Gorontalo."
    },
    "Angin": {
        "Monsun Baratan (DJF)": "Angin permukaan bertiup dominan dari arah Barat hingga Barat Laut dengan kecepatan lebih tinggi di wilayah perairan utara Gorontalo dibandingkan area teluk yang terhalang topografi daratan.",
        "Peralihan I (MAM)"   : "Arah angin pada periode MAM sangat bervariasi (variable) dengan kecepatan yang cenderung lemah, sehingga pengaruh angin darat dan angin laut lokal menjadi lebih dominan.",
        "Monsun Timuran (JJA)": "Angin bertiup konsisten dari arah Timur hingga Tenggara. Kondisi ini memicu peningkatan kecepatan angin terutama di perairan selatan Gorontalo dan Teluk Tomini.",
        "Peralihan II (SON)"  : "Pada periode SON, arah angin kembali mengalami transisi dari timuran menuju baratan dengan kecepatan rata-rata yang relatif tenang."
    }
}

LINKS = [
    ("🌐 Website Resmi BMKG", "https://www.bmkg.go.id"),
    ("🚢 Info Maritim BMKG", "https://maritim.bmkg.go.id"),
    ("🗺️ InaWIS / OFS BMKG", "https://peta-maritim.bmkg.go.id/ofs/"),
    ("🗺️ Maritim Tools BMKG", "https://https://maritim.bmkg.go.id/tools/"),
    ("📊 Klimatologi Pusmar", "https://api-maritim.bmkg.go.id/met/analisis/")
]

# CSS RINGKAS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(180deg, #F0F6FC 0%, #E8F1F9 100%); }

/* AGAR HEADER TRANSPARAN TIDAK MENGHALANGI KLIK PADA SELECTBOX */
header[data-testid="stHeader"] { background: transparent !important; pointer-events: none; }
header[data-testid="stHeader"] button { pointer-events: auto; }

.block-container { max-width: 1440px; padding: 1.5rem 1.2rem 1rem !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #091D34 0%, #0F2D52 100%); box-shadow: 4px 0 20px rgba(0,0,0,0.06); }
[data-testid="stSidebar"] * { color: #F8FAFC !important; }
.hero-card { background: linear-gradient(135deg, #0A3C6B 0%, #1664A3 60%, #1789A3 100%); border-radius: 20px; padding: 28px 36px; color: white; box-shadow: 0 12px 28px rgba(10,60,107,0.16); margin-bottom: 20px; }
.hero-tag { background: rgba(255,255,255,0.18); backdrop-filter: blur(8px); display: inline-block; padding: 4px 12px; border-radius: 99px; font-size: 11px; letter-spacing: 1px; font-weight: 700; text-transform: uppercase; color: #E0F2FE; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.2); }
.hero-title { font-size: 30px; font-weight: 800; line-height: 1.2; margin: 0; color: #FFF !important; }
.hero-desc { font-size: 13.5px; color: #E2E8F0; margin-top: 8px; line-height: 1.6; max-width: 700px; }
.stat-pill { background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.22); border-radius: 14px; padding: 12px 18px; text-align: center; backdrop-filter: blur(6px); }
.stat-num { font-size: 26px; font-weight: 800; color: #FFF; line-height: 1; }
.stat-label { font-size: 10.5px; color: #BAE6FD; font-weight: 600; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.section-header { display: flex; align-items: center; gap: 10px; margin: 6px 0 14px; }
.section-bar { width: 5px; height: 22px; background: #0284C7; border-radius: 4px; }
.section-title { color: #0F172A; font-size: 19px; font-weight: 700; }
div[data-testid="stVerticalBlockBorderWrapper"] { background: #FFF !important; border: 1px solid #E2E8F0 !important; border-radius: 16px !important; box-shadow: 0 4px 16px rgba(15,23,42,0.04) !important; padding: 6px !important; transition: 0.2s ease; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: 0 8px 24px rgba(15,23,42,0.08) !important; }
div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button { background: #F0F7FF !important; color: #0284C7 !important; border: 1px solid #BAE6FD !important; font-weight: 700 !important; font-size: 13px !important; border-radius: 10px !important; transition: 0.25s ease !important; }
div[data-testid="stButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover { background: #0284C7 !important; color: #FFF !important; border-color: #0284C7 !important; box-shadow: 0 4px 12px rgba(2,132,199,0.25) !important; transform: translateY(-1px); }
.sidebar-link { display: block; padding: 7px 10px; margin: 4px 0; border-radius: 8px; font-size: 12.5px; text-decoration: none !important; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); transition: 0.2s; }
.sidebar-link:hover { background: rgba(2,132,199,0.35); border-color: #38BDF8; }
.month-badge { background: #E0F2FE; color: #0369A1; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 8px; display: inline-block; margin-bottom: 8px; }
.analisis-box { background: #F8FAFC; border-left: 4px solid #0284C7; padding: 16px 20px; border-radius: 10px; margin-top: 8px; }
.footer-text { text-align: center; color: #64748B; font-size: 12px; font-weight: 500; padding-top: 10px; margin-top: 14px; border-top: 1px solid #CBD5E1; }

/* PEMBATAS TINGGI GAMBAR DI AREA KONTEN UTAMA (ANTI-SCROLL) */
section[data-testid="stMain"] [data-testid="stImage"],
[data-testid="stAppViewContainer"] > section:nth-child(2) [data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
section[data-testid="stMain"] [data-testid="stImage"] img,
[data-testid="stAppViewContainer"] > section:nth-child(2) [data-testid="stImage"] img {
    max-height: 58vh !important;
    width: auto !important;
    max-width: 100% !important;
    object-fit: contain !important;
}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    _, col_logo, _ = st.columns([1, 1.2, 1])
    with col_logo:
        if os.path.exists("assets/logo_bmkg.png"):
            st.image("assets/logo_bmkg.png", use_container_width=True)
        else:
            st.markdown("<h2 style='margin:0; text-align:center;'>🌊 BMKG</h2>", unsafe_allow_html=True)

    st.markdown("""
        <div style='text-align:center; margin-top:-6px;'>
            <h3 style='margin:0; font-size:17px;'>MARITIM GORONTALO</h3>
            <div style='font-size:12px; color:#94A3B8; margin-top:2px;'>Ocean Climatology Dashboard</div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("<span style='font-size:12px; font-weight:700; letter-spacing:0.8px; color:#94A3B8;'>NAVIGASI UTAMA</span>", unsafe_allow_html=True)
    menu_opsi = ["Beranda", "Tinggi Gelombang", "Arus Laut", "Periode Gelombang", "Angin"]
    if st.session_state.nav_menu not in menu_opsi:
        st.session_state.nav_menu = "Beranda"

    menu_terpilih = st.radio("Menu", menu_opsi, index=menu_opsi.index(st.session_state.nav_menu), label_visibility="collapsed")
    if menu_terpilih != st.session_state.nav_menu:
        st.session_state.nav_menu = menu_terpilih
        st.session_state.is_playing = False
        st.rerun()

    st.divider()
    st.markdown("<span style='font-size:12px; font-weight:700; letter-spacing:0.8px; color:#94A3B8;'>LINK TERKAIT</span>", unsafe_allow_html=True)
    st.markdown("".join([f"<a href='{url}' target='_blank' class='sidebar-link'>{label} ↗</a>" for label, url in LINKS]), unsafe_allow_html=True)

    st.divider()
    st.markdown("""
        <div style='background:rgba(255,255,255,0.06); padding:14px; border-radius:12px; border:1px solid rgba(255,255,255,0.1);'>
            <div style='font-size:11px; color:#93C5FD; font-weight:600;'>STASIUN METEOROLOGI</div>
            <div style='font-size:13px; font-weight:700; margin-top:2px;'>DJALALUDDIN GORONTALO</div>
            <div style='font-size:11px; color:#CBD5E1; margin-top:6px;'>Periode Data: 2016–2025</div>
        </div>
    """, unsafe_allow_html=True)

# HALAMAN: BERANDA
if st.session_state.nav_menu == "Beranda":
    stats = "".join([f"<div class='stat-pill'><div class='stat-num'>{n}</div><div class='stat-label'>{l}</div></div>" for n, l in [("4", "Parameter"), ("12", "Bulan"), ("10", "Tahun Data")]])
    st.markdown(f"""
        <div class="hero-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:20px;">
                <div style="flex:2; min-width:320px;">
                    <div class="hero-tag">Sistem Informasi Maritim</div>
                    <h1 class="hero-title">Klimatologi Maritim Gorontalo</h1>
                    <p class="hero-desc">Platform visualisasi variabilitas dan karakteristik kondisi laut bulanan wilayah perairan Gorontalo dan Teluk Tomini berbasis data reanalisis Ocean Forecast System (OFS) BMKG.</p>
                </div>
                <div style="display:flex; gap:12px; flex-wrap:wrap;">{stats}</div>
            </div>
        </div>
        <div class="section-header"><div class="section-bar"></div><div class="section-title">Parameter Oseanografi & Meteorologi</div></div>
    """, unsafe_allow_html=True)

    for col, (icon, judul, satuan, warna, target, _, _) in zip(st.columns(4), PARAMS):
        with col, st.container(border=True):
            st.markdown(f"""
                <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                    <div style='font-size:26px; background:{warna}1A; border:1.5px solid {warna}40; width:52px; height:52px; border-radius:14px; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 10px {warna}1A;'>{icon}</div>
                    <span style='background:#F1F5F9; color:#475569; font-size:11px; font-weight:700; padding:4px 9px; border-radius:8px;'>12 PETA</span>
                </div>
                <div style='margin-top:14px;'>
                    <div style='font-weight:700; font-size:15px; color:#0F172A;'>{judul}</div>
                    <div style='font-size:12px; color:#64748B; margin-top:2px; height:32px;'>{satuan}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Buka Data →", key=f"btn_{judul}", use_container_width=True):
                st.session_state.nav_menu = target
                st.rerun()

    st.markdown("<div class='section-header' style='margin-top:18px;'><div class='section-bar' style='background:#0D9488;'></div><div class='section-title'>Metadata & Lingkup Wilayah</div></div>", unsafe_allow_html=True)

    metadata = [
        ("📍", "Wilayah Kajian", "Perairan Gorontalo & Teluk Tomini", "Cakupan Laut Sulawesi bagian selatan hingga perairan Teluk Tomini"),
        ("📅", "Rentang Waktu", "2016 – 2025 (Klimatologi 10 Tahun)", "Rata-rata klimatologi bulanan periode 10 tahun"),
        ("🛰️", "Sumber Model", "BMKG-OFS (InaWaves & InaFlows)", "InaWaves (WaveWatch III 7 km) & InaFlows (9.25 km)")
    ]
    for col, (icon, label, val, sub) in zip(st.columns(3), metadata):
        with col, st.container(border=True):
            st.markdown(f"""
                <div style='display:flex; align-items:flex-start; gap:14px; padding:8px 6px;'>
                    <div style='font-size:24px; display:flex; align-items:center; justify-content:center; width:44px; height:44px; background:#F8FAFC; border-radius:12px; border:1px solid #E2E8F0; flex-shrink:0;'>{icon}</div>
                    <div>
                        <div style='font-size:11px; font-weight:600; color:#64748B; text-transform:uppercase;'>{label}</div>
                        <div style='font-size:13.5px; font-weight:700; color:#0F172A; margin-top:2px;'>{val}</div>
                        <div style='font-size:11.5px; color:#64748B; margin-top:3px; line-height:1.4;'>{sub}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # KARTU KONTAK & LAYANAN INFORMASI
    with st.container(border=True):
        st.markdown("""
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; padding:6px 10px;'>
                <div>
                    <span style='font-size:11px; font-weight:700; color:#0284C7; text-transform:uppercase; letter-spacing:0.5px;'>Layanan Informasi & Kontak</span>
                    <div style='font-size:14px; font-weight:700; color:#0F172A; margin-top:2px;'>Stasiun Meteorologi Kelas I Djalaluddin Gorontalo</div>
                    <div style='font-size:12px; color:#64748B; margin-top:2px;'>Kawasan Bandara Djalaluddin, Kab. Gorontalo • Email: stamet.gorontalo@bmkg.go.id</div>
                </div>
                <div style='background:#F0F9FF; border:1px solid #BAE6FD; padding:8px 14px; border-radius:10px; font-size:12px; color:#0369A1; font-weight:600;'>
                    🌊 Mendukung Keselamatan Pelayaran & Kelautan Gorontalo
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='footer-text'>© 2026 Stasiun Meteorologi Djalaluddin Gorontalo — Badan Meteorologi, Klimatologi, dan Geofisika</div>", unsafe_allow_html=True)

# HALAMAN: PARAMETER (TAMPILAN PETA KLIMATOLOGI & MUSIM)
else:
    curr = st.session_state.nav_menu
    info = PARAM_MAP[curr]
    folder_path = os.path.join("data", info["folder"])

    # BARIS ATAS RINGKAS
    c_back, c_head, c_filter = st.columns([1.0, 3.3, 1.8])
    with c_back:
        if st.button("← Beranda", use_container_width=True):
            st.session_state.nav_menu = "Beranda"
            st.session_state.is_playing = False
            st.rerun()
    with c_head:
        st.markdown(f"<h3 style='margin:0; color:#0F172A; line-height:1.2;'>{curr}</h3><div style='color:#64748B; font-size:12px;'>{info['caption']}</div>", unsafe_allow_html=True)
    with c_filter:
        opsi_tampilan = [
            "🔍 Detail per Bulan (Animasi)",
            "🌬️ Monsun Baratan (DJF)",
            "🔄 Peralihan I (MAM)",
            "☀️ Monsun Timuran (JJA)",
            "🍂 Peralihan II (SON)",
            "🗓️ Semua Bulan (Grid 12 Bulan)"
        ]
        mode_tampilan = st.selectbox("Mode Tampilan:", opsi_tampilan, label_visibility="collapsed")
        if mode_tampilan != "🔍 Detail per Bulan (Animasi)":
            st.session_state.is_playing = False

    # MODE 1: DETAIL PER BULAN + PLAY/PAUSE ANIMASI (PAS 1 LAYAR)
    if mode_tampilan == "🔍 Detail per Bulan (Animasi)":
        with st.container(border=True):
            c_play, c_speed, c_slider, c_dl = st.columns([1.0, 1.1, 3.8, 1.1])

            with c_play:
                btn_label = "⏸️ Pause" if st.session_state.is_playing else "▶️ Play"
                if st.button(btn_label, use_container_width=True):
                    st.session_state.is_playing = not st.session_state.is_playing
                    st.rerun()

            with c_speed:
                kecepatan = st.selectbox("Kecepatan", [1.0, 1.5, 2.0, 0.5], format_func=lambda x: f"{x} dtk/bln", label_visibility="collapsed")

            with c_slider:
                bulan_terpilih = st.select_slider(
                    "Pilih atau Geser Bulan:",
                    options=BULAN_LIST,
                    value=BULAN_LIST[st.session_state.idx_bulan],
                    label_visibility="collapsed"
                )
                if BULAN_LIST.index(bulan_terpilih) != st.session_state.idx_bulan and not st.session_state.is_playing:
                    st.session_state.idx_bulan = BULAN_LIST.index(bulan_terpilih)

            bulan_aktif = BULAN_LIST[st.session_state.idx_bulan]
            img_path = os.path.join(folder_path, f"{bulan_aktif}.png")

            if os.path.exists(img_path):
                with c_dl:
                    with open(img_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Unduh",
                            data=file,
                            file_name=f"Klimatologi_{info['folder']}_{bulan_aktif}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                _, col_map, _ = st.columns([0.6, 5, 0.6])
                with col_map:
                    st.image(img_path)
            else:
                st.warning(f"File peta tidak ditemukan di lokasi: `{img_path}`")

        if st.session_state.is_playing:
            time.sleep(kecepatan)
            st.session_state.idx_bulan = (st.session_state.idx_bulan + 1) % 12
            st.rerun()

    # MODE 2: PERIODE MONSUN / PERALIHAN + KOTAK ANALISIS
    elif any(k in mode_tampilan for k in MUSIM_MAP.keys()):
        nama_musim = mode_tampilan.split(" ", 1)[1]
        daftar_bulan_musim = MUSIM_MAP[nama_musim]

        cols = st.columns(3)
        for col, bulan in zip(cols, daftar_bulan_musim):
            img_path = os.path.join(folder_path, f"{bulan}.png")
            with col, st.container(border=True):
                st.markdown(f"<div class='month-badge'>📅 {bulan}</div>", unsafe_allow_html=True)
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.warning(f"`{bulan}.png` belum tersedia")

        with st.container(border=True):
            teks_analisis = ANALISIS_DATA.get(curr, {}).get(nama_musim, "Analisis klimatologi belum tersedia.")
            st.markdown(f"""
                <div class='analisis-box'>
                    <div style='font-size:12px; font-weight:700; color:#0284C7; text-transform:uppercase; letter-spacing:0.5px;'>
                        📝 Analisis Klimatologi — {nama_musim}
                    </div>
                    <h4 style='margin:4px 0 8px; color:#0F172A;'>Karakteristik {curr} Wilayah Gorontalo & Teluk Tomini</h4>
                    <p style='font-size:14px; color:#334155; line-height:1.65; margin:0;'>{teks_analisis}</p>
                </div>
            """, unsafe_allow_html=True)

    # MODE 3: GRID 12 BULAN
    else:
        for i in range(0, 12, 3):
            cols = st.columns(3)
            for col, bulan in zip(cols, BULAN_LIST[i:i+3]):
                img_path = os.path.join(folder_path, f"{bulan}.png")
                with col, st.container(border=True):
                    st.markdown(f"<div class='month-badge'>📅 {bulan}</div>", unsafe_allow_html=True)
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    else:
                        st.warning(f"`{bulan}.png` belum tersedia")

    st.markdown("<div class='footer-text'>© 2026 Stasiun Meteorologi Djalaluddin Gorontalo — Badan Meteorologi, Klimatologi, dan Geofisika</div>", unsafe_allow_html=True)
