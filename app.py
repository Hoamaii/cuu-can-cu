"""
CUU CAN CU - AI Financial Companion for Gen Z
Streamlit Demo for CEO / Board / Innovation Judges
"""

import streamlit as st
import time
import random

# ── PAGE CONFIG ──────────────────────────────────────
st.set_page_config(
    page_title="Cuu Can Cu",
    page_icon="sheep",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL STYLES ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
.stDeployButton { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #0A0A0F; }

/* ── TABS ── */
[data-testid="stTabs"] { background: transparent; }
[data-testid="stTabsTabList"] {
    background: #13131A;
    border-bottom: 1px solid #1E1E2E;
    padding: 0 24px;
    gap: 0;
}
[data-testid="stTabsTab"] {
    color: #555 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 14px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s;
}
[data-testid="stTabsTab"][aria-selected="true"] {
    color: #fff !important;
    border-bottom: 2px solid #7C5CFC !important;
    background: transparent !important;
}
[data-testid="stTabsTabPanel"] {
    background: #0A0A0F;
    padding: 0 !important;
}

/* ── BUTTONS ── */
[data-testid="stButton"] > button {
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    cursor: pointer !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2A2A3A; border-radius: 4px; }

/* ── ANIMATIONS ── */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(124, 92, 252, 0.3); }
    50% { box-shadow: 0 0 40px rgba(124, 92, 252, 0.6); }
}
@keyframes slide-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes coin-fly {
    0% { opacity: 1; transform: translateY(0) scale(1); }
    100% { opacity: 0; transform: translateY(-60px) scale(0.5); }
}
@keyframes progress-fill {
    from { width: 0%; }
    to { width: var(--target-w); }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* ── CARD BASE ── */
.card {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 20px;
    padding: 24px;
    animation: slide-up 0.4s ease;
}
.card-glass {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 24px;
}

/* ── SHEEP MASCOT ── */
.sheep-container {
    text-align: center;
    padding: 40px 20px 20px;
    animation: slide-up 0.5s ease;
}
.sheep-emoji {
    font-size: 100px;
    display: block;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 20px 40px rgba(124, 92, 252, 0.4));
    margin-bottom: 16px;
}
.sheep-greeting {
    font-size: 28px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 6px;
}
.sheep-sub {
    font-size: 16px;
    color: #888;
    font-weight: 400;
}

