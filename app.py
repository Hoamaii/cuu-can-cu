"""
Cừu Cần Cù — AI Financial Companion · TCBS
streamlit run app.py
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import re
import html as html_lib
import base64
import os
import random

# ── MASCOT IMAGE — base64 embed (hoạt động local + Streamlit Cloud) ──
def _load_mascot() -> str:
    for path in ["mascot.png", os.path.join(os.path.dirname(__file__), "mascot.png")]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{b64}"
    return ""

MASCOT_SRC = _load_mascot()

# ── PAGE CONFIG ──────────────────────────────────────
st.set_page_config(
    page_title="Cừu Cần Cù — AI Financial Companion",
    page_icon="🐏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL CSS ────────────────────────────────────────
st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════
   CỪU CẦN CÙ v4 — Emotional AI Companion
   Design: Finch × Character.AI × Duolingo × Calm
═══════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

/* ── Streamlit chrome ── */
#MainMenu,footer,header,
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
.stDeployButton{display:none!important}

/* ── Reset ── */
*{font-family:'Nunito',sans-serif!important}
.block-container{padding:12px 16px!important;max-width:100%!important}
.stApp{background:#F0EBE3!important}
[data-testid="stColumn"]>div{padding:4px 8px!important}

/* ─── ANIMATIONS ─────────────────── */
@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(1.04)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
@keyframes float-h{0%,100%{transform:translateX(0)}50%{transform:translateX(18px)}}
@keyframes wag{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(8deg)}}
@keyframes slide-up{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes fade-in{from{opacity:0}to{opacity:1}}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.35)}}

/* ─── SIDEBAR ────────────────────── */
.sidebar{background:white;border-radius:28px;padding:22px 15px 18px;
  min-height:96vh;display:flex;flex-direction:column;gap:8px;
  box-shadow:0 4px 28px rgba(0,0,0,.07);animation:fade-in .5s ease}
.sb-mascot-wrap{text-align:center;padding-bottom:16px;
  border-bottom:1px solid #F0EBE3;margin-bottom:4px}
.sb-mascot{width:84px;height:84px;border-radius:50%;object-fit:cover;
  border:3px solid #E8E4FF;box-shadow:0 4px 20px rgba(124,111,232,.22);
  animation:breathe 4s ease-in-out infinite}
.sb-name{font-size:14px;font-weight:800;color:#1A1A2E;margin:8px 0 2px}
.sb-sub{font-size:11px;color:#9E9E9E;margin:0}
.sb-nav{display:flex;flex-direction:column;gap:1px;flex:1;margin:4px 0}
.sb-item{display:flex;align-items:center;gap:10px;padding:10px 13px;
  border-radius:16px;font-size:13px;font-weight:600;color:#555;
  cursor:pointer;transition:all .2s;white-space:nowrap}
.sb-item:hover{background:#F5F3FF;color:#7C6FE8}
.sb-item.active{background:linear-gradient(135deg,#EDE7F6,#E8E4FF);color:#4A3ACA;font-weight:700}
.sb-streak{background:linear-gradient(135deg,#FFF9EC,#FFE4C4);border-radius:18px;
  padding:14px;border:1px solid #FFD54F;text-align:center;
  font-size:12px;color:#5D4037;line-height:1.6}
.sb-streak-icon{font-size:22px;display:block;margin-bottom:4px}

/* ─── CENTER HERO ────────────────── */
.hero-outer{position:relative;margin-bottom:14px;animation:fade-in .6s ease}
.hero-wrap{border-radius:28px;overflow:hidden;
  box-shadow:0 6px 32px rgba(0,0,0,.1);display:block}
.hero-svg{width:100%;display:block}
.hero-sheep-float{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);
  display:flex;flex-direction:column;align-items:center;z-index:10;
  animation:float 3.5s ease-in-out infinite}
.hero-sheep-img{width:108px;height:108px;object-fit:contain;
  filter:drop-shadow(0 8px 24px rgba(0,0,0,.18));background:transparent}
.hero-sheep-state{font-size:22px;position:absolute;top:-2px;right:-6px;
  animation:wag 2.5s ease-in-out infinite}
.hero-bubble{background:white;border-radius:20px 20px 20px 6px;
  padding:7px 13px;font-size:12px;color:#1A1A2E;
  box-shadow:0 3px 16px rgba(0,0,0,.1);font-weight:600;
  margin-top:6px;max-width:180px;text-align:center;white-space:nowrap}

/* Dream card */
.dream-card{background:white;border-radius:24px;padding:18px 20px;
  box-shadow:0 2px 16px rgba(0,0,0,.06);margin-bottom:12px;
  animation:slide-up .5s ease .1s both}
.dc-title{font-size:13.5px;font-weight:800;color:#1A1A2E;margin:0 0 10px;
  display:flex;align-items:center;gap:8px}
.dc-house{font-size:40px;float:right;line-height:1;margin:0 0 4px 12px}
.dc-text{font-size:12.5px;color:#555;line-height:1.75;margin:0 0 14px}
.dc-path-wrap{background:linear-gradient(90deg,#E8F5E9,#F0FFF4);
  border-radius:14px;height:38px;overflow:hidden;position:relative;margin:10px 0 6px}
.dc-path-fill{height:100%;border-radius:14px;
  background:linear-gradient(90deg,#43e97b,#1de9b6);
  display:flex;align-items:center;justify-content:flex-end;
  padding-right:8px;font-size:18px;animation:breathe 3s ease-in-out infinite}
.dc-steps{font-size:12px;color:#388E3C;font-weight:700;text-align:center;margin-top:4px}

/* Memory card (diary style) */
.memory-card{background:linear-gradient(135deg,#FFFDE7,#FFF9C4);
  border-radius:24px;padding:18px 20px;border-left:4px solid #FFD54F;
  box-shadow:0 2px 16px rgba(255,213,79,.2);margin-bottom:12px;
  animation:slide-up .5s ease .2s both}
.mc-title{font-size:13px;font-weight:800;color:#5D4037;margin:0 0 10px;
  display:flex;align-items:center;gap:6px}
.mc-item{font-size:12.5px;color:#6D4C41;line-height:1.7;
  padding:5px 0;border-bottom:1px dashed #FFE082}
.mc-item:last-child{border-bottom:none}

/* Daily message */
.daily-msg{background:linear-gradient(135deg,#EFF6FF,#DBEAFE);
  border-radius:24px;padding:18px 20px;
  box-shadow:0 2px 16px rgba(59,130,246,.08);margin-bottom:12px;
  animation:slide-up .5s ease .3s both}
.dm-title{font-size:13px;font-weight:800;color:#1E40AF;margin:0 0 8px;
  display:flex;align-items:center;gap:6px}
.dm-text{font-size:13px;color:#1D4ED8;line-height:1.75}

/* Chat preview card */
.chat-preview{background:white;border-radius:24px;padding:18px 20px;
  box-shadow:0 2px 16px rgba(0,0,0,.06);animation:slide-up .5s ease .4s both}
.cp-title{font-size:13px;font-weight:800;color:#1A1A2E;margin:0 0 12px;
  display:flex;align-items:center;gap:6px}
.cp-bubble-ai{background:linear-gradient(135deg,#F5F3FF,#EDE7F6);
  border-radius:16px 16px 16px 4px;padding:10px 14px;
  font-size:12.5px;color:#1A1A2E;margin-bottom:8px;max-width:85%;line-height:1.65}
.cp-bubble-user{background:#FCE4EC;border-radius:16px 16px 4px 16px;
  padding:10px 14px;font-size:12.5px;color:#1A1A2E;
  margin-bottom:8px;margin-left:auto;max-width:78%;line-height:1.65}
.cp-row{display:flex;gap:8px;align-items:flex-end;margin-bottom:4px}
.cp-row.right{flex-direction:row-reverse}
.cp-av{width:26px;height:26px;border-radius:50%;object-fit:cover;
  flex-shrink:0;border:1.5px solid #E8E4FF}

/* ─── RIGHT PANEL ────────────────── */
.right-panel{background:white;border-radius:28px;padding:20px 15px;
  min-height:96vh;display:flex;flex-direction:column;gap:16px;
  box-shadow:0 4px 28px rgba(0,0,0,.07);animation:fade-in .5s ease}
.rp-section{margin-bottom:4px}
.rp-title{font-size:12.5px;font-weight:800;color:#1A1A2E;margin:0 0 10px;
  display:flex;align-items:center;gap:6px}
.worry-chip{display:inline-flex;align-items:center;gap:6px;
  background:#EFF6FF;border-radius:12px;padding:7px 12px;
  font-size:12px;font-weight:600;color:#1E40AF;
  margin:3px 4px 3px 0;border:1.5px solid #BFDBFE}
.dream-goal{display:flex;align-items:center;gap:10px;padding:10px 13px;
  border-radius:16px;background:#F0FFF4;font-size:12.5px;font-weight:600;
  color:#15803D;margin-bottom:6px;border:1.5px solid #BBF7D0}
.achievement{display:flex;align-items:center;gap:10px;padding:9px 13px;
  border-radius:14px;background:linear-gradient(135deg,#F0FFF4,#DCFCE7);
  font-size:12px;font-weight:600;color:#15803D;margin-bottom:6px;
  border:1px solid #86EFAC}
.ach-check{width:20px;height:20px;border-radius:50%;background:#22C55E;
  display:flex;align-items:center;justify-content:center;
  color:white;font-size:11px;flex-shrink:0}

/* Emotion chips via Streamlit buttons */
div.emotion-zone [data-testid="stButton"]>button{
  border-radius:14px!important;padding:5px 8px!important;font-size:11.5px!important;
  font-weight:600!important;width:100%!important;border:1.5px solid #EEE!important;
  background:#FEFAF6!important;color:#1A1A2E!important;
  transition:all .2s!important;text-align:left!important;line-height:1.4!important}
div.emotion-zone [data-testid="stButton"]>button:hover{
  background:#F5F3FF!important;border-color:#7C6FE8!important;color:#4A3ACA!important}
div.em-sel [data-testid="stButton"]>button{
  background:linear-gradient(135deg,#EDE7F6,#E8E4FF)!important;
  border-color:#7C6FE8!important;color:#4A3ACA!important;
  box-shadow:0 2px 12px rgba(124,111,232,.3)!important}

/* ─── CHAT SCREEN ────────────────── */
.chat-top-bar{background:rgba(255,255,255,.95);border-radius:24px;
  padding:14px 18px;margin-bottom:12px;
  display:flex;align-items:center;gap:14px;
  box-shadow:0 2px 16px rgba(0,0,0,.07)}
.chat-sheep-av{width:48px;height:48px;border-radius:50%;object-fit:cover;
  border:2px solid #E8E4FF;animation:breathe 4s ease-in-out infinite}
.chat-name{font-size:15px;font-weight:800;color:#1A1A2E}
.chat-status{font-size:12px;color:#7C6FE8;font-weight:600;
  display:flex;align-items:center;gap:5px}
.status-dot{width:7px;height:7px;border-radius:50%;background:#22C55E;
  display:inline-block;animation:pulse-dot 1.5s infinite}
.chat-sheep-hero-wrap{text-align:center;padding:20px 0 10px;animation:slide-up .4s ease}
.chat-sheep-hero-circle{
  width:140px;height:140px;border-radius:50%;
  background:linear-gradient(135deg,#F5F3FF,#EDE7F6);
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 32px rgba(124,111,232,.22);
  margin:0 auto;animation:float 3.5s ease-in-out infinite;
  border:3px solid #E8E4FF}
.chat-sheep-hero-img{width:112px;height:112px;object-fit:cover;border-radius:50%}
.chat-sheep-emotion-badge{font-size:28px;display:block;margin-top:6px;
  animation:wag 2.5s ease-in-out infinite}
.pulse-dot{display:inline-block;width:7px;height:7px;border-radius:50%;
  background:#7C6FE8;animation:pulse-dot 1.2s infinite}

/* ─── QR BUTTONS ─────────────────── */
[data-testid="stHorizontalBlock"]{gap:6px!important}
div.qr-zone [data-testid="stButton"]>button{
  background:linear-gradient(135deg,#F5F3FF,#EDE7F6)!important;
  border:1.5px solid #C4B5FD!important;border-radius:20px!important;
  color:#4A3ACA!important;font-size:12px!important;font-weight:700!important;
  padding:10px 12px!important;width:100%!important;
  transition:all .2s!important;line-height:1.4!important}
div.qr-zone [data-testid="stButton"]>button:hover{
  background:linear-gradient(135deg,#7C6FE8,#a78bfa)!important;
  color:white!important;border-color:#7C6FE8!important;transform:translateY(-1px)!important}

/* ─── CHAT INPUT ─────────────────── */
[data-testid="stChatInput"]{border-radius:22px!important;
  border:2px solid #E8E4FF!important;
  box-shadow:0 4px 24px rgba(124,111,232,.15)!important;background:white!important}
[data-testid="stChatInput"] textarea{font-size:14px!important;color:#1A1A2E!important}
[data-testid="stChatInput"] textarea::placeholder{color:#C4B5FD!important;font-style:italic!important}
[data-testid="stChatInput"] button{
  background:linear-gradient(135deg,#7C6FE8,#a78bfa)!important;
  border-radius:50%!important;width:38px!important;height:38px!important;
  box-shadow:0 4px 14px rgba(124,111,232,.4)!important}

/* ─── SPECIAL BUTTONS ────────────── */
div.back-btn [data-testid="stButton"]>button{
  background:none!important;border:none!important;color:#555!important;
  font-size:16px!important;padding:6px 10px!important;border-radius:50%!important;
  transition:background .2s!important}
div.back-btn [data-testid="stButton"]>button:hover{
  background:#F5F3FF!important;color:#7C6FE8!important}
div.start-btn [data-testid="stButton"]>button{
  background:linear-gradient(135deg,#7C6FE8,#a78bfa)!important;
  border:none!important;border-radius:18px!important;color:white!important;
  font-size:14px!important;font-weight:800!important;padding:14px!important;
  width:100%!important;box-shadow:0 4px 22px rgba(124,111,232,.4)!important;
  transition:all .25s!important}
div.start-btn [data-testid="stButton"]>button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 6px 30px rgba(124,111,232,.5)!important}

.disclaimer{font-size:10px;color:#C4B5FD;text-align:center;padding:6px 0}
</style>
""", unsafe_allow_html=True)

