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
/* Ẩn Streamlit chrome */
#MainMenu,footer,header,
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
.stDeployButton{display:none!important}

/* Reset padding */
.block-container{padding:0!important;max-width:100%!important}
.stApp{background:#F5F7FA}

/* === LEFT PANEL === */
.left-panel{
  background:#fff;
  min-height:100vh;
  border-right:1px solid #EEEEEE;
  box-shadow:2px 0 12px rgba(0,0,0,.06);
  display:flex;flex-direction:column;
  padding-bottom:16px;
}
.sheep-header{
  text-align:center;padding:26px 14px 14px;
  border-bottom:1px solid #F5F5F5;
}
.sheep-img{width:200px;height:200px;object-fit:contain;display:block;margin:0 auto 10px}
.sheep-name{font-size:19px;font-weight:800;color:#1A1A2E}
.sheep-sub{font-size:12px;color:#999;margin-top:3px}

.nav-section{padding:12px 10px 6px}
.nav-label{font-size:10px;font-weight:700;color:#BDBDBD;
  text-transform:uppercase;letter-spacing:.9px;padding:0 8px;margin-bottom:4px}
.nav-item{
  display:flex;align-items:center;gap:10px;padding:9px 12px;
  border-radius:11px;font-size:13px;font-weight:500;color:#555;
  cursor:pointer;margin-bottom:2px;text-decoration:none;
}
.nav-item.active{background:#FDE8EA;color:#D0021B;font-weight:700}
.nav-icon{font-size:16px;width:20px;text-align:center}

.tip-green{
  margin:16px 12px 0;
  background:linear-gradient(135deg,#E8F5E9,#F1F8E9);
  border:1px solid #A5D6A7;border-radius:13px;padding:13px 14px;
}
.tip-green-title{font-size:12.5px;font-weight:700;color:#2E7D32;margin-bottom:5px}
.tip-green-text{font-size:11.5px;line-height:1.6;color:#388E3C}

/* === WELCOME BANNER === */
.welcome-banner{
  background:white;border-radius:18px;
  padding:18px 24px;margin-bottom:0;
  box-shadow:0 2px 14px rgba(0,0,0,.07);
  display:flex;align-items:center;justify-content:space-between;gap:18px;
}
.wb-left h2{font-size:21px;font-weight:800;color:#1A1A2E;margin:0 0 5px}
.wb-left p{font-size:13px;color:#555;margin:0 0 3px}
.wb-red{color:#D0021B!important;font-weight:600}
.tip-yellow{
  background:#FFFDE7;border:1.5px solid #FDD835;
  border-radius:13px;padding:12px 15px;
  min-width:190px;max-width:230px;flex-shrink:0;
}
.ty-label{font-size:11px;font-weight:700;color:#F57F17;margin-bottom:5px}
.ty-text{font-size:12px;line-height:1.6;color:#795548}

/* === QR BUTTONS === */
[data-testid="stHorizontalBlock"]{gap:6px!important}
[data-testid="stColumn"]>div{padding:0!important}
div.qr-zone [data-testid="stButton"]>button{
  background:white!important;border:1.5px solid #E0E0E0!important;
  border-radius:20px!important;color:#333!important;
  font-size:12.5px!important;font-weight:500!important;
  padding:6px 14px!important;white-space:nowrap!important;
}
div.qr-zone [data-testid="stButton"]>button:hover{
  background:#D0021B!important;color:white!important;border-color:#D0021B!important;
}

/* chat_input */
[data-testid="stChatInput"]{
  border-radius:16px!important;border:1.5px solid #E0E0E0!important;
  box-shadow:0 2px 14px rgba(0,0,0,.09)!important;background:white!important;
}
[data-testid="stChatInput"] textarea{font-size:14px!important}
[data-testid="stChatInput"] button{
  background:#D0021B!important;border-radius:50%!important;
  width:38px!important;height:38px!important;
  box-shadow:0 3px 9px rgba(208,2,27,.35)!important;
}

.disclaimer{font-size:11px;color:#BDBDBD;text-align:center;padding:4px 0 2px}
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
for k, v in [("messages", []), ("qr", QR_DEFAULT), ("qr_trigger", None), ("mood_ctx", None)]:
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
    # Bullet points
    lines = text.split("\n")
    result_lines = []
    for line in lines:
        if re.match(r"^•\s", line) or re.match(r"^-\s", line) or re.match(r"^\d+\.\s", line):
            result_lines.append(f"<div style='padding-left:8px'>{line}</div>")
        else:
            result_lines.append(line)
    text = "\n".join(result_lines)
    paras = text.split("\n\n")
    result = []
    for para in paras:
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

# ══════════════════════════════════════════════════════
#  AI PIPELINE:  User → Emotion → Memory → Knowledge → LLM → Response
# ══════════════════════════════════════════════════════

# ── STAGE 1 · EMOTION ANALYSIS ───────────────────────
def analyze_emotion(t: str, ctx: str) -> dict:
    """
    Phân tích cảm xúc từ input đã norm.
    Trả về: {label, intensity, mood_shift}
      label     : 'negative' | 'positive' | 'journal' | 'neutral'
      intensity : 0–3  (0=không, 3=rất mạnh)
      mood_shift: True nếu cảm xúc thay đổi so với memory
    """
    neg_kws = ["buon", "stress", "met", "chan", "lo", "lo lang", "ap luc",
               "so hai", "that vong", "tuyet vong", "kho khan", "nan long",
               "that bai", "bi quan", "chiu khong noi", "qua suc", "kiet suc",
               "mo mo", "roi", "co don", "cang thang", "tram cam", "kiet suc",
               "khong on", "khong biet lam sao", "mat ngu"]
    pos_kws = ["vui", "hanh phuc", "tu hao", "phan khich", "tuyet voi",
               "on roi", "tot lam", "hom nay tot", "phan khoi", "sung suong",
               "binh yen", "nhe nhom", "thanh thoi", "on dinh", "tot dep"]
    jrn_kws = ["tam su", "nhat ky", "ke cuuu", "ke cuu", "nghe khong",
               "can ai do", "can chia se", "muon noi", "toi cam thay",
               "minh cam thay", "trong long", "khong biet ke ai"]

    neg = score(t, neg_kws)
    pos = score(t, pos_kws)
    jrn = score(t, jrn_kws)

    prev_mood = st.session_state.get("mood_ctx", "neutral")

    if jrn >= 1:
        label, intensity = "journal", min(jrn, 3)
    elif neg >= pos and neg >= 1:
        label = "negative"
        intensity = min(neg, 3)
    elif pos >= 1:
        label = "positive"
        intensity = min(pos, 3)
    else:
        label = "neutral"
        intensity = 0

    mood_shift = (label != prev_mood) and (label != "neutral")
    return {"label": label, "intensity": intensity, "mood_shift": mood_shift}


# ── STAGE 2 · MEMORY ─────────────────────────────────
def fetch_memory() -> dict:
    """
    Truy xuất context từ session state.
    Trả về: {history_text, prev_mood, turn_count, last_products}
    """
    msgs = st.session_state.messages
    history_text = " ".join(norm(m["content"]) for m in msgs[-6:])
    prev_mood    = st.session_state.get("mood_ctx", "neutral")
    turn_count   = len([m for m in msgs if m["role"] == "user"])
    last_products = []
    for m in reversed(msgs):
        if m["role"] == "ai" and m.get("products"):
            last_products = m["products"]
            break
    return {
        "history_text": history_text,
        "prev_mood":    prev_mood,
        "turn_count":   turn_count,
        "last_products": last_products,
    }


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
    Tổng hợp response từ Emotion + Memory + Knowledge.
    (Rule-based engine — có thể swap bằng GPT/Claude API call tại đây)
    Trả về: {content, products, qr}
    """
    t          = norm(text)
    amount     = extract_amount(text)
    intent     = knowledge["intent"]
    emotion_label = emotion["label"]
    turn       = memory["turn_count"]

    def pick(*opts): return random.choice(opts)
    def out(content, products=None, qr=None):
        return {"content": content, "products": products or [], "qr": qr or QR_DEFAULT}

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
    """
    Pipeline chính:
      User → Emotion Analysis → Memory → Knowledge Search → LLM → Response
    """
    now = datetime.now().strftime("%H:%M")

    # Stage 1 — Emotion Analysis
    t   = norm(text)
    ctx = " ".join(norm(m["content"]) for m in st.session_state.messages[-6:])
    emotion   = analyze_emotion(t, ctx)

    # Stage 2 — Memory
    memory    = fetch_memory()

    # Stage 3 — Knowledge Search
    knowledge = search_knowledge(t, ctx, extract_amount(text))

    # Stage 4 — LLM / Response Generator
    result    = generate_response(text, emotion, memory, knowledge)

    # Stage 5 — Format & return
    return {
        "content":  result["content"],
        "time":     now,
        "products": result.get("products", []),
        "qr":       result.get("qr", QR_DEFAULT),
    }

def process(text: str):
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": text, "time": now})
    resp = get_resp(text)
    st.session_state.messages.append({
        "role": "ai",
        "content": resp["content"],
        "time": resp["time"],
        "products": resp["products"]
    })
    st.session_state.qr = resp["qr"]

# ── QR TRIGGER (trước render) ─────────────────────────
if st.session_state.qr_trigger:
    process(st.session_state.qr_trigger)
    st.session_state.qr_trigger = None
    st.rerun()

# ── LAYOUT ───────────────────────────────────────────
col_left, col_main = st.columns([1.05, 4.5])

# ═══ LEFT PANEL ═══
# Fix #1: "Tìm sản phẩm" đã được xoá khỏi nav
nav_items = [
    ("💬", "Chat cùng Cừu", True),
    ("🎯", "Kế hoạch tiết kiệm", False),
    ("❤️", "Nhật ký cảm xúc", False),
    ("🕐", "Lịch sử hội thoại", False),
    ("⚙️", "Cài đặt", False),
]
nav_html = "".join(
    f'<div class="nav-item {"active" if a else ""}"><span class="nav-icon">{ic}</span>{lb}</div>'
    for ic, lb, a in nav_items
)
with col_left:
    st.markdown(f"""
<div class="left-panel">
  <div class="sheep-header">
    <img src="{MASCOT_SRC}" class="sheep-img" alt="Cừu Cần Cù">
    <div class="sheep-name">Cừu Cần Cù</div>
    <div class="sheep-sub">Người bạn đồng hành tài chính ❤️</div>
  </div>
  <div class="nav-section">
    <div class="nav-label">Tính năng</div>
    {nav_html}
  </div>
  <div class="tip-green">
    <div class="tip-green-title">🌱 Tích tiểu thành đại</div>
    <div class="tip-green-text">Bắt đầu từ những khoản nhỏ mỗi ngày, Cừu sẽ giúp bạn đầu tư thông minh để đạt mục tiêu lớn! 🌱</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══ MAIN PANEL ═══
with col_main:
    # Welcome banner — Fix #6: đổi tagline, không lặp "tích tiểu thành đại"
    tip = DAILY_TIPS[datetime.now().weekday() % len(DAILY_TIPS)]
    st.markdown(f"""
<div class="welcome-banner">
  <div class="wb-left">
    <h2>👋 Xin chào!</h2>
    <p>Mình là <strong>Cừu Cần Cù</strong>, người bạn đồng hành tài chính của bạn.</p>
    <p class="wb-red">Hãy để Cừu đồng hành cùng bạn mỗi ngày — tài chính vững, cuộc sống nhẹ! 💙</p>
  </div>
  <div class="tip-yellow">
    <div class="ty-label">💡 Tip của Cừu</div>
    <div class="ty-text">{tip}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CHAT MESSAGES — Fix #3: chiều cao cố định 460px, scroll-to-bottom qua JS ──
    chat_iframe_html = build_chat_html(st.session_state.messages)
    components.html(chat_iframe_html, height=460, scrolling=False)

    # ── QUICK REPLIES ──
    qr_list = st.session_state.qr
    st.markdown('<div class="qr-zone">', unsafe_allow_html=True)
    if qr_list:
        cols = st.columns(len(qr_list) + 1)
        for i, txt in enumerate(qr_list):
            with cols[i]:
                if st.button(txt, key=f"qr_{i}_{txt[:6]}"):
                    st.session_state.qr_trigger = txt
                    st.rerun()
        with cols[-1]:
            if st.button("🔄", key="qr_reset"):
                st.session_state.qr = QR_DEFAULT
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── CHAT INPUT ──
    user_input = st.chat_input("Nhắn tin cho Cừu...", key="cin")
    if user_input:
        process(user_input)
        st.rerun()

    st.markdown(
        '<div class="disclaimer">🛡️ Cừu Cần Cù cung cấp thông tin, không phải lời khuyên đầu tư. Bạn nên cân nhắc kỹ trước khi ra quyết định.</div>',
        unsafe_allow_html=True
    )
