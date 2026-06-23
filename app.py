import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Cuu Can Cu - TCBS",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- GLOBAL STYLES (injected once, reliably) ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #0A0A0F !important;
    color: #E0E0F0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: #0D0D14;
    border-top: 1px solid #1E1E2E;
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 999;
    padding: 0; justify-content: space-around;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    color: #555570 !important; font-size: 10px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 4px 8px !important; flex-direction: column !important;
    gap: 2px !important; min-width: 0 !important; flex: 1 !important;
    justify-content: center !important; align-items: center !important;
    line-height: 1.3 !important;
}
.stTabs [aria-selected="true"] { color: #7C5CFC !important; background: transparent !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; padding-bottom: 80px !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #2A2A3E; border-radius: 2px; }
.stButton > button {
    background: linear-gradient(135deg, #7C5CFC, #5C8EFC) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
}
.stTextInput > div > div > input {
    background: #13131A !important; border: 1px solid #2A2A3E !important;
    border-radius: 12px !important; color: #E0E0F0 !important;
    font-family: 'Inter', sans-serif !important; padding: 12px 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ---- SESSION STATE ----
if "tcbs_unlocked" not in st.session_state:
    st.session_state.tcbs_unlocked = False

# ---- SHARED CSS FOR components.html ----
SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: #0A0A0F; color: #E0E0F0;
    font-family: 'Inter', sans-serif; overflow-x: hidden;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #2A2A3E; border-radius: 2px; }
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes slide-up {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-soft {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
@keyframes flow-dash {
    from { stroke-dashoffset: 30; }
    to { stroke-dashoffset: 0; }
}
"""


# ====================================================
# SCREEN 1: HOME
# ====================================================
def screen_home():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.header {{ display:flex; justify-content:space-between; align-items:center;
           padding:20px 24px 8px; background:#0A0A0F; }}
.sheep-wrap {{ text-align:center; padding:20px 0 8px; }}
.sheep-emoji {{ font-size:76px; display:inline-block; animation:float 4s ease-in-out infinite;
                filter:drop-shadow(0 8px 24px rgba(124,92,252,0.4)); }}
.tagline {{ font-size:16px; font-weight:600; color:#E0E0F0; line-height:1.6; margin-top:12px; }}
.tagline-sub {{ font-size:13px; color:#555570; margin-top:6px; }}
.stats {{ display:flex; gap:12px; padding:12px 24px; overflow-x:auto; }}
.stat-card {{ background:#13131A; border:1px solid #1E1E2E; border-radius:16px;
              padding:16px 18px; min-width:120px; flex-shrink:0; }}
.stat-label {{ font-size:11px; color:#555570; margin-bottom:4px; }}
.stat-value {{ font-size:22px; font-weight:700; }}
.stat-sub {{ font-size:11px; margin-top:2px; }}
.section-title {{ font-size:14px; font-weight:600; color:#E0E0F0; margin-bottom:12px; }}
.dreams {{ padding:8px 24px 0; }}
.dream-card {{ border-radius:20px; padding:18px; margin-bottom:12px; }}
.dream-top {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; }}
.dream-name {{ font-size:15px; font-weight:600; color:#E0E0F0; }}
.dream-sub {{ font-size:11px; color:#555570; margin-top:2px; }}
.dream-badge {{ border-radius:20px; padding:4px 12px; font-size:13px; font-weight:600; }}
.progress-bg {{ background:#0A0A0F; border-radius:100px; height:8px; overflow:hidden; }}
.progress-fill {{ height:100%; border-radius:100px; position:relative; overflow:hidden; }}
.progress-shine {{ position:absolute; top:0; left:0; right:0; bottom:0;
                   background:linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent);
                   animation:shimmer 2s infinite; }}
.dream-hint {{ font-size:11px; margin-top:6px; }}
.add-dream {{ border:1.5px dashed #2A2A3E; border-radius:20px; padding:18px;
              text-align:center; color:#555570; font-size:14px; margin:8px 24px 24px; }}
.avatar {{ width:40px; height:40px; border-radius:50%;
           background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
           display:flex; align-items:center; justify-content:center;
           font-size:18px; font-weight:700; color:white; }}
</style></head><body>

<div class="header">
  <div>
    <div style="font-size:11px;color:#555570;letter-spacing:1px;text-transform:uppercase;">Chao Buoi Sang</div>
    <div style="font-size:20px;font-weight:700;">Chao Minh An 👋</div>
  </div>
  <div class="avatar">M</div>
</div>

<div class="sheep-wrap">
  <span class="sheep-emoji">🐑</span>
  <div class="tagline">"Anh dang giu ho<br>tuong lai cua em"</div>
  <div class="tagline-sub">Cuu Can Cu &nbsp;•&nbsp; Nguoi ban tai chinh</div>
</div>

<div class="stats">
  <div class="stat-card">
    <div class="stat-label">Da tiet kiem</div>
    <div class="stat-value" style="color:#7C5CFC;">4.2M</div>
    <div class="stat-sub" style="color:#2ECC71;">+12% thang nay</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Streak hien tai</div>
    <div class="stat-value" style="color:#F5A623;">🔥 14</div>
    <div class="stat-sub" style="color:#555570;">ngay lien tiep</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Muc tieu gan nhat</div>
    <div class="stat-value" style="color:#2ECC71;">68%</div>
    <div class="stat-sub" style="color:#555570;">Concert Blackpink</div>
  </div>
</div>

<div class="dreams">
  <div class="section-title">Nhung giac mo cua em ✨</div>

  <div class="dream-card" style="background:#13131A;border:1px solid #2A1E5E;">
    <div class="dream-top">
      <div><div class="dream-name">🎵 Concert Blackpink</div><div class="dream-sub">VIP ticket &nbsp;•&nbsp; Thang 8/2025</div></div>
      <div class="dream-badge" style="background:rgba(124,92,252,0.15);border:1px solid rgba(124,92,252,0.3);color:#7C5CFC;">3.4M / 5M</div>
    </div>
    <div class="progress-bg"><div class="progress-fill" style="background:linear-gradient(90deg,#7C5CFC,#A78BFA);width:68%;">
      <div class="progress-shine"></div></div></div>
    <div class="dream-hint" style="color:#A78BFA;">🐑 Con 1.6M nua thoi! Co len nao~</div>
  </div>

  <div class="dream-card" style="background:#13131A;border:1px solid #1A2E1A;">
    <div class="dream-top">
      <div><div class="dream-name">✈️ Du lich Da Lat</div><div class="dream-sub">3 ngay 2 dem &nbsp;•&nbsp; Tet 2025</div></div>
      <div class="dream-badge" style="background:rgba(46,204,113,0.15);border:1px solid rgba(46,204,113,0.3);color:#2ECC71;">1.8M / 3M</div>
    </div>
    <div class="progress-bg"><div class="progress-fill" style="background:linear-gradient(90deg,#2ECC71,#27AE60);width:60%;"></div></div>
    <div class="dream-hint" style="color:#2ECC71;">🐑 Tuan nay tiet kiem them 200K nhe!</div>
  </div>

  <div class="dream-card" style="background:#13131A;border:1px solid #2E1A1A;">
    <div class="dream-top">
      <div><div class="dream-name">💻 MacBook Air M3</div><div class="dream-sub">Hoc lap trinh &nbsp;•&nbsp; Cuoi nam 2025</div></div>
      <div class="dream-badge" style="background:rgba(245,166,35,0.15);border:1px solid rgba(245,166,35,0.3);color:#F5A623;">800K / 28M</div>
    </div>
    <div class="progress-bg"><div class="progress-fill" style="background:linear-gradient(90deg,#F5A623,#E67E22);width:3%;"></div></div>
    <div class="dream-hint" style="color:#F5A623;">🐑 Moi bat dau! Moi ngay mot chut nhe~</div>
  </div>

  <div class="dream-card" style="background:#13131A;border:1px solid #1A1A2E;">
    <div class="dream-top">
      <div><div class="dream-name">🏠 Quy nha tuong lai</div><div class="dream-sub">iPower Fund &nbsp;•&nbsp; 5 nam</div></div>
      <div class="dream-badge" style="background:rgba(92,142,252,0.15);border:1px solid rgba(92,142,252,0.3);color:#5C8EFC;">0 / 500M</div>
    </div>
    <div class="progress-bg"><div class="progress-fill" style="background:linear-gradient(90deg,#5C8EFC,#7C5CFC);width:0.5%;"></div></div>
    <div class="dream-hint" style="color:#5C8EFC;">🐑 Hanh trinh van dam bat dau tu buoc dau tien!</div>
  </div>
</div>

<div class="add-dream">+ Them giac mo moi</div>

</body></html>"""
    components.html(html, height=1100, scrolling=True)


# ====================================================
# SCREEN 2: CHAT
# ====================================================
def screen_chat():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.chat-header {{ display:flex; justify-content:space-between; align-items:center;
                padding:14px 20px 12px; border-bottom:1px solid #1E1E2E;
                background:#0A0A0F; position:sticky; top:0; z-index:10; }}
.chat-body {{ padding:16px 20px 90px; display:flex; flex-direction:column; gap:14px; }}
.bubble-sheep {{ display:flex; gap:10px; align-items:flex-end; animation:slide-up 0.4s ease; }}
.bubble-sheep .text {{ background:#1E1A2E; border:1px solid #2A1E5E;
                       border-radius:18px 18px 18px 4px; padding:13px 15px;
                       max-width:82%; font-size:13.5px; color:#E0E0F0; line-height:1.65; }}
.bubble-user {{ display:flex; justify-content:flex-end; animation:slide-up 0.4s ease; }}
.bubble-user .text {{ background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
                      border-radius:18px 18px 4px 18px; padding:13px 15px;
                      max-width:72%; font-size:13.5px; color:#fff; line-height:1.65; }}
.quick-replies {{ margin-top:4px; }}
.qr-label {{ font-size:11px; color:#555570; margin-bottom:8px; }}
.qr-chips {{ display:flex; flex-wrap:wrap; gap:8px; }}
.qr-chip {{ background:#13131A; border:1px solid #2A1E5E; border-radius:20px;
            padding:8px 14px; font-size:12px; color:#A78BFA; cursor:pointer; }}
.input-bar {{ position:fixed; bottom:0; left:0; right:0; background:#0A0A0F;
              padding:10px 18px 14px; border-top:1px solid #1E1E2E; z-index:100; }}
.input-row {{ display:flex; gap:10px; align-items:center; }}
.input-box {{ flex:1; background:#13131A; border:1px solid #2A2A3E; border-radius:24px;
              padding:12px 18px; font-size:14px; color:#555570; }}
.send-btn {{ width:44px; height:44px; background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
             border-radius:50%; display:flex; align-items:center; justify-content:center;
             font-size:18px; flex-shrink:0; color:white; font-weight:bold; }}
.online-dot {{ width:7px; height:7px; background:#2ECC71; border-radius:50%; display:inline-block; }}
</style></head><body>

<div class="chat-header">
  <div style="display:flex;align-items:center;gap:12px;">
    <span style="font-size:30px;animation:float 4s ease-in-out infinite;display:inline-block;">🐑</span>
    <div>
      <div style="font-size:16px;font-weight:600;">Cuu Can Cu</div>
      <div style="display:flex;align-items:center;gap:5px;margin-top:2px;">
        <span class="online-dot"></span>
        <span style="font-size:11px;color:#555570;">Luon o day cho em</span>
      </div>
    </div>
  </div>
</div>

<div class="chat-body">

  <div class="bubble-sheep">
    <span style="font-size:26px;flex-shrink:0;">🐑</span>
    <div class="text">Chao buoi sang Minh An! ☀️ Hom nay em cam thay the nao roi?</div>
  </div>

  <div class="bubble-user">
    <div class="text">Minh kha on ban oi, hom qua minh da tiet kiem duoc 150K roi 😊</div>
  </div>

  <div class="bubble-sheep">
    <span style="font-size:26px;flex-shrink:0;">🐑</span>
    <div class="text">Oa, nghe ma vui ghe a! 🎉 150K hom qua cong voi streak 14 ngay roi do.
Em dang tien rat gan toi concert Blackpink — con khoang 1.6M nua thoi!<br><br>
Nhan tien, minh thay dao nay em hay nhac den "tu do" va "khong phu thuoc tai chinh"
— em dang mo den dieu gi vay?</div>
  </div>

  <div class="bubble-user">
    <div class="text">That ra minh muon co the tu quyet dinh cuoc song cua minh, khong can xin tien bo me nua</div>
  </div>

  <div class="bubble-sheep">
    <span style="font-size:26px;flex-shrink:0;">🐑</span>
    <div class="text">Minh hieu cam giac do! 💜 Tu do tai chinh khong chi la co nhieu tien
— ma la CO LUA CHON.<br><br>
Em biet khong, voi thoi quen tiet kiem deu dan nhu bay gio, chi can 6 thang nua
em co the xay duoc mot quy khan cap 3 thang chi tieu.
Do la buoc dau tien cua tu do do! 🌱</div>
  </div>

  <div class="bubble-user">
    <div class="text">Nghe hay do, nhung minh khong biet bat dau tu dau</div>
  </div>

  <div class="bubble-sheep">
    <span style="font-size:26px;flex-shrink:0;">🐑</span>
    <div class="text">Don gian lam! Cu lam theo 3 buoc:<br><br>
1️⃣ Tiep tuc tiet kiem moi ngay (em dang lam rat tot!)<br>
2️⃣ Khi du 2M, minh se giup em mo iPower de tien "de them tien"<br>
3️⃣ Tu tu giam phu thuoc, tang tu chu<br><br>
Muon minh dat muc tieu cu the cho em khong? 🐑</div>
  </div>

  <div class="quick-replies">
    <div class="qr-label">Goi y tra loi:</div>
    <div class="qr-chips">
      <div class="qr-chip">Co, giup minh dat muc tieu nhe!</div>
      <div class="qr-chip">iPower la gi vay?</div>
      <div class="qr-chip">Cho minh xem tien do tiet kiem</div>
    </div>
  </div>

</div>

<div class="input-bar">
  <div class="input-row">
    <div class="input-box">Noi chuyen voi Cuu...</div>
    <div class="send-btn">&#9658;</div>
  </div>
</div>

</body></html>"""
    components.html(html, height=750, scrolling=True)


# ====================================================
# SCREEN 3: JOURNAL
# ====================================================
def screen_journal():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.journal-wrap {{ padding:20px 24px 0; }}
.title {{ font-size:20px; font-weight:700; color:#E0E0F0; margin-bottom:4px; }}
.subtitle {{ font-size:13px; color:#555570; margin-bottom:20px; }}
.timeline-row {{ display:flex; gap:0; margin-bottom:0; }}
.day-col {{ display:flex; flex-direction:column; align-items:center; width:46px; flex-shrink:0; }}
.day-circle-active {{ width:34px;height:34px;background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
                      border-radius:50%;display:flex;align-items:center;justify-content:center;
                      font-size:11px;font-weight:700;color:#fff; }}
.day-circle {{ width:34px;height:34px;background:#1E1E2E;border:2px solid #2A2A3E;
               border-radius:50%;display:flex;align-items:center;justify-content:center;
               font-size:11px;font-weight:700;color:#555570; }}
.timeline-line {{ width:2px;flex:1;background:#1E1E2E;margin-top:4px;min-height:24px; }}
.entry-col {{ flex:1;padding-bottom:20px;margin-left:12px; }}
.entry-date {{ font-size:11px;color:#555570;margin-bottom:8px; }}
.entry-card {{ background:#13131A;border:1px solid #1E1E2E;border-radius:16px;padding:16px; }}
.entry-text {{ font-size:14px;color:#E0E0F0;line-height:1.6;margin-bottom:12px; }}
.sheep-reply {{ background:#1E1A2E;border-radius:12px;padding:12px;
                display:flex;gap:8px;margin-bottom:10px; }}
.sheep-reply-text {{ font-size:13px;color:#A78BFA;line-height:1.5; }}
.tag-row {{ display:flex;gap:8px;flex-wrap:wrap; }}
.tag {{ border-radius:20px;padding:4px 10px;font-size:11px; }}
.write-btn {{ background:linear-gradient(135deg,rgba(124,92,252,0.15),rgba(92,142,252,0.15));
              border:1.5px solid rgba(124,92,252,0.3);border-radius:20px;padding:18px;
              text-align:center;cursor:pointer;margin:0 0 24px; }}
</style></head><body>
<div class="journal-wrap">
  <div class="title">📖 Nhat ky tai chinh</div>
  <div class="subtitle">Hanh trinh cua Minh An</div>

  <!-- Entry T4 -->
  <div class="timeline-row">
    <div class="day-col">
      <div class="day-circle-active">T4</div>
      <div class="timeline-line"></div>
    </div>
    <div class="entry-col">
      <div class="entry-date">18/06/2025 &nbsp;•&nbsp; 21:30</div>
      <div class="entry-card">
        <div class="entry-text">Hom nay minh an com nha, tiet kiem duoc 80K tien an ngoai.
Cam thay tu hao lam! Tu nhien nghi den concert Blackpink,
khong biet minh co du tien khong...</div>
        <div class="sheep-reply">
          <span style="font-size:18px;">🐑</span>
          <div class="sheep-reply-text">Em ngoan lam! 80K hom nay + streak 14 ngay = em dang lam rat tot roi.
Concert chi con 1.6M nua thoi, cu giu da nay la duoc! 💜</div>
        </div>
        <div class="tag-row">
          <div class="tag" style="background:rgba(124,92,252,0.15);color:#A78BFA;">😊 Tu hao</div>
          <div class="tag" style="background:rgba(124,92,252,0.15);color:#A78BFA;">💰 +80K</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Entry T3 -->
  <div class="timeline-row">
    <div class="day-col">
      <div class="day-circle">T3</div>
      <div class="timeline-line"></div>
    </div>
    <div class="entry-col">
      <div class="entry-date">17/06/2025 &nbsp;•&nbsp; 19:15</div>
      <div class="entry-card">
        <div class="entry-text">Minh vua xem TED talk ve financial freedom. Wow, hoa ra voi 10 trieu moi thang,
neu dau tu dung cach thi 30 tuoi co the nghi huu som duoc.
Minh muon lam duoc vay!</div>
        <div class="sheep-reply">
          <span style="font-size:18px;">🐑</span>
          <div class="sheep-reply-text">Minh cung tin em lam duoc! "Tu do 30 tuoi" — minh se nho dieu nay
de nhac em moi khi em muon bo cuoc nhe. Day la dong luc that su cua em! 🌟</div>
        </div>
        <div class="tag-row">
          <div class="tag" style="background:rgba(46,204,113,0.15);color:#2ECC71;">🌟 Cam hung</div>
          <div class="tag" style="background:rgba(46,204,113,0.15);color:#2ECC71;">💡 Financial freedom</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Entry T2 -->
  <div class="timeline-row">
    <div class="day-col">
      <div class="day-circle">T2</div>
      <div class="timeline-line" style="min-height:4px;"></div>
    </div>
    <div class="entry-col">
      <div class="entry-date">16/06/2025 &nbsp;•&nbsp; 22:00</div>
      <div class="entry-card">
        <div class="entry-text">Hom nay minh bi cam do mua doi giay moi 1.2M nhung minh da khong mua.
Cam giac vua tiec vua tu hao.
Giay dep that nhung concert quan trong hon!</div>
        <div class="sheep-reply">
          <span style="font-size:18px;">🐑</span>
          <div class="sheep-reply-text">Em vua lam mot dieu rat dung cam! Chon tuong lai thay vi cam xuc nhat thoi
— day moi la that su truong thanh ve tai chinh. Minh tu hao ve em! 🎉</div>
        </div>
        <div class="tag-row">
          <div class="tag" style="background:rgba(245,166,35,0.15);color:#F5A623;">💪 Ky luat</div>
          <div class="tag" style="background:rgba(245,166,35,0.15);color:#F5A623;">Tranh mua sam</div>
        </div>
      </div>
    </div>
  </div>

  <div class="write-btn">
    <div style="font-size:22px;margin-bottom:6px;">✍️</div>
    <div style="font-size:14px;font-weight:600;color:#A78BFA;">Viet nhat ky hom nay</div>
    <div style="font-size:12px;color:#555570;margin-top:4px;">Chia se ngay hom nay cua em voi Cuu</div>
  </div>
</div>
</body></html>"""
    components.html(html, height=1000, scrolling=True)


# ====================================================
# SCREEN 4: COMMUNITY
# ====================================================
def screen_community():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.wrap {{ padding:20px 24px 0; }}
.title {{ font-size:20px;font-weight:700;color:#E0E0F0;margin-bottom:4px; }}
.subtitle {{ font-size:13px;color:#555570;margin-bottom:20px; }}
.post-card {{ background:#13131A;border:1px solid #1E1E2E;border-radius:20px;
              padding:18px;margin-bottom:14px; }}
.post-header {{ display:flex;align-items:center;gap:10px;margin-bottom:10px; }}
.avatar {{ width:36px;height:36px;border-radius:50%;display:flex;align-items:center;
           justify-content:center;font-size:15px;font-weight:700;color:white;flex-shrink:0; }}
.post-name {{ font-size:13px;font-weight:600;color:#E0E0F0; }}
.post-time {{ font-size:11px;color:#555570; }}
.badge {{ margin-left:auto;border-radius:20px;padding:4px 10px;font-size:11px; }}
.post-text {{ font-size:14px;color:#E0E0F0;line-height:1.5;margin-bottom:10px; }}
.sheep-note {{ background:#1E1A2E;border-radius:12px;padding:12px;
               display:flex;gap:8px;margin-bottom:10px; }}
.reactions {{ display:flex;gap:12px;font-size:13px;color:#555570; }}
.referral {{ background:linear-gradient(135deg,#7C5CFC,#5C8EFC);border-radius:20px;
             padding:20px;margin:16px 0 24px;position:relative;overflow:hidden; }}
</style></head><body>
<div class="wrap">
  <div class="title">🌟 Cong dong</div>
  <div class="subtitle">Cung nhau tien len!</div>

  <div class="post-card">
    <div class="post-header">
      <div class="avatar" style="background:linear-gradient(135deg,#FF6B6B,#FF8E53);">T</div>
      <div><div class="post-name">Thu Ha</div><div class="post-time">2 gio truoc</div></div>
      <div class="badge" style="background:rgba(46,204,113,0.15);color:#2ECC71;">🎯 Dat muc tieu</div>
    </div>
    <div class="post-text">Thang nay minh da tiet kiem duoc 3.5M! 🎉 Du tien mua ve xem phim hang thang roi.
Cam on Cuu Can Cu da nhac minh moi ngay!</div>
    <div class="reactions"><span>❤️ 24</span><span>💬 8</span><span>🔄 Chia se</span></div>
  </div>

  <div class="post-card">
    <div class="post-header">
      <div class="avatar" style="background:linear-gradient(135deg,#4FACFE,#00F2FE);">N</div>
      <div><div class="post-name">Nam Phong</div><div class="post-time">5 gio truoc</div></div>
      <div class="badge" style="background:rgba(124,92,252,0.15);color:#A78BFA;">🔥 Streak 30</div>
    </div>
    <div class="post-text">30 ngay streak! Khong bo sot ngay nao 💪 Cuu Can Cu da thay doi thoi quen tai chinh
cua minh hoan toan. Ai dang o streak ngay may roi?</div>
    <div class="reactions"><span>❤️ 47</span><span>💬 15</span><span>🔄 Chia se</span></div>
  </div>

  <div class="post-card">
    <div class="post-header">
      <div class="avatar" style="background:linear-gradient(135deg,#A18CD1,#FBC2EB);">L</div>
      <div><div class="post-name">Lan Anh</div><div class="post-time">8 gio truoc</div></div>
    </div>
    <div class="post-text">Moi nguoi oi! Cuu vua goi y minh mo iPower, minh dang phan van co nen thu khong?
Ai da dung cho minh xin review voi a 🙏</div>
    <div class="sheep-note">
      <span style="font-size:17px;">🐑</span>
      <div style="font-size:12px;color:#A78BFA;line-height:1.5;">
        Minh da giai thich cho Lan Anh roi nhe! iPower phu hop khi em co it nhat 1M tien nhan roi.
        Lai suat hien tai ~8%/nam, cao hon gui ngan hang nhieu!
      </div>
    </div>
    <div class="reactions"><span>❤️ 12</span><span>💬 23</span><span>🔄 Chia se</span></div>
  </div>

  <div class="referral">
    <div style="position:absolute;right:-20px;top:-20px;font-size:80px;opacity:0.08;">🐑</div>
    <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:6px;">Moi ban be, nhan 50K</div>
    <div style="font-size:13px;color:rgba(255,255,255,0.8);margin-bottom:14px;">
      Moi nguoi ban mo tai khoan = em nhan 50K vao quy tiet kiem!</div>
    <div style="background:rgba(255,255,255,0.2);border-radius:12px;padding:10px 16px;
                font-size:13px;color:#fff;font-weight:600;">🔗 Chia se link gioi thieu</div>
  </div>
</div>
</body></html>"""
    components.html(html, height=900, scrolling=True)


# ====================================================
# TCBS - SCREEN 5: MEMORY
# ====================================================
def screen_memory():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.wrap {{ padding:20px 24px 24px; }}
.tcbs-badge {{ display:inline-flex;align-items:center;gap:6px;
               background:rgba(124,92,252,0.15);border:1px solid rgba(124,92,252,0.3);
               border-radius:8px;padding:4px 10px;font-size:11px;color:#A78BFA;
               font-weight:600;margin-bottom:10px;letter-spacing:0.5px; }}
.title {{ font-size:20px;font-weight:700;color:#E0E0F0;margin-bottom:4px; }}
.subtitle {{ font-size:13px;color:#555570;margin-bottom:20px; }}
.grid2 {{ display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px; }}
.mem-card {{ border-radius:16px;padding:16px; }}
.mem-card-label {{ font-size:11px;font-weight:600;margin-bottom:10px;letter-spacing:0.5px; }}
.mem-row {{ display:flex;gap:8px;align-items:flex-start;margin-bottom:7px; }}
.mem-name {{ font-size:13px;color:#E0E0F0; }}
.mem-sub {{ font-size:11px;color:#555570; }}
.tag {{ border-radius:20px;padding:5px 12px;font-size:12px;margin:3px; }}
.score-box {{ background:linear-gradient(135deg,rgba(124,92,252,0.1),rgba(92,142,252,0.1));
              border:1px solid rgba(124,92,252,0.2);border-radius:16px;
              padding:16px;margin-top:4px; }}
</style></head><body>
<div class="wrap">
  <div class="tcbs-badge">🔒 TCBS INTERNAL</div>
  <div class="title">🧠 Memory Engine</div>
  <div class="subtitle">Nhung gi Cuu Can Cu dang nho ve Minh An</div>

  <!-- Dreams -->
  <div class="mem-card" style="background:#1A1A10;border:1px solid #2E2A10;margin-bottom:12px;">
    <div class="mem-card-label" style="color:#F5A623;">DREAMS + ASPIRATIONS</div>
    <div class="mem-row">
      <span style="font-size:16px;">🎵</span>
      <div><div class="mem-name">Concert Blackpink VIP</div><div class="mem-sub">Nhac den 8 lan &nbsp;•&nbsp; Cam xuc: Rat hung khoi</div></div>
    </div>
    <div class="mem-row">
      <span style="font-size:16px;">🏠</span>
      <div><div class="mem-name">Tu do tai chinh truoc 30 tuoi</div><div class="mem-sub">Nhac den 5 lan &nbsp;•&nbsp; Core motivation</div></div>
    </div>
    <div class="mem-row">
      <span style="font-size:16px;">✈️</span>
      <div><div class="mem-name">Du lich Da Lat + Nhat Ban</div><div class="mem-sub">Nhac den 3 lan &nbsp;•&nbsp; Ket noi voi "tu do"</div></div>
    </div>
  </div>

  <!-- 2 col grid -->
  <div class="grid2">
    <div class="mem-card" style="background:#0F1A1F;border:1px solid #1A2E3A;">
      <div class="mem-card-label" style="color:#5C8EFC;">HAPPINESS TRIGGERS</div>
      <div style="font-size:13px;color:#E0E0F0;line-height:1.8;">🍱 Com nha<br>💪 Dat muc tieu nho<br>🎵 Nghe K-pop<br>📚 Hoc dieu moi</div>
    </div>
    <div class="mem-card" style="background:#1A0F1A;border:1px solid #2E1A3A;">
      <div class="mem-card-label" style="color:#A78BFA;">VALUES</div>
      <div style="font-size:13px;color:#E0E0F0;line-height:1.8;">Tu do, doc lap<br>Ky luat ban than<br>Gia dinh<br>Phat trien ban than</div>
    </div>
  </div>

  <!-- Behavior -->
  <div class="mem-card" style="background:#0F1A0F;border:1px solid #1A2E1A;margin-bottom:12px;">
    <div class="mem-card-label" style="color:#2ECC71;">BEHAVIOR PATTERNS</div>
    <div style="display:flex;flex-wrap:wrap;">
      <span class="tag" style="background:rgba(46,204,113,0.15);color:#2ECC71;">Tiet kiem buoi toi 21-22h</span>
      <span class="tag" style="background:rgba(46,204,113,0.15);color:#2ECC71;">Nhac ban be cung tiet kiem</span>
      <span class="tag" style="background:rgba(46,204,113,0.15);color:#2ECC71;">Can duoc khuyen khich</span>
      <span class="tag" style="background:rgba(46,204,113,0.15);color:#2ECC71;">Phan hoi nhanh buoi sang</span>
    </div>
  </div>

  <!-- Pain points -->
  <div class="mem-card" style="background:#1A100F;border:1px solid #3A1A1A;margin-bottom:12px;">
    <div class="mem-card-label" style="color:#FF6B6B;">PAIN POINTS</div>
    <div style="font-size:13px;color:#E0E0F0;line-height:1.8;">
      Lo so khong du tien cuoi thang<br>
      Tuc gian khi bi cam do chi tieu<br>
      Bat an ve tuong lai tai chinh
    </div>
  </div>

  <div class="score-box">
    <div style="font-size:12px;color:#555570;margin-bottom:4px;">TCBS Memory Score</div>
    <div style="font-size:28px;font-weight:700;color:#7C5CFC;">87 / 100</div>
    <div style="font-size:12px;color:#A78BFA;margin-top:4px;">
      Du lieu tu 23 cuoc hoi thoai &nbsp;•&nbsp; 14 ngay streak &nbsp;•&nbsp; 3 journal entries</div>
  </div>
</div>
</body></html>"""
    components.html(html, height=1000, scrolling=True)


# ====================================================
# TCBS - SCREEN 6: INTEREST MAP
# ====================================================
def screen_interest_map():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.wrap {{ padding:20px 24px 0; }}
.tcbs-badge {{ display:inline-flex;align-items:center;gap:6px;
               background:rgba(124,92,252,0.15);border:1px solid rgba(124,92,252,0.3);
               border-radius:8px;padding:4px 10px;font-size:11px;color:#A78BFA;
               font-weight:600;margin-bottom:10px; }}
.title {{ font-size:20px;font-weight:700;color:#E0E0F0;margin-bottom:4px; }}
.subtitle {{ font-size:13px;color:#555570;margin-bottom:16px; }}
svg {{ width:100%;max-height:440px;display:block; }}
@keyframes pulse-core {{ 0%,100%{{opacity:1;}}50%{{opacity:0.55;}} }}
@keyframes dash-flow {{ from{{stroke-dashoffset:30;}}to{{stroke-dashoffset:0;}} }}
.insight-box {{ background:#13131A;border:1px solid #1E1E2E;border-radius:16px;padding:16px;margin:16px 0 24px; }}
.ins-row {{ display:flex;gap:8px;align-items:flex-start;margin-bottom:8px; }}
</style></head><body>
<div class="wrap">
  <div class="tcbs-badge">🔒 TCBS INTERNAL</div>
  <div class="title">🕸 Interest Map</div>
  <div class="subtitle">Mang luoi mong muon — phong cach Obsidian</div>
</div>

<svg viewBox="0 0 380 440">
  <defs>
    <radialGradient id="bg" cx="50%" cy="49%" r="50%">
      <stop offset="0%" stop-color="#7C5CFC" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#7C5CFC" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="380" height="440" fill="#0A0A0F"/>
  <ellipse cx="190" cy="210" rx="165" ry="145" fill="url(#bg)"/>

  <!-- Animated edges -->
  <line x1="190" y1="210" x2="72" y2="115" stroke="#7C5CFC" stroke-width="1.5" opacity="0.5" stroke-dasharray="6,4" style="animation:dash-flow 3s linear infinite"/>
  <line x1="190" y1="210" x2="308" y2="90" stroke="#A78BFA" stroke-width="1.5" opacity="0.45" stroke-dasharray="6,4" style="animation:dash-flow 3s linear infinite 0.5s"/>
  <line x1="190" y1="210" x2="342" y2="208" stroke="#5C8EFC" stroke-width="1.5" opacity="0.4" stroke-dasharray="6,4" style="animation:dash-flow 3s linear infinite 1s"/>
  <line x1="190" y1="210" x2="282" y2="345" stroke="#2ECC71" stroke-width="1.5" opacity="0.4" stroke-dasharray="6,4" style="animation:dash-flow 3s linear infinite 1.5s"/>
  <line x1="190" y1="210" x2="60" y2="318" stroke="#F5A623" stroke-width="1.5" opacity="0.4" stroke-dasharray="6,4" style="animation:dash-flow 3s linear infinite 2s"/>
  <line x1="190" y1="210" x2="115" y2="375" stroke="#FF9FF3" stroke-width="1.2" opacity="0.3" stroke-dasharray="5,4" style="animation:dash-flow 3s linear infinite 2.5s"/>
  <!-- Cross edges -->
  <line x1="72" y1="115" x2="308" y2="90" stroke="#333" stroke-width="0.8" opacity="0.25" stroke-dasharray="4,4" style="animation:dash-flow 4s linear infinite"/>
  <line x1="308" y1="90" x2="342" y2="208" stroke="#333" stroke-width="0.8" opacity="0.2" stroke-dasharray="4,4" style="animation:dash-flow 4s linear infinite 1s"/>
  <line x1="282" y1="345" x2="115" y2="375" stroke="#333" stroke-width="0.8" opacity="0.2" stroke-dasharray="4,4" style="animation:dash-flow 4s linear infinite 2s"/>

  <!-- Satellite nodes -->
  <!-- Travel -->
  <circle cx="72" cy="115" r="31" fill="#050810" stroke="#5C8EFC" stroke-width="1.5" opacity="0.9" filter="url(#glow)"/>
  <text x="72" y="106" text-anchor="middle" font-size="17" font-family="sans-serif">✈️</text>
  <text x="72" y="121" text-anchor="middle" font-size="9.5" fill="#5C8EFC" font-family="Inter,sans-serif" font-weight="600">Du lich</text>
  <text x="72" y="132" text-anchor="middle" font-size="8.5" fill="#555570" font-family="Inter,sans-serif">Da Lat, Nhat</text>

  <!-- Concert -->
  <circle cx="308" cy="90" r="35" fill="#050810" stroke="#A78BFA" stroke-width="2" opacity="0.95" filter="url(#glow)"/>
  <text x="308" y="80" text-anchor="middle" font-size="19" font-family="sans-serif">🎵</text>
  <text x="308" y="96" text-anchor="middle" font-size="9.5" fill="#A78BFA" font-family="Inter,sans-serif" font-weight="600">Concert</text>
  <text x="308" y="107" text-anchor="middle" font-size="8.5" fill="#555570" font-family="Inter,sans-serif">Blackpink VIP</text>

  <!-- MacBook -->
  <circle cx="342" cy="208" r="28" fill="#050810" stroke="#2ECC71" stroke-width="1.5" opacity="0.9"/>
  <text x="342" y="199" text-anchor="middle" font-size="16" font-family="sans-serif">💻</text>
  <text x="342" y="214" text-anchor="middle" font-size="9" fill="#2ECC71" font-family="Inter,sans-serif" font-weight="600">MacBook</text>
  <text x="342" y="225" text-anchor="middle" font-size="8" fill="#555570" font-family="Inter,sans-serif">Hoc lap trinh</text>

  <!-- House -->
  <circle cx="282" cy="345" r="29" fill="#050810" stroke="#F5A623" stroke-width="1.5" opacity="0.9"/>
  <text x="282" y="336" text-anchor="middle" font-size="16" font-family="sans-serif">🏠</text>
  <text x="282" y="351" text-anchor="middle" font-size="9" fill="#F5A623" font-family="Inter,sans-serif" font-weight="600">Nha rieng</text>
  <text x="282" y="362" text-anchor="middle" font-size="8" fill="#555570" font-family="Inter,sans-serif">Muc tieu 5 nam</text>

  <!-- Freedom -->
  <circle cx="60" cy="318" r="33" fill="#050810" stroke="#FF6B6B" stroke-width="1.5" opacity="0.9"/>
  <text x="60" y="308" text-anchor="middle" font-size="17" font-family="sans-serif">💸</text>
  <text x="60" y="324" text-anchor="middle" font-size="9" fill="#FF6B6B" font-family="Inter,sans-serif" font-weight="600">Tu do TC</text>
  <text x="60" y="335" text-anchor="middle" font-size="8" fill="#555570" font-family="Inter,sans-serif">Truoc 30 tuoi</text>

  <!-- Family -->
  <circle cx="115" cy="375" r="25" fill="#050810" stroke="#FF9FF3" stroke-width="1.5" opacity="0.8"/>
  <text x="115" y="366" text-anchor="middle" font-size="14" font-family="sans-serif">👨‍👩‍👧</text>
  <text x="115" y="381" text-anchor="middle" font-size="9" fill="#FF9FF3" font-family="Inter,sans-serif" font-weight="600">Gia dinh</text>

  <!-- Core node -->
  <circle cx="190" cy="210" r="58" fill="rgba(124,92,252,0.07)" style="animation:pulse-core 3s ease-in-out infinite"/>
  <circle cx="190" cy="210" r="44" fill="#0C0818" stroke="#7C5CFC" stroke-width="2.5" filter="url(#glow)"/>
  <text x="190" y="197" text-anchor="middle" font-size="20" font-family="sans-serif">🕊️</text>
  <text x="190" y="215" text-anchor="middle" font-size="13.5" fill="#A78BFA" font-family="Inter,sans-serif" font-weight="700">Tu Do</text>
  <text x="190" y="229" text-anchor="middle" font-size="9.5" fill="#555570" font-family="Inter,sans-serif">Core Value</text>

  <text x="10" y="435" fill="#444" font-size="9" font-family="Inter,sans-serif">Phan tich tu 23 cuoc hoi thoai • Cuu Can Cu Memory Engine</text>
</svg>

<div style="padding:0 24px 24px;">
  <div class="insight-box">
    <div style="font-size:11px;color:#555570;margin-bottom:10px;letter-spacing:0.5px;">KEY INSIGHTS</div>
    <div class="ins-row"><span style="font-size:15px;">🎯</span>
      <div style="font-size:13px;color:#E0E0F0;line-height:1.5;">
        <strong style="color:#A78BFA;">"Tu Do"</strong> la node trung tam — ket noi voi TAT CA cac mong muon</div></div>
    <div class="ins-row"><span style="font-size:15px;">📊</span>
      <div style="font-size:13px;color:#E0E0F0;line-height:1.5;">
        Concert + Travel cung nhom <strong style="color:#7C5CFC;">trai nghiem song</strong></div></div>
    <div class="ins-row"><span style="font-size:15px;">💡</span>
      <div style="font-size:13px;color:#E0E0F0;line-height:1.5;">
        Segment: <strong style="color:#2ECC71;">Goal-Driven Saver</strong> &nbsp;•&nbsp; Risk: Medium</div></div>
  </div>
</div>
</body></html>"""
    components.html(html, height=900, scrolling=True)


# ====================================================
# TCBS - SCREEN 7: FLOW
# ====================================================
def screen_tcbs_flow():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.wrap {{ padding:20px 24px 24px; }}
.tcbs-badge {{ display:inline-flex;align-items:center;gap:6px;background:rgba(124,92,252,0.15);
               border:1px solid rgba(124,92,252,0.3);border-radius:8px;padding:4px 10px;
               font-size:11px;color:#A78BFA;font-weight:600;margin-bottom:10px; }}
.title {{ font-size:20px;font-weight:700;color:#E0E0F0;margin-bottom:4px; }}
.subtitle {{ font-size:13px;color:#555570;margin-bottom:20px; }}
.flow-step {{ border-radius:20px;padding:18px;margin-bottom:0; }}
.step-header {{ display:flex;gap:12px;align-items:center; }}
.step-title {{ font-size:14px;font-weight:600; }}
.step-desc {{ font-size:12px;color:#555570;margin-top:2px; }}
.step-badge {{ border-radius:10px;padding:4px 8px;font-size:10px;white-space:nowrap;margin-left:auto; }}
.step-tags {{ display:flex;flex-wrap:wrap;gap:6px;margin-top:10px; }}
.step-tag {{ border-radius:20px;padding:4px 10px;font-size:11px; }}
.arrow {{ display:flex;flex-direction:column;align-items:center;height:28px; }}
.arrow-line {{ width:2px;flex:1; }}
.arrow-head {{ font-size:13px;line-height:1; }}
</style></head><body>
<div class="wrap">
  <div class="tcbs-badge">🔒 TCBS INTERNAL</div>
  <div class="title">🔒 TCBS Intelligence Flow</div>
  <div class="subtitle">Tu cuoc tro chuyen → Hieu khach hang → De xuat san pham</div>

  <!-- Step 1 -->
  <div class="flow-step" style="background:linear-gradient(135deg,#1E1A2E,#13131A);border:1.5px solid #7C5CFC;">
    <div class="step-header">
      <span style="font-size:26px;">💬</span>
      <div style="flex:1;"><div class="step-title" style="color:#A78BFA;">Chat + Journal</div>
        <div class="step-desc">Khach hang noi chuyen tu nhien, chia se cam xuc, ghi nhat ky</div></div>
      <div class="step-badge" style="background:rgba(124,92,252,0.2);color:#7C5CFC;">INPUT</div>
    </div>
    <div class="step-tags">
      <div class="step-tag" style="background:#0A0A0F;color:#555570;">"Muon tu do tai chinh"</div>
      <div class="step-tag" style="background:#0A0A0F;color:#555570;">"Mua ve concert"</div>
      <div class="step-tag" style="background:#0A0A0F;color:#555570;">"Tiet kiem 150K"</div>
    </div>
  </div>

  <div class="arrow"><div class="arrow-line" style="background:linear-gradient(180deg,#7C5CFC,#5C8EFC);"></div>
    <div class="arrow-head" style="color:#5C8EFC;">▼</div></div>

  <!-- Step 2 -->
  <div class="flow-step" style="background:linear-gradient(135deg,#1A1A2E,#13131A);border:1.5px solid #5C8EFC;">
    <div class="step-header">
      <span style="font-size:26px;">🧠</span>
      <div style="flex:1;"><div class="step-title" style="color:#5C8EFC;">Memory Engine</div>
        <div class="step-desc">AI trich xuat: Dreams, Values, Triggers, Pain Points, Behavior</div></div>
      <div class="step-badge" style="background:rgba(92,142,252,0.2);color:#5C8EFC;">PROCESS</div>
    </div>
  </div>

  <div class="arrow"><div class="arrow-line" style="background:linear-gradient(180deg,#5C8EFC,#2ECC71);"></div>
    <div class="arrow-head" style="color:#2ECC71;">▼</div></div>

  <!-- Step 3 -->
  <div class="flow-step" style="background:linear-gradient(135deg,#0F1A1F,#13131A);border:1.5px solid #2ECC71;">
    <div class="step-header">
      <span style="font-size:26px;">🕸️</span>
      <div style="flex:1;"><div class="step-title" style="color:#2ECC71;">Interest Graph</div>
        <div class="step-desc">Xay dung mang luoi mong muon → Tim core motivation</div></div>
      <div class="step-badge" style="background:rgba(46,204,113,0.2);color:#2ECC71;">ANALYZE</div>
    </div>
  </div>

  <div class="arrow"><div class="arrow-line" style="background:linear-gradient(180deg,#2ECC71,#F5A623);"></div>
    <div class="arrow-head" style="color:#F5A623;">▼</div></div>

  <!-- Step 4 -->
  <div class="flow-step" style="background:linear-gradient(135deg,#1A1A10,#13131A);border:1.5px solid #F5A623;">
    <div class="step-header">
      <span style="font-size:26px;">🔍</span>
      <div style="flex:1;"><div class="step-title" style="color:#F5A623;">Insight Engine</div>
        <div class="step-desc">Deep Research: Segment + Risk Profile + Product Readiness</div></div>
      <div class="step-badge" style="background:rgba(245,166,35,0.2);color:#F5A623;">INSIGHT</div>
    </div>
    <div class="step-tags">
      <div class="step-tag" style="background:rgba(245,166,35,0.15);color:#F5A623;">Goal-Driven Saver</div>
      <div class="step-tag" style="background:rgba(245,166,35,0.15);color:#F5A623;">Risk: Medium</div>
      <div class="step-tag" style="background:rgba(245,166,35,0.15);color:#F5A623;">iPower Ready: 68%</div>
    </div>
  </div>

  <div class="arrow"><div class="arrow-line" style="background:linear-gradient(180deg,#F5A623,#FF6B6B);"></div>
    <div class="arrow-head" style="color:#FF6B6B;">▼</div></div>

  <!-- Step 5 -->
  <div class="flow-step" style="background:linear-gradient(135deg,#1A100F,#13131A);border:1.5px solid #FF6B6B;">
    <div class="step-header">
      <span style="font-size:26px;">💰</span>
      <div style="flex:1;"><div class="step-title" style="color:#FF6B6B;">Product Recommendation</div>
        <div class="step-desc">De xuat dung san pham, dung luc, dung nguoi</div></div>
      <div class="step-badge" style="background:rgba(255,107,107,0.2);color:#FF6B6B;">OUTPUT</div>
    </div>
    <div class="step-tags">
      <div class="step-tag" style="background:rgba(255,107,107,0.15);border:1px solid rgba(255,107,107,0.3);color:#FF6B6B;">iPower Fund</div>
      <div class="step-tag" style="background:rgba(255,107,107,0.15);border:1px solid rgba(255,107,107,0.3);color:#FF6B6B;">TCBS Stocks Starter</div>
      <div class="step-tag" style="background:rgba(255,107,107,0.15);border:1px solid rgba(255,107,107,0.3);color:#FF6B6B;">Goal Savings</div>
    </div>
  </div>

</div>
</body></html>"""
    components.html(html, height=980, scrolling=True)


# ====================================================
# TCBS - SCREEN 8: INSIGHT + CEO SLIDE
# ====================================================
def screen_tcbs_insight():
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.wrap {{ padding:20px 24px 24px; }}
.tcbs-badge {{ display:inline-flex;align-items:center;gap:6px;background:rgba(124,92,252,0.15);
               border:1px solid rgba(124,92,252,0.3);border-radius:8px;padding:4px 10px;
               font-size:11px;color:#A78BFA;font-weight:600;margin-bottom:10px; }}
.title {{ font-size:20px;font-weight:700;color:#E0E0F0;margin-bottom:4px; }}
.subtitle {{ font-size:13px;color:#555570;margin-bottom:20px; }}
.card {{ background:#13131A;border:1px solid #1E1E2E;border-radius:20px;padding:20px;margin-bottom:16px; }}
.grid2 {{ display:grid;grid-template-columns:1fr 1fr;gap:10px; }}
.mini-card {{ background:#0A0A0F;border-radius:12px;padding:12px; }}
.mini-label {{ font-size:10px;color:#555570;margin-bottom:4px; }}
.mini-val {{ font-size:13px;font-weight:600; }}
.desire-row {{ display:flex;gap:10px;align-items:center;margin-bottom:10px; }}
.desire-icon {{ width:32px;height:32px;border-radius:8px;display:flex;align-items:center;
                justify-content:center;font-size:15px;flex-shrink:0; }}
.desire-bar-bg {{ background:#0A0A0F;border-radius:100px;height:4px;margin-top:4px; }}
.desire-bar {{ height:100%;border-radius:100px; }}
.journey {{ display:flex;gap:4px;align-items:center;margin-bottom:14px;overflow-x:auto; }}
.journey-step {{ text-align:center;flex-shrink:0;min-width:46px; }}
.ceo-slide {{ background:linear-gradient(135deg,#070412,#050C12,#050C06);
              border:1px solid #2A2A3E;border-radius:24px;padding:22px;
              position:relative;overflow:hidden; }}
.two-col {{ display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px; }}
.split-box {{ border-radius:16px;padding:14px; }}
.split-item {{ font-size:12px;color:#E0E0F0;margin-bottom:4px; }}
.moat-box {{ background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
             border-radius:14px;padding:14px;text-align:center; }}
</style></head><body>
<div class="wrap">
  <div class="tcbs-badge">🔒 TCBS INTERNAL</div>
  <div class="title">🔍 TCBS Insight</div>
  <div class="subtitle">Nhung gi TCBS thuc su hieu ve khach hang</div>

  <!-- Profile -->
  <div class="card">
    <div style="display:flex;gap:12px;align-items:center;margin-bottom:16px;">
      <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
                  display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:white;">M</div>
      <div style="flex:1;"><div style="font-size:15px;font-weight:600;color:#E0E0F0;">Nguyen Minh An</div>
        <div style="font-size:12px;color:#555570;">22 tuoi &nbsp;•&nbsp; Streak 14 ngay</div></div>
      <div style="text-align:right;"><div style="font-size:22px;font-weight:700;color:#7C5CFC;">87</div>
        <div style="font-size:10px;color:#555570;">Engagement</div></div>
    </div>
    <div class="grid2">
      <div class="mini-card"><div class="mini-label">SEGMENT</div><div class="mini-val" style="color:#2ECC71;">Goal-Driven Saver</div></div>
      <div class="mini-card"><div class="mini-label">RISK</div><div class="mini-val" style="color:#F5A623;">Medium</div></div>
      <div class="mini-card"><div class="mini-label">LIFE STAGE</div><div class="mini-val" style="color:#5C8EFC;">Emerging Adult</div></div>
      <div class="mini-card"><div class="mini-label">NEXT PRODUCT</div><div class="mini-val" style="color:#FF6B6B;">iPower Fund</div></div>
    </div>
  </div>

  <!-- Core Desires -->
  <div class="card">
    <div style="font-size:13px;font-weight:600;color:#E0E0F0;margin-bottom:12px;">Core Desires — CAM XUC, khong phai san pham</div>
    <div class="desire-row">
      <div class="desire-icon" style="background:rgba(124,92,252,0.15);">🕊️</div>
      <div style="flex:1;"><div style="font-size:13px;color:#E0E0F0;">TU DO — khong phu thuoc</div>
        <div class="desire-bar-bg"><div class="desire-bar" style="background:#7C5CFC;width:92%;"></div></div></div>
      <div style="font-size:12px;color:#7C5CFC;font-weight:600;flex-shrink:0;margin-left:8px;">92%</div>
    </div>
    <div class="desire-row">
      <div class="desire-icon" style="background:rgba(46,204,113,0.15);">🎯</div>
      <div style="flex:1;"><div style="font-size:13px;color:#E0E0F0;">TIEN BO — co muc tieu ro rang</div>
        <div class="desire-bar-bg"><div class="desire-bar" style="background:#2ECC71;width:85%;"></div></div></div>
      <div style="font-size:12px;color:#2ECC71;font-weight:600;flex-shrink:0;margin-left:8px;">85%</div>
    </div>
    <div class="desire-row" style="margin-bottom:0;">
      <div class="desire-icon" style="background:rgba(245,166,35,0.15);">💎</div>
      <div style="flex:1;"><div style="font-size:13px;color:#E0E0F0;">TRUONG THANH — tu lap</div>
        <div class="desire-bar-bg"><div class="desire-bar" style="background:#F5A623;width:78%;"></div></div></div>
      <div style="font-size:12px;color:#F5A623;font-weight:600;flex-shrink:0;margin-left:8px;">78%</div>
    </div>
  </div>

  <!-- Revenue Journey -->
  <div class="card">
    <div style="font-size:13px;font-weight:600;color:#E0E0F0;margin-bottom:14px;">Revenue Journey — Dream to Product</div>
    <div class="journey">
      <div class="journey-step"><div style="font-size:22px;">🌱</div><div style="font-size:9px;color:#555570;margin-top:3px;">10K/ngay</div></div>
      <div style="color:#444;font-size:14px;">→</div>
      <div class="journey-step"><div style="font-size:22px;">💰</div><div style="font-size:9px;color:#555570;margin-top:3px;">Tiet kiem</div></div>
      <div style="color:#444;font-size:14px;">→</div>
      <div class="journey-step"><div style="font-size:22px;">🔥</div><div style="font-size:9px;color:#555570;margin-top:3px;">Thoi quen</div></div>
      <div style="color:#444;font-size:14px;">→</div>
      <div class="journey-step"><div style="font-size:22px;">📈</div><div style="font-size:9px;color:#A78BFA;margin-top:3px;font-weight:600;">iPower</div></div>
      <div style="color:#444;font-size:14px;">→</div>
      <div class="journey-step"><div style="font-size:22px;">🏆</div><div style="font-size:9px;color:#FF6B6B;margin-top:3px;font-weight:600;">TCBS Fund</div></div>
    </div>
    <div class="grid2" style="gap:8px;">
      <div class="mini-card" style="text-align:center;"><div style="font-size:14px;font-weight:700;color:#7C5CFC;">0.3M</div><div style="font-size:10px;color:#555570;">AUM hien tai</div></div>
      <div class="mini-card" style="text-align:center;"><div style="font-size:14px;font-weight:700;color:#2ECC71;">2M</div><div style="font-size:10px;color:#555570;">Target iPower</div></div>
    </div>
  </div>

  <!-- CEO FINAL SLIDE -->
  <div class="ceo-slide">
    <div style="position:absolute;top:-40px;right:-40px;font-size:130px;opacity:0.04;pointer-events:none;">🐑</div>
    <div style="text-align:center;margin-bottom:18px;">
      <div style="font-size:10px;color:#555570;letter-spacing:2px;margin-bottom:8px;">THE BIG PICTURE</div>
      <div style="font-size:17px;font-weight:700;color:#E0E0F0;line-height:1.55;">
        Chung ta khong xay dung chatbot.<br>
        <span style="color:#A78BFA;">Chung ta xay dung</span>
      </div>
      <div style="font-size:20px;font-weight:800;
                  background:linear-gradient(90deg,#7C5CFC,#5C8EFC,#2ECC71);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  margin-top:4px;">
        Second Financial Brain.
      </div>
    </div>
    <div class="two-col">
      <div class="split-box" style="background:rgba(124,92,252,0.1);border:1px solid rgba(124,92,252,0.2);">
        <div style="font-size:10px;color:#7C5CFC;font-weight:600;margin-bottom:8px;letter-spacing:0.5px;">KHACH HANG THAY</div>
        <div class="split-item">🐑 Nguoi ban tai chinh</div>
        <div class="split-item">Ho tro giac mo</div>
        <div class="split-item">Tro chuyen tu nhien</div>
        <div class="split-item">Nhat ky cam xuc</div>
        <div class="split-item">Cong dong ung ho</div>
      </div>
      <div class="split-box" style="background:rgba(46,204,113,0.1);border:1px solid rgba(46,204,113,0.2);">
        <div style="font-size:10px;color:#2ECC71;font-weight:600;margin-bottom:8px;letter-spacing:0.5px;">TCBS NHAN DUOC</div>
        <div class="split-item">Deep customer insight</div>
        <div class="split-item">Precise segmentation</div>
        <div class="split-item">Behavior prediction</div>
        <div class="split-item">Right product, right time</div>
        <div class="split-item">Higher conversion</div>
      </div>
    </div>
    <div class="moat-box">
      <div style="font-size:10px;color:#555570;margin-bottom:6px;letter-spacing:1px;">THE MOAT</div>
      <div style="font-size:13px;font-weight:600;color:#E0E0F0;line-height:1.5;">
        Moi cuoc tro chuyen = TCBS hieu KH hon doi thu.
      </div>
      <div style="font-size:12px;color:#A78BFA;margin-top:6px;">
        Khong the copy. Khong the mua. Chi co the XAY DUNG.
      </div>
    </div>
  </div>

</div>
</body></html>"""
    components.html(html, height=1300, scrolling=True)


# ====================================================
# MAIN
# ====================================================
def main():
    if st.session_state.tcbs_unlocked:
        tabs = st.tabs(["🏠", "💬", "📖", "🌟", "🧠 Memory", "🕸 Map", "🔒 Flow", "🔍 Insight"])
        with tabs[0]: screen_home()
        with tabs[1]: screen_chat()
        with tabs[2]: screen_journal()
        with tabs[3]: screen_community()
        with tabs[4]: screen_memory()
        with tabs[5]: screen_interest_map()
        with tabs[6]: screen_tcbs_flow()
        with tabs[7]: screen_tcbs_insight()
    else:
        tabs = st.tabs(["🏠 Home", "💬 Chat", "📖 Journal", "🌟 Cong dong", "🔒"])
        with tabs[0]: screen_home()
        with tabs[1]: screen_chat()
        with tabs[2]: screen_journal()
        with tabs[3]: screen_community()
        with tabs[4]:
            components.html(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{SHARED_CSS}
.lock-wrap {{ min-height:70vh; display:flex; flex-direction:column; align-items:center;
              justify-content:center; padding:40px 24px; text-align:center; }}
.lock-icon {{ font-size:60px; display:inline-block; animation:float 3s ease-in-out infinite; margin-bottom:18px; }}
.lock-title {{ font-size:22px; font-weight:700; color:#E0E0F0; margin-bottom:8px; }}
.lock-desc {{ font-size:14px; color:#555570; line-height:1.6; max-width:260px; }}
</style></head><body>
<div class="lock-wrap">
  <div class="lock-icon">🔒</div>
  <div class="lock-title">TCBS Intelligence</div>
  <div class="lock-desc">Khu vuc noi bo TCBS.<br>Nhap PIN de xem toan bo du lieu phan tich khach hang.<br><br>
    <strong style="color:#7C5CFC;">Demo PIN: 1234</strong>
  </div>
</div>
</body></html>""", height=500)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                pin = st.text_input(
                    "PIN",
                    type="password",
                    placeholder="Nhap PIN TCBS...",
                    key="pin_input",
                    label_visibility="collapsed"
                )
                if st.button("Unlock TCBS World", use_container_width=True):
                    if pin in ["1234", "tcbs", "TCBS", "demo"]:
                        st.session_state.tcbs_unlocked = True
                        st.rerun()
                    elif pin:
                        st.error("PIN khong dung. Demo PIN: 1234")


if __name__ == "__main__":
    main()
