import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Cuu Can Cu - TCBS",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- GLOBAL CSS ----
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

/* Streamlit tabs as bottom navigation */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #0D0D14;
    border-top: 1px solid #1E1E2E;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    padding: 0;
    justify-content: space-around;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #555570 !important;
    font-size: 10px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 4px 8px !important;
    flex-direction: column !important;
    gap: 2px !important;
    min-width: 0 !important;
    flex: 1 !important;
    justify-content: center !important;
    align-items: center !important;
    line-height: 1.3 !important;
}
.stTabs [aria-selected="true"] {
    color: #7C5CFC !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] {
    padding: 0 !important;
    padding-bottom: 80px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2A2A3E; border-radius: 2px; }

/* Streamlit button overrides */
.stButton > button {
    background: linear-gradient(135deg, #7C5CFC, #5C8EFC) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
}
.stTextInput > div > div > input {
    background: #13131A !important;
    border: 1px solid #2A2A3E !important;
    border-radius: 12px !important;
    color: #E0E0F0 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 12px 16px !important;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-12px); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(124,92,252,0.3); }
    50% { box-shadow: 0 0 40px rgba(124,92,252,0.6); }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes slide-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ---- SESSION STATE ----
if "tcbs_unlocked" not in st.session_state:
    st.session_state.tcbs_unlocked = False


# ====================================================
# SCREEN 1: HOME
# ====================================================
def screen_home():
    st.markdown("""
<div style="padding: 0; min-height: 100vh; background: #0A0A0F;">

  <div style="display:flex; justify-content:space-between; align-items:center;
              padding: 20px 24px 8px; position:sticky; top:0; z-index:10;
              background: linear-gradient(180deg, #0A0A0F 80%, transparent);">
    <div>
      <div style="font-size:11px; color:#555570; letter-spacing:1px; text-transform:uppercase;">Chao Buoi Sang</div>
      <div style="font-size:20px; font-weight:700; color:#E0E0F0;">Chao Minh An 👋</div>
    </div>
    <div style="width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
                display:flex; align-items:center; justify-content:center; font-size:18px; font-weight:700; color:white;">M</div>
  </div>

  <div style="text-align:center; padding: 20px 0 8px;">
    <div style="animation: float 4s ease-in-out infinite; display:inline-block;">
      <div style="font-size:80px; filter: drop-shadow(0 8px 24px rgba(124,92,252,0.4));">🐑</div>
    </div>
    <div style="margin-top:16px; padding: 0 40px;">
      <div style="font-size:16px; font-weight:600; color:#E0E0F0; line-height:1.5;">
        "Anh dang giu ho<br>tuong lai cua em"
      </div>
      <div style="font-size:13px; color:#555570; margin-top:6px;">Cuu Can Cu  •  Nguoi ban tai chinh</div>
    </div>
  </div>

  <div style="display:flex; gap:12px; padding: 12px 24px; overflow-x:auto; scrollbar-width:none;">
    <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:16px;
                padding:16px 20px; min-width:130px; flex-shrink:0;">
      <div style="font-size:11px; color:#555570; margin-bottom:4px;">Da tiet kiem</div>
      <div style="font-size:22px; font-weight:700; color:#7C5CFC;">4.2M</div>
      <div style="font-size:11px; color:#2ECC71; margin-top:2px;">12% thang nay</div>
    </div>
    <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:16px;
                padding:16px 20px; min-width:130px; flex-shrink:0;">
      <div style="font-size:11px; color:#555570; margin-bottom:4px;">Streak hien tai</div>
      <div style="font-size:22px; font-weight:700; color:#F5A623;">🔥 14</div>
      <div style="font-size:11px; color:#555570; margin-top:2px;">ngay lien tiep</div>
    </div>
    <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:16px;
                padding:16px 20px; min-width:130px; flex-shrink:0;">
      <div style="font-size:11px; color:#555570; margin-bottom:4px;">Muc tieu gan nhat</div>
      <div style="font-size:22px; font-weight:700; color:#2ECC71;">68%</div>
      <div style="font-size:11px; color:#555570; margin-top:2px;">Concert Blackpink</div>
    </div>
  </div>

  <div style="padding: 8px 24px 0;">
    <div style="font-size:14px; font-weight:600; color:#E0E0F0; margin-bottom:12px;">
      Nhung giac mo cua em ✨
    </div>

    <div style="background:#13131A; border:1px solid #2A1E5E; border-radius:20px;
                padding:18px; margin-bottom:12px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
        <div>
          <div style="font-size:15px; font-weight:600; color:#E0E0F0;">🎵 Concert Blackpink</div>
          <div style="font-size:11px; color:#555570; margin-top:2px;">VIP ticket  •  Thang 8/2025</div>
        </div>
        <div style="background:rgba(124,92,252,0.15); border:1px solid rgba(124,92,252,0.3);
                    border-radius:20px; padding:4px 12px; font-size:13px; font-weight:600; color:#7C5CFC;">
          3.4M / 5M
        </div>
      </div>
      <div style="background:#0A0A0F; border-radius:100px; height:8px; overflow:hidden;">
        <div style="background:linear-gradient(90deg,#7C5CFC,#A78BFA); height:100%;
                    width:68%; border-radius:100px; position:relative; overflow:hidden;">
          <div style="position:absolute; top:0; left:0; right:0; bottom:0;
                      background:linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent);
                      animation:shimmer 2s infinite;"></div>
        </div>
      </div>
      <div style="font-size:11px; color:#A78BFA; margin-top:6px;">🐑 Con 1.6M nua thoi! Co len nao~</div>
    </div>

    <div style="background:#13131A; border:1px solid #1A2E1A; border-radius:20px;
                padding:18px; margin-bottom:12px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
        <div>
          <div style="font-size:15px; font-weight:600; color:#E0E0F0;">✈️ Du lich Da Lat</div>
          <div style="font-size:11px; color:#555570; margin-top:2px;">3 ngay 2 dem  •  Tet 2025</div>
        </div>
        <div style="background:rgba(46,204,113,0.15); border:1px solid rgba(46,204,113,0.3);
                    border-radius:20px; padding:4px 12px; font-size:13px; font-weight:600; color:#2ECC71;">
          1.8M / 3M
        </div>
      </div>
      <div style="background:#0A0A0F; border-radius:100px; height:8px; overflow:hidden;">
        <div style="background:linear-gradient(90deg,#2ECC71,#27AE60); height:100%;
                    width:60%; border-radius:100px;"></div>
      </div>
      <div style="font-size:11px; color:#2ECC71; margin-top:6px;">🐑 Tuan nay tiet kiem them 200K nhe!</div>
    </div>

    <div style="background:#13131A; border:1px solid #2E1A1A; border-radius:20px;
                padding:18px; margin-bottom:12px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
        <div>
          <div style="font-size:15px; font-weight:600; color:#E0E0F0;">💻 MacBook Air M3</div>
          <div style="font-size:11px; color:#555570; margin-top:2px;">Hoc lap trinh  •  Cuoi nam 2025</div>
        </div>
        <div style="background:rgba(245,166,35,0.15); border:1px solid rgba(245,166,35,0.3);
                    border-radius:20px; padding:4px 12px; font-size:13px; font-weight:600; color:#F5A623;">
          800K / 28M
        </div>
      </div>
      <div style="background:#0A0A0F; border-radius:100px; height:8px; overflow:hidden;">
        <div style="background:linear-gradient(90deg,#F5A623,#E67E22); height:100%;
                    width:3%; border-radius:100px;"></div>
      </div>
      <div style="font-size:11px; color:#F5A623; margin-top:6px;">🐑 Moi bat dau! Moi ngay mot chut nhe~</div>
    </div>

    <div style="background:#13131A; border:1px solid #1A1A2E; border-radius:20px;
                padding:18px; margin-bottom:12px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
        <div>
          <div style="font-size:15px; font-weight:600; color:#E0E0F0;">🏠 Quy nha tuong lai</div>
          <div style="font-size:11px; color:#555570; margin-top:2px;">iPower Fund  •  5 nam</div>
        </div>
        <div style="background:rgba(92,142,252,0.15); border:1px solid rgba(92,142,252,0.3);
                    border-radius:20px; padding:4px 12px; font-size:13px; font-weight:600; color:#5C8EFC;">
          0 / 500M
        </div>
      </div>
      <div style="background:#0A0A0F; border-radius:100px; height:8px; overflow:hidden;">
        <div style="background:linear-gradient(90deg,#5C8EFC,#7C5CFC); height:100%;
                    width:0.5%; border-radius:100px;"></div>
      </div>
      <div style="font-size:11px; color:#5C8EFC; margin-top:6px;">🐑 Hanh trinh van dam bat dau tu buoc dau tien!</div>
    </div>

  </div>

  <div style="padding: 8px 24px 24px;">
    <div style="border:1.5px dashed #2A2A3E; border-radius:20px; padding:18px;
                text-align:center; cursor:pointer; color:#555570; font-size:14px;">
      + Them giac mo moi
    </div>
  </div>

</div>
""", unsafe_allow_html=True)


# ====================================================
# SCREEN 2: CHAT
# ====================================================
def screen_chat():
    st.markdown("""
<div style="background:#0A0A0F; padding: 16px 24px 12px; display:flex;
            justify-content:space-between; align-items:center; position:sticky; top:0;
            z-index:10; border-bottom:1px solid #1E1E2E;">
  <div style="display:flex; align-items:center; gap:12px;">
    <div style="font-size:32px; animation: float 4s ease-in-out infinite; display:inline-block;">🐑</div>
    <div>
      <div style="font-size:16px; font-weight:600; color:#E0E0F0;">Cuu Can Cu</div>
      <div style="display:flex; align-items:center; gap:5px;">
        <div style="width:7px; height:7px; background:#2ECC71; border-radius:50%;"></div>
        <div style="font-size:11px; color:#555570;">Luon o day cho em</div>
      </div>
    </div>
  </div>
</div>

<div style="padding: 16px 24px; display:flex; flex-direction:column; gap:12px;">

  <div style="display:flex; gap:10px; align-items:flex-end;">
    <div style="font-size:26px; flex-shrink:0;">🐑</div>
    <div style="background:#1E1A2E; border:1px solid #2A1E5E; border-radius:18px 18px 18px 4px;
                padding:14px 16px; max-width:85%; font-size:14px; color:#E0E0F0; line-height:1.6;">
      Chao buoi sang Minh An! Hom nay em cam thay the nao roi? ☀️
    </div>
  </div>

  <div style="display:flex; justify-content:flex-end;">
    <div style="background:linear-gradient(135deg,#7C5CFC,#5C8EFC); border-radius:18px 18px 4px 18px;
                padding:14px 16px; max-width:75%; font-size:14px; color:#fff; line-height:1.6;">
      Minh kha on ban oi, hom qua minh da tiet kiem duoc 150K roi 😊
    </div>
  </div>

  <div style="display:flex; gap:10px; align-items:flex-end;">
    <div style="font-size:26px; flex-shrink:0;">🐑</div>
    <div style="background:#1E1A2E; border:1px solid #2A1E5E; border-radius:18px 18px 18px 4px;
                padding:14px 16px; max-width:85%; font-size:14px; color:#E0E0F0; line-height:1.6;">
      Oa, nghe ma vui ghe a! 🎉 150K hom qua cong voi streak 14 ngay roi do. Em dang tien rat gan toi concert Blackpink — con khoang 1.6M nua thoi!<br><br>
      Nhan tien, minh thay dao nay em hay nhac den "tu do" va "khong phu thuoc tai chinh" — em dang mo den dieu gi vay?
    </div>
  </div>

  <div style="display:flex; justify-content:flex-end;">
    <div style="background:linear-gradient(135deg,#7C5CFC,#5C8EFC); border-radius:18px 18px 4px 18px;
                padding:14px 16px; max-width:75%; font-size:14px; color:#fff; line-height:1.6;">
      That ra minh muon co the tu quyet dinh cuoc song cua minh, khong can xin tien bo me nua
    </div>
  </div>

  <div style="display:flex; gap:10px; align-items:flex-end;">
    <div style="font-size:26px; flex-shrink:0;">🐑</div>
    <div style="background:#1E1A2E; border:1px solid #2A1E5E; border-radius:18px 18px 18px 4px;
                padding:14px 16px; max-width:85%; font-size:14px; color:#E0E0F0; line-height:1.6;">
      Minh hieu cam giac do! 💜 Tu do tai chinh khong chi la co nhieu tien — ma la CO LUA CHON.<br><br>
      Em biet khong, voi thoi quen tiet kiem deu dan nhu bay gio, chi can 6 thang nua em co the xay duoc mot quy khan cap 3 thang chi tieu. Do la buoc dau tien cua tu do do! 🌱
    </div>
  </div>

  <div style="display:flex; justify-content:flex-end;">
    <div style="background:linear-gradient(135deg,#7C5CFC,#5C8EFC); border-radius:18px 18px 4px 18px;
                padding:14px 16px; max-width:75%; font-size:14px; color:#fff; line-height:1.6;">
      Nghe hay do, nhung minh khong biet bat dau tu dau
    </div>
  </div>

  <div style="display:flex; gap:10px; align-items:flex-end;">
    <div style="font-size:26px; flex-shrink:0;">🐑</div>
    <div style="background:#1E1A2E; border:1px solid #2A1E5E; border-radius:18px 18px 18px 4px;
                padding:14px 16px; max-width:85%; font-size:14px; color:#E0E0F0; line-height:1.6;">
      Don gian lam! Cu lam theo 3 buoc:<br><br>
      1️⃣ Tiep tuc tiet kiem moi ngay (em dang lam rat tot!)<br>
      2️⃣ Khi du 2M, minh se giup em mo iPower de tien "de them tien"<br>
      3️⃣ Tu tu giam phu thuoc, tang tu chu<br><br>
      Muon minh dat muc tieu cu the cho em khong? 🐑
    </div>
  </div>

  <!-- Quick replies -->
  <div style="margin-top:4px;">
    <div style="font-size:12px; color:#555570; margin-bottom:8px;">Goi y tra loi:</div>
    <div style="display:flex; flex-wrap:wrap; gap:8px;">
      <div style="background:#13131A; border:1px solid #2A1E5E; border-radius:20px;
                  padding:8px 14px; font-size:12px; color:#A78BFA; cursor:pointer;">
        Co, giup minh dat muc tieu nhe!
      </div>
      <div style="background:#13131A; border:1px solid #2A1E5E; border-radius:20px;
                  padding:8px 14px; font-size:12px; color:#A78BFA; cursor:pointer;">
        iPower la gi vay?
      </div>
      <div style="background:#13131A; border:1px solid #2A1E5E; border-radius:20px;
                  padding:8px 14px; font-size:12px; color:#A78BFA; cursor:pointer;">
        Cho minh xem tien do tiet kiem
      </div>
    </div>
  </div>

</div>

<div style="position:fixed; bottom:72px; left:0; right:0; background:#0A0A0F;
            padding:12px 20px; border-top:1px solid #1E1E2E; z-index:100;">
  <div style="display:flex; gap:10px; align-items:center;">
    <div style="flex:1; background:#13131A; border:1px solid #2A2A3E; border-radius:24px;
                padding:12px 18px; font-size:14px; color:#555570;">
      Noi chuyen voi Cuu...
    </div>
    <div style="width:44px; height:44px; background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
                border-radius:50%; display:flex; align-items:center; justify-content:center;
                font-size:18px; cursor:pointer; flex-shrink:0; color:white; font-weight:bold;">></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ====================================================
# SCREEN 3: JOURNAL
# ====================================================
def screen_journal():
    st.markdown("""
<div style="padding: 20px 24px 0;">
  <div style="font-size:20px; font-weight:700; color:#E0E0F0; margin-bottom:4px;">📖 Nhat ky tai chinh</div>
  <div style="font-size:13px; color:#555570; margin-bottom:20px;">Hanh trinh cua Minh An</div>

  <div style="display:flex; gap:0; margin-bottom:0;">
    <div style="display:flex; flex-direction:column; align-items:center; width:48px; flex-shrink:0;">
      <div style="width:36px; height:36px; background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
                  border-radius:50%; display:flex; align-items:center; justify-content:center;
                  font-size:12px; font-weight:700; color:#fff;">T4</div>
      <div style="width:2px; flex:1; background:#1E1E2E; margin-top:4px; min-height:20px;"></div>
    </div>
    <div style="flex:1; padding-bottom:20px; margin-left:12px;">
      <div style="font-size:11px; color:#555570; margin-bottom:8px;">18/06/2025  •  21:30</div>
      <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:16px; padding:16px;">
        <div style="font-size:14px; color:#E0E0F0; line-height:1.6; margin-bottom:12px;">
          Hom nay minh an com nha, tiet kiem duoc 80K tien an ngoai. Cam thay tu hao lam!
          Tu nhien nghi den concert Blackpink, khong biet minh co du tien khong...
        </div>
        <div style="background:#1E1A2E; border-radius:12px; padding:12px; display:flex; gap:8px;">
          <div style="font-size:18px;">🐑</div>
          <div style="font-size:13px; color:#A78BFA; line-height:1.5;">
            Em ngoan lam! 80K hom nay + streak 14 ngay = em dang lam rat tot roi.
            Concert chi con 1.6M nua thoi, cu giu da nay la duoc! 💜
          </div>
        </div>
        <div style="display:flex; gap:8px; margin-top:10px;">
          <div style="background:rgba(124,92,252,0.15); border-radius:20px; padding:4px 10px;
                      font-size:11px; color:#A78BFA;">😊 Tu hao</div>
          <div style="background:rgba(124,92,252,0.15); border-radius:20px; padding:4px 10px;
                      font-size:11px; color:#A78BFA;">💰 +80K</div>
        </div>
      </div>
    </div>
  </div>

  <div style="display:flex; gap:0; margin-bottom:0;">
    <div style="display:flex; flex-direction:column; align-items:center; width:48px; flex-shrink:0;">
      <div style="width:36px; height:36px; background:#1E1E2E; border:2px solid #2A2A3E;
                  border-radius:50%; display:flex; align-items:center; justify-content:center;
                  font-size:12px; font-weight:700; color:#555570;">T3</div>
      <div style="width:2px; flex:1; background:#1E1E2E; margin-top:4px; min-height:20px;"></div>
    </div>
    <div style="flex:1; padding-bottom:20px; margin-left:12px;">
      <div style="font-size:11px; color:#555570; margin-bottom:8px;">17/06/2025  •  19:15</div>
      <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:16px; padding:16px;">
        <div style="font-size:14px; color:#E0E0F0; line-height:1.6; margin-bottom:12px;">
          Minh vua xem TED talk ve financial freedom. Wow, hoa ra voi 10 trieu moi thang,
          neu dau tu dung cach thi 30 tuoi co the nghi huu som duoc. Minh muon lam duoc vay!
        </div>
        <div style="background:#1E1A2E; border-radius:12px; padding:12px; display:flex; gap:8px;">
          <div style="font-size:18px;">🐑</div>
          <div style="font-size:13px; color:#A78BFA; line-height:1.5;">
            Minh cung tin em lam duoc! "Tu do 30 tuoi" — minh se nho dieu nay de nhac em
            moi khi em muon bo cuoc nhe. Day la dong luc that su cua em do! 🌟
          </div>
        </div>
        <div style="display:flex; gap:8px; margin-top:10px;">
          <div style="background:rgba(46,204,113,0.15); border-radius:20px; padding:4px 10px;
                      font-size:11px; color:#2ECC71;">🌟 Cam hung</div>
          <div style="background:rgba(46,204,113,0.15); border-radius:20px; padding:4px 10px;
                      font-size:11px; color:#2ECC71;">💡 Financial freedom</div>
        </div>
      </div>
    </div>
  </div>

  <div style="display:flex; gap:0; margin-bottom:0;">
    <div style="display:flex; flex-direction:column; align-items:center; width:48px; flex-shrink:0;">
      <div style="width:36px; height:36px; background:#1E1E2E; border:2px solid #2A2A3E;
                  border-radius:50%; display:flex; align-items:center; justify-content:center;
                  font-size:12px; font-weight:700; color:#555570;">T2</div>
      <div style="width:2px; background:#1E1E2E; margin-top:4px; height:20px;"></div>
    </div>
    <div style="flex:1; padding-bottom:20px; margin-left:12px;">
      <div style="font-size:11px; color:#555570; margin-bottom:8px;">16/06/2025  •  22:00</div>
      <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:16px; padding:16px;">
        <div style="font-size:14px; color:#E0E0F0; line-height:1.6; margin-bottom:12px;">
          Hom nay minh bi cam do mua doi giay moi 1.2M nhung minh da khong mua.
          Cam giac vua tiec vua tu hao. Giay dep that nhung concert quan trong hon!
        </div>
        <div style="background:#1E1A2E; border-radius:12px; padding:12px; display:flex; gap:8px;">
          <div style="font-size:18px;">🐑</div>
          <div style="font-size:13px; color:#A78BFA; line-height:1.5;">
            Em vua lam mot dieu rat dung cam do! Chon tuong lai thay vi cam xuc nhat thoi —
            day moi la that su truong thanh ve tai chinh. Minh tu hao ve em! 🎉
          </div>
        </div>
        <div style="display:flex; gap:8px; margin-top:10px;">
          <div style="background:rgba(245,166,35,0.15); border-radius:20px; padding:4px 10px;
                      font-size:11px; color:#F5A623;">💪 Ky luat</div>
          <div style="background:rgba(245,166,35,0.15); border-radius:20px; padding:4px 10px;
                      font-size:11px; color:#F5A623;">Tranh mua sam</div>
        </div>
      </div>
    </div>
  </div>

  <div style="padding: 0 0 24px;">
    <div style="background:linear-gradient(135deg,rgba(124,92,252,0.15),rgba(92,142,252,0.15));
                border:1.5px solid rgba(124,92,252,0.3); border-radius:20px; padding:18px;
                text-align:center; cursor:pointer;">
      <div style="font-size:24px; margin-bottom:8px;">✍️</div>
      <div style="font-size:14px; font-weight:600; color:#A78BFA;">Viet nhat ky hom nay</div>
      <div style="font-size:12px; color:#555570; margin-top:4px;">Chia se ngay hom nay cua em voi Cuu</div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)


# ====================================================
# SCREEN 4: COMMUNITY
# ====================================================
def screen_community():
    st.markdown("""
<div style="padding: 20px 24px 0;">
  <div style="font-size:20px; font-weight:700; color:#E0E0F0; margin-bottom:4px;">🌟 Cong dong</div>
  <div style="font-size:13px; color:#555570; margin-bottom:20px;">Cung nhau tien len!</div>

  <div style="display:flex; flex-direction:column; gap:14px;">

    <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:20px; padding:18px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="width:36px; height:36px; border-radius:50%;
                    background:linear-gradient(135deg,#FF6B6B,#FF8E53);
                    display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; color:white;">T</div>
        <div>
          <div style="font-size:13px; font-weight:600; color:#E0E0F0;">Thu Ha</div>
          <div style="font-size:11px; color:#555570;">2 gio truoc</div>
        </div>
        <div style="margin-left:auto; background:rgba(46,204,113,0.15); border-radius:20px;
                    padding:4px 10px; font-size:11px; color:#2ECC71;">🎯 Dat muc tieu</div>
      </div>
      <div style="font-size:14px; color:#E0E0F0; line-height:1.5; margin-bottom:10px;">
        Thang nay minh da tiet kiem duoc 3.5M! 🎉 Du tien mua ve xem phim hang thang roi.
        Cam on Cuu Can Cu da nhac minh moi ngay!
      </div>
      <div style="display:flex; gap:12px; font-size:13px; color:#555570;">
        <span>❤️ 24</span>
        <span>💬 8</span>
        <span>🔄 Chia se</span>
      </div>
    </div>

    <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:20px; padding:18px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="width:36px; height:36px; border-radius:50%;
                    background:linear-gradient(135deg,#4FACFE,#00F2FE);
                    display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; color:white;">N</div>
        <div>
          <div style="font-size:13px; font-weight:600; color:#E0E0F0;">Nam Phong</div>
          <div style="font-size:11px; color:#555570;">5 gio truoc</div>
        </div>
        <div style="margin-left:auto; background:rgba(124,92,252,0.15); border-radius:20px;
                    padding:4px 10px; font-size:11px; color:#A78BFA;">🔥 Streak 30</div>
      </div>
      <div style="font-size:14px; color:#E0E0F0; line-height:1.5; margin-bottom:10px;">
        30 ngay streak! Khong bo sot ngay nao 💪 Cuu Can Cu da thay doi thoi quen tai chinh
        cua minh hoan toan. Ai dang o streak ngay may roi?
      </div>
      <div style="display:flex; gap:12px; font-size:13px; color:#555570;">
        <span>❤️ 47</span>
        <span>💬 15</span>
        <span>🔄 Chia se</span>
      </div>
    </div>

    <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:20px; padding:18px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="width:36px; height:36px; border-radius:50%;
                    background:linear-gradient(135deg,#A18CD1,#FBC2EB);
                    display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; color:white;">L</div>
        <div>
          <div style="font-size:13px; font-weight:600; color:#E0E0F0;">Lan Anh</div>
          <div style="font-size:11px; color:#555570;">8 gio truoc</div>
        </div>
      </div>
      <div style="font-size:14px; color:#E0E0F0; line-height:1.5; margin-bottom:10px;">
        Moi nguoi oi! Cuu vua goi y minh mo iPower, minh dang phan van co nen thu khong?
        Ai da dung cho minh xin review voi a 🙏
      </div>
      <div style="background:#1E1A2E; border-radius:12px; padding:12px; margin-bottom:10px;
                  display:flex; gap:8px;">
        <div style="font-size:18px;">🐑</div>
        <div style="font-size:12px; color:#A78BFA; line-height:1.5;">
          Minh da giai thich cho Lan Anh roi nhe! iPower phu hop khi em co it nhat 1M tien nhan roi.
          Lai suat hien tai ~8%/nam, cao hon gui ngan hang nhieu!
        </div>
      </div>
      <div style="display:flex; gap:12px; font-size:13px; color:#555570;">
        <span>❤️ 12</span>
        <span>💬 23</span>
        <span>🔄 Chia se</span>
      </div>
    </div>

  </div>

  <div style="margin: 16px 0 24px;">
    <div style="background:linear-gradient(135deg,#7C5CFC,#5C8EFC); border-radius:20px;
                padding:20px; position:relative; overflow:hidden;">
      <div style="position:absolute; right:-20px; top:-20px; font-size:80px; opacity:0.1;">🐑</div>
      <div style="font-size:15px; font-weight:700; color:#fff; margin-bottom:6px;">
        Moi ban be, nhan 50K
      </div>
      <div style="font-size:13px; color:rgba(255,255,255,0.8); margin-bottom:14px;">
        Moi nguoi ban mo tai khoan = em nhan 50K vao quy tiet kiem!
      </div>
      <div style="background:rgba(255,255,255,0.2); border-radius:12px; padding:10px 16px;
                  font-size:13px; color:#fff; font-weight:600;">
        🔗 Chia se link gioi thieu
      </div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)


# ====================================================
# TCBS WORLD - SCREEN 5: MEMORY
# ====================================================
def screen_memory():
    st.markdown("""
<div style="padding: 20px 24px 0;">

  <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(124,92,252,0.15);
              border:1px solid rgba(124,92,252,0.3); border-radius:8px; padding:4px 10px;
              font-size:11px; color:#A78BFA; font-weight:600; margin-bottom:10px;">
    🔒 TCBS INTERNAL
  </div>
  <div style="font-size:20px; font-weight:700; color:#E0E0F0; margin-bottom:4px;">🧠 Memory Engine</div>
  <div style="font-size:13px; color:#555570; margin-bottom:20px;">
    Nhung gi Cuu Can Cu dang nho ve Minh An
  </div>

  <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">

    <div style="background:#1A1A10; border:1px solid #2E2A10; border-radius:16px; padding:16px;
                grid-column: span 2;">
      <div style="font-size:12px; color:#F5A623; font-weight:600; margin-bottom:10px; letter-spacing:0.5px;">
        DREAMS + ASPIRATIONS
      </div>
      <div style="display:flex; flex-direction:column; gap:8px;">
        <div style="display:flex; gap:8px; align-items:flex-start;">
          <div style="font-size:16px; margin-top:1px;">🎵</div>
          <div>
            <div style="font-size:13px; color:#E0E0F0;">Concert Blackpink VIP</div>
            <div style="font-size:11px; color:#555570;">Nhac den 8 lan  •  Cam xuc: Rat hung khoi</div>
          </div>
        </div>
        <div style="display:flex; gap:8px; align-items:flex-start;">
          <div style="font-size:16px; margin-top:1px;">🏠</div>
          <div>
            <div style="font-size:13px; color:#E0E0F0;">Tu do tai chinh truoc 30 tuoi</div>
            <div style="font-size:11px; color:#555570;">Nhac den 5 lan  •  Core motivation</div>
          </div>
        </div>
        <div style="display:flex; gap:8px; align-items:flex-start;">
          <div style="font-size:16px; margin-top:1px;">✈️</div>
          <div>
            <div style="font-size:13px; color:#E0E0F0;">Du lich Da Lat + Nhat Ban</div>
            <div style="font-size:11px; color:#555570;">Nhac den 3 lan  •  Ket noi voi "tu do"</div>
          </div>
        </div>
      </div>
    </div>

    <div style="background:#0F1A1F; border:1px solid #1A2E3A; border-radius:16px; padding:16px;">
      <div style="font-size:12px; color:#5C8EFC; font-weight:600; margin-bottom:10px;">HAPPINESS TRIGGERS</div>
      <div style="display:flex; flex-direction:column; gap:6px;">
        <div style="font-size:13px; color:#E0E0F0;">🍱 Com nha</div>
        <div style="font-size:13px; color:#E0E0F0;">💪 Dat muc tieu nho</div>
        <div style="font-size:13px; color:#E0E0F0;">🎵 Nghe nhac K-pop</div>
        <div style="font-size:13px; color:#E0E0F0;">📚 Hoc dieu moi</div>
      </div>
    </div>

    <div style="background:#1A0F1A; border:1px solid #2E1A3A; border-radius:16px; padding:16px;">
      <div style="font-size:12px; color:#A78BFA; font-weight:600; margin-bottom:10px;">VALUES</div>
      <div style="display:flex; flex-direction:column; gap:6px;">
        <div style="font-size:13px; color:#E0E0F0;">Tu do, doc lap</div>
        <div style="font-size:13px; color:#E0E0F0;">Ky luat ban than</div>
        <div style="font-size:13px; color:#E0E0F0;">Gia dinh</div>
        <div style="font-size:13px; color:#E0E0F0;">Phat trien ban than</div>
      </div>
    </div>

    <div style="background:#0F1A0F; border:1px solid #1A2E1A; border-radius:16px; padding:16px;
                grid-column: span 2;">
      <div style="font-size:12px; color:#2ECC71; font-weight:600; margin-bottom:10px;">BEHAVIOR PATTERNS</div>
      <div style="display:flex; flex-wrap:wrap; gap:8px;">
        <div style="background:rgba(46,204,113,0.15); border-radius:20px; padding:5px 12px;
                    font-size:12px; color:#2ECC71;">Tiet kiem buoi toi 21-22h</div>
        <div style="background:rgba(46,204,113,0.15); border-radius:20px; padding:5px 12px;
                    font-size:12px; color:#2ECC71;">Hay nhac ban be cung tiet kiem</div>
        <div style="background:rgba(46,204,113,0.15); border-radius:20px; padding:5px 12px;
                    font-size:12px; color:#2ECC71;">Can duoc khuyen khich</div>
        <div style="background:rgba(46,204,113,0.15); border-radius:20px; padding:5px 12px;
                    font-size:12px; color:#2ECC71;">Phan hoi nhanh buoi sang</div>
      </div>
    </div>

    <div style="background:#1A100F; border:1px solid #3A1A1A; border-radius:16px; padding:16px;
                grid-column: span 2;">
      <div style="font-size:12px; color:#FF6B6B; font-weight:600; margin-bottom:10px;">PAIN POINTS</div>
      <div style="display:flex; flex-direction:column; gap:6px;">
        <div style="font-size:13px; color:#E0E0F0;">Lo so khong du tien cuoi thang</div>
        <div style="font-size:13px; color:#E0E0F0;">Tuc gian khi bi cam do chi tieu</div>
        <div style="font-size:13px; color:#E0E0F0;">Bat an ve tuong lai tai chinh</div>
      </div>
    </div>

  </div>

  <div style="background:linear-gradient(135deg,rgba(124,92,252,0.1),rgba(92,142,252,0.1));
              border:1px solid rgba(124,92,252,0.2); border-radius:16px; padding:16px; margin-bottom:24px;">
    <div style="font-size:12px; color:#555570; margin-bottom:4px;">TCBS Memory Score</div>
    <div style="font-size:28px; font-weight:700; color:#7C5CFC;">87 / 100</div>
    <div style="font-size:12px; color:#A78BFA; margin-top:4px;">
      Du lieu tu 23 cuoc hoi thoai  •  14 ngay streak  •  3 journal entries
    </div>
  </div>

</div>
""", unsafe_allow_html=True)


# ====================================================
# TCBS WORLD - SCREEN 6: INTEREST MAP
# ====================================================
def screen_interest_map():
    st.markdown("""
<div style="padding: 20px 24px 0;">
  <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(124,92,252,0.15);
              border:1px solid rgba(124,92,252,0.3); border-radius:8px; padding:4px 10px;
              font-size:11px; color:#A78BFA; font-weight:600; margin-bottom:10px;">
    🔒 TCBS INTERNAL
  </div>
  <div style="font-size:20px; font-weight:700; color:#E0E0F0; margin-bottom:4px;">🕸 Interest Map</div>
  <div style="font-size:13px; color:#555570; margin-bottom:16px;">
    Mang luoi mong muon — phong cach Obsidian
  </div>
</div>
""", unsafe_allow_html=True)

    components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0A0A0F; font-family:'Inter',sans-serif; overflow:hidden; }
  svg { width:100%; height:460px; display:block; }

  @keyframes pulse-node {
    0%,100% { opacity:1; }
    50% { opacity:0.5; }
  }
  @keyframes flow {
    from { stroke-dashoffset: 30; }
    to { stroke-dashoffset: 0; }
  }
  .core-ring { animation: pulse-node 3s ease-in-out infinite; }
  .edge { stroke-dasharray: 6,4; animation: flow 3s linear infinite; }
</style>
</head>
<body>
<svg viewBox="0 0 380 460">
  <defs>
    <radialGradient id="bg-glow" cx="50%" cy="48%" r="50%">
      <stop offset="0%" style="stop-color:#7C5CFC;stop-opacity:0.12"/>
      <stop offset="100%" style="stop-color:#7C5CFC;stop-opacity:0"/>
    </radialGradient>
    <filter id="glow-filter" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="380" height="460" fill="#0A0A0F"/>
  <ellipse cx="190" cy="220" rx="160" ry="150" fill="url(#bg-glow)"/>

  <!-- Edges -->
  <line x1="190" y1="220" x2="75" y2="120" stroke="#7C5CFC" stroke-width="1.5" opacity="0.5" class="edge"/>
  <line x1="190" y1="220" x2="305" y2="95" stroke="#A78BFA" stroke-width="1.5" opacity="0.45" class="edge"/>
  <line x1="190" y1="220" x2="340" y2="210" stroke="#5C8EFC" stroke-width="1.5" opacity="0.4" class="edge"/>
  <line x1="190" y1="220" x2="285" y2="355" stroke="#2ECC71" stroke-width="1.5" opacity="0.4" class="edge"/>
  <line x1="190" y1="220" x2="65" y2="325" stroke="#F5A623" stroke-width="1.5" opacity="0.4" class="edge"/>
  <line x1="190" y1="220" x2="120" y2="385" stroke="#FF9FF3" stroke-width="1.2" opacity="0.3" class="edge"/>

  <line x1="75" y1="120" x2="305" y2="95" stroke="#333" stroke-width="1" opacity="0.25" class="edge"/>
  <line x1="305" y1="95" x2="340" y2="210" stroke="#333" stroke-width="1" opacity="0.2" class="edge"/>
  <line x1="285" y1="355" x2="120" y2="385" stroke="#333" stroke-width="1" opacity="0.2" class="edge"/>
  <line x1="65" y1="325" x2="120" y2="385" stroke="#333" stroke-width="1" opacity="0.2" class="edge"/>

  <!-- Travel node -->
  <circle cx="75" cy="120" r="32" fill="#050810" stroke="#5C8EFC" stroke-width="1.5" opacity="0.9" filter="url(#glow-filter)"/>
  <text x="75" y="110" text-anchor="middle" font-size="18" fill="#fff">✈️</text>
  <text x="75" y="126" text-anchor="middle" font-size="10" fill="#5C8EFC" font-family="Inter" font-weight="600">Du lich</text>
  <text x="75" y="138" text-anchor="middle" font-size="9" fill="#555570" font-family="Inter">Da Lat, Nhat</text>

  <!-- Concert node -->
  <circle cx="305" cy="95" r="36" fill="#050810" stroke="#A78BFA" stroke-width="2" opacity="0.95" filter="url(#glow-filter)"/>
  <text x="305" y="84" text-anchor="middle" font-size="20" fill="#fff">🎵</text>
  <text x="305" y="100" text-anchor="middle" font-size="10" fill="#A78BFA" font-family="Inter" font-weight="600">Concert</text>
  <text x="305" y="113" text-anchor="middle" font-size="9" fill="#555570" font-family="Inter">Blackpink VIP</text>

  <!-- MacBook node -->
  <circle cx="340" cy="210" r="30" fill="#050810" stroke="#2ECC71" stroke-width="1.5" opacity="0.9"/>
  <text x="340" y="200" text-anchor="middle" font-size="18" fill="#fff">💻</text>
  <text x="340" y="216" text-anchor="middle" font-size="10" fill="#2ECC71" font-family="Inter" font-weight="600">MacBook</text>
  <text x="340" y="228" text-anchor="middle" font-size="9" fill="#555570" font-family="Inter">Hoc lap trinh</text>

  <!-- House node -->
  <circle cx="285" cy="355" r="30" fill="#050810" stroke="#F5A623" stroke-width="1.5" opacity="0.9"/>
  <text x="285" y="345" text-anchor="middle" font-size="18" fill="#fff">🏠</text>
  <text x="285" y="361" text-anchor="middle" font-size="10" fill="#F5A623" font-family="Inter" font-weight="600">Nha rieng</text>
  <text x="285" y="373" text-anchor="middle" font-size="9" fill="#555570" font-family="Inter">Muc tieu 5 nam</text>

  <!-- Freedom node -->
  <circle cx="65" cy="325" r="34" fill="#050810" stroke="#FF6B6B" stroke-width="1.5" opacity="0.9"/>
  <text x="65" y="314" text-anchor="middle" font-size="18" fill="#fff">💸</text>
  <text x="65" y="330" text-anchor="middle" font-size="10" fill="#FF6B6B" font-family="Inter" font-weight="600">Tu do TC</text>
  <text x="65" y="343" text-anchor="middle" font-size="9" fill="#555570" font-family="Inter">Truoc 30 tuoi</text>

  <!-- Family node -->
  <circle cx="120" cy="385" r="26" fill="#050810" stroke="#FF9FF3" stroke-width="1.5" opacity="0.8"/>
  <text x="120" y="375" text-anchor="middle" font-size="16" fill="#fff">👨‍👩‍👧</text>
  <text x="120" y="391" text-anchor="middle" font-size="10" fill="#FF9FF3" font-family="Inter" font-weight="600">Gia dinh</text>

  <!-- Core node: Freedom/Tu Do -->
  <circle cx="190" cy="220" r="60" fill="rgba(124,92,252,0.08)" class="core-ring"/>
  <circle cx="190" cy="220" r="46" fill="#0D0A1A" stroke="#7C5CFC" stroke-width="2.5" filter="url(#glow-filter)"/>
  <text x="190" y="207" text-anchor="middle" font-size="22" fill="#fff">🕊️</text>
  <text x="190" y="226" text-anchor="middle" font-size="14" fill="#A78BFA" font-family="Inter" font-weight="700">Tu Do</text>
  <text x="190" y="241" text-anchor="middle" font-size="10" fill="#555570" font-family="Inter">Core Value</text>

  <text x="10" y="453" fill="#444" font-size="9" font-family="Inter">Phan tich tu 23 cuoc hoi thoai • Cuu Can Cu Memory Engine</text>
</svg>
</body>
</html>
""", height=470)

    st.markdown("""
<div style="padding: 0 24px 24px;">
  <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:16px; padding:16px;">
    <div style="font-size:12px; color:#555570; margin-bottom:10px; letter-spacing:0.5px;">KEY INSIGHTS</div>
    <div style="display:flex; flex-direction:column; gap:8px;">
      <div style="display:flex; gap:8px; align-items:flex-start;">
        <div style="font-size:15px;">🎯</div>
        <div style="font-size:13px; color:#E0E0F0; line-height:1.5;">
          <strong style="color:#A78BFA;">"Tu Do"</strong> la node trung tam — ket noi voi TAT CA cac mong muon khac
        </div>
      </div>
      <div style="display:flex; gap:8px; align-items:flex-start;">
        <div style="font-size:15px;">📊</div>
        <div style="font-size:13px; color:#E0E0F0; line-height:1.5;">
          Concert + Travel cung thuoc nhom <strong style="color:#7C5CFC;">trai nghiem song</strong>
        </div>
      </div>
      <div style="display:flex; gap:8px; align-items:flex-start;">
        <div style="font-size:15px;">💡</div>
        <div style="font-size:13px; color:#E0E0F0; line-height:1.5;">
          Segment: <strong style="color:#2ECC71;">Goal-Driven Saver</strong>  •  Risk appetite: Medium
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ====================================================
# TCBS WORLD - SCREEN 7: FLOW (CEO SLIDE)
# ====================================================
def screen_tcbs_flow():
    st.markdown("""
<div style="padding: 20px 24px 0;">
  <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(124,92,252,0.15);
              border:1px solid rgba(124,92,252,0.3); border-radius:8px; padding:4px 10px;
              font-size:11px; color:#A78BFA; font-weight:600; margin-bottom:10px;">
    🔒 TCBS INTERNAL
  </div>
  <div style="font-size:20px; font-weight:700; color:#E0E0F0; margin-bottom:4px;">🔒 TCBS Intelligence Flow</div>
  <div style="font-size:13px; color:#555570; margin-bottom:20px;">
    Tu cuoc tro chuyen → Hieu khach hang → De xuat san pham
  </div>

  <div style="display:flex; flex-direction:column; align-items:stretch; gap:0;">

    <div style="background:linear-gradient(135deg,#1E1A2E,#13131A); border:1.5px solid #7C5CFC;
                border-radius:20px; padding:18px;">
      <div style="display:flex; gap:12px; align-items:center;">
        <div style="font-size:28px;">💬</div>
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:600; color:#A78BFA;">Chat + Journal</div>
          <div style="font-size:12px; color:#555570; margin-top:2px;">
            Khach hang noi chuyen tu nhien, chia se cam xuc, ghi nhat ky
          </div>
        </div>
        <div style="background:rgba(124,92,252,0.2); border-radius:10px;
                    padding:4px 8px; font-size:10px; color:#7C5CFC; white-space:nowrap;">INPUT</div>
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;">
        <div style="background:#0A0A0F; border-radius:8px; padding:4px 8px; font-size:11px; color:#555570;">
          "Muon tu do tai chinh"
        </div>
        <div style="background:#0A0A0F; border-radius:8px; padding:4px 8px; font-size:11px; color:#555570;">
          "Mua ve concert Blackpink"
        </div>
        <div style="background:#0A0A0F; border-radius:8px; padding:4px 8px; font-size:11px; color:#555570;">
          "Tiet kiem 150K hom nay"
        </div>
      </div>
    </div>

    <div style="display:flex; flex-direction:column; align-items:center; height:32px;">
      <div style="width:2px; flex:1; background:linear-gradient(180deg,#7C5CFC,#5C8EFC);"></div>
      <div style="color:#5C8EFC; font-size:14px; line-height:1;">▼</div>
    </div>

    <div style="background:linear-gradient(135deg,#1A1A2E,#13131A); border:1.5px solid #5C8EFC;
                border-radius:20px; padding:18px;">
      <div style="display:flex; gap:12px; align-items:center;">
        <div style="font-size:28px;">🧠</div>
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:600; color:#5C8EFC;">Memory Engine</div>
          <div style="font-size:12px; color:#555570; margin-top:2px;">
            AI trich xuat: Dreams, Values, Triggers, Pain Points, Behavior
          </div>
        </div>
        <div style="background:rgba(92,142,252,0.2); border-radius:10px;
                    padding:4px 8px; font-size:10px; color:#5C8EFC; white-space:nowrap;">PROCESS</div>
      </div>
    </div>

    <div style="display:flex; flex-direction:column; align-items:center; height:32px;">
      <div style="width:2px; flex:1; background:linear-gradient(180deg,#5C8EFC,#2ECC71);"></div>
      <div style="color:#2ECC71; font-size:14px; line-height:1;">▼</div>
    </div>

    <div style="background:linear-gradient(135deg,#0F1A1F,#13131A); border:1.5px solid #2ECC71;
                border-radius:20px; padding:18px;">
      <div style="display:flex; gap:12px; align-items:center;">
        <div style="font-size:28px;">🕸️</div>
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:600; color:#2ECC71;">Interest Graph</div>
          <div style="font-size:12px; color:#555570; margin-top:2px;">
            Xay dung mang luoi mong muon → Tim core motivation
          </div>
        </div>
        <div style="background:rgba(46,204,113,0.2); border-radius:10px;
                    padding:4px 8px; font-size:10px; color:#2ECC71; white-space:nowrap;">ANALYZE</div>
      </div>
    </div>

    <div style="display:flex; flex-direction:column; align-items:center; height:32px;">
      <div style="width:2px; flex:1; background:linear-gradient(180deg,#2ECC71,#F5A623);"></div>
      <div style="color:#F5A623; font-size:14px; line-height:1;">▼</div>
    </div>

    <div style="background:linear-gradient(135deg,#1A1A10,#13131A); border:1.5px solid #F5A623;
                border-radius:20px; padding:18px;">
      <div style="display:flex; gap:12px; align-items:center;">
        <div style="font-size:28px;">🔍</div>
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:600; color:#F5A623;">Insight Engine</div>
          <div style="font-size:12px; color:#555570; margin-top:2px;">
            Deep Research: Segment + Risk Profile + Product Readiness
          </div>
        </div>
        <div style="background:rgba(245,166,35,0.2); border-radius:10px;
                    padding:4px 8px; font-size:10px; color:#F5A623; white-space:nowrap;">INSIGHT</div>
      </div>
      <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
        <div style="background:rgba(245,166,35,0.15); border-radius:20px; padding:4px 10px;
                    font-size:11px; color:#F5A623;">Goal-Driven Saver</div>
        <div style="background:rgba(245,166,35,0.15); border-radius:20px; padding:4px 10px;
                    font-size:11px; color:#F5A623;">Risk: Medium</div>
        <div style="background:rgba(245,166,35,0.15); border-radius:20px; padding:4px 10px;
                    font-size:11px; color:#F5A623;">iPower Ready: 68%</div>
      </div>
    </div>

    <div style="display:flex; flex-direction:column; align-items:center; height:32px;">
      <div style="width:2px; flex:1; background:linear-gradient(180deg,#F5A623,#FF6B6B);"></div>
      <div style="color:#FF6B6B; font-size:14px; line-height:1;">▼</div>
    </div>

    <div style="background:linear-gradient(135deg,#1A100F,#13131A); border:1.5px solid #FF6B6B;
                border-radius:20px; padding:18px; margin-bottom:24px;">
      <div style="display:flex; gap:12px; align-items:center;">
        <div style="font-size:28px;">💰</div>
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:600; color:#FF6B6B;">Product Recommendation</div>
          <div style="font-size:12px; color:#555570; margin-top:2px;">
            De xuat dung san pham, dung luc, dung nguoi
          </div>
        </div>
        <div style="background:rgba(255,107,107,0.2); border-radius:10px;
                    padding:4px 8px; font-size:10px; color:#FF6B6B; white-space:nowrap;">OUTPUT</div>
      </div>
      <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
        <div style="background:rgba(255,107,107,0.15); border:1px solid rgba(255,107,107,0.3);
                    border-radius:20px; padding:5px 12px; font-size:12px; color:#FF6B6B;">
          iPower Fund
        </div>
        <div style="background:rgba(255,107,107,0.15); border:1px solid rgba(255,107,107,0.3);
                    border-radius:20px; padding:5px 12px; font-size:12px; color:#FF6B6B;">
          TCBS Stocks Starter
        </div>
        <div style="background:rgba(255,107,107,0.15); border:1px solid rgba(255,107,107,0.3);
                    border-radius:20px; padding:5px 12px; font-size:12px; color:#FF6B6B;">
          Goal Savings
        </div>
      </div>
    </div>

  </div>
</div>
""", unsafe_allow_html=True)


# ====================================================
# TCBS WORLD - SCREEN 8: INSIGHT + CEO FINAL SLIDE
# ====================================================
def screen_tcbs_insight():
    st.markdown("""
<div style="padding: 20px 24px 0;">
  <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(124,92,252,0.15);
              border:1px solid rgba(124,92,252,0.3); border-radius:8px; padding:4px 10px;
              font-size:11px; color:#A78BFA; font-weight:600; margin-bottom:10px;">
    🔒 TCBS INTERNAL
  </div>
  <div style="font-size:20px; font-weight:700; color:#E0E0F0; margin-bottom:4px;">🔍 TCBS Insight</div>
  <div style="font-size:13px; color:#555570; margin-bottom:20px;">
    Nhung gi TCBS thuc su hieu ve khach hang
  </div>

  <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:20px; padding:20px; margin-bottom:16px;">
    <div style="display:flex; gap:12px; align-items:center; margin-bottom:16px;">
      <div style="width:48px; height:48px; border-radius:50%;
                  background:linear-gradient(135deg,#7C5CFC,#5C8EFC);
                  display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:700; color:white;">M</div>
      <div>
        <div style="font-size:15px; font-weight:600; color:#E0E0F0;">Nguyen Minh An</div>
        <div style="font-size:12px; color:#555570;">22 tuoi  •  Streak 14 ngay</div>
      </div>
      <div style="margin-left:auto; text-align:right;">
        <div style="font-size:22px; font-weight:700; color:#7C5CFC;">87</div>
        <div style="font-size:10px; color:#555570;">Engagement</div>
      </div>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
      <div style="background:#0A0A0F; border-radius:12px; padding:12px;">
        <div style="font-size:10px; color:#555570; margin-bottom:4px;">SEGMENT</div>
        <div style="font-size:13px; font-weight:600; color:#2ECC71;">Goal-Driven Saver</div>
      </div>
      <div style="background:#0A0A0F; border-radius:12px; padding:12px;">
        <div style="font-size:10px; color:#555570; margin-bottom:4px;">RISK</div>
        <div style="font-size:13px; font-weight:600; color:#F5A623;">Medium</div>
      </div>
      <div style="background:#0A0A0F; border-radius:12px; padding:12px;">
        <div style="font-size:10px; color:#555570; margin-bottom:4px;">LIFE STAGE</div>
        <div style="font-size:13px; font-weight:600; color:#5C8EFC;">Emerging Adult</div>
      </div>
      <div style="background:#0A0A0F; border-radius:12px; padding:12px;">
        <div style="font-size:10px; color:#555570; margin-bottom:4px;">NEXT PRODUCT</div>
        <div style="font-size:13px; font-weight:600; color:#FF6B6B;">iPower Fund</div>
      </div>
    </div>
  </div>

  <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:20px; padding:20px; margin-bottom:16px;">
    <div style="font-size:13px; font-weight:600; color:#E0E0F0; margin-bottom:12px;">
      Core Desires — khong phai san pham, ma la CAM XUC
    </div>
    <div style="display:flex; flex-direction:column; gap:10px;">
      <div style="display:flex; gap:10px; align-items:center;">
        <div style="width:32px; height:32px; background:rgba(124,92,252,0.15); border-radius:8px;
                    display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0;">🕊️</div>
        <div style="flex:1;">
          <div style="font-size:13px; color:#E0E0F0;">TU DO — khong phu thuoc</div>
          <div style="background:#0A0A0F; border-radius:100px; height:4px; margin-top:5px;">
            <div style="background:#7C5CFC; height:100%; width:92%; border-radius:100px;"></div>
          </div>
        </div>
        <div style="font-size:12px; color:#7C5CFC; font-weight:600; flex-shrink:0;">92%</div>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <div style="width:32px; height:32px; background:rgba(46,204,113,0.15); border-radius:8px;
                    display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0;">🎯</div>
        <div style="flex:1;">
          <div style="font-size:13px; color:#E0E0F0;">TIEN BO — co muc tieu ro rang</div>
          <div style="background:#0A0A0F; border-radius:100px; height:4px; margin-top:5px;">
            <div style="background:#2ECC71; height:100%; width:85%; border-radius:100px;"></div>
          </div>
        </div>
        <div style="font-size:12px; color:#2ECC71; font-weight:600; flex-shrink:0;">85%</div>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <div style="width:32px; height:32px; background:rgba(245,166,35,0.15); border-radius:8px;
                    display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0;">💎</div>
        <div style="flex:1;">
          <div style="font-size:13px; color:#E0E0F0;">TRUONG THANH — tu lap</div>
          <div style="background:#0A0A0F; border-radius:100px; height:4px; margin-top:5px;">
            <div style="background:#F5A623; height:100%; width:78%; border-radius:100px;"></div>
          </div>
        </div>
        <div style="font-size:12px; color:#F5A623; font-weight:600; flex-shrink:0;">78%</div>
      </div>
    </div>
  </div>

  <div style="background:#13131A; border:1px solid #1E1E2E; border-radius:20px; padding:20px; margin-bottom:16px;">
    <div style="font-size:13px; font-weight:600; color:#E0E0F0; margin-bottom:14px;">
      Revenue Journey — Dream to Product
    </div>
    <div style="display:flex; gap:4px; align-items:center; margin-bottom:16px; overflow-x:auto; padding-bottom:4px;">
      <div style="text-align:center; flex-shrink:0; min-width:50px;">
        <div style="font-size:22px;">🌱</div>
        <div style="font-size:9px; color:#555570; margin-top:3px;">10K/ngay</div>
      </div>
      <div style="color:#444; font-size:14px;">→</div>
      <div style="text-align:center; flex-shrink:0; min-width:50px;">
        <div style="font-size:22px;">💰</div>
        <div style="font-size:9px; color:#555570; margin-top:3px;">Tiet kiem</div>
      </div>
      <div style="color:#444; font-size:14px;">→</div>
      <div style="text-align:center; flex-shrink:0; min-width:50px;">
        <div style="font-size:22px;">🔥</div>
        <div style="font-size:9px; color:#555570; margin-top:3px;">Thoi quen</div>
      </div>
      <div style="color:#444; font-size:14px;">→</div>
      <div style="text-align:center; flex-shrink:0; min-width:50px;">
        <div style="font-size:22px;">📈</div>
        <div style="font-size:9px; color:#A78BFA; margin-top:3px; font-weight:600;">iPower</div>
      </div>
      <div style="color:#444; font-size:14px;">→</div>
      <div style="text-align:center; flex-shrink:0; min-width:50px;">
        <div style="font-size:22px;">🏆</div>
        <div style="font-size:9px; color:#FF6B6B; margin-top:3px; font-weight:600;">TCBS Fund</div>
      </div>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;">
      <div style="background:#0A0A0F; border-radius:12px; padding:10px; text-align:center;">
        <div style="font-size:14px; font-weight:700; color:#7C5CFC;">0.3M</div>
        <div style="font-size:10px; color:#555570;">AUM hien tai</div>
      </div>
      <div style="background:#0A0A0F; border-radius:12px; padding:10px; text-align:center;">
        <div style="font-size:14px; font-weight:700; color:#2ECC71;">2M</div>
        <div style="font-size:10px; color:#555570;">Target iPower</div>
      </div>
      <div style="background:#0A0A0F; border-radius:12px; padding:10px; text-align:center;">
        <div style="font-size:14px; font-weight:700; color:#F5A623;">~90</div>
        <div style="font-size:10px; color:#555570;">Ngay con lai</div>
      </div>
    </div>
  </div>

  <!-- CEO FINAL SLIDE -->
  <div style="background:linear-gradient(135deg,#080514,#060D14,#060E08); border:1px solid #2A2A3E;
              border-radius:24px; padding:24px; margin-bottom:24px; position:relative; overflow:hidden;">
    <div style="position:absolute; top:-40px; right:-40px; font-size:140px; opacity:0.04; pointer-events:none;">🐑</div>

    <div style="text-align:center; margin-bottom:20px;">
      <div style="font-size:11px; color:#555570; letter-spacing:2px; margin-bottom:8px;">THE BIG PICTURE</div>
      <div style="font-size:18px; font-weight:700; color:#E0E0F0; line-height:1.5;">
        Chung ta khong xay dung chatbot.<br>
        <span style="color:#A78BFA;">Chung ta xay dung</span><br>
        <span style="font-size:20px; font-weight:800; background:linear-gradient(90deg,#7C5CFC,#5C8EFC,#2ECC71);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
          Second Financial Brain.
        </span>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
      <div style="background:rgba(124,92,252,0.1); border:1px solid rgba(124,92,252,0.2);
                  border-radius:16px; padding:14px;">
        <div style="font-size:10px; color:#7C5CFC; font-weight:600; margin-bottom:8px; letter-spacing:0.5px;">
          KHACH HANG THAY
        </div>
        <div style="display:flex; flex-direction:column; gap:5px;">
          <div style="font-size:12px; color:#E0E0F0;">🐑 Nguoi ban tai chinh</div>
          <div style="font-size:12px; color:#E0E0F0;">Ho tro giac mo</div>
          <div style="font-size:12px; color:#E0E0F0;">Tro chuyen tu nhien</div>
          <div style="font-size:12px; color:#E0E0F0;">Nhat ky cam xuc</div>
          <div style="font-size:12px; color:#E0E0F0;">Cong dong ung ho</div>
        </div>
      </div>
      <div style="background:rgba(46,204,113,0.1); border:1px solid rgba(46,204,113,0.2);
                  border-radius:16px; padding:14px;">
        <div style="font-size:10px; color:#2ECC71; font-weight:600; margin-bottom:8px; letter-spacing:0.5px;">
          TCBS NHAN DUOC
        </div>
        <div style="display:flex; flex-direction:column; gap:5px;">
          <div style="font-size:12px; color:#E0E0F0;">Deep customer insight</div>
          <div style="font-size:12px; color:#E0E0F0;">Precise segmentation</div>
          <div style="font-size:12px; color:#E0E0F0;">Behavior prediction</div>
          <div style="font-size:12px; color:#E0E0F0;">Right product, right time</div>
          <div style="font-size:12px; color:#E0E0F0;">Higher conversion</div>
        </div>
      </div>
    </div>

    <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                border-radius:14px; padding:16px; text-align:center;">
      <div style="font-size:11px; color:#555570; margin-bottom:6px; letter-spacing:1px;">THE MOAT</div>
      <div style="font-size:14px; font-weight:600; color:#E0E0F0; line-height:1.5;">
        Moi cuoc tro chuyen = TCBS hieu KH<br>hon doi thu.
      </div>
      <div style="font-size:12px; color:#A78BFA; margin-top:6px;">
        Khong the copy. Khong the mua. Chi co the XAY DUNG.
      </div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)


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
            st.markdown("""
<div style="min-height:75vh; display:flex; flex-direction:column; align-items:center;
            justify-content:center; padding:40px 24px; text-align:center;">
  <div style="font-size:64px; margin-bottom:20px; animation: float 3s ease-in-out infinite; display:inline-block;">🔒</div>
  <div style="font-size:22px; font-weight:700; color:#E0E0F0; margin-bottom:8px;">
    TCBS Intelligence
  </div>
  <div style="font-size:14px; color:#555570; margin-bottom:32px; line-height:1.6; max-width:280px;">
    Khu vuc noi bo TCBS. Nhap PIN de xem toan bo du lieu phan tich khach hang.
  </div>
</div>
""", unsafe_allow_html=True)
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
                st.markdown("""
<div style="text-align:center; margin-top:10px;">
  <div style="font-size:12px; color:#555570;">Demo PIN: <strong style="color:#7C5CFC;">1234</strong></div>
</div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