# ── CSS nhúng vào iframe chat ─────────────────────────
CHAT_CSS = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:transparent;
}
#chat-wrap{
  height:100vh;
  overflow-y:auto;
  padding:8px 2px 12px;
  scroll-behavior:smooth;
}
.msg-row{display:flex;align-items:flex-end;gap:10px;margin-bottom:14px}
.msg-row.user{flex-direction:row-reverse}
.av-sheep{
  width:36px;height:36px;border-radius:50%;background:#FFF0F0;
  display:flex;align-items:center;justify-content:center;
  overflow:hidden;flex-shrink:0;box-shadow:0 2px 7px rgba(0,0,0,.12);
}
.av-user{
  width:34px;height:34px;border-radius:50%;background:#FCE4EC;
  display:flex;align-items:center;justify-content:center;
  font-size:16px;flex-shrink:0;
}
.bwrap{display:flex;flex-direction:column;gap:3px;max-width:520px}
.msg-row.user .bwrap{align-items:flex-end}
.bubble-ai{
  background:white;border-radius:16px 16px 16px 4px;
  padding:11px 15px;font-size:13.5px;line-height:1.7;color:#1A1A2E;
  box-shadow:0 2px 10px rgba(0,0,0,.09);border:1px solid #EEEEEE;
  word-break:break-word;
}
.bubble-user{
  background:#FCE4EC;border-radius:16px 16px 4px 16px;
  padding:11px 15px;font-size:13.5px;line-height:1.7;color:#1A1A2E;
  box-shadow:0 2px 10px rgba(0,0,0,.09);word-break:break-word;
}
.msg-time{font-size:10.5px;color:#BDBDBD;padding:0 3px}
.msg-row.user .msg-time{text-align:right}
/* product cards */
.cards-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.p-card{
  background:white;border-radius:13px;border:1px solid #EEEEEE;
  box-shadow:0 2px 9px rgba(0,0,0,.08);overflow:hidden;
  width:240px;font-size:12.5px;
}
.p-ch{padding:10px 13px;border-bottom:1px solid #F5F5F5;
  display:flex;align-items:center;gap:9px}
.p-icon{font-size:20px}
.p-name{font-weight:700;font-size:13px}
.p-type{font-size:10.5px;color:#9E9E9E;margin-top:1px}
.p-body{padding:9px 13px;display:flex;flex-direction:column;gap:5px}
.p-row{display:flex;justify-content:space-between;align-items:center}
.p-lbl{color:#9E9E9E;font-size:11.5px}
.p-val{font-weight:600;font-size:12px}
.p-green{color:#27AE60}.p-red{color:#D0021B}
.p-desc{font-size:11px;color:#666;background:#F8FAFD;
  border-radius:7px;padding:6px 8px;border:1px solid #EEF0F5;margin-top:1px}
.p-btn{
  background:#D0021B;color:white;text-align:center;
  padding:9px;font-size:12.5px;font-weight:700;
  border-radius:0 0 13px 13px;cursor:pointer;
}
/* markdown tables inside bubbles */
.msg-table{border-collapse:collapse;width:100%;font-size:12px;margin:8px 0;border-radius:8px;overflow:hidden}
.msg-table th{background:#EDE7F6;color:#4A3ACA;font-weight:700;padding:6px 10px;text-align:left;font-size:11.5px}
.msg-table td{padding:5px 10px;border-bottom:1px solid #F0F0F0;font-size:12px}
.msg-table tr:last-child td{border-bottom:none}
.msg-table tr:nth-child(even) td{background:#FAFAFA}
</style>
"""

# ── KB — thông tin sản phẩm TCBS chi tiết ─────────────
KB = {
    "ipower": {
        "name": "iPower",
        "min": 50_000,
        "ret": "~5–6%/năm",
        "liq": "Rút bất kỳ lúc",
        "emoji": "🌱",
        "desc": "Tích lũy linh hoạt, không kỳ hạn, lãi cộng dồn hằng ngày. Phù hợp người mới bắt đầu hoặc cần quỹ khẩn cấp.",
        "detail": (
            "**iPower** là tài khoản tích lũy linh hoạt của TCBS:\n"
            "• **Lãi suất:** ~5–6%/năm, cộng dồn hàng ngày\n"
            "• **Tối thiểu:** 50.000đ — thấp nhất thị trường\n"
            "• **Rút tiền:** Bất kỳ lúc nào, tiền về tức thì\n"
            "• **Phù hợp:** Người mới, quỹ dự phòng, tiết kiệm ngắn hạn\n"
            "• **Cách mua:** TCInvest App → Tích lũy → iPower → Nạp tiền"
        ),
    },
    "ifund": {
        "name": "iFund / TCEF",
        "min": 100_000,
        "ret": "~12–18%/năm",
        "liq": "T+3",
        "emoji": "📊",
        "desc": "Quỹ mở cổ phiếu, đa dạng hóa danh mục tự động. Phù hợp tích lũy 3–10 năm.",
        "detail": (
            "**iFund / TCEF** — Quỹ mở đầu tư cổ phiếu:\n"
            "• **Lợi nhuận lịch sử:** ~12–18%/năm (biến động theo thị trường)\n"
            "• **Tối thiểu:** 100.000đ/lần mua\n"
            "• **Thanh khoản:** T+3 (tiền về sau 3 ngày làm việc)\n"
            "• **Rủi ro:** Trung bình — phân tán tự động vào 20–30 cổ phiếu\n"
            "• **Phù hợp:** Mục tiêu 3–10 năm, mua nhà, xe, hưu trí\n"
            "• **DCA tip:** Đầu tư đều mỗi tháng để giảm rủi ro biến động\n"
            "• **Cách mua:** TCInvest App → Quỹ → TCEF → Mua"
        ),
    },
    "ibond": {
        "name": "iBond",
        "min": 1_000_000,
        "ret": "8–11%/năm",
        "liq": "Theo kỳ hạn",
        "emoji": "📋",
        "desc": "Trái phiếu doanh nghiệp chọn lọc, lãi suất cố định, biết trước thu nhập.",
        "detail": (
            "**iBond** — Trái phiếu doanh nghiệp qua TCBS:\n"
            "• **Lãi suất:** 8–11%/năm, cố định, biết trước từ đầu\n"
            "• **Tối thiểu:** 1.000.000đ (1 triệu đồng)\n"
            "• **Kỳ hạn:** 6 tháng, 1 năm, 2 năm, 3 năm\n"
            "• **Thanh khoản:** Theo kỳ hạn — bán trước hạn được nhưng có phí\n"
            "• **Rủi ro:** Thấp — TCBS chọn lọc kỹ tổ chức phát hành\n"
            "• **Phù hợp:** Người cần thu nhập ổn định, vốn trên 5 triệu\n"
            "• **Cách mua:** TCInvest App → Trái phiếu → Chọn kỳ hạn → Mua"
        ),
    },
    "zerofee": {
        "name": "Zero Fee",
        "min": 0,
        "ret": "Tiềm năng cao",
        "liq": "T+2",
        "emoji": "🆓",
        "desc": "Giao dịch cổ phiếu miễn phí hoàn toàn từ 01/01/2023. Không có phí mua, bán cổ phiếu.",
        "detail": (
            "**Zero Fee** — Miễn phí giao dịch cổ phiếu tại TCBS:\n"
            "• **Phí giao dịch:** 0đ — không thu phí mua, bán\n"
            "• **Áp dụng:** Từ 01/01/2023, tất cả cổ phiếu niêm yết\n"
            "• **Thanh khoản:** T+2 (tiền về sau 2 ngày làm việc)\n"
            "• **Rủi ro:** Cao — phụ thuộc thị trường, cần kiến thức phân tích\n"
            "• **Phù hợp:** Người đã có kinh nghiệm đầu tư cổ phiếu\n"
            "• **Lợi thế:** Tiết kiệm 0.15–0.25% phí/giao dịch so với các CTCK khác\n"
            "• **Mở tài khoản:** TCInvest App → Đăng ký (3 phút, eKYC)"
        ),
    },
    "margin789": {
        "name": "Margin 789",
        "min": 0,
        "ret": "Vay từ 7.89%/năm",
        "liq": "Theo hợp đồng",
        "emoji": "📐",
        "desc": "Lãi suất margin ưu đãi 7.89%/năm cho lần đầu sử dụng. Tăng sức mua nhưng cũng tăng rủi ro.",
        "detail": (
            "**Margin 789** — Vay ký quỹ lãi suất ưu đãi:\n"
            "• **Lãi suất:** 7.89%/năm (áp dụng lần đầu tiên)\n"
            "• **Tỷ lệ vay:** Tối đa 1:1 (có 10tr → vay thêm 10tr)\n"
            "• **Điều kiện:** Tài khoản TCBS có số dư tối thiểu\n"
            "• **Rủi ro:** CAO — lỗ nhân đôi, có thể bị call margin\n"
            "• **Phù hợp:** Nhà đầu tư có kinh nghiệm, hiểu rõ rủi ro\n"
            "• **Lưu ý:** Cừu khuyên bạn tìm hiểu kỹ trước khi dùng margin\n"
            "• **Đăng ký:** TCInvest App → Tài khoản → Margin → Đăng ký"
        ),
    },
}

DAILY_TIPS = [
    "Đầu tư từ số tiền nhỏ hôm nay, tương lai sẽ lớn hơn bạn nghĩ! ✨",
    "10.000đ/ngày = 3.650.000đ sau 1 năm. Bắt đầu nhỏ thôi! 🌱",
    "Người giàu có nhiều tiền vì tiết kiệm — không phải ngược lại. 💡",
    "Mục tiêu rõ ràng giúp bạn tiết kiệm dễ hơn 3 lần. 🎯",
    "Đa dạng hóa danh mục — cách tốt nhất để ngủ ngon. 😴",
    "DCA: đầu tư đều mỗi tháng, bất kể thị trường lên hay xuống. 📈",
    "Kỷ luật quan trọng hơn tài năng trong đầu tư dài hạn. 🏆",
]

QR_DEFAULT = ["So sánh iPower và iFund", "Đầu tư với 500k/tháng", "Lập mục tiêu tiết kiệm", "Tôi là người mới"]

# ── SESSION STATE ─────────────────────────────────────
_defaults = {
    "messages":    [],
    "qr":          QR_DEFAULT,
    "qr_trigger":  None,
    "mood_ctx":    "neutral",
    "mood_score":  50,
    "screen":      "home",      # "home" | "chat"
    "selected_emotion": None,   # emoji string
    "sheep_state": "calm",      # happy|excited|calm|concerned|worried|sad|listening
    "second_brain": {
        "goals":         [],    # mục tiêu KH đã đề cập
        "events":        [],    # sự kiện KH vừa kể (tối đa 5)
        "mood_timeline": [],    # [{date, score, label}]
        "last_topic":    None,  # chủ đề lần cuối
        "micro_streak":  0,     # số lần chat liên tiếp hôm nay
        "pending_hook":  False, # đã đặt câu hỏi nhật ký chưa
    },
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ───────────────────────────────────────────
def norm(text: str) -> str:
    t = text.lower()
    replacements = [
        ("đ","d"),
        ("á","a"),("à","a"),("ả","a"),("ã","a"),("ạ","a"),
        ("ă","a"),("ắ","a"),("ằ","a"),("ặ","a"),("ẵ","a"),("ẳ","a"),
        ("â","a"),("ấ","a"),("ầ","a"),("ậ","a"),("ẫ","a"),("ẩ","a"),
        ("é","e"),("è","e"),("ẻ","e"),("ẹ","e"),("ẽ","e"),
        ("ê","e"),("ế","e"),("ề","e"),("ệ","e"),("ễ","e"),("ể","e"),
        ("í","i"),("ì","i"),("ị","i"),("ĩ","i"),("ỉ","i"),
        ("ó","o"),("ò","o"),("ọ","o"),("õ","o"),("ỏ","o"),
        ("ô","o"),("ố","o"),("ồ","o"),("ộ","o"),("ỗ","o"),("ổ","o"),
        ("ơ","o"),("ớ","o"),("ờ","o"),("ợ","o"),("ỡ","o"),("ở","o"),
        ("ú","u"),("ù","u"),("ụ","u"),("ũ","u"),("ủ","u"),
        ("ư","u"),("ứ","u"),("ừ","u"),("ự","u"),("ữ","u"),("ử","u"),
        ("ý","y"),("ỳ","y"),("ỵ","y"),("ỹ","y"),("ỷ","y"),
    ]
    for s, d in replacements:
        t = t.replace(s, d)
    return t

def score(t: str, keywords: list) -> int:
    """Đếm số từ khóa match trong text đã norm."""
    return sum(1 for kw in keywords if kw in t)

def extract_amount(text: str):
    t = norm(text)
    m = re.search(r'(\d[\d.,]*)[\s]*(k|tr|trieu|nghin|trieu dong|trieu d)', t)
    if not m:
        m = re.search(r'(\d{3,})', t)
    if not m:
        return None
    raw = float(m.group(1).replace(",", "").replace(".", ""))
    unit = m.group(2) if m.lastindex and m.lastindex >= 2 else ""
    if unit in ("k", "nghin"):
        raw *= 1000
    elif unit in ("tr", "trieu", "trieu dong", "trieu d"):
        raw *= 1_000_000
    if 1000 <= raw <= 9999:
        raw *= 1000
    return int(raw)

def fmtm(n: int) -> str:
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{v:.0f} triệu đ" if v == int(v) else f"{v:.1f} triệu đ"
    if n >= 1000:
        return f"{n // 1000}.000đ"
    return f"{n}đ"

def recent_context() -> str:
    """Lấy 4 tin nhắn gần nhất (user + ai) để hiểu context."""
    msgs = st.session_state.messages[-4:]
    return " ".join(norm(m["content"]) for m in msgs)

def md_to_html(text: str) -> str:
    text = html_lib.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)

    # ── Markdown table parser ──────────────────────────
    lines = text.split("\n")
    result_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Separator row: |---|---|---|
        if re.match(r"^\s*\|[\s\-|:]+\|\s*$", line):
            # Previous line should be the header
            if result_lines and "|" in result_lines[-1]:
                header_raw = result_lines.pop()
                headers = [h.strip() for h in header_raw.strip("|").split("|")]
                table = '<table class="msg-table"><thead><tr>'
                for h in headers:
                    table += f"<th>{h}</th>"
                table += "</tr></thead><tbody>"
                i += 1
                while i < len(lines) and "|" in lines[i] and not re.match(r"^\s*\|[\s\-|:]+\|\s*$", lines[i]):
                    cells = [c.strip() for c in lines[i].strip("|").split("|")]
                    table += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
                    i += 1
                table += "</tbody></table>"
                result_lines.append(table)
                continue
        # Bullet points
        if re.match(r"^[•\-]\s", line) or re.match(r"^\d+\.\s", line):
            result_lines.append(f"<div style='padding-left:8px'>{line}</div>")
        else:
            result_lines.append(line)
        i += 1

    text = "\n".join(result_lines)
    paras = text.split("\n\n")
    result = []
    for para in paras:
        if para.strip().startswith("<table"):
            result.append(para)
        else:
            lines2 = para.split("\n")
            result.append("<p>" + "<br>".join(lines2) + "</p>")
    return "".join(result)

def card_html(pid: str) -> str:
    p = KB.get(pid)
    if not p:
        return ""
    min_row = (
        f'<div class="p-row"><span class="p-lbl">Tối thiểu</span>'
        f'<span class="p-val p-red">{fmtm(p["min"])}</span></div>'
    ) if p["min"] else ""
    return f"""
<div class="p-card">
  <div class="p-ch">
    <span class="p-icon">{p['emoji']}</span>
    <div><div class="p-name">{p['name']}</div><div class="p-type">Sản phẩm TCBS</div></div>
  </div>
  <div class="p-body">
    <div class="p-row"><span class="p-lbl">Sinh lời</span><span class="p-val p-green">{p['ret']}</span></div>
    <div class="p-row"><span class="p-lbl">Thanh khoản</span><span class="p-val">{p['liq']}</span></div>
    {min_row}
    <div class="p-desc">✨ {p['desc']}</div>
  </div>
  <div class="p-btn">Tìm hiểu thêm →</div>
</div>"""

def build_chat_html(messages: list) -> str:
    rows = []
    for msg in messages:
        content = md_to_html(msg["content"])
        t = msg["time"]
        products = msg.get("products", [])
        cards = "".join(card_html(p) for p in products)
        cards_block = f'<div class="cards-row">{cards}</div>' if cards else ""

        if msg["role"] == "user":
            rows.append(f"""
<div class="msg-row user">
  <div class="bwrap">
    <div class="bubble-user">{content}</div>
    <div class="msg-time">{t}</div>
  </div>
  <div class="av-user">👤</div>
</div>""")
        else:
            av_inner = (
                f'<img src="{MASCOT_SRC}" style="width:36px;height:36px;object-fit:cover;border-radius:50%">'
                if MASCOT_SRC else "🐏"
            )
            rows.append(f"""
<div class="msg-row">
  <div class="av-sheep">{av_inner}</div>
  <div class="bwrap">
    <div class="bubble-ai">{content}</div>
    {cards_block}
    <div class="msg-time">{t}</div>
  </div>
</div>""")

    body = "\n".join(rows) if rows else (
        '<p style="color:#BDBDBD;text-align:center;margin-top:40px;font-size:13px">'
        'Bắt đầu cuộc trò chuyện với Cừu bên dưới 💬</p>'
    )
    # JS scroll-to-bottom: cuộn wrapper div, không phải body
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">{CHAT_CSS}</head>
<body>
<div id="chat-wrap">
  <div id="chat-inner">{body}</div>
  <div id="anchor"></div>
</div>
<script>
  (function(){{
    var wrap = document.getElementById('chat-wrap');
    var anchor = document.getElementById('anchor');
    function scrollDown(){{ anchor.scrollIntoView({{behavior:'auto'}}); wrap.scrollTop = wrap.scrollHeight; }}
    scrollDown();
    setTimeout(scrollDown, 80);
    setTimeout(scrollDown, 300);
  }})();
</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════
#  AI PIPELINE  —  Companion-First, Financial-Second
#
#  process_message(text)
#    ↓
#  [Stage 1]  Emotional Mirroring  — cảm nhận, phản chiếu ngôn ngữ KH
#    ↓
#  [Stage 2]  Second Brain         — truy vấn mục tiêu + sự kiện gần nhất
#    ↓
#  [Stage 3]  Behavioral Nudge     — Micro-Commitment CTA, không mệnh lệnh
#    ↓
#  [Stage 4]  Retention Hook       — câu hỏi nhật ký + closer mở luồng
#    ↓
#  JSON output: {content, products, qr, mood_score}
# ══════════════════════════════════════════════════════════════════════

# ── STAGE 1 · EMOTIONAL MIRRORING ────────────────────
def analyze_emotion(t: str, ctx: str) -> dict:
    """
    Stage 1 — Emotional Mirroring.
    Không chỉ classify cảm xúc mà còn:
    - Chấm mood_score (0–100) để theo dõi tâm lý KH theo ngày
    - Phát hiện sự kiện cụ thể KH vừa kể (event extraction)
    - Nhận ra sub-emotion để phản chiếu ngôn ngữ tự nhiên hơn
    """
    # ── Keyword banks ──
    very_neg = ["tuyet vong", "tram cam", "chiu khong noi", "muon bo cuoc",
                "that vong hoan toan", "qua suc chiu dung", "suy sup"]
    neg_kws  = ["buon", "stress", "met", "chan", "lo lang", "ap luc", "so hai",
                "that vong", "kho khan", "nan long", "that bai", "bi quan",
                "qua suc", "kiet suc", "mo mo", "co don", "cang thang",
                "khong on", "mat ngu", "met moi", "lo au", "khong biet lam sao",
                "roi loan", "khong yen", "tuc gian", "buc boi"]
    pos_kws  = ["vui", "hanh phuc", "tu hao", "phan khich", "tuyet voi",
                "on roi", "tot lam", "hom nay tot", "phan khoi", "sung suong",
                "binh yen", "nhe nhom", "thanh thoi", "on dinh", "phuc khoi",
                "mim cuoi", "cuoi", "vui ve", "yen tam", "tu tin"]
    very_pos = ["hanh phuc nhat", "vo cung vui", "qua tuyet", "dinh cao",
                "tuyet voi that su", "khong the tin duoc"]
    jrn_kws  = ["tam su", "nhat ky", "ke cuuu", "ke cuu", "muon ke",
                "can ai do", "can chia se", "muon noi", "toi cam thay",
                "minh cam thay", "trong long", "khong biet ke ai", "ke ban nghe",
                "muon tam su", "can nguoi nghe"]

    # ── Event extraction (sự kiện cụ thể KH kể) ──
    event_patterns = {
        "tang luong":   ["tang luong", "duoc tang luong", "luong cao hon"],
        "mat viec":     ["mat viec", "bi sa thai", "bi cat giam", "nghi viec"],
        "con om":       ["con om", "con bi benh", "dua tre om"],
        "cuoi":         ["sap cuoi", "cuoi sap toi", "dam cuoi"],
        "mua nha":      ["mua nha", "dat coc nha", "vay mua nha"],
        "du lich":      ["di du lich", "sap di du lich", "ve du lich"],
        "ho hoi":       ["buon chuyen", "cai nhau", "chia tay"],
        "thanh cong":   ["thanh cong", "hoan thanh", "dat muc tieu", "thang"],
    }
    detected_event = None
    for event_key, patterns in event_patterns.items():
        if any(p in t for p in patterns):
            detected_event = event_key
            break

    s_vneg = score(t, very_neg)
    s_neg  = score(t, neg_kws)
    s_pos  = score(t, pos_kws)
    s_vpos = score(t, very_pos)
    s_jrn  = score(t, jrn_kws)

    # ── mood_score tính từ 0–100 ──
    raw = 50
    raw -= s_vneg * 20
    raw -= s_neg  * 8
    raw += s_pos  * 8
    raw += s_vpos * 15
    mood_score = max(0, min(100, raw))

    # ── label ──
    if s_jrn >= 1:
        label, intensity = "journal", min(s_jrn, 3)
    elif s_vneg >= 1 or (s_neg >= 2):
        label, intensity = "very_negative", min(s_vneg + s_neg, 3)
    elif s_neg >= 1:
        label, intensity = "negative", min(s_neg, 3)
    elif s_vpos >= 1 or (s_pos >= 2):
        label, intensity = "very_positive", min(s_vpos + s_pos, 3)
    elif s_pos >= 1:
        label, intensity = "positive", min(s_pos, 3)
    else:
        label, intensity = "neutral", 0

    prev_mood = st.session_state.get("mood_ctx", "neutral")
    mood_shift = (label not in ("neutral",)) and (label != prev_mood)

    return {
        "label":          label,
        "intensity":      intensity,
        "mood_score":     mood_score,
        "mood_shift":     mood_shift,
        "detected_event": detected_event,
    }


# ── STAGE 2 · SECOND BRAIN (Memory) ─────────────────
def fetch_memory() -> dict:
    """
    Stage 2 — Context Retrieval từ Second Brain.
    Truy vấn: mục tiêu KH, sự kiện gần nhất, chuỗi mood,
    chủ đề hôm qua — để phản hồi mang tính liên tục.
    """
    msgs   = st.session_state.messages
    sb     = st.session_state.second_brain

    history_text  = " ".join(norm(m["content"]) for m in msgs[-6:])
    prev_mood     = st.session_state.get("mood_ctx", "neutral")
    prev_score    = st.session_state.get("mood_score", 50)
    turn_count    = len([m for m in msgs if m["role"] == "user"])

    last_products = []
    for m in reversed(msgs):
        if m["role"] == "ai" and m.get("products"):
            last_products = m["products"]
            break

    # Mood trend: đang tốt lên hay xấu đi?
    timeline = sb.get("mood_timeline", [])
    mood_trend = "stable"
    if len(timeline) >= 2:
        diff = timeline[-1]["score"] - timeline[-2]["score"]
        mood_trend = "improving" if diff > 10 else ("declining" if diff < -10 else "stable")

    return {
        "history_text":   history_text,
        "prev_mood":      prev_mood,
        "prev_score":     prev_score,
        "turn_count":     turn_count,
        "last_products":  last_products,
        "goals":          sb.get("goals", []),
        "events":         sb.get("events", []),
        "last_topic":     sb.get("last_topic"),
        "micro_streak":   sb.get("micro_streak", 0),
        "pending_hook":   sb.get("pending_hook", False),
        "mood_trend":     mood_trend,
    }


def update_second_brain(emotion: dict, knowledge: dict, text: str):
    """Cập nhật Second Brain sau mỗi lượt chat."""
    sb = st.session_state.second_brain
    t  = norm(text)

    # Cập nhật mood timeline
    today = datetime.now().strftime("%Y-%m-%d")
    timeline = sb.get("mood_timeline", [])
    if not timeline or timeline[-1]["date"] != today:
        timeline.append({"date": today, "score": emotion["mood_score"], "label": emotion["label"]})
    else:
        # Average với điểm cũ trong ngày
        timeline[-1]["score"] = int((timeline[-1]["score"] + emotion["mood_score"]) / 2)
    sb["mood_timeline"] = timeline[-14:]  # giữ 14 ngày

    # Cập nhật sự kiện
    if emotion.get("detected_event"):
        events = sb.get("events", [])
        events.append({"event": emotion["detected_event"], "date": today})
        sb["events"] = events[-5:]  # giữ 5 sự kiện gần nhất

    # Cập nhật goals nếu KH đề cập
    goal_kws = {"mua xe": "Mua xe", "mua nha": "Mua nhà",
                "du lich": "Du lịch", "huu tri": "Hưu trí",
                "tu do tai chinh": "Tự do tài chính", "dam cuoi": "Đám cưới"}
    for kw, label in goal_kws.items():
        if kw in t and label not in sb.get("goals", []):
            sb.setdefault("goals", []).append(label)

    # Cập nhật last_topic
    if knowledge.get("intent") not in ("unknown", None):
        sb["last_topic"] = knowledge["intent"]

    # Tăng streak
    sb["micro_streak"] = sb.get("micro_streak", 0) + 1

    st.session_state.second_brain = sb
    st.session_state.mood_ctx     = emotion["label"]
    st.session_state.mood_score   = emotion["mood_score"]


# ── STAGE 3 · KNOWLEDGE SEARCH ───────────────────────
def search_knowledge(t: str, ctx: str, amount) -> dict:
    """
    Xác định intent và tra cứu KB phù hợp.
    Trả về: {intent, products, goal, detail_text}
    """
    # Product affinity scores
    prod_scores = {
        "ipower":    score(t + ctx, ["ipower", "linh hoat", "50k", "50.000",
                                     "tich luy", "gui tiet kiem", "khong ky han"]),
        "ifund":     score(t + ctx, ["ifund", "tcef", "quy mo", "co phieu dai han",
                                     "5 nam", "10 nam", "quy dau tu"]),
        "ibond":     score(t + ctx, ["ibond", "trai phieu", "lai co dinh",
                                     "co dinh", "khoai an toan"]),
        "zerofee":   score(t + ctx, ["zero fee", "zerofee", "mien phi giao dich",
                                     "co phieu", "mua co phieu", "chung khoan"]),
        "margin789": score(t + ctx, ["margin", "vay", "ky quy", "789", "don bay"]),
    }

    # Intent detection (theo thứ tự ưu tiên)
    intent = "unknown"
    if re.search(r"so sanh|ipower.*ifund|ifund.*ipower|khac nhau|chon gi", t):
        intent = "compare"
    elif re.search(r"moi bat dau|nguoi moi|chua biet|chua hieu|lan dau|newbie|biet bat dau tu dau", t):
        intent = "onboarding"
    elif re.search(r"nap tien|chuyen tien|deposit|mo tai khoan|mo tk|dang ki", t):
        intent = "how_to"
    elif re.search(r"lai suat|lai|ty le sinh loi|loi nhuan|bao nhieu phan", t):
        intent = "rates"
    elif re.search(r"gui ngan hang|tiet kiem ngan hang|so voi ngan hang", t):
        intent = "bank_compare"
    elif re.search(r"\bmargin\b|vay ky quy|789|don bay tai chinh", t):
        intent = "margin"
    elif re.search(r"\bibond\b|trai phieu|lai co dinh", t):
        intent = "ibond"
    elif re.search(r"\bifund\b|tcef|quy mo co phieu", t):
        intent = "ifund"
    elif re.search(r"ipower|tich luy linh hoat|gui khong ky han", t):
        intent = "ipower"
    elif re.search(r"co phieu|chung khoan|stock|zero.?fee|mua co phieu", t):
        intent = "zerofee"
    elif re.search(r"muc tieu|ke hoach|tiet kiem|mua xe|mua nha|du lich|gom tien|cuoi|huu tri|tu do tai chinh", t):
        intent = "goal"
    elif amount:
        intent = "amount"
    elif re.search(r"chao|hello|hi\b|xin chao|bat dau|oi cuu|hey", t) and len(t) < 25:
        intent = "greeting"

    # Goal detection
    goal = None
    goal_map = {
        "mua xe":   ("mua xe",     "500 triệu–1 tỷ đ",  3),
        "mua nha":  ("mua nhà",    "1–3 tỷ đ",         10),
        "du lich":  ("du lịch",    "20–100 triệu đ",    1),
        "huu tri":  ("hưu trí",    "3–5 tỷ đ",         20),
        "cuoi":     ("đám cưới",   "100–300 triệu đ",   2),
    }
    for kw, info in goal_map.items():
        if kw in t:
            goal = info
            break

    # Lấy sản phẩm liên quan nhất
    top_products = [p for p, s in sorted(prod_scores.items(), key=lambda x: -x[1]) if s > 0]

    return {
        "intent":      intent,
        "products":    top_products[:3],
        "prod_scores": prod_scores,
        "goal":        goal,
    }


# ── STAGE 4 · LLM / RESPONSE GENERATOR ──────────────
def generate_response(text: str, emotion: dict, memory: dict, knowledge: dict) -> dict:
    """
    Stage 4 — Companion-First Response Generator.
    Mỗi response đi qua 3 bước ẩn:

    Bước 1 · Emotional Mirroring
      → Phản chiếu ngôn ngữ KH, không dùng câu công thức
      → Đồng cảm tự nhiên như người bạn, không như bot

    Bước 2 · Context Retrieval (Second Brain)
      → Nhắc đến mục tiêu KH đã kể
      → Kết nối sự kiện hôm nay với kế hoạch tài chính

    Bước 3 · Behavioral CTA (Micro-Commitment)
      → Gợi ý hành động nhỏ gắn với cảm xúc/sự kiện
      → Không bảo "hãy đầu tư", hỏi "hay là mình thử...?"

    + Retention Hook: câu hỏi nhật ký + closer mở luồng ngày mai
    """
    t             = norm(text)
    amount        = extract_amount(text)
    intent        = knowledge["intent"]
    emotion_label = emotion["label"]
    mood_score    = emotion["mood_score"]
    detected_evt  = emotion.get("detected_event")
    turn          = memory["turn_count"]
    goals         = memory.get("goals", [])
    prev_events   = memory.get("events", [])
    mood_trend    = memory.get("mood_trend", "stable")

    def pick(*opts): return random.choice(opts)

    def out(content, products=None, qr=None, mood_score=mood_score):
        return {
            "content":    content,
            "products":   products or [],
            "qr":         qr or QR_DEFAULT,
            "mood_score": mood_score,
        }

    # ── Helper: Bước 3 · Micro-Commitment CTA ────────────
    def micro_cta(event=None, mood=None, amount_hint=10_000) -> str:
        """Tạo CTA gợi ý nhỏ, gắn với cảm xúc/sự kiện — không phải lệnh đầu tư."""
        amt_str = fmtm(amount_hint)
        event_map = {
            "tang luong":  f"Vừa có tin vui tăng lương — hay là mình 'thưởng' bản thân bằng cách để {amt_str} vào iPower? Nhỏ thôi, nhưng bắt đầu là thắng rồi! 🌱",
            "mat viec":    f"Giai đoạn này quan trọng lắm — hay là mình lập 'quỹ bình tĩnh' nhỏ, chỉ {amt_str}/tuần thôi, để cảm giác vững hơn một chút?",
            "cuoi":        f"Sắp có đám cưới rồi! Hay là mình tạo một mục tiêu nhỏ hôm nay — {amt_str}/ngày, gọi là 'quỹ hạnh phúc'? Cừu tính toán giúp nha!",
            "du lich":     f"Du lịch sắp tới — hay là thử thách: tiết kiệm {amt_str}/ngày từ hôm nay, Cừu sẽ đếm ngược cùng bạn đến ngày đó nhé?",
            "thanh cong":  f"Xứng đáng được kỷ niệm! Hay là đánh dấu thành công bằng cách để {amt_str} vào iPower hôm nay — coi như 'hạt giống' cho thành công tiếp theo?",
        }
        mood_map = {
            "very_negative": f"Hôm nay nặng nề vậy — Cừu có một gợi ý nhỏ thôi: thử thách bản thân với {fmtm(5_000)} hôm nay, gọi là 'quỹ bình yên'. Nhỏ lắm, nhưng đôi khi làm một việc nhỏ giúp mình thấy bớt bất lực hơn.",
            "negative":      f"Hay là mình thử 'thử thách 10k hôm nay'? Chỉ {fmtm(10_000)} thôi — không phải vì số tiền, mà vì cảm giác tự chăm sóc bản thân. 🌱",
            "positive":      f"Ngày đẹp như vầy xứng đáng được đánh dấu! Hay là để {amt_str} vào iPower hôm nay — gọi là 'quỹ kỷ niệm ngày vui'? 🎉",
            "very_positive": f"Năng lượng tích cực như vậy phải chuyển thành hành động luôn! Thử thách: {amt_str} hôm nay, Cừu sẽ cổ vũ bạn! 💪",
        }
        if event and event in event_map:
            return event_map[event]
        if mood and mood in mood_map:
            return mood_map[mood]
        return pick(
            f"Hay là mình thử thách nhỏ hôm nay: chỉ {amt_str} thôi, bắt đầu là thắng rồi! 🌱",
            f"Cừu có một gợi ý vui: {amt_str} hôm nay, gọi là 'ngày bắt đầu'. Nhỉ?",
        )

    # ── Helper: Retention Hook ────────────────────────────
    def retention_hook(mood=None) -> str:
        """Câu hỏi nhật ký cuối mỗi response để tạo thói quen quay lại."""
        positive_hooks = [
            "\n\n💬 *Cừu tò mò: hôm nay điều gì khiến bạn mỉm cười nhất?*",
            "\n\n💬 *À, kể Cừu nghe — hôm nay bạn làm được điều gì mà bạn tự hào?*",
            "\n\n💬 *Ngày mai Cừu sẽ ở đây — kể tiếp nhé! Hôm nay bạn kết thúc thế nào?*",
        ]
        neutral_hooks = [
            "\n\n💬 *Nhân tiện — hôm nay của bạn bắt đầu thế nào? Cừu muốn biết thiệt.*",
            "\n\n💬 *Cừu đặt một câu hỏi nhỏ: gần đây bạn đang vui, buồn, hay đang trong giai đoạn 'cứ trôi'?*",
            "\n\n💬 *Tuần này bạn có một khoảnh khắc nào đáng nhớ không? Nhỏ thôi cũng được — kể Cừu nghe.*",
        ]
        negative_hooks = [
            "\n\n💙 *Cừu sẽ ở đây ngày mai — nếu muốn kể tiếp, Cừu luôn lắng nghe nhé.*",
            "\n\n💙 *Câu hỏi nhỏ thôi: hôm nay có một khoảnh khắc nào khiến bạn thở phào không?*",
        ]
        if mood in ("positive", "very_positive"):
            return pick(*positive_hooks)
        if mood in ("negative", "very_negative"):
            return pick(*negative_hooks)
        return pick(*neutral_hooks)

    # ── Helper: Goal Reminder (Bước 2) ───────────────────
    def goal_reminder() -> str:
        if not goals:
            return ""
        g = goals[-1]  # mục tiêu gần nhất
        return pick(
            f"\n\n🎯 *Nhớ lại mục tiêu '{g}' bạn kể lần trước — mỗi bước nhỏ hôm nay là đang tiến về đó đó.*",
            f"\n\n🎯 *Cừu đang giữ mục tiêu '{g}' của bạn trong lòng — mình cùng nhích thêm một chút hôm nay nha.*",
        )

    # ══════════════════════════════════════════════════════
    #  XỬ LÝ THEO PRIORITY: Cảm xúc → Mục tiêu → Hành động
    # ══════════════════════════════════════════════════════

    # ── [PRIORITY 1] Cảm xúc tiêu cực / Tâm sự ──────────
    if emotion_label in ("very_negative", "negative", "journal"):
        # Bước 1: Emotional Mirroring — không dùng câu công thức
        if detected_evt == "mat viec":
            opener = pick(
                "Trời, mất việc không bao giờ dễ — dù hoàn cảnh nào đi nữa cũng sốc lắm.",
                "Nghe chuyện mà Cừu thấy nặng hộ bạn rồi. Giai đoạn này thật sự không dễ.",
            )
        elif detected_evt == "ho hoi":
            opener = pick(
                "Chuyện tình cảm mà... nhiều khi nặng hơn cả chuyện tiền nữa.",
                "Nghe vậy Cừu thấy bạn đang gánh nhiều lắm. Kể tiếp đi, Cừu nghe.",
            )
        elif emotion_label == "very_negative":
            opener = pick(
                "Bạn đang trải qua giai đoạn thật sự nặng nề — Cừu không muốn nói câu 'Cừu hiểu' rỗng tuếch. Chỉ muốn nói: Cừu ở đây.",
                "Nghe bạn kể mà Cừu thấy... không biết nói gì hơn ngoài việc ở bên bạn lúc này.",
            )
        else:
            opener = pick(
                "Trời, nghe vậy mà Cừu cũng thấy nặng theo.",
                "Ừ, đôi khi mọi thứ cứ dồn vào một lúc không biết bắt đầu từ đâu nhỉ.",
                "Kể được ra như vậy là dũng cảm lắm đó bạn — không phải ai cũng làm được.",
            )

        # Bước 2: Nhắc mục tiêu (nhẹ nhàng nếu mood rất tiêu cực)
        goal_note = ""
        if goals and emotion_label != "very_negative":
            goal_note = pick(
                f"\n\nCừu vẫn đang giữ mục tiêu '{goals[-1]}' của bạn trong lòng đây — khi bạn sẵn sàng, mình cùng tiếp tục nhé.",
                f"\n\nMục tiêu '{goals[-1]}' vẫn ở đó, không đi đâu hết — hôm nay chỉ cần lo cho bản thân thôi.",
            )

        # Bước 3: Micro-Commitment CTA (không ép)
        cta = ""
        if emotion_label == "negative":  # chỉ gợi ý khi không quá nặng
            cta = "\n\n" + micro_cta(event=detected_evt, mood=emotion_label, amount_hint=10_000)

        # Retention Hook
        hook = retention_hook(mood=emotion_label)

        content = opener + goal_note + cta + hook
        return out(content,
                   qr=["Kể thêm với Cừu", "Viết nhật ký cảm xúc", "Giúp tôi lập kế hoạch nhỏ", "Tôi chỉ cần được lắng nghe"],
                   mood_score=mood_score)

    # ── [PRIORITY 1b] Cảm xúc tích cực ──────────────────
    if emotion_label in ("positive", "very_positive"):
        if detected_evt == "tang luong":
            opener = pick(
                "Ôi, tăng lương! Xứng đáng lắm — chắc bạn đã làm việc rất chăm chỉ rồi!",
                "Tăng lương rồi! Cừu thay bạn mà cũng phấn khích nè!",
            )
        elif detected_evt == "thanh cong":
            opener = pick(
                "Nghe tin vui mà Cừu cũng thấy vui lây!",
                "Thành công mà — đáng được ăn mừng lắm chứ!",
            )
        else:
            opener = pick(
                "Ôi, hôm nay của bạn nghe vui vậy! Cừu cũng phấn chấn theo.",
                "Ngày đẹp như vầy thì phải tận dụng chứ nhỉ!",
                "Wow, năng lượng của bạn hôm nay lan sang Cừu rồi đó!",
            )

        # Bước 3: Micro-Commitment CTA gắn với niềm vui
        cta = "\n\n" + micro_cta(event=detected_evt, mood=emotion_label, amount_hint=50_000)

        # Bước 2: Goal connection
        goal_note = goal_reminder()

        hook = retention_hook(mood=emotion_label)
        content = opener + cta + goal_note + hook
        return out(content,
                   products=["ipower"],
                   qr=["Tôi muốn bắt đầu ngay!", "Tính toán chi tiết hơn", "Kể Cừu nghe thêm", "Đặt mục tiêu mới"],
                   mood_score=mood_score)

    # ── [PRIORITY 2] Nhật ký / Tâm sự ───────────────────
    if intent == "journal" or re.search(r"nhat ky|viet nhat|tam su|ke cuu|ke cuuu|muon tam su", t):
        return out(
            pick(
                "Cừu rất vui khi bạn muốn kể! 📝 Đây là không gian chỉ có hai đứa mình — bạn nói gì Cừu cũng nghe, không phán xét gì đâu.\n\n**Hôm nay của bạn bắt đầu thế nào?**" + retention_hook("neutral"),
                "Tốt quá! Cừu thích nghe bạn kể lắm.\n\nBắt đầu bằng một câu thôi — *\"Hôm nay tôi cảm thấy...\"* — Cừu sẽ ở đây đọc và phản hồi từ trái tim. 💙" + retention_hook("neutral"),
            ),
            qr=["Hôm nay tôi cảm thấy...", "Tôi đang lo về tài chính", "Tôi muốn thay đổi thói quen", "Kể chuyện vui hôm nay"]
        )

    # ── [PRIORITY 3] Xử lý theo Intent từ Knowledge ──────
    # Greeting
    if intent == "greeting":
        hour = datetime.now().hour
        gr = "Buổi sáng" if hour < 11 else ("Buổi trưa" if hour < 13 else ("Buổi chiều" if hour < 18 else "Buổi tối"))
        is_return = turn > 1
        if is_return:
            opener = pick(
                f"{gr} bạn! Cừu nhớ bạn đó — hôm nay thế nào rồi? 😊",
                f"Bạn quay lại rồi! {gr} nhé — kể Cừu nghe hôm nay của bạn đi.",
            )
        else:
            opener = pick(
                f"{gr} bạn! ✨ Cừu đây — không chỉ là trợ lý tài chính, mà là người bạn muốn thực sự hiểu bạn.\n\nHôm nay bạn đang cảm thấy thế nào?",
                f"{gr}! 🌸 Mình là Cừu — bạn có thể tâm sự tự do về tiền bạc, cảm xúc, hay mục tiêu.\n\nCừu muốn hỏi ngay: hôm nay của bạn bắt đầu ra sao? 😊",
            )
        return out(opener + retention_hook("neutral"),
                   qr=["Tôi đang stress về tiền", "Muốn bắt đầu đầu tư", "Kể chuyện hôm nay", "Giúp tôi lập mục tiêu"])

    # Số tiền
    if intent == "amount" and amount:
        if amount <= 200_000:
            yearly = amount * 365
            body = pick(
                f"**{fmtm(amount)}** — nhỏ thôi nhưng bắt đầu là thắng rồi! ✨\n\n🌱 **iPower** sinh ra để dành cho những bước đầu này: tối thiểu 50k, lãi cộng dồn hằng ngày, rút bất kỳ lúc.\n\nNếu để dành {fmtm(amount)}/ngày → sau 1 năm là **{fmtm(yearly)}** + lãi ~5–6%. Không cần nhiều, cần đều! 🌱",
                f"Với **{fmtm(amount)}** bạn đã bắt đầu được rồi — đừng nghĩ nhỏ, nghĩ 'đều' mới đúng!\n\n🌱 **iPower**: tối thiểu 50k · lãi hằng ngày · rút bất kỳ lúc.\n\nTiết kiệm đều {fmtm(amount)}/ngày → 1 năm = **{fmtm(yearly)}** + lãi!",
            )
            cta = "\n\n" + micro_cta(event=detected_evt, mood=emotion_label, amount_hint=amount)
            hook = goal_reminder() + retention_hook(emotion_label)
            return out(body + cta + hook, products=["ipower"],
                       qr=["Cách mở tài khoản TCBS", "Lãi suất iPower bao nhiêu?", "Nạp tiền vào iPower", "Tôi muốn lập mục tiêu"])

        if amount <= 5_000_000:
            body = pick(
                f"**{fmtm(amount)} mỗi tháng** — con số tốt lắm, đủ để tạo ra thay đổi thật sự! 💪\n\nCừu gợi ý chia đôi:\n• 50% → **iPower** (quỹ dự phòng, rút được khi cần)\n• 50% → **iFund** (tăng trưởng dài hạn ~12–18%/năm)\n\nSau 5 năm ước tính: **~{fmtm(int(amount * 12 * 5 * 1.35))}** 🚀",
                f"Wow, {fmtm(amount)}/tháng! Với số này, bạn có thể xây dựng cả một danh mục nhỏ.\n\n🌱 **iPower** — an toàn, rút được · 📊 **iFund** — tăng trưởng theo thời gian\n\nBạn đang có mục tiêu gì? Cừu sẽ tính toán phù hợp với mục tiêu đó nhé.",
            )
            cta = "\n\n" + micro_cta(event=detected_evt, mood=emotion_label, amount_hint=min(amount // 10, 100_000))
            hook = goal_reminder() + retention_hook(emotion_label)
            return out(body + cta + hook, products=["ipower", "ifund"],
                       qr=["Tính toán theo mục tiêu cụ thể", "Tôi muốn mua nhà", "Mục tiêu 5 năm", "So sánh iPower và iFund"])

        body = (f"**{fmtm(amount)}** — đây là số vốn đủ để xây danh mục bài bản rồi! 💎\n\n"
                f"Cừu gợi ý đa dạng hóa:\n• 🌱 **iPower** (~20%) — quỹ dự phòng linh hoạt\n"
                f"• 📊 **iFund** (~50%) — tăng trưởng dài hạn\n• 📋 **iBond** (~30%) — thu nhập cố định 8–11%/năm\n\n"
                "Bạn muốn Cừu phân tích chi tiết hơn theo mục tiêu không?")
        return out(body + goal_reminder() + retention_hook(emotion_label),
                   products=["ipower", "ifund", "ibond"],
                   qr=["Phân tích danh mục", "Tôi muốn thu nhập cố định", "Mục tiêu hưu trí", "Tìm hiểu iBond"])

    # So sánh
    if intent == "compare":
        body = ("Cừu so sánh thật sự khách quan cho bạn nha! 📊\n\n"
                "| | 🌱 iPower | 📊 iFund |\n|---|---|---|\n"
                "| Tối thiểu | 50.000đ | 100.000đ |\n"
                "| Sinh lời | ~5–6%/năm | ~12–18%/năm |\n"
                "| Rủi ro | Thấp | Trung bình |\n"
                "| Rút tiền | Bất kỳ lúc | T+3 |\n"
                "| Phù hợp | Ngắn hạn, dự phòng | Dài hạn 3–10 năm |\n\n"
                "**Gợi ý:** Chưa chắc thì bắt đầu iPower — quen rồi phân bổ thêm sang iFund. Không bao giờ là 'quá muộn' để bắt đầu! 🌱")
        return out(body + goal_reminder() + retention_hook(emotion_label),
                   products=["ipower", "ifund"],
                   qr=["Bắt đầu với iPower", "Tìm hiểu iFund", "Tôi muốn cả hai", "Cần bao nhiêu để bắt đầu?"])

    # Onboarding
    if intent == "onboarding":
        body = ("Chào mừng bạn đến với hành trình đầu tư! 🌱 Cừu đồng hành từng bước — không cần biết nhiều, chỉ cần bắt đầu đúng chỗ.\n\n"
                "**3 bước siêu đơn giản:**\n\n"
                "**1.** Mở tài khoản TCBS miễn phí — 3 phút qua TCInvest App\n\n"
                "**2.** Nạp tối thiểu **50.000đ** (bất kỳ ngân hàng nào)\n\n"
                "**3.** Gửi vào **iPower** — lãi chạy ngay từ ngày đầu, rút bất kỳ lúc\n\n"
                + micro_cta(event=detected_evt, mood=emotion_label, amount_hint=50_000))
        return out(body + retention_hook(emotion_label), products=["ipower"],
                   qr=["Cách mở tài khoản TCBS", "Cách nạp tiền đầu tiên", "iPower hoạt động thế nào?", "Mất bao lâu để thấy lãi?"])

    # How-to / Nạp tiền
    if intent == "how_to":
        body = ("Nạp tiền vào TCBS — chỉ 2 phút thôi! 💰\n\n"
                "**Qua TCInvest App:**\n1. Tài khoản → Nạp tiền\n"
                "2. Chọn ngân hàng (hỗ trợ 20+)\n3. Nhập số tiền → Xác nhận\n\n"
                "**Qua TCB Mobile:** Đầu tư → Tài khoản CK → Chuyển tiền vào\n\nTiền về ngay lập tức! ✅")
        return out(body + retention_hook(emotion_label),
                   qr=["Tải TCInvest App ở đâu?", "Tôi dùng ngân hàng khác được không?", "Sau khi nạp làm gì tiếp?", "Hỗ trợ ngân hàng nào?"])

    # Rates / Lãi suất
    if intent == "rates":
        return out(
            "Lãi suất các sản phẩm TCBS: 📋\n\n"
            "🌱 **iPower:** ~5–6%/năm, cộng dồn hàng ngày\n"
            "📊 **iFund/TCEF:** ~12–18%/năm (lịch sử)\n"
            "📋 **iBond:** 8–11%/năm cố định\n"
            "🆓 **Cổ phiếu (Zero Fee):** Tiềm năng không giới hạn, rủi ro cao\n"
            "📐 **Margin 789:** Vay từ 7.89%/năm\n\n"
            + micro_cta(event=detected_evt, mood=emotion_label)
            + retention_hook(emotion_label),
            qr=["Chi tiết iPower", "Chi tiết iFund", "Chi tiết iBond", "Tôi muốn lợi nhuận cao nhất"]
        )

    # Bank compare
    if intent == "bank_compare":
        return out(
            "So sánh TCBS vs Gửi ngân hàng truyền thống: 📊\n\n"
            "**Ngân hàng thường:** ~4–5%/năm · kỳ hạn cố định · rút sớm mất lãi\n\n"
            "**iPower TCBS:** ~5–6%/năm · **không kỳ hạn** · rút bất kỳ lúc\n\n"
            "**iBond TCBS:** 8–11%/năm · cố định · biết trước thu nhập\n\n"
            "**iFund TCBS:** ~12–18%/năm · biến động nhưng tiềm năng cao hơn nhiều\n\n"
            + micro_cta(event=detected_evt, mood=emotion_label)
            + retention_hook(emotion_label),
            products=["ipower", "ibond"],
            qr=["Mở tài khoản iPower ngay", "Tìm hiểu iBond", "Rủi ro của iPower?", "Có bảo hiểm tiền gửi không?"]
        )

    # Product intents — iPower, iFund, iBond, ZeroFee, Margin
    product_map = {
        "ipower":   ("ipower",    KB["ipower"]["detail"]   + "\n\nTóm lại: **iPower là điểm khởi đầu zero-risk nhất** — tiền sinh lời trong khi bạn học thêm. 💡",
                     ["Cách nạp tiền vào iPower", "Lãi suất cụ thể?", "So sánh với gửi ngân hàng", "Bước tiếp theo?"]),
        "ifund":    ("ifund",     KB["ifund"]["detail"]    + "\n\n**Chiến lược DCA:** đầu tư đều mỗi tháng, bất kể thị trường — cách giảm rủi ro hiệu quả nhất. 📈",
                     ["Đầu tư 300k/tháng vào iFund", "Rủi ro thực sự?", "iFund vs gửi tiết kiệm", "Bắt đầu ngay"]),
        "ibond":    ("ibond",     KB["ibond"]["detail"]    + "\n\niBond phù hợp nếu bạn muốn **biết trước** mình nhận được bao nhiêu. 💡",
                     ["Lãi suất iBond hiện tại", "Mua iBond cần bao nhiêu?", "Kỳ hạn nào tốt?", "So sánh iBond và iPower"]),
        "zerofee":  ("zerofee",  "Cổ phiếu — tiềm năng cao nhưng cần kiến thức! 📈\n\n" + KB["zerofee"]["detail"] + "\n\nNếu chưa có kinh nghiệm, Cừu gợi ý bắt đầu bằng iFund trước — được chuyên gia quản lý, ít rủi ro hơn. 😊",
                     ["Chưa có kinh nghiệm — bắt đầu thế nào?", "Tôi đã giao dịch rồi", "Muốn dùng margin", "iFund vs tự mua cổ phiếu"]),
        "margin":   ("margin789", "Margin — công cụ mạnh, dùng cần cẩn thận! ⚠️\n\n" + KB["margin789"]["detail"] + "\n\n**Nhắc nhở:** Margin nhân đôi lãi nhưng cũng nhân đôi lỗ. Chỉ dùng khi hiểu rõ rủi ro. 💡",
                     ["Điều kiện dùng Margin 789", "Rủi ro margin là gì?", "Tôi chưa muốn dùng margin", "Tìm hiểu thêm"]),
    }
    if intent in product_map:
        prod_key, body, qrs = product_map[intent]
        cta = "\n\n" + micro_cta(event=detected_evt, mood=emotion_label)
        return out(body + cta + goal_reminder() + retention_hook(emotion_label),
                   products=[prod_key], qr=qrs)

    # Goal intent
    if intent == "goal":
        goal_info = knowledge.get("goal")
        if goal_info:
            gname, grange, gyears = goal_info
            body = (f"Mục tiêu **{gname}** — Cừu sẽ đồng hành đến đó cùng bạn! 🎯\n\n"
                    f"Thường cần: **{grange}** trong **{gyears}–{gyears+3} năm**.\n\n"
                    f"**Bước nhỏ đầu tiên:**\n• Xác định số tiền mục tiêu\n"
                    f"• Chia thành khoản tiết kiệm hàng tháng\n"
                    f"• Chọn iPower (linh hoạt) + iFund (tăng trưởng)\n\n"
                    + micro_cta(event=gname.lower().replace(" ", "_") if gname else None, mood=emotion_label))
            return out(body + retention_hook(emotion_label), products=["ipower", "ifund"],
                       qr=[f"Tính tiết kiệm cho {gname}", "Tôi cần bao nhiêu mỗi tháng?", "Xem sản phẩm phù hợp", "Tôi muốn mục tiêu khác"])
        return out(
            "Mục tiêu rõ ràng giúp tiết kiệm hiệu quả hơn **3 lần** so với không có mục tiêu. 🎯\n\n"
            "**Mục tiêu lớn nhất của bạn trong 3–5 năm tới?** Mua xe? Mua nhà? Du lịch? Tự do tài chính?\n\n"
            "Kể Cừu nghe — Cừu sẽ tính toán cụ thể giúp bạn nhé!" + retention_hook(emotion_label),
            qr=["Mua xe", "Mua nhà", "Du lịch nước ngoài", "Tự do tài chính"]
        )

    # ── FALLBACK — dùng Second Brain context ─────────────
    # Nếu có mood trend xấu nhiều ngày, ưu tiên đồng cảm
    if mood_trend == "declining":
        return out(
            pick(
                "Cừu để ý bạn có vẻ mệt hơn mấy hôm nay — không cần phải ổn, chỉ cần kể Cừu nghe thôi. 💙",
                "Hôm nay bạn thế nào? Cừu đang để ý và quan tâm đó.",
            ) + retention_hook("negative"),
            qr=["Kể Cừu nghe", "Lập kế hoạch nhỏ", "Tôi muốn thay đổi", "Tôi ổn hơn rồi"]
        )

    if memory["prev_mood"] in ("negative", "very_negative"):
        return out(
            pick(
                "Cừu vẫn ở đây nhé — hôm nay bạn thế nào rồi? 💙",
                "Hôm nay nhẹ hơn hôm qua chút không? Cừu đang nghĩ đến bạn đó.",
            ) + retention_hook("negative"),
            qr=["Kể thêm", "Hôm nay tốt hơn rồi", "Giúp tôi lập kế hoạch", "Tôi muốn tâm sự"]
        )

    return out(
        pick(
            "Cừu đang lắng nghe! 💙\n\nBạn có thể hỏi về sản phẩm, lập mục tiêu, tính toán tiết kiệm — hoặc chỉ tâm sự cũng được.\n\nHôm nay bạn muốn bắt đầu từ đâu?" + retention_hook(emotion_label),
            "Cừu chưa hiểu rõ lắm — bạn có thể nói cụ thể hơn không? 😊\n\nVí dụ: 'Tôi có 500k muốn đầu tư' hay 'Tôi đang stress về tiền' — Cừu sẽ phản hồi phù hợp nhất." + retention_hook(emotion_label),
        ),
        qr=["So sánh sản phẩm TCBS", "Tôi có 500k muốn đầu tư", "Giúp tôi lập mục tiêu", "Tôi muốn tâm sự"]
    )

    # ── Emotion ghi nhớ vào Memory ──
    if emotion_label in ("negative", "positive", "journal"):
        st.session_state.mood_ctx = emotion_label

    # ── Cảm xúc tiêu cực / Tâm sự ──────────────────────
    if emotion_label in ("negative", "journal"):
        openers = [
            "Cừu nghe thấy bạn rồi. Cảm giác đó không nhẹ chút nào — bạn đang gánh nhiều thứ quá. 🤍",
            "Bạn nói ra được như vậy là dũng cảm lắm đó. Cừu ở đây, không đi đâu hết. 💙",
            "Cừu hiểu — đôi khi mọi thứ cứ dồn vào một lúc, không biết bắt đầu từ đâu. 🤍",
        ]
        follows = [
            "\n\nBạn muốn tâm sự thêm không? Cừu lắng nghe hết, không phán xét gì đâu nhé. 😊\n\nHoặc nếu bạn muốn, Cừu có thể giúp bạn **lập một kế hoạch tài chính nhỏ** — đôi khi thấy mọi thứ rõ ràng hơn sẽ nhẹ lòng hơn nhiều. 🌱",
            "\n\nKể Cừu nghe thêm đi — điều gì đang khiến bạn nặng lòng nhất? Cừu muốn thực sự hiểu. 💙",
            "\n\nBạn có muốn **viết nhật ký cảm xúc** cùng Cừu không? Đôi khi viết ra giúp đầu óc nhẹ hơn. 📝",
        ]
        return out(pick(*openers) + pick(*follows),
                   qr=["Tâm sự thêm với Cừu", "Viết nhật ký cảm xúc", "Lập kế hoạch tài chính nhỏ", "Cứ nghe Cừu nói đi"])

    # ── Cảm xúc tích cực ────────────────────────────────
    if emotion_label == "positive":
        return out(pick(
            "Cừu thấy vui lây rồi! 🎉 Ngày tốt xứng đáng được đánh dấu bằng một quyết định tài chính thông minh nữa chứ! 😄\n\nBạn có muốn dùng năng lượng tích cực hôm nay để đặt một mục tiêu mới không?",
            "Ôi, nghe mà Cừu cũng phấn chấn theo! ✨ Khi tâm trạng tốt là lúc suy nghĩ rõ nhất đó bạn.\n\nHôm nay mình có thể làm gì tốt cho tương lai tài chính không? Cừu đề xuất vài ý nhỏ nếu bạn muốn! 🌱",
            "Thật tuyệt! 🌟 Bạn có muốn để Cừu giúp **biến cảm giác tốt này thành hành động cụ thể** — như đặt mục tiêu tiết kiệm hoặc bắt đầu đầu tư? 💪"
        ), qr=["Đặt mục tiêu mới", "Đầu tư thêm hôm nay", "Xem tiến độ tiết kiệm", "Tôi muốn tâm sự"])

    # ── Xử lý theo Intent từ Knowledge Search ───────────
    if intent == "greeting":
        hour = datetime.now().hour
        gr = "Buổi sáng" if hour < 11 else ("Buổi trưa" if hour < 13 else ("Buổi chiều" if hour < 18 else "Buổi tối"))
        return out(pick(
            f"{gr} bạn! ✨ Cừu đây — người bạn đồng hành tài chính của bạn tại TCBS.\n\nCừu không chỉ tư vấn sản phẩm — Cừu muốn **thực sự hiểu bạn**: mục tiêu, cảm xúc, hoàn cảnh.\n\nHôm nay bạn đang cảm thấy thế nào? 😊",
            f"{gr} bạn thân mến! 🌸 Cừu đang ở đây, sẵn sàng lắng nghe và đồng hành.\n\nBạn có thể tâm sự tự do — về tiền bạc, về cảm xúc, về mục tiêu tương lai.\n\nHôm nay Cừu có thể giúp gì cho bạn? 💙"
        ), qr=["Tôi đang stress về tiền", "Muốn bắt đầu đầu tư", "Có bao nhiêu thì đủ?", "Giúp tôi lập mục tiêu"])

    if intent == "journal":
        return out(
            "Cừu rất vui khi bạn muốn tâm sự! 📝 Đây là không gian an toàn — chỉ có Cừu và bạn thôi.\n\n"
            "Hôm nay bạn đang cảm thấy thế nào? Có thể bắt đầu bằng một câu ngắn thôi:\n\n"
            "**\"Hôm nay tôi cảm thấy...\"** hoặc **\"Điều tôi đang lo là...\"**\n\nCừu sẽ lắng nghe và phản hồi từ trái tim. 💙",
            qr=["Tôi đang lo về tài chính", "Tôi muốn thay đổi thói quen", "Tôi cần lời khuyên", "Kể Cừu nghe về ngày hôm nay"]
        )

    if intent == "amount" and amount:
        if amount <= 200_000:
            yearly = amount * 365
            return out(pick(
                f"**{fmtm(amount)}** — và bạn muốn nó sinh ra tiền. Cừu thích tư duy này lắm! ✨\n\n🌱 **iPower** hoàn toàn phù hợp: tối thiểu chỉ **50.000đ**, lãi cộng dồn hằng ngày, rút tiền bất kỳ lúc.\n\nĐể dành {fmtm(amount)}/ngày → tích lũy được **{fmtm(yearly)}** sau 1 năm (chưa tính lãi ~5–6%). 🌱\n\nCừu hướng dẫn cách bắt đầu nhé?",
                f"Với **{fmtm(amount)}**, bạn đã có đủ để bắt đầu rồi! 🎉\n\n🌱 **iPower** là lựa chọn số 1 cho người mới:\n• Tối thiểu: 50.000đ\n• Lãi: ~5–6%/năm, cộng dồn mỗi ngày\n• Rút tiền: bất kỳ lúc nào, không phạt\n\nTiết kiệm đều {fmtm(amount)}/ngày → sau 1 năm có **{fmtm(yearly)}** + lãi! ✨"
            ), products=["ipower"],
               qr=["Cách mở tài khoản TCBS", "Lãi suất iPower bao nhiêu?", "Nạp tiền vào iPower", "Tôi muốn tiết kiệm thêm"])

        if amount <= 5_000_000:
            return out(pick(
                f"**{fmtm(amount)} mỗi tháng** — số tiền hoàn toàn có thể tạo ra tương lai tốt hơn! 💪\n\nCừu gợi ý chia đôi:\n• 50% vào **iPower** — linh hoạt, là quỹ dự phòng\n• 50% vào **iFund** — đầu tư dài hạn, sinh lời tốt hơn\n\nSau 5 năm với {fmtm(amount)}/tháng vào iFund (~12%/năm): ước tính **~{fmtm(int(amount * 12 * 5 * 1.35))}** 🚀\n\nBạn có mục tiêu cụ thể nào không?",
                f"Wow, {fmtm(amount)}/tháng là một con số rất ý nghĩa! ✨\n\nCừu nghĩ bạn nên kết hợp:\n🌱 **iPower** — phần an toàn, rút được khi cần\n📊 **iFund** — phần tăng trưởng, để dài hạn sinh lời\n\nBạn đang có mục tiêu gì — mua nhà, du lịch, hay tự do tài chính?"
            ), products=["ipower", "ifund"],
               qr=["Tính toán chi tiết hơn", "Tôi muốn mua nhà", "Mục tiêu 5 năm", "So sánh iPower và iFund"])

        return out(
            f"**{fmtm(amount)}** — bạn đang nghĩ nghiêm túc về tài chính rồi đó! 💎\n\nCừu gợi ý **đa dạng hóa**:\n• 🌱 **iPower** (~20%) — quỹ dự phòng linh hoạt\n• 📊 **iFund** (~50%) — tăng trưởng dài hạn\n• 📋 **iBond** (~30%) — thu nhập cố định 8–11%/năm\n\nBạn có muốn Cừu phân tích chi tiết hơn không?",
            products=["ipower", "ifund", "ibond"],
            qr=["Phân tích danh mục chi tiết", "Tôi muốn thu nhập cố định", "Mục tiêu hưu trí", "Tìm hiểu iBond"]
        )

    if intent == "compare":
        return out(
            "Cừu so sánh thật sự khách quan cho bạn nhé! 📊\n\n"
            "| | 🌱 iPower | 📊 iFund |\n|---|---|---|\n"
            "| Tối thiểu | 50.000đ | 100.000đ |\n"
            "| Sinh lời | ~5–6%/năm | ~12–18%/năm |\n"
            "| Rủi ro | Thấp | Trung bình |\n"
            "| Rút tiền | Bất kỳ lúc | T+3 |\n"
            "| Phù hợp | Ngắn hạn, dự phòng | Dài hạn 3–10 năm |\n\n"
            "**Gợi ý của Cừu:** Chưa chắc thì bắt đầu iPower. Ổn định rồi phân bổ thêm sang iFund! 🌱",
            products=["ipower", "ifund"],
            qr=["Bắt đầu với iPower", "Tìm hiểu iFund", "Tôi muốn cả hai", "Cần bao nhiêu để bắt đầu?"]
        )

    if intent == "onboarding":
        return out(
            "Chào mừng bạn đến với hành trình đầu tư! 🌱 Cừu đồng hành từng bước.\n\n**3 bước đơn giản để bắt đầu:**\n\n"
            "**1.** Mở tài khoản TCBS miễn phí (3 phút qua TCInvest App)\n\n"
            "**2.** Nạp tiền tối thiểu **50.000đ** (từ bất kỳ ngân hàng nào)\n\n"
            "**3.** Bắt đầu với **iPower** — lãi cộng dồn hằng ngày, rút bất kỳ lúc\n\nBước nào bạn muốn Cừu hướng dẫn?",
            products=["ipower"],
            qr=["Cách mở tài khoản TCBS", "Cách nạp tiền đầu tiên", "iPower hoạt động thế nào?", "Mất bao lâu để thấy lãi?"]
        )

    if intent == "how_to":
        return out(
            "Hướng dẫn nạp tiền vào TCBS — nhanh lắm, chỉ 2 phút! 💰\n\n"
            "**Qua TCInvest App:**\n1. Mở TCInvest App → Tài khoản → Nạp tiền\n"
            "2. Chọn ngân hàng nguồn (hỗ trợ 20+ ngân hàng)\n"
            "3. Nhập số tiền (tối thiểu **50.000đ**) → Xác nhận\n\n"
            "**Qua TCB Mobile:** Đầu tư → Tài khoản CK → Chuyển tiền vào\n\nTiền về ngay lập tức! ✅",
            qr=["Tải TCInvest App ở đâu?", "Tôi dùng ngân hàng khác được không?", "Sau khi nạp làm gì tiếp?", "Hỗ trợ ngân hàng nào?"]
        )

    if intent == "rates":
        return out(
            "Thông tin lãi suất các sản phẩm TCBS: 📋\n\n"
            "🌱 **iPower:** ~5–6%/năm, cộng dồn hàng ngày\n"
            "📊 **iFund/TCEF:** ~12–18%/năm (lịch sử, không đảm bảo)\n"
            "📋 **iBond:** 8–11%/năm cố định theo kỳ hạn\n"
            "🆓 **Cổ phiếu (Zero Fee):** Tiềm năng không giới hạn, rủi ro cao\n"
            "📐 **Margin 789:** Vay từ 7.89%/năm\n\nBạn muốn tìm hiểu sản phẩm nào kỹ hơn?",
            qr=["Chi tiết iPower", "Chi tiết iFund", "Chi tiết iBond", "Tôi muốn lợi nhuận cao nhất"]
        )

    if intent == "bank_compare":
        return out(
            "So sánh TCBS vs Gửi ngân hàng truyền thống: 📊\n\n"
            "**Gửi ngân hàng thường:** ~4–5%/năm, kỳ hạn cố định, rút sớm mất lãi\n\n"
            "**iPower TCBS:** ~5–6%/năm, **không kỳ hạn**, rút bất kỳ lúc nào\n\n"
            "**iBond TCBS:** 8–11%/năm, cố định theo kỳ hạn\n\n"
            "**iFund TCBS:** Tiềm năng 12–18%/năm (biến động theo thị trường)\n\niPower là lựa chọn thông minh hơn gửi tiết kiệm thông thường! 💡",
            products=["ipower", "ibond"],
            qr=["Mở tài khoản iPower ngay", "Tìm hiểu iBond", "Rủi ro của iPower là gì?", "Có bảo hiểm tiền gửi không?"]
        )

    if intent == "ipower":
        return out(
            KB["ipower"]["detail"] + "\n\nCừu tóm tắt: **iPower là lựa chọn zero-risk nhất** để bắt đầu — tiền vẫn sinh lời trong khi bạn học thêm về đầu tư. 💡",
            products=["ipower"],
            qr=["Cách nạp tiền vào iPower", "Lãi suất cụ thể là bao nhiêu?", "So sánh với gửi ngân hàng", "Bước tiếp theo sau iPower?"]
        )

    if intent == "ifund":
        return out(
            KB["ifund"]["detail"] + "\n\n**Chiến lược DCA:** Đầu tư đều mỗi tháng, bất kể thị trường lên hay xuống — đây là cách giảm rủi ro hiệu quả nhất. 📈",
            products=["ifund"],
            qr=["Đầu tư 300k/tháng vào iFund", "Rủi ro thực sự là bao nhiêu?", "iFund vs gửi tiết kiệm", "Bắt đầu ngay"]
        )

    if intent == "ibond":
        return out(
            KB["ibond"]["detail"] + "\n\niBond phù hợp nếu bạn **không thích rủi ro** và muốn biết trước mình sẽ nhận được bao nhiêu. 💡",
            products=["ibond"],
            qr=["Lãi suất iBond hiện tại", "Mua iBond cần bao nhiêu?", "Kỳ hạn nào tốt nhất?", "So sánh iBond và iPower"]
        )

    if intent == "zerofee":
        return out(
            "Cổ phiếu — kênh đầu tư tiềm năng cao nhưng cần kiến thức! 📈\n\n"
            + KB["zerofee"]["detail"] + "\n\nBạn đã có kinh nghiệm giao dịch chưa? Nếu chưa, Cừu gợi ý bắt đầu bằng iFund trước — được quản lý bởi chuyên gia, ít rủi ro hơn. 😊",
            products=["zerofee"],
            qr=["Chưa có kinh nghiệm — bắt đầu thế nào?", "Tôi đã giao dịch rồi", "Muốn dùng margin", "iFund vs tự mua cổ phiếu"]
        )

    if intent == "margin":
        return out(
            "Margin — công cụ mạnh nhưng phải thật cẩn thận nhé bạn! ⚠️\n\n"
            + KB["margin789"]["detail"] + "\n\n**Cừu nhắc nhở:** Margin có thể nhân đôi lãi nhưng cũng nhân đôi lỗ. Chỉ dùng khi bạn thực sự hiểu rõ rủi ro. 💡",
            products=["margin789"],
            qr=["Điều kiện dùng Margin 789", "Rủi ro margin là gì?", "Tôi chưa muốn dùng margin", "Tìm hiểu thêm"]
        )

    if intent == "goal":
        goal = knowledge.get("goal")
        if goal:
            goal_name, goal_range, years = goal
            return out(
                f"Mục tiêu **{goal_name}** — Cừu sẽ đồng hành cùng bạn đến đó! 🎯\n\n"
                f"Thông thường mục tiêu này cần: **{goal_range}** trong **{years}–{years+3} năm**.\n\n"
                f"**Cừu gợi ý:**\n• Đặt mục tiêu số tiền cụ thể\n"
                f"• Chia nhỏ thành khoản tiết kiệm hàng tháng\n"
                f"• Chọn sản phẩm phù hợp: iPower (linh hoạt) + iFund (tăng trưởng)\n\n"
                "Bạn muốn Cừu tính toán cụ thể bao nhiêu tiền/tháng cần không?",
                products=["ipower", "ifund"],
                qr=[f"Tính tiết kiệm cho {goal_name}", "Tôi cần bao nhiêu mỗi tháng?", "Xem sản phẩm phù hợp", "Tôi muốn mục tiêu khác"]
            )
        return out(
            "Đặt mục tiêu tài chính — bước thông minh nhất hôm nay! 🎯\n\n"
            "Mục tiêu rõ ràng giúp bạn tiết kiệm hiệu quả hơn **3 lần** so với không có mục tiêu.\n\n"
            "**Mục tiêu lớn nhất của bạn trong 3–5 năm tới là gì?** Mua xe? Mua nhà? Du lịch? Hưu trí sớm? 😊",
            qr=["Mua xe", "Mua nhà", "Du lịch nước ngoài", "Tự do tài chính"]
        )

    # ── Fallback — dùng mood context từ Memory ──────────
    if memory["prev_mood"] == "negative":
        return out(pick(
            "Cừu vẫn ở đây với bạn nhé. 💙 Bạn không cần phải nói gì nhiều — đôi khi chỉ cần có người nghe là đủ rồi.\n\nBạn muốn Cừu giúp gì không?",
            "Cừu đang lắng nghe bạn đây. 🤍 Mình có thể nói chuyện về bất cứ điều gì — tài chính, cảm xúc, hay đơn giản là tâm sự.\n\nBạn cảm thấy thế nào rồi?"
        ), qr=["Kể thêm về tình trạng của mình", "Giúp tôi lập kế hoạch tài chính", "Tôi muốn thay đổi", "Tôi ổn hơn rồi"])

    return out(pick(
        "Cừu đang lắng nghe bạn đây! 💙\n\nBạn có thể hỏi Cừu về:\n• Sản phẩm đầu tư TCBS (iPower, iFund, iBond, cổ phiếu)\n• Lập kế hoạch tiết kiệm theo mục tiêu\n• Tính toán số tiền cần đầu tư mỗi tháng\n• Hay đơn giản là tâm sự với Cừu 😊\n\nBạn muốn bắt đầu từ đâu?",
        "Cừu chưa hiểu rõ ý bạn — bạn có thể nói cụ thể hơn không? 😊\n\nVí dụ: \"Tôi có 500k muốn đầu tư\" hoặc \"So sánh iPower và iFund\" hoặc đơn giản là chia sẻ cảm xúc hôm nay. 💙",
    ), qr=["So sánh sản phẩm TCBS", "Tôi có 500k muốn đầu tư", "Giúp tôi lập mục tiêu", "Tôi muốn tâm sự"])


# ── STAGE 5 · ORCHESTRATOR ───────────────────────────
def get_resp(text: str) -> dict:
    """Orchestrator: chạy pipeline 4 stage, trả về JSON chuẩn."""
    now = datetime.now().strftime("%H:%M")
    t   = norm(text)
    ctx = " ".join(norm(m["content"]) for m in st.session_state.messages[-6:])

    emotion   = analyze_emotion(t, ctx)                    # Stage 1
    memory    = fetch_memory()                              # Stage 2
    knowledge = search_knowledge(t, ctx, extract_amount(text))  # Stage 3
    result    = generate_response(text, emotion, memory, knowledge)  # Stage 4

    # Cập nhật Second Brain sau khi có đầy đủ context
    update_second_brain(emotion, knowledge, text)

    return {
        "content":    result["content"],
        "time":       now,
        "products":   result.get("products", []),
        "qr":         result.get("qr", QR_DEFAULT),
        "mood_score": result.get("mood_score", emotion["mood_score"]),
    }


# ── process_message — entry point chính ──────────────
def process_message(text: str):
    """
    Entry point chính. Priority order:
      [1] Kết nối cảm xúc
      [2] Nhắc nhở mục tiêu (từ Second Brain)
      [3] Gợi ý hành động nhỏ (Micro-Commitment)
    Output JSON bao gồm mood_score để theo dõi tâm lý KH.
    """
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": text, "time": now})

    resp = get_resp(text)

    st.session_state.messages.append({
        "role":       "ai",
        "content":    resp["content"],
        "time":       resp["time"],
        "products":   resp["products"],
        "mood_score": resp["mood_score"],   # ← trường mới theo dõi tâm lý
    })
    st.session_state.qr         = resp["qr"]
    st.session_state.mood_score = resp["mood_score"]

# ── QR TRIGGER ─────────────────────────────────────────
if st.session_state.qr_trigger:
    process_message(st.session_state.qr_trigger)
    st.session_state.qr_trigger = None
    st.session_state.screen = "chat"
    st.rerun()

# ══════════════════════════════════════════════════════
# UI CONSTANTS
# ══════════════════════════════════════════════════════

LANDSCAPE_SVG = """
<svg viewBox="0 0 900 240" xmlns="http://www.w3.org/2000/svg" class="hero-svg">
  <defs>
    <linearGradient id="sky-g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#B8D4F8"/>
      <stop offset="55%" stop-color="#FFD9B4"/>
      <stop offset="100%" stop-color="#FFBD80"/>
    </linearGradient>
    <linearGradient id="hill-far" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#81C784"/>
      <stop offset="100%" stop-color="#4CAF50"/>
    </linearGradient>
    <linearGradient id="hill-near" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#A5D6A7"/>
      <stop offset="100%" stop-color="#66BB6A"/>
    </linearGradient>
  </defs>
  <rect fill="url(#sky-g)" width="900" height="240"/>
  <circle cx="738" cy="54" r="34" fill="#FFE082" opacity=".6"/>
  <circle cx="738" cy="54" r="23" fill="#FFD54F" opacity=".75"/>
  <g style="animation:float-h 8s ease-in-out infinite">
    <ellipse cx="130" cy="64" rx="58" ry="25" fill="white" opacity=".92"/>
    <ellipse cx="166" cy="54" rx="38" ry="23" fill="white" opacity=".92"/>
    <ellipse cx="95" cy="69" rx="30" ry="18" fill="white" opacity=".92"/>
  </g>
  <g style="animation:float-h 11s ease-in-out infinite reverse">
    <ellipse cx="438" cy="46" rx="50" ry="21" fill="white" opacity=".85"/>
    <ellipse cx="472" cy="38" rx="35" ry="20" fill="white" opacity=".85"/>
    <ellipse cx="406" cy="50" rx="28" ry="16" fill="white" opacity=".85"/>
  </g>
  <g style="animation:float-h 13s ease-in-out infinite">
    <ellipse cx="618" cy="76" rx="34" ry="14" fill="white" opacity=".7"/>
    <ellipse cx="645" cy="69" rx="23" ry="13" fill="white" opacity=".7"/>
  </g>
  <ellipse cx="450" cy="285" rx="560" ry="155" fill="url(#hill-far)" opacity=".65"/>
  <ellipse cx="90" cy="295" rx="230" ry="110" fill="#88D49A" opacity=".55"/>
  <ellipse cx="840" cy="290" rx="210" ry="100" fill="#88D49A" opacity=".55"/>
  <ellipse cx="450" cy="305" rx="580" ry="115" fill="url(#hill-near)"/>
  <path d="M 30 226 Q 180 208 330 216 Q 480 224 630 208 Q 750 198 870 214"
        stroke="rgba(255,255,255,.65)" stroke-width="5" fill="none"
        stroke-dasharray="14,9" stroke-linecap="round"/>
  <g transform="translate(638,148)">
    <rect x="0" y="20" width="46" height="34" fill="#FFCCBC" rx="3"/>
    <polygon points="23,0 -5,22 51,22" fill="#EF9A9A"/>
    <rect x="31" y="-10" width="9" height="15" fill="#BCAAA4"/>
    <rect x="29" y="-13" width="13" height="5" fill="#A1887F" rx="1.5"/>
    <rect x="18" y="32" width="10" height="22" fill="#BCAAA4" rx="3"/>
    <rect x="3" y="26" width="11" height="11" fill="#B3E5FC" rx="2"/>
    <line x1="5" y1="28" x2="5" y2="35" stroke="white" stroke-width="1.5" opacity=".7"/>
    <rect x="32" y="26" width="11" height="11" fill="#B3E5FC" rx="2"/>
    <line x1="34" y1="28" x2="34" y2="35" stroke="white" stroke-width="1.5" opacity=".7"/>
    <path d="M35.5,-14 Q38,-22 35,-30 Q32,-38 35,-46"
          stroke="#BDBDBD" stroke-width="2.5" fill="none" opacity=".65" stroke-linecap="round"/>
  </g>
  <g transform="translate(175,174)">
    <rect x="6" y="24" width="8" height="18" fill="#8D6E63"/>
    <ellipse cx="10" cy="20" rx="16" ry="24" fill="#66BB6A" opacity=".9"/>
    <ellipse cx="10" cy="12" rx="11" ry="16" fill="#81C784"/>
  </g>
  <g transform="translate(748,180)">
    <rect x="5" y="20" width="7" height="16" fill="#8D6E63"/>
    <ellipse cx="8" cy="16" rx="14" ry="20" fill="#66BB6A" opacity=".9"/>
    <ellipse cx="8" cy="9" rx="10" ry="14" fill="#81C784"/>
  </g>
  <circle cx="74" cy="224" r="7" fill="#F8BBD9" opacity=".9"/>
  <circle cx="74" cy="224" r="3.5" fill="#FFE082"/>
  <circle cx="99" cy="231" r="6" fill="#CE93D8" opacity=".8"/>
  <circle cx="99" cy="231" r="3" fill="#FFE082"/>
  <circle cx="51" cy="233" r="5" fill="#80DEEA" opacity=".8"/>
  <circle cx="51" cy="233" r="2.5" fill="#FFE082"/>
  <circle cx="820" cy="227" r="7" fill="#F8BBD9" opacity=".9"/>
  <circle cx="820" cy="227" r="3.5" fill="#FFE082"/>
  <circle cx="845" cy="234" r="6" fill="#CE93D8" opacity=".8"/>
  <circle cx="845" cy="234" r="3" fill="#FFE082"/>
  <g transform="translate(268,210)">
    <ellipse cx="0" cy="0" rx="12" ry="10" fill="white" opacity=".95"/>
    <ellipse cx="0" cy="-8" rx="9" ry="8" fill="white" opacity=".95"/>
    <circle cx="-3" cy="-12" r="3" fill="#6D4C41"/>
    <circle cx="3" cy="-12" r="3" fill="#6D4C41"/>
    <circle cx="-4" cy="2" r="2" fill="#6D4C41"/>
    <circle cx="4" cy="2" r="2" fill="#6D4C41"/>
  </g>
</svg>
"""

EMOTIONS = [
    ("😊", "Bình yên"),
    ("😌", "Ổn hơn hôm qua"),
    ("🥲", "Hơi mệt"),
    ("😣", "Căng thẳng"),
    ("😭", "Buồn"),
    ("😍", "Rất vui"),
]

EMOTION_SHEEP = {
    "😊": "happy", "😌": "calm", "🥲": "concerned",
    "😣": "worried", "😭": "sad", "😍": "excited",
}

SHEEP_EMOJI = {
    "happy": "😊", "excited": "🤩", "calm": "😌",
    "concerned": "🥺", "worried": "😟", "sad": "😢",
    "listening": "👂",
}

SHEEP_BUBBLE = {
    "happy":     "Cừu vui vì bạn vui! 😊",
    "excited":   "Tin vui rồi! Kể Cừu nghe đi! ✨",
    "calm":      "Hôm nay bạn thế nào rồi? 🌸",
    "concerned": "Cừu đang ở đây với bạn nhé 🥺",
    "worried":   "Cừu hiểu cảm giác đó 😟",
    "sad":       "Cừu hiểu... Mình ở đây nha 💙",
    "listening": "Bạn muốn tâm sự gì hôm nay? 💬",
}


def detect_sheep_from_message(text: str) -> str:
    """Phát hiện trạng thái cừu từ nội dung tin nhắn người dùng."""
    t = norm(text)
    if any(w in t for w in ["vui", "thuong", "tang luong", "tot", "cam on", "tuyet", "hanh phuc"]):
        return "happy"
    if any(w in t for w in ["met", "ap luc", "stress", "kho"]):
        return "concerned"
    if any(w in t for w in ["buon", "that vong", "te", "chan", "khoc"]):
        return "sad"
    return "listening"


def get_sheep_state() -> str:
    """Lấy trạng thái cừu hiện tại — ưu tiên tin nhắn gần nhất."""
    msgs = st.session_state.messages
    for m in reversed(msgs):
        if m["role"] == "user":
            return detect_sheep_from_message(m["content"])
    return st.session_state.get("sheep_state", "calm")


# ══════════════════════════════════════════════════════
# SCREEN 1 — HOME COMPANION
# ══════════════════════════════════════════════════════
def render_home():
    _sb      = st.session_state.second_brain
    _mood    = st.session_state.mood_score
    _streak  = _sb.get("micro_streak", 0)
    _turns   = max(len(st.session_state.messages) // 2, 0)
    _level   = _turns // 5 + 1
    _xp      = (_turns % 5) * 20
    _goals   = _sb.get("goals", [])
    _events  = _sb.get("events", [])
    _sel     = st.session_state.get("selected_emotion", None)
    _ss      = st.session_state.get("sheep_state", "calm")
    _s_emoji = SHEEP_EMOJI.get(_ss, "🐑")
    _bubble  = SHEEP_BUBBLE.get(_ss, SHEEP_BUBBLE["listening"])

    col_sb, col_ctr, col_rp = st.columns([1.0, 2.3, 1.7])

    # ── LEFT SIDEBAR ──────────────────────────────────
    with col_sb:
        st.markdown(f"""
<div class="sidebar">
  <div class="sb-mascot-wrap">
    <img src="{MASCOT_SRC}" class="sb-mascot" alt="Cừu Cần Cù">
    <div class="sb-name">Cừu Cần Cù</div>
    <div class="sb-sub">Người bạn đồng hành tài chính</div>
  </div>
  <div class="sb-nav">
    <div class="sb-item active">🏠 Trang chủ</div>
    <div class="sb-item">💬 Trò chuyện với Cừu</div>
    <div class="sb-item">⭐ Ước mơ của bạn</div>
    <div class="sb-item">📖 Ký niệm nhỏ</div>
    <div class="sb-item">🌸 Khoảnh khắc hôm nay</div>
    <div class="sb-item">❤️ Thư viện động lực</div>
    <div class="sb-item">⚙️ Cài đặt</div>
  </div>
  <div class="sb-streak">
    <span class="sb-streak-icon">🔥</span>
    Bạn đã ghé thăm Cừu <strong>{max(_streak, 3)} ngày</strong> liên tiếp rồi đó 💜
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CENTER CONTENT ────────────────────────────────
    with col_ctr:
        # Pastoral hero landscape + floating sheep
        _g_pct  = min(_streak * 5 + 5, 20)  # path progress %
        _g_steps = max(842 - _turns * 20, 50)
        st.markdown(f"""
<div class="hero-outer">
  <div class="hero-wrap">{LANDSCAPE_SVG}</div>
  <div class="hero-sheep-float">
    <div style="position:relative;display:inline-block">
      <img src="{MASCOT_SRC}" class="hero-sheep-img" alt="Cừu">
      <span class="hero-sheep-state">{_s_emoji}</span>
    </div>
    <div class="hero-bubble">{_bubble}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Dream card — walking path progress
        st.markdown(f"""
<div class="dream-card">
  <div class="dc-title">
    🏠 Mua căn nhà đầu tiên
    <span class="dc-house">🏡</span>
  </div>
  <div class="dc-text">
    Hôm nay bạn đã tiến gần hơn một chút đến căn nhà mơ ước.<br>
    Cừu thấy bạn vẫn đang cố gắng mỗi ngày.<br>
    <em>Bạn không cần giàu ngay hôm nay. Chỉ cần tiến thêm một bước nhỏ.</em>
  </div>
  <div class="dc-path-wrap">
    <div class="dc-path-fill" style="width:{_g_pct}%">🐑</div>
  </div>
  <div class="dc-steps">Còn {_g_steps} bước nhỏ nữa 🌱</div>
</div>
""", unsafe_allow_html=True)

        # Memory card — diary style
        _mem1 = "Bạn đang cố gắng tiết kiệm để có một nơi thuộc về riêng mình."
        _mem2 = f"Tháng này bạn đã từ chối {max(_streak, 3)} lần mua sắm bốc đồng."
        _mem3 = _events[-1] if _events else "Bạn đang cố gắng cân bằng giữa công việc và tương lai."
        st.markdown(f"""
<div class="memory-card">
  <div class="mc-title">🌱 Điều Cừu vẫn nhớ về bạn</div>
  <div class="mc-item">🌸 {_mem1}</div>
  <div class="mc-item">✨ {_mem2}</div>
  <div class="mc-item">💙 {_mem3}</div>
</div>
""", unsafe_allow_html=True)

        # Daily message card
        _tip = DAILY_TIPS[datetime.now().weekday() % len(DAILY_TIPS)]
        st.markdown(f"""
<div class="daily-msg">
  <div class="dm-title">☀️ Lời nhắn hôm nay từ Cừu</div>
  <div class="dm-text">
    Hôm nay có thể vẫn nhiều áp lực.<br>
    Nhưng bạn đang làm tốt hơn bạn nghĩ.<br>
    Mỗi quyết định nhỏ đều đang xây nên căn nhà tương lai. 🏡
  </div>
</div>
""", unsafe_allow_html=True)

        # Chat preview card
        st.markdown(f"""
<div class="chat-preview">
  <div class="cp-title">💬 Trò chuyện với Cừu</div>
  <div class="cp-row">
    <img src="{MASCOT_SRC}" class="cp-av" alt="Cừu">
    <div class="cp-bubble-ai">Chào bạn 🌤️<br>Hôm nay công việc có khiến bạn mệt không?</div>
  </div>
  <div class="cp-row right">
    <div class="cp-av" style="background:#FCE4EC;display:flex;align-items:center;justify-content:center;font-size:14px;border:1.5px solid #E8E4FF">👤</div>
    <div class="cp-bubble-user">Mình hơi áp lực vì chi tiêu tháng này.</div>
  </div>
  <div class="cp-row">
    <img src="{MASCOT_SRC}" class="cp-av" alt="Cừu">
    <div class="cp-bubble-ai">
      Mình hiểu cảm giác đó. 💙<br>
      Mình thấy bạn vẫn đang cố gắng rất nhiều.<br>
      <em>Bạn muốn kể mình nghe chuyện gì đang làm bạn lo nhất không?</em>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # CTA — navigate to chat screen
        st.markdown('<div class="start-btn" style="margin-top:12px">', unsafe_allow_html=True)
        if st.button("💬  Bắt đầu trò chuyện với Cừu", key="home_start", use_container_width=True):
            st.session_state.screen = "chat"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT PANEL ───────────────────────────────────
    with col_rp:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)

        # 1. Emotion chips
        st.markdown('<div class="rp-section"><div class="rp-title">🌈 Tâm trạng hôm nay</div>', unsafe_allow_html=True)
        st.markdown('<div class="emotion-zone">', unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        for i, (emoji, label) in enumerate(EMOTIONS):
            col = ec1 if i % 2 == 0 else ec2
            is_sel = _sel == emoji
            with col:
                st.markdown(f'<div class="{"em-sel" if is_sel else ""}">', unsafe_allow_html=True)
                if st.button(f"{emoji} {label}", key=f"em_{i}"):
                    st.session_state.selected_emotion = emoji
                    st.session_state.sheep_state = EMOTION_SHEEP.get(emoji, "calm")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        # 2. Worry topics
        st.markdown("""
<div class="rp-section">
  <div class="rp-title">🧸 Điều đang làm bạn lo</div>
  <span class="worry-chip">💼 Công việc</span>
  <span class="worry-chip">💰 Tiền bạc</span>
  <span class="worry-chip">👨‍👩‍👧 Gia đình</span>
  <span class="worry-chip">📚 Học tập</span>
  <span class="worry-chip">🔮 Tương lai</span>
</div>
""", unsafe_allow_html=True)

        # 3. Dream goals
        st.markdown("""
<div class="rp-section">
  <div class="rp-title">⭐ Điều bạn mong chờ</div>
  <div class="dream-goal">🏠 Nhà riêng</div>
  <div class="dream-goal">🚗 Chiếc xe đầu tiên</div>
  <div class="dream-goal">✈️ Chuyến đi mơ ước</div>
  <div class="dream-goal">🎓 Học thêm kỹ năng mới</div>
</div>
""", unsafe_allow_html=True)

        # 4. Daily achievements
        st.markdown("""
<div class="rp-section">
  <div class="rp-title">🌼 Điều đáng tự hào hôm nay</div>
  <div class="achievement"><span class="ach-check">✓</span> Không đặt đồ ăn khuya</div>
  <div class="achievement"><span class="ach-check">✓</span> Dành 20.000đ cho tương lai</div>
  <div class="achievement"><span class="ach-check">✓</span> Hoàn thành một ngày làm việc khó khăn</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close .right-panel


# ══════════════════════════════════════════════════════
# SCREEN 2 — FULL CHAT EXPERIENCE
# ══════════════════════════════════════════════════════
def render_chat():
    _ss      = get_sheep_state()
    _s_emoji = SHEEP_EMOJI.get(_ss, "👂")
    _qr_list = st.session_state.qr

    # Centered layout: narrow margins + wide chat column
    _, col_chat, _ = st.columns([0.6, 3.8, 0.6])

    with col_chat:
        # Header bar — back button + sheep info
        hdr_back, hdr_info = st.columns([0.12, 0.88])
        with hdr_back:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("◀", key="back_home"):
                st.session_state.screen = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with hdr_info:
            st.markdown(f"""
<div class="chat-top-bar" style="margin-bottom:0;box-shadow:none;background:transparent;padding:6px 0">
  <img src="{MASCOT_SRC}" class="chat-sheep-av" alt="Cừu">
  <div>
    <div class="chat-name">Cừu Cần Cù</div>
    <div class="chat-status"><span class="status-dot"></span> Đang lắng nghe bạn</div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:1px solid #F0EBE3;margin:6px 0 12px">', unsafe_allow_html=True)

        # Sheep hero — reacts emotionally to messages
        st.markdown(f"""
<div class="chat-sheep-hero-wrap">
  <div class="chat-sheep-hero-circle">
    <img src="{MASCOT_SRC}" class="chat-sheep-hero-img" alt="Cừu">
  </div>
  <span class="chat-sheep-emotion-badge">{_s_emoji}</span>
</div>
""", unsafe_allow_html=True)

        # Chat messages
        components.html(build_chat_html(st.session_state.messages), height=460, scrolling=False)

        # Quick replies — 2×2 grid
        st.markdown('<div class="qr-zone">', unsafe_allow_html=True)
        if _qr_list:
            r1c1, r1c2 = st.columns(2)
            for i, txt in enumerate(_qr_list[:4]):
                col = r1c1 if i % 2 == 0 else r1c2
                with col:
                    if st.button(txt, key=f"qr_{i}_{txt[:6]}"):
                        st.session_state.qr_trigger = txt
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat input — spans full page width (Streamlit default)
    user_input = st.chat_input("Hôm nay bạn muốn tâm sự điều gì với Cừu? 🌸", key="cin")
    if user_input:
        process_message(user_input)
        st.session_state.sheep_state = detect_sheep_from_message(user_input)
        st.rerun()

    st.markdown(
        '<div class="disclaimer">🛡️ Cừu Cần Cù cung cấp thông tin tham khảo, không phải lời khuyên đầu tư. 💙</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════
# SCREEN ROUTER
# ══════════════════════════════════════════════════════
_screen = st.session_state.get("screen", "home")
if _screen == "home":
    render_home()
else:
    render_chat()