/* ── WISHLIST CARD ── */
.wishlist-card {
    background: linear-gradient(135deg, #13131A 0%, #1A1A2E 100%);
    border: 1px solid #2A2A4A;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 12px;
    transition: all 0.3s;
}
.wishlist-card:hover {
    border-color: #7C5CFC;
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(124, 92, 252, 0.15);
}
.wish-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.wish-title {
    font-size: 15px;
    font-weight: 600;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 8px;
}
.wish-pct {
    font-size: 13px;
    font-weight: 700;
    color: #7C5CFC;
    background: rgba(124, 92, 252, 0.12);
    padding: 4px 10px;
    border-radius: 20px;
}
.progress-track {
    height: 8px;
    background: #1E1E2E;
    border-radius: 99px;
    overflow: hidden;
    margin-bottom: 8px;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #7C5CFC, #B47AFF);
    transition: width 1s ease;
}
.wish-amount {
    font-size: 12px;
    color: #555;
}

/* ── CHAT BUBBLES ── */
.chat-day-label {
    text-align: center;
    color: #444;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 20px 0 16px;
}
.bubble-wrap { animation: slide-up 0.3s ease; }
.bubble-sheep {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
}
.bubble-sheep-av {
    width: 38px; height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7C5CFC, #B47AFF);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(124, 92, 252, 0.4);
}
.bubble-sheep-body {
    background: #13131A;
    border: 1px solid #2A2A3A;
    border-radius: 4px 18px 18px 18px;
    padding: 13px 16px;
    max-width: 420px;
    font-size: 14px;
    line-height: 1.7;
    color: #E0E0F0;
}
.bubble-user-wrap {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 16px;
}
.bubble-user {
    background: linear-gradient(135deg, #7C5CFC, #5A3FD4);
    border-radius: 18px 4px 18px 18px;
    padding: 13px 16px;
    max-width: 340px;
    font-size: 14px;
    line-height: 1.7;
    color: #fff;
    font-weight: 500;
}

/* ── QUICK ACTION BUTTONS (chat) ── */
.qr-btn {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1A1A2E; border: 1.5px solid #2A2A4A;
    border-radius: 99px; padding: 8px 16px;
    font-size: 13px; color: #C0C0E0; font-weight: 500;
    cursor: pointer; transition: all 0.2s; margin: 4px;
    white-space: nowrap;
}
.qr-btn:hover { background: #7C5CFC; border-color: #7C5CFC; color: #fff; }

/* ── MEMORY GRAPH ── */
.memory-node {
    background: linear-gradient(135deg, #1A1A2E, #13131A);
    border: 2px solid #7C5CFC;
    border-radius: 16px;
    padding: 16px 20px;
    text-align: center;
    animation: pulse-glow 3s ease-in-out infinite;
}
.memory-tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(124, 92, 252, 0.12);
    border: 1px solid rgba(124, 92, 252, 0.3);
    border-radius: 99px;
    padding: 6px 14px;
    font-size: 13px; color: #B47AFF; font-weight: 500;
    margin: 4px;
}

/* ── DEEP RESEARCH ── */
.research-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 16px;
    border-radius: 99px;
    font-size: 13px; font-weight: 600;
    margin: 4px;
}
.chip-green { background: rgba(52, 211, 153, 0.12); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.3); }
.chip-purple { background: rgba(124, 92, 252, 0.12); color: #B47AFF; border: 1px solid rgba(124, 92, 252, 0.3); }
.chip-blue { background: rgba(96, 165, 250, 0.12); color: #60A5FA; border: 1px solid rgba(96, 165, 250, 0.3); }
.chip-orange { background: rgba(251, 146, 60, 0.12); color: #FB923C; border: 1px solid rgba(251, 146, 60, 0.3); }

/* ── COMMUNITY ── */
.community-card {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 20px;
    padding: 22px 24px;
    display: flex; align-items: center; justify-content: space-between;
    transition: all 0.3s; cursor: pointer;
    margin-bottom: 10px;
}
.community-card:hover {
    border-color: #7C5CFC;
    background: linear-gradient(135deg, #13131A, #1A1A2E);
    transform: translateX(4px);
}
.comm-left { display: flex; align-items: center; gap: 16px; }
.comm-icon {
    width: 52px; height: 52px; border-radius: 16px;
    background: linear-gradient(135deg, #7C5CFC22, #B47AFF22);
    border: 1px solid #7C5CFC44;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
}
.comm-name { font-size: 15px; font-weight: 600; color: #fff; margin-bottom: 4px; }
.comm-members { font-size: 12px; color: #555; }
.comm-join {
    background: linear-gradient(135deg, #7C5CFC, #5A3FD4);
    color: white; border: none; border-radius: 12px;
    padding: 10px 20px; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.2s;
    white-space: nowrap;
}

/* ── EXEC DASHBOARD ── */
.metric-card {
    background: linear-gradient(135deg, #13131A, #1A1A2E);
    border: 1px solid #2A2A4A;
    border-radius: 18px; padding: 22px;
    text-align: center;
}
.metric-num { font-size: 36px; font-weight: 800; color: #7C5CFC; margin-bottom: 4px; }
.metric-label { font-size: 12px; color: #666; font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; }

.signal-row {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(124, 92, 252, 0.05);
    border: 1px solid rgba(124, 92, 252, 0.15);
    border-radius: 14px; padding: 14px 18px; margin-bottom: 8px;
    transition: all 0.2s;
}
.signal-row:hover { background: rgba(124, 92, 252, 0.1); }
.signal-label { font-size: 14px; color: #C0C0E0; font-weight: 500; }
.signal-value { font-size: 13px; font-weight: 700; }

/* ── COIN ANIMATION ── */
.coin-anim {
    display: inline-block;
    animation: coin-fly 1s ease forwards;
}

/* ── SECTION HEADER ── */
.sec-header {
    font-size: 13px; font-weight: 700; color: #555;
    text-transform: uppercase; letter-spacing: 1.2px;
    margin-bottom: 14px; padding: 0 4px;
}

/* ── SHIMMER LOADING ── */
.shimmer {
    background: linear-gradient(90deg, #1A1A2E 25%, #2A2A4A 50%, #1A1A2E 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px; height: 14px; margin: 6px 0;
}

/* ── PAGE WRAPPER ── */
.page-wrap {
    max-width: 540px; margin: 0 auto; padding: 0 20px 80px;
}
.page-wide { max-width: 860px; margin: 0 auto; padding: 0 24px 80px; }

/* ── FINAL REVEAL ── */
.reveal-card {
    background: linear-gradient(135deg, #13131A 0%, #1A0A2E 100%);
    border: 1px solid #7C5CFC44;
    border-radius: 24px; padding: 32px;
    text-align: center;
    animation: pulse-glow 4s ease-in-out infinite;
    margin-top: 24px;
}

.home-action-btn {
    width: 100%;
    background: #1A1A2E !important;
    border: 1.5px solid #2A2A4A !important;
    color: #C0C0E0 !important;
    border-radius: 16px !important;
    padding: 16px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 8px;
    transition: all 0.2s !important;
}
.home-action-btn:hover {
    background: #7C5CFC !important;
    border-color: #7C5CFC !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────
if "day" not in st.session_state:
    st.session_state.day = 0
if "concert_fund" not in st.session_state:
    st.session_state.concert_fund = 27000
if "bonus_choice" not in st.session_state:
    st.session_state.bonus_choice = None
if "coin_anim" not in st.session_state:
    st.session_state.coin_anim = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ── HELPERS ──────────────────────────────────────────
def fmt_vnd(n):
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{v:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n // 1000}.000d"
    return f"{n}d"

def progress_bar(pct, color="#7C5CFC"):
    return f"""
<div class="progress-track">
  <div class="progress-fill" style="width:{pct}%;background:linear-gradient(90deg,{color},{color}CC);"></div>
</div>"""

# ── TABS ──────────────────────────────────────────────
tabs = st.tabs([
    "  Home  ",
    "  7 Days Chat  ",
    "  Memory  ",
    "  Deep Research  ",
    "  Community  ",
    "  Executive  ",
])

# ═══════════════════════════════════════════════════════
# TAB 1 — HOME
# ═══════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    # Sheep mascot
    st.markdown("""
<div class="sheep-container">
  <span class="sheep-emoji">🐑</span>
  <div class="sheep-greeting">Chao 👋</div>
  <div class="sheep-sub">Hom nay minh tien gan hon toi wishlist chua?</div>
</div>
""", unsafe_allow_html=True)

    # Quote
    st.markdown("""
<div style="text-align:center;margin:0 0 28px;">
  <span style="font-size:13px;color:#555;font-style:italic;">
    "Bien nhung dong tien le thanh nhung dieu minh muon."
  </span>
</div>
""", unsafe_allow_html=True)

    # Wishlist header
    st.markdown('<div class="sec-header">🎯 Dieu minh dang muon</div>', unsafe_allow_html=True)

    wishes = [
        ("🎤", "Concert Blackpink", 15, 4_500_000, 30_000_000),
        ("✈️", "Du lich Thai Lan", 8, 1_200_000, 15_000_000),
        ("💻", "Macbook Air", 3, 750_000, 25_000_000),
        ("🏠", "Ra o rieng", 1, 500_000, 50_000_000),
    ]

    for icon, name, pct, saved, total in wishes:
        st.markdown(f"""
<div class="wishlist-card">
  <div class="wish-header">
    <div class="wish-title">{icon} {name}</div>
    <div class="wish-pct">{pct}%</div>
  </div>
  {progress_bar(pct)}
  <div class="wish-amount">{fmt_vnd(saved)} / {fmt_vnd(total)}</div>
</div>
""", unsafe_allow_html=True)

    # Sheep note
    st.markdown("""
<div style="
  background: linear-gradient(135deg, rgba(124,92,252,0.08), rgba(180,122,255,0.05));
  border: 1px solid rgba(124,92,252,0.2);
  border-radius: 16px; padding: 18px 20px; margin: 20px 0;
  text-align: center;
">
  <div style="font-size:28px;margin-bottom:8px;">🐑</div>
  <div style="font-size:15px;color:#C0C0E0;font-weight:500;font-style:italic;">
    "Anh dang giu ho tuong lai cua em."
  </div>
</div>
""", unsafe_allow_html=True)

    # Action buttons
    st.markdown('<div class="sec-header">Kham pha</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("💬\nChat voi Cuu", use_container_width=True)
    with c2:
        st.button("📖\nNhat ky", use_container_width=True)
    with c3:
        st.button("👥\nCong dong", use_container_width=True)

    # Stats strip
    st.markdown("""
<div style="
  display:flex; justify-content:space-around;
  background:#13131A; border:1px solid #1E1E2E;
  border-radius:16px; padding:18px 12px; margin-top:24px;
">
  <div style="text-align:center;">
    <div style="font-size:22px;font-weight:800;color:#7C5CFC;">7</div>
    <div style="font-size:11px;color:#555;margin-top:2px;">Ngay streak</div>
  </div>
  <div style="width:1px;background:#1E1E2E;"></div>
  <div style="text-align:center;">
    <div style="font-size:22px;font-weight:800;color:#34D399;">125k</div>
    <div style="font-size:11px;color:#555;margin-top:2px;">Tuan nay tiet kiem</div>
  </div>
  <div style="width:1px;background:#1E1E2E;"></div>
  <div style="text-align:center;">
    <div style="font-size:22px;font-weight:800;color:#FB923C;">4</div>
    <div style="font-size:11px;color:#555;margin-top:2px;">Uoc mo dang theo</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# TAB 2 — 7 DAYS CHAT
# ═══════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    # Day selector
    st.markdown('<div style="padding-top:24px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-header">Hanh trinh 7 ngay</div>', unsafe_allow_html=True)

    day_cols = st.columns(7)
    days_label = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    for i, col in enumerate(day_cols):
        with col:
            selected = st.session_state.day == i
            label = f"**D{i+1}**\n{days_label[i]}"
            if col.button(
                f"D{i+1}",
                key=f"day_btn_{i}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.day = i
                st.session_state.coin_anim = False
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    def sheep_bubble(text):
        st.markdown(f"""
<div class="bubble-wrap">
  <div class="bubble-sheep">
    <div class="bubble-sheep-av">🐑</div>
    <div class="bubble-sheep-body">{text}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    def user_bubble(text):
        st.markdown(f"""
<div class="bubble-wrap">
  <div class="bubble-user-wrap">
    <div class="bubble-user">{text}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    d = st.session_state.day

    # ── DAY 0 ──
    if d == 0:
        st.markdown('<div class="chat-day-label">Ngay 1 — The bat dau</div>', unsafe_allow_html=True)
        user_bubble("Em muon di concert. 🎤")
        time.sleep(0.05)
        sheep_bubble("Anh ung ho. <br><br>Nhung hien tai quy concert cua em dang co dung...")
        time.sleep(0.05)
        st.markdown("""
<div style="text-align:center;margin:16px 0;">
  <div style="font-size:42px;font-weight:900;color:#7C5CFC;">27.000d</div>
  <div style="font-size:13px;color:#555;margin-top:4px;">Quy Concert Blackpink</div>
</div>
""", unsafe_allow_html=True)
        sheep_bubble("🙂<br>Van du mua nuoc suoi.")
        st.markdown("""
<div style="
  background: rgba(124,92,252,0.06); border:1px solid rgba(124,92,252,0.15);
  border-radius:14px; padding:16px 18px; margin-top:16px;
">
  <div style="font-size:12px;color:#7C5CFC;font-weight:600;margin-bottom:8px;">TIN HIEU PHAT HIEN</div>
  <div style="font-size:13px;color:#888;">
    Uoc mo: <strong style="color:#fff;">Concert Blackpink</strong><br>
    Quyen luc hien tai: <strong style="color:#FB923C;">27.000d</strong><br>
    Khoang cach: <strong style="color:#34D399;">29.973.000d</strong>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── DAY 1 ──
    elif d == 1:
        st.markdown('<div class="chat-day-label">Ngay 2 — Tra sua va ban cam</div>', unsafe_allow_html=True)
        user_bubble("Hom nay em mua tra sua 65k. 🧋")
        sheep_bubble("Update nhanh.<br><br>Concert vua lui them nua bai hat. 😂")

        if not st.session_state.coin_anim:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🧋 Khong hoi han", use_container_width=True):
                    st.session_state.coin_anim = True
                    st.session_state.bonus_choice = "no_regret"
                    st.rerun()
            with c2:
                if st.button("🎤 Gui lai 10.000d cho Concert", use_container_width=True):
                    st.session_state.coin_anim = True
                    st.session_state.bonus_choice = "save_concert"
                    st.session_state.concert_fund += 10000
                    st.rerun()
        else:
            if st.session_state.bonus_choice == "no_regret":
                sheep_bubble("Hop le. Tra sua cung la dau tu vao hanh phuc. 🙂<br><br><em style='color:#555;font-size:12px;'>(Nhung concert thi..)</em>")
            else:
                st.markdown("""
<div style="text-align:center;padding:20px 0;animation:slide-up 0.4s ease;">
  <div style="font-size:48px;margin-bottom:8px;">🐑💰</div>
  <div style="font-size:15px;color:#34D399;font-weight:600;">Anh cat giup em nha.</div>
  <div style="font-size:13px;color:#555;margin-top:4px;">10.000d -> Quy Uoc Mo (iPower)</div>
</div>
""", unsafe_allow_html=True)
                sheep_bubble(f"Concert fund: <strong style='color:#7C5CFC;'>{fmt_vnd(st.session_state.concert_fund)}</strong> 🎤<br><br>Moi hanh trinh nghin dam bat dau tu mot buoc chan. Va buoc chan do gia 10k.")

            if st.button("Tiep theo →", use_container_width=True):
                st.session_state.coin_anim = False
                st.session_state.bonus_choice = None

    # ── DAY 2 ──
    elif d == 2:
        st.markdown('<div class="chat-day-label">Ngay 3 — Ngay dep</div>', unsafe_allow_html=True)
        user_bubble("Em vua duoc thuong 1 trieu. 🎉")
        sheep_bubble("Wow.<br><br>Tai khoan cua em vua co ngay dep nhat thang. 🎉")

        if not st.session_state.coin_anim:
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("💸\nTieu luon", use_container_width=True):
                    st.session_state.coin_anim = True
                    st.session_state.bonus_choice = "spend"
                    st.rerun()
            with c2:
                if st.button("⚖️\nChia doi", use_container_width=True):
                    st.session_state.coin_anim = True
                    st.session_state.bonus_choice = "split"
                    st.session_state.concert_fund += 500000
                    st.rerun()
            with c3:
                if st.button("🚀\nGui 50k cho Wishlist", use_container_width=True):
                    st.session_state.coin_anim = True
                    st.session_state.bonus_choice = "save_50"
                    st.session_state.concert_fund += 50000
                    st.rerun()
        else:
            choice = st.session_state.bonus_choice
            if choice == "spend":
                sheep_bubble("Okay. 🙂<br>Anh khong phan xet.<br><br><em style='color:#555;font-size:12px;'>(Nhung concert thi anh cung khong the lam phep la.)</em>")
            elif choice == "split":
                sheep_bubble("Khon ngoan. 500k tieu, 500k vao Quy Uoc Mo. ⚖️<br><br>Quy Concert: <strong style='color:#7C5CFC;'>" + fmt_vnd(st.session_state.concert_fund) + "</strong>")
            else:
                sheep_bubble("50k vao iPower. Tich luy dang chay. 🚀<br><br>Quy Concert: <strong style='color:#7C5CFC;'>" + fmt_vnd(st.session_state.concert_fund) + "</strong><br><br><em style='color:#555;font-size:12px;'>Sieu ngan sach cua em: tieu vi, tiet kiem vi, hanh phuc 100%.</em>")

            if st.button("Tiep theo →", use_container_width=True):
                st.session_state.coin_anim = False

    # ── DAY 3 ──
    elif d == 3:
        st.markdown('<div class="chat-day-label">Ngay 4 — Nhat ky stress</div>', unsafe_allow_html=True)
        st.markdown("""
<div style="
  background: linear-gradient(135deg, rgba(251,146,60,0.08), rgba(251,146,60,0.03));
  border: 1px solid rgba(251,146,60,0.2);
  border-radius: 16px; padding: 16px 18px; margin-bottom: 16px;
">
  <div style="font-size:12px;color:#FB923C;font-weight:600;margin-bottom:6px;">📖 NHAT KY HOM NAY</div>
  <div style="font-size:14px;color:#E0E0F0;line-height:1.7;">"Hom nay hoi stress. Khong biet tai sao."</div>
</div>
""", unsafe_allow_html=True)
        sheep_bubble("Anh de y nhe.<br><br>Moi lan stress em deu mo Shopee. 👀")
        sheep_bubble("Khong sao.<br>Anh cung co nhung quyet dinh kho giai thich. 😂")

        st.markdown("""
<div style="
  background:#13131A; border:1px solid #2A2A3A;
  border-radius:16px; padding:18px; margin-top:16px;
">
  <div style="font-size:12px;color:#555;font-weight:600;margin-bottom:14px;">PATTERN PHAT HIEN</div>
""", unsafe_allow_html=True)
        patterns = [
            ("Stress → mo Shopee", "#FB923C", 85),
            ("Vui → nhac Concert", "#7C5CFC", 70),
            ("Chan → ngheu bao gio di du lich", "#60A5FA", 60),
        ]
        for pat, color, pct in patterns:
            st.markdown(f"""
<div style="margin-bottom:12px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
    <span style="font-size:13px;color:#C0C0E0;">{pat}</span>
    <span style="font-size:12px;color:{color};font-weight:600;">{pct}%</span>
  </div>
  {progress_bar(pct, color)}
</div>
""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── DAY 4 ──
    elif d == 4:
        st.markdown('<div class="chat-day-label">Ngay 5 — Weekly Tea</div>', unsafe_allow_html=True)

        st.markdown("""
<div style="
  background: linear-gradient(135deg, #1A1A2E, #13131A);
  border: 1px solid #2A2A4A; border-radius: 20px; padding: 24px;
  margin-bottom: 16px;
">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
    <div style="font-size:28px;">☕</div>
    <div>
      <div style="font-size:16px;font-weight:700;color:#fff;">Weekly Tea</div>
      <div style="font-size:12px;color:#555;">Tu Cuu den em — tuan nay</div>
    </div>
  </div>
""", unsafe_allow_html=True)

        mentions = [
            ("🎤 Concert", 7, "#7C5CFC"),
            ("✈️ Du lich", 4, "#60A5FA"),
            ("💻 Macbook", 2, "#34D399"),
            ("💸 Shopee", 11, "#FB923C"),
        ]
        for item, count, color in mentions:
            st.markdown(f"""
<div style="
  display:flex; align-items:center; justify-content:space-between;
  padding: 12px 0; border-bottom: 1px solid #1E1E2E;
">
  <span style="font-size:14px;color:#C0C0E0;">{item}</span>
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="font-size:13px;font-weight:700;color:{color};">{count} lan</span>
    <div style="width:60px;height:6px;background:#1E1E2E;border-radius:3px;overflow:hidden;">
      <div style="width:{min(count*8,100)}%;height:100%;background:{color};border-radius:3px;"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        sheep_bubble("Anh nghi hien tai em dang uu tien song vui truoc. 🙂<br><br>Va Shopee dang thang concert 11:7.<br><br>Anh khong phan xet. Anh chi giu so lieu. 😂")

    # ── DAY 5 ──
    elif d == 5:
        st.markdown('<div class="chat-day-label">Ngay 6 — Tien du</div>', unsafe_allow_html=True)
        user_bubble("Em tiet kiem duoc 100k. 💪")
        sheep_bubble("100k chua mua duoc Macbook.<br><br>🙂<br><br>Nhung Macbook cung bat dau tu 100k. ✨")

        # Progress animation
        fund_new = st.session_state.concert_fund + 100000
        concert_pct_new = min(int(fund_new / 30_000_000 * 100), 100)
        st.markdown(f"""
<div style="
  background:#13131A; border:1px solid #2A2A3A;
  border-radius:16px; padding:20px; margin-top:16px;
">
  <div style="font-size:12px;color:#555;font-weight:600;margin-bottom:16px;">TIEN TRINH CAP NHAT</div>
  <div style="margin-bottom:14px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
      <span style="font-size:13px;color:#C0C0E0;">🎤 Concert Blackpink</span>
      <span style="font-size:13px;font-weight:700;color:#7C5CFC;">{concert_pct_new}%</span>
    </div>
    {progress_bar(concert_pct_new)}
    <div style="font-size:12px;color:#555;margin-top:4px;">{fmt_vnd(fund_new)} / 30M</div>
  </div>
  <div style="
    background:rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.2);
    border-radius:12px; padding:12px 14px; text-align:center;
  ">
    <span style="font-size:13px;color:#34D399;font-weight:600;">
      +100.000d vao Quy Uoc Mo (iPower) ✨
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── DAY 6 ──
    elif d == 6:
        st.markdown('<div class="chat-day-label">Ngay 7 — Big Reveal</div>', unsafe_allow_html=True)
        sheep_bubble("Anh vua tong hop tuan nay.<br><br>Yen tam.<br>Anh khong phai HR. 😂")

        st.markdown("""
<div style="
  background: linear-gradient(135deg, #1A1A2E, #0A0A1E);
  border: 1px solid #7C5CFC44; border-radius: 20px; padding: 24px;
  margin: 16px 0;
">
  <div style="font-size:12px;color:#7C5CFC;font-weight:600;margin-bottom:16px;">BAO CAO TUAN — BY CUU</div>
""", unsafe_allow_html=True)

        report = [
            ("🎤 Concert", 8, "#7C5CFC"),
            ("✈️ Du lich", 5, "#60A5FA"),
            ("💻 Macbook", 3, "#34D399"),
            ("💸 Shopee", 11, "#FB923C"),
        ]
        for item, n, color in report:
            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
  padding:10px 0;border-bottom:1px solid #1E1E2E;">
  <span style="font-size:14px;color:#C0C0E0;">{item}</span>
  <span style="font-size:16px;font-weight:800;color:{color};">{n} lan</span>
</div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        sheep_bubble(
            "Anh phat hien.<br><br>"
            "Em khong thuc su thich mua do.<br><br>"
            "Em thich <strong>cam giac duoc thuong cho ban than</strong>. ❤️<br><br>"
            "Shopee la phan thuong nhanh nhat em tim duoc.<br>"
            "Concert la phan thuong em that su muon.<br><br>"
            "Anh se giup em chon cai thu 2."
        )

        st.markdown("""
<div class="reveal-card">
  <div style="font-size:36px;margin-bottom:12px;">🐑✨</div>
  <div style="font-size:20px;font-weight:800;color:#fff;margin-bottom:8px;">
    Tuan nay em tiet kiem duoc
  </div>
  <div style="font-size:44px;font-weight:900;
    background:linear-gradient(135deg,#7C5CFC,#B47AFF);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin-bottom:8px;">
    135.000d
  </div>
  <div style="font-size:13px;color:#555;">
    Da gui vao Quy Uoc Mo (iPower) · Tu dong moi toi
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# TAB 3 — MEMORY
# ═══════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="page-wide">', unsafe_allow_html=True)
    st.markdown('<div style="padding-top:32px;"></div>', unsafe_allow_html=True)

    st.markdown("""
<div style="text-align:center;margin-bottom:32px;animation:slide-up 0.5s ease;">
  <div style="font-size:40px;margin-bottom:12px;">🧠</div>
  <div style="font-size:24px;font-weight:800;color:#fff;margin-bottom:6px;">Cuu Nho Gi Ve Ban?</div>
  <div style="font-size:14px;color:#555;">Moi cuoc tro chuyen xay dung them mot manh ghep</div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
<div class="card" style="margin-bottom:16px;">
  <div style="font-size:12px;color:#7C5CFC;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">Uoc Mo</div>
""", unsafe_allow_html=True)
        dreams = [
            ("🎤", "Concert Blackpink", "Cap thiet — nhac 8 lan/tuan", "#7C5CFC"),
            ("✈️", "Du lich Thai Lan", "Quan trong — nhac 5 lan/tuan", "#60A5FA"),
            ("💻", "Macbook Air", "Vua cao — nhac 3 lan/tuan", "#34D399"),
            ("🏠", "Ra o rieng", "Muc tieu xa — nhac 1 lan/tuan", "#FB923C"),
        ]
        for icon, name, note, color in dreams:
            st.markdown(f"""
<div style="
  display:flex; align-items:center; gap:12px;
  background: rgba(255,255,255,0.02); border: 1px solid #1E1E2E;
  border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;
  border-left: 3px solid {color};
">
  <div style="font-size:22px;">{icon}</div>
  <div>
    <div style="font-size:14px;font-weight:600;color:#fff;">{name}</div>
    <div style="font-size:11px;color:#555;margin-top:2px;">{note}</div>
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
<div class="card">
  <div style="font-size:12px;color:#34D399;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">Gia Tri Song</div>
  <div style="display:flex;flex-wrap:wrap;gap:8px;">
    <span class="memory-tag">❤️ Tu do</span>
    <span class="memory-tag">❤️ Trai nghiem</span>
    <span class="memory-tag">❤️ Doc lap</span>
    <span class="memory-tag">❤️ Song vui</span>
    <span class="memory-tag">❤️ Khong no nan</span>
    <span class="memory-tag">❤️ Thuong ban than</span>
  </div>
</div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="card" style="margin-bottom:16px;">
  <div style="font-size:12px;color:#FB923C;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">Hanh Vi Tai Chinh</div>
""", unsafe_allow_html=True)
        behaviors = [
            ("Tiet kiem khi vui", 72, "#34D399"),
            ("Chi tieu khi stress", 88, "#FB923C"),
            ("Phan thuong ban than", 91, "#7C5CFC"),
            ("Khong thich no nan", 95, "#60A5FA"),
        ]
        for b, pct, color in behaviors:
            st.markdown(f"""
<div style="margin-bottom:14px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
    <span style="font-size:13px;color:#C0C0E0;">{b}</span>
    <span style="font-size:12px;font-weight:700;color:{color};">{pct}%</span>
  </div>
  {progress_bar(pct, color)}
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
<div class="card">
  <div style="font-size:12px;color:#60A5FA;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">Cam Xuc 7 Ngay</div>
""", unsafe_allow_html=True)
        emo_data = [
            ("T2", "😊", 75, "#34D399"),
            ("T3", "😔", 35, "#FB923C"),
            ("T4", "😐", 55, "#888"),
            ("T5", "🎉", 90, "#7C5CFC"),
            ("T6", "😊", 80, "#34D399"),
            ("T7", "😔", 40, "#FB923C"),
            ("CN", "😊", 85, "#34D399"),
        ]
        st.markdown('<div style="display:flex;align-items:flex-end;gap:6px;height:80px;margin-bottom:8px;">', unsafe_allow_html=True)
        for day_n, emo, h, color in emo_data:
            st.markdown(f"""
<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
  <div style="font-size:14px;">{emo}</div>
  <div style="width:100%;height:{h*0.6:.0f}px;background:{color};border-radius:6px 6px 0 0;opacity:0.8;"></div>
  <div style="font-size:10px;color:#555;">{day_n}</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Wealth Genome
    st.markdown("""
<div style="
  background: linear-gradient(135deg, #13131A, #1A0A2E);
  border: 1px solid #7C5CFC33; border-radius: 20px;
  padding: 28px; margin-top: 8px; text-align: center;
">
  <div style="font-size:13px;color:#7C5CFC;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">
    Wealth Genome
  </div>
  <div style="font-size:15px;color:#888;margin-bottom:20px;">
    Cuu xay dung ho so nay tu moi cuoc tro chuyen
  </div>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;">
    <span class="research-chip chip-purple">Experience Seeker</span>
    <span class="research-chip chip-green">High Commitment</span>
    <span class="research-chip chip-blue">Reward Spender</span>
    <span class="research-chip chip-orange">Dream Achiever</span>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# TAB 4 — DEEP RESEARCH
# ═══════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="page-wide">', unsafe_allow_html=True)
    st.markdown('<div style="padding-top:32px;"></div>', unsafe_allow_html=True)

    st.markdown("""
<div style="text-align:center;margin-bottom:36px;">
  <div style="font-size:40px;margin-bottom:12px;">🔍</div>
  <div style="font-size:24px;font-weight:800;color:#fff;margin-bottom:8px;">Cuu Phat Hien Gi?</div>
  <div style="font-size:14px;color:#555;">
    Deep Research tu 7 ngay noi chuyen va hanh vi
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("""
<div class="card" style="margin-bottom:16px;">
  <div style="font-size:12px;color:#7C5CFC;font-weight:700;margin-bottom:20px;text-transform:uppercase;letter-spacing:1px;">
    Phan Tich Muc Tieu
  </div>
""", unsafe_allow_html=True)
        metrics = [
            ("Goal Cluster", "Experience Seeker", "92%", "#7C5CFC"),
            ("Saving Ability", "Medium", "68%", "#60A5FA"),
            ("Commitment Level", "High", "85%", "#34D399"),
            ("Behavior Pattern", "Reward Spending", "88%", "#FB923C"),
        ]
        for label, value, conf, color in metrics:
            st.markdown(f"""
<div style="
  display:flex; align-items:center; justify-content:space-between;
  padding: 14px 0; border-bottom: 1px solid #1E1E2E;
">
  <div>
    <div style="font-size:12px;color:#555;margin-bottom:3px;">{label}</div>
    <div style="font-size:15px;font-weight:700;color:#fff;">{value}</div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:11px;color:#555;margin-bottom:4px;">Do tin cay</div>
    <div style="
      background:rgba(124,92,252,0.1);border:1px solid rgba(124,92,252,0.3);
      border-radius:99px;padding:4px 12px;
      font-size:13px;font-weight:700;color:{color};
    ">{conf}</div>
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="card" style="margin-bottom:16px;">
  <div style="font-size:12px;color:#34D399;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">
    Ket Luan AI
  </div>
  <div style="
    background: rgba(52,211,153,0.05); border: 1px solid rgba(52,211,153,0.2);
    border-radius: 14px; padding: 16px;
  ">
    <div style="font-size:13px;color:#C0C0E0;line-height:1.8;">
      <strong style="color:#34D399;">Khong phai:</strong> Nguoi dung bi thuc day boi dau tu.<br><br>
      <strong style="color:#7C5CFC;">Ma la:</strong> Nguoi dung bi thuc day boi <em>trai nghiem va tu do</em>.<br><br>
      <strong style="color:#FB923C;">Hanh dong phu hop:</strong> Ket noi tiet kiem voi uoc mo cu the — khong phai san pham tai chinh.
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("""
<div class="card">
  <div style="font-size:12px;color:#60A5FA;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">
    Tin Hieu Intent
  </div>
""", unsafe_allow_html=True)
        signals = [
            ("Concert", "Cap thiet", "#7C5CFC", 8),
            ("Du lich", "Cao", "#60A5FA", 5),
            ("Macbook", "Trung binh", "#34D399", 3),
            ("Ra o rieng", "Dai han", "#FB923C", 1),
        ]
        for goal, level, color, strength in signals:
            st.markdown(f"""
<div style="
  display:flex; align-items:center; justify-content:space-between;
  padding: 10px 0; border-bottom: 1px solid #1E1E2E;
">
  <span style="font-size:13px;color:#C0C0E0;">{goal}</span>
  <div style="display:flex;align-items:center;gap:6px;">
    <span style="font-size:12px;color:{color};font-weight:600;">{level}</span>
    <div style="display:flex;gap:3px;">
      {''.join([f"<div style='width:8px;height:8px;background:{color};border-radius:2px;opacity:{0.3 + 0.7*(i<strength)};' />" for i in range(5)])}
    </div>
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # The path
    st.markdown("""
<div style="
  background: linear-gradient(135deg, #13131A, #1A0A2E);
  border: 1px solid #7C5CFC33; border-radius: 20px;
  padding: 28px; margin-top: 8px;
">
  <div style="font-size:13px;color:#7C5CFC;font-weight:700;margin-bottom:20px;text-transform:uppercase;letter-spacing:1px;">
    Con Duong Tu Uoc Mo Den Dau Tu
  </div>
  <div style="display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:8px;">
    <div style="text-align:center;padding:12px 16px;background:#1E1E2E;border-radius:14px;">
      <div style="font-size:20px;margin-bottom:4px;">💭</div>
      <div style="font-size:12px;color:#888;">Uoc Mo</div>
    </div>
    <div style="color:#7C5CFC;font-size:20px;">→</div>
    <div style="text-align:center;padding:12px 16px;background:#1E1E2E;border-radius:14px;">
      <div style="font-size:20px;margin-bottom:4px;">💬</div>
      <div style="font-size:12px;color:#888;">Tam Su</div>
    </div>
    <div style="color:#7C5CFC;font-size:20px;">→</div>
    <div style="text-align:center;padding:12px 16px;background:#1E1E2E;border-radius:14px;">
      <div style="font-size:20px;margin-bottom:4px;">🪙</div>
      <div style="font-size:12px;color:#888;">10.000d</div>
    </div>
    <div style="color:#7C5CFC;font-size:20px;">→</div>
    <div style="text-align:center;padding:12px 16px;background:#1E1E2E;border-radius:14px;">
      <div style="font-size:20px;margin-bottom:4px;">📈</div>
      <div style="font-size:12px;color:#888;">Thoi quen</div>
    </div>
    <div style="color:#7C5CFC;font-size:20px;">→</div>
    <div style="text-align:center;padding:12px 20px;
      background:linear-gradient(135deg,rgba(124,92,252,0.2),rgba(124,92,252,0.05));
      border:1px solid #7C5CFC44;border-radius:14px;">
      <div style="font-size:20px;margin-bottom:4px;">🌱</div>
      <div style="font-size:12px;color:#7C5CFC;font-weight:600;">iPower</div>
    </div>
    <div style="color:#7C5CFC;font-size:20px;">→</div>
    <div style="text-align:center;padding:12px 20px;
      background:linear-gradient(135deg,rgba(52,211,153,0.2),rgba(52,211,153,0.05));
      border:1px solid #34D39944;border-radius:14px;">
      <div style="font-size:20px;margin-bottom:4px;">🚀</div>
      <div style="font-size:12px;color:#34D399;font-weight:600;">Fund Saving</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# TAB 5 — COMMUNITY
# ═══════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('<div style="padding-top:28px;"></div>', unsafe_allow_html=True)

    st.markdown("""
<div style="text-align:center;margin-bottom:28px;">
  <div style="font-size:40px;margin-bottom:12px;">👥</div>
  <div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:6px;">Cong Dong Uoc Mo</div>
  <div style="font-size:14px;color:#555;">Tim nguoi cung chi huong. Cung nhau len xe.</div>
</div>
""", unsafe_allow_html=True)

    communities = [
        ("🎤", "Concert Without Going Broke", 18000, "Dang hot 🔥", "#7C5CFC"),
        ("✈️", "Travel From Your Own Savings", 22000, "Lon nhat", "#60A5FA"),
        ("💻", "Macbook Without Installments", 11000, "Moi that su", "#34D399"),
        ("🏠", "Move Out Club", 30000, "Pho bien nhat", "#FB923C"),
    ]

    for icon, name, members, badge, color in communities:
        st.markdown(f"""
<div class="community-card">
  <div class="comm-left">
    <div class="comm-icon" style="background:rgba(124,92,252,0.08);border-color:{color}44;">
      {icon}
    </div>
    <div>
      <div class="comm-name">{name}</div>
      <div class="comm-members">
        <strong style="color:{color};">{members:,}</strong> thanh vien &nbsp;·&nbsp;
        <span style="background:{color}22;color:{color};padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600;">{badge}</span>
      </div>
    </div>
  </div>
  <button class="comm-join" style="background:linear-gradient(135deg,{color},{color}AA);">Tham gia</button>
</div>""", unsafe_allow_html=True)

    # User segment badge
    st.markdown("""
<div style="
  background: linear-gradient(135deg, rgba(124,92,252,0.1), rgba(124,92,252,0.03));
  border: 1px solid rgba(124,92,252,0.25);
  border-radius: 18px; padding: 22px 24px; margin-top: 16px; text-align: center;
">
  <div style="font-size:12px;color:#7C5CFC;font-weight:700;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">
    Phan Khuc Cua Ban
  </div>
  <div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:8px;">
    ✨ Experience Seeker
  </div>
  <div style="font-size:13px;color:#888;line-height:1.7;">
    Ban song vi trai nghiem. Tiet kiem vi tu do.<br>
    <strong style="color:#B47AFF;">3.420 nguoi</strong> cung phan khuc dang tiet kiem cung nhau.
  </div>
</div>
""", unsafe_allow_html=True)

    # Referral
    st.markdown("""
<div style="
  background: #13131A; border: 1px dashed #2A2A4A;
  border-radius: 18px; padding: 20px 24px; margin-top: 12px; text-align: center;
">
  <div style="font-size:22px;margin-bottom:8px;">🎁</div>
  <div style="font-size:15px;font-weight:600;color:#fff;margin-bottom:6px;">
    Moi ban be — nhan 50.000d vao Quy Uoc Mo
  </div>
  <div style="font-size:13px;color:#555;">
    Moi ban tham gia = cong dong lon hon = thoi quen manh hon
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# TAB 6 — EXECUTIVE VIEW
# ═══════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="page-wide">', unsafe_allow_html=True)
    st.markdown('<div style="padding-top:28px;"></div>', unsafe_allow_html=True)

    st.markdown("""
<div style="
  background: linear-gradient(135deg, rgba(251,146,60,0.08), rgba(251,146,60,0.02));
  border: 1px solid rgba(251,146,60,0.3);
  border-radius: 16px; padding: 14px 20px; margin-bottom: 28px;
  display: flex; align-items: center; gap: 10px;
">
  <span style="font-size:18px;">🏢</span>
  <div>
    <div style="font-size:13px;font-weight:700;color:#FB923C;">EXECUTIVE VIEW — ONLY FOR TCBS</div>
    <div style="font-size:12px;color:#888;">Hidden from customers. Real-time intent signals & segment data.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    exec_metrics = [
        ("81.000", "Gen Z Users", "#7C5CFC"),
        ("4", "Phan Khuc", "#60A5FA"),
        ("92%", "Intent Accuracy", "#34D399"),
        ("3.2x", "Conversion Lift", "#FB923C"),
    ]
    for col, (num, label, color) in zip([col1, col2, col3, col4], exec_metrics):
        with col:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-num" style="color:{color};">{num}</div>
  <div class="metric-label">{label}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
<div class="card" style="margin-bottom:16px;">
  <div style="font-size:12px;color:#60A5FA;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">
    Intent Signals Phat Hien
  </div>
""", unsafe_allow_html=True)
        intent_data = [
            ("Du lich", "Travel 2025", "#60A5FA", "22.000 users"),
            ("Concert", "Blackpink comeback", "#7C5CFC", "18.500 users"),
            ("Ra o rieng", "First apartment", "#FB923C", "30.000 users"),
            ("Macbook", "Upgrade device", "#34D399", "11.200 users"),
        ]
        for intent, note, color, users in intent_data:
            st.markdown(f"""
<div class="signal-row">
  <div>
    <div class="signal-label">{intent}</div>
    <div style="font-size:11px;color:#444;margin-top:2px;">{note}</div>
  </div>
  <span class="signal-value" style="color:{color};">{users}</span>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
<div class="card">
  <div style="font-size:12px;color:#34D399;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">
    San Pham Khuyen Nghi
  </div>
""", unsafe_allow_html=True)
        recs = [
            ("Muc tieu ngan han (Concert, Du lich)", "iPower", "#7C5CFC"),
            ("Muc tieu dai han (Nha, Ra o rieng)", "Fund Saving", "#34D399"),
            ("Tiet kiem dieu tiet", "iPower + DCA", "#60A5FA"),
        ]
        for goal, product, color in recs:
            st.markdown(f"""
<div style="
  display:flex; align-items:center; justify-content:space-between;
  padding: 12px 0; border-bottom: 1px solid #1E1E2E;
">
  <div style="font-size:12px;color:#888;max-width:200px;">{goal}</div>
  <div style="
    background:rgba(124,92,252,0.1); border:1px solid rgba(124,92,252,0.3);
    border-radius:99px; padding:5px 14px;
    font-size:12px;font-weight:700;color:{color};
  ">→ {product}</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
<div class="card" style="margin-bottom:16px;">
  <div style="font-size:12px;color:#FB923C;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">
    Phan Khuc Khach Hang
  </div>
""", unsafe_allow_html=True)
        segments_data = [
            ("Experience Seekers", "Concert, Travel", 38, "#7C5CFC"),
            ("Future Independence", "Move Out, Freedom", 32, "#60A5FA"),
            ("Device Upgraders", "Macbook, Tech", 18, "#34D399"),
            ("Mixed Goals", "Multiple", 12, "#FB923C"),
        ]
        for seg, traits, pct, color in segments_data:
            st.markdown(f"""
<div style="margin-bottom:14px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
    <div>
      <div style="font-size:13px;font-weight:600;color:#fff;">{seg}</div>
      <div style="font-size:11px;color:#555;">{traits}</div>
    </div>
    <span style="font-size:16px;font-weight:800;color:{color};">{pct}%</span>
  </div>
  {progress_bar(pct, color)}
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Wealth data
        st.markdown("""
<div class="card">
  <div style="font-size:12px;color:#7C5CFC;font-weight:700;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px;">
    Du Lieu Thu Thap
  </div>
""", unsafe_allow_html=True)
        data_points = [
            ("Memory Graph", "Uoc mo + Gia tri song", "✅"),
            ("Emotion Timeline", "7 ngay cam xuc", "✅"),
            ("Behavior Pattern", "Trigger chi tieu", "✅"),
            ("Intent Signals", "Muc tieu theo uoc tinh", "✅"),
            ("Wealth Genome", "Ho so tai chinh ca nhan", "✅"),
        ]
        for dp, desc, status in data_points:
            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
  padding:10px 0;border-bottom:1px solid #1E1E2E;">
  <div>
    <div style="font-size:13px;font-weight:600;color:#fff;">{dp}</div>
    <div style="font-size:11px;color:#555;margin-top:1px;">{desc}</div>
  </div>
  <span style="font-size:16px;">{status}</span>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # FINAL CEO SLIDE
    st.markdown("""
<div style="
  background: linear-gradient(135deg, #0A0A1E 0%, #1A0A2E 50%, #0A1A0E 100%);
  border: 1px solid rgba(124,92,252,0.3); border-radius: 24px;
  padding: 40px 36px; margin-top: 24px; text-align: center;
  position: relative; overflow: hidden;
">
  <div style="
    position:absolute;top:-40px;right:-40px;width:200px;height:200px;
    background:radial-gradient(circle,rgba(124,92,252,0.15),transparent 70%);
    border-radius:50%;
  "></div>
  <div style="
    position:absolute;bottom:-40px;left:-40px;width:200px;height:200px;
    background:radial-gradient(circle,rgba(52,211,153,0.1),transparent 70%);
    border-radius:50%;
  "></div>

  <div style="font-size:48px;margin-bottom:16px;">🐑</div>

  <div style="font-size:13px;color:#555;font-weight:600;text-transform:uppercase;letter-spacing:2px;margin-bottom:20px;">
    NHAN THUC NGUOI DUNG
  </div>
  <div style="
    background: rgba(255,255,255,0.04); border-radius: 16px;
    padding: 16px 24px; margin-bottom: 24px; display:inline-block;
  ">
    <span style="font-size:18px;color:#C0C0E0;font-weight:500;font-style:italic;">
      "Toi dang noi chuyen voi mot con Cuu hai huoc."
    </span>
  </div>

  <div style="font-size:13px;color:#555;font-weight:600;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;">
    THUC TE
  </div>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-bottom:28px;">
    <span class="research-chip chip-purple">Memory Graph</span>
    <span class="research-chip chip-blue">Deep Research</span>
    <span class="research-chip chip-green">Wealth Genome</span>
    <span class="research-chip chip-orange">Intent Signals</span>
  </div>

  <div style="
    width: 60px; height: 2px;
    background: linear-gradient(90deg, transparent, #7C5CFC, transparent);
    margin: 0 auto 24px;
  "></div>

  <div style="font-size:15px;color:#888;line-height:2;margin-bottom:24px;">
    Micro-saving tro thanh:
  </div>

  <div style="display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:8px;margin-bottom:28px;">
    <div style="text-align:center;padding:12px 20px;background:#1A1A2E;border-radius:14px;">
      <div style="font-size:22px;font-weight:800;color:#7C5CFC;">10.000d</div>
    </div>
    <div style="color:#7C5CFC;font-size:22px;">→</div>
    <div style="text-align:center;padding:12px 20px;background:#1A1A2E;border-radius:14px;">
      <div style="font-size:16px;font-weight:600;color:#C0C0E0;">Wishlist</div>
    </div>
    <div style="color:#7C5CFC;font-size:22px;">→</div>
    <div style="text-align:center;padding:12px 20px;background:#1A1A2E;border-radius:14px;">
      <div style="font-size:16px;font-weight:600;color:#C0C0E0;">Thoi quen</div>
    </div>
    <div style="color:#7C5CFC;font-size:22px;">→</div>
    <div style="text-align:center;padding:12px 20px;
      background:linear-gradient(135deg,rgba(124,92,252,0.15),rgba(124,92,252,0.05));
      border:1px solid #7C5CFC44;border-radius:14px;">
      <div style="font-size:16px;font-weight:700;color:#B47AFF;">iPower</div>
    </div>
    <div style="color:#7C5CFC;font-size:22px;">→</div>
    <div style="text-align:center;padding:12px 20px;
      background:linear-gradient(135deg,rgba(52,211,153,0.15),rgba(52,211,153,0.05));
      border:1px solid #34D39944;border-radius:14px;">
      <div style="font-size:16px;font-weight:700;color:#34D399;">Fund Saving</div>
    </div>
  </div>

  <div style="
    background: rgba(124,92,252,0.06); border: 1px solid rgba(124,92,252,0.2);
    border-radius: 16px; padding: 20px 28px;
  ">
    <div style="font-size:16px;color:#888;margin-bottom:10px;">
      "Chung toi khong ban san pham dau tu."
    </div>
    <div style="font-size:18px;font-weight:700;
      background: linear-gradient(135deg, #7C5CFC, #B47AFF, #34D399);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      line-height: 1.6;
    ">
      "Chung toi giup Gen Z mua tuong lai ho muon,<br>
      tung hanh dong 10.000d mot lan."
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

