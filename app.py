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

# ── MASCOT IMAGE — base64 embed (hoạt động local + Streamlit Cloud) ──
def _load_mascot() -> str:
    for path in ["mascot.png", os.path.join(os.path.dirname(__file__), "mascot.png")]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{b64}"
    return ""  # fallback: no image

MASCOT_SRC = _load_mascot()

# ── PAGE CONFIG ──────────────────────────────────────
st.set_page_config(
    page_title="Cừu Cần Cù — AI Financial Companion",
    page_icon="🐏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL CSS (layout, sidebar, widgets) ────────────
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
.sheep-img{width:120px;height:120px;object-fit:contain;display:block;margin:0 auto 8px}
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

# ── CSS nhúng vào iframe chat (components.html) ──────
CHAT_CSS = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:transparent;padding:8px 2px 4px;
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

# ── KB ────────────────────────────────────────────────
KB = {
    "ipower":    {"name":"iPower",        "min":50_000,   "ret":"Linh hoạt",    "liq":"Rút bất kỳ lúc","emoji":"🌱","desc":"Tích lũy linh hoạt, không kỳ hạn, lãi cộng dồn hằng ngày."},
    "ifund":     {"name":"iFund / TCEF",  "min":100_000,  "ret":"~12–18%/năm",  "liq":"T+3",           "emoji":"📊","desc":"Quỹ cổ phiếu đa dạng hóa, phù hợp tích lũy 5–10 năm."},
    "ibond":     {"name":"iBond",         "min":1_000_000,"ret":"Cố định",       "liq":"Theo kỳ hạn",   "emoji":"📋","desc":"Trái phiếu DN, lãi suất cố định, rủi ro thấp."},
    "zerofee":   {"name":"Zero Fee",      "min":0,        "ret":"Tiềm năng cao", "liq":"T+2",           "emoji":"🆓","desc":"Giao dịch cổ phiếu miễn phí hoàn toàn từ 01/01/2023."},
    "margin789": {"name":"Margin 789",    "min":0,        "ret":"Vay 7.89%/năm","liq":"Theo hợp đồng", "emoji":"📐","desc":"Lãi suất margin 7.89%/năm cho lần đầu dùng."},
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

QR_DEFAULT = ["So sánh iPower và iFund","Đầu tư với 200k/tháng","Mục tiêu dài hạn","Tôi là người mới"]

# ── SESSION STATE ─────────────────────────────────────
for k, v in [("messages",[]),("qr",QR_DEFAULT),("qr_trigger",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ───────────────────────────────────────────
def norm(text: str) -> str:
    t = text.lower()
    for s,d in [("đ","d"),("á","a"),("à","a"),("ả","a"),("ã","a"),("ạ","a"),
                ("ă","a"),("ắ","a"),("ằ","a"),("ặ","a"),("â","a"),("ấ","a"),("ầ","a"),("ậ","a"),
                ("é","e"),("è","e"),("ẻ","e"),("ẹ","e"),("ê","e"),("ế","e"),("ề","e"),("ệ","e"),
                ("í","i"),("ì","i"),("ị","i"),("ó","o"),("ò","o"),("ọ","o"),
                ("ô","o"),("ố","o"),("ồ","o"),("ộ","o"),("ơ","o"),("ớ","o"),("ờ","o"),("ợ","o"),
                ("ú","u"),("ù","u"),("ụ","u"),("ư","u"),("ứ","u"),("ừ","u"),("ự","u"),
                ("ý","y"),("ỳ","y"),("ỵ","y")]:
        t = t.replace(s,d)
    return t

def extract_amount(text: str):
    t = norm(text)
    m = re.search(r'(\d[\d.,]*)[\s]*(k|tr|trieu|nghin)', t) or re.search(r'(\d{3,})', t)
    if not m: return None
    raw = float(m.group(1).replace(",","").replace(".",""))
    unit = m.group(2) if m.lastindex and m.lastindex >= 2 else ""
    if unit in ("k","nghin"): raw *= 1000
    elif unit in ("tr","trieu"): raw *= 1_000_000
    if 1000 <= raw <= 9999: raw *= 1000
    return int(raw)

def fmtm(n: int) -> str:
    if n >= 1_000_000:
        v = n/1_000_000
        return f"{v:.0f} triệu đ" if v == int(v) else f"{v:.1f} triệu đ"
    if n >= 1000: return f"{n//1000}.000đ"
    return f"{n}đ"

def md_to_html(text: str) -> str:
    """Convert response text to safe HTML — dùng <p> thay <br> để tránh Streamlit parse lỗi."""
    # Escape HTML entities trước
    text = html_lib.escape(text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Paragraphs: split by \n\n
    paras = text.split("\n\n")
    result = []
    for para in paras:
        lines = para.split("\n")
        result.append("<p>" + "<br>".join(lines) + "</p>")
    return "".join(result)

def card_html(pid: str) -> str:
    p = KB.get(pid)
    if not p: return ""
    min_row = (f'<div class="p-row"><span class="p-lbl">Tối thiểu</span>'
               f'<span class="p-val p-red">{fmtm(p["min"])}</span></div>') if p["min"] else ""
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
    """Build self-contained HTML cho iframe — không dùng st.markdown."""
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
            av_inner = (f'<img src="{MASCOT_SRC}" style="width:36px;height:36px;object-fit:cover;border-radius:50%">'
                        if MASCOT_SRC else "🐏")
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
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">{CHAT_CSS}</head>
<body>
<div id="chat">{body}</div>
<script>window.onload=()=>{{var c=document.getElementById('chat');c.scrollTop=c.scrollHeight;}}</script>
</body></html>"""

# ── AI ENGINE ─────────────────────────────────────────
def get_resp(text: str) -> dict:
    t = norm(text)
    amount = extract_amount(text)
    now = datetime.now().strftime("%H:%M")

    def r(content, products=None, qr=None):
        return {"content":content,"time":now,"products":products or [],"qr":qr or QR_DEFAULT}

    if re.search(r"buon|stress|met|chan|lo lang|ap luc|so hai|that vong|tuyet vong", t):
        return r(
            "Cừu nghe thấy bạn rồi — áp lực kiểu đó nặng lắm, không ai muốn gánh một mình. 🤍\n\n"
            "Bạn không cần giải quyết hết ngay hôm nay. Đôi khi **một bước nhỏ** là đủ để cảm thấy nhẹ hơn.\n\n"
            "Điều gì đang khiến bạn lo nhất lúc này?",
            qr=["Áp lực tài chính","Áp lực công việc","Cứ nghe Cừu nói đi"]
        )

    if re.search(r"vui|hanh phuc|tu hao|phan khich|tuyet voi|hom nay tot|ok roi|on roi", t):
        return r(
            "Cừu thấy vui lây rồi! 🎉 Ngày tốt xứng đáng được kỷ niệm!\n\nKể Cừu nghe có gì vui không? 😊",
            qr=["Kể chuyện vui","Tiết kiệm để ăn mừng","Tạo mục tiêu mới"]
        )

    if amount and amount <= 100_000:
        yearly = amount * 365
        return r(
            f"**{fmtm(amount)}** — và bạn muốn nó sinh ra tiền. Cừu thích tư duy này lắm! ✨\n\n"
            f"🌱 **iPower** là lựa chọn hoàn hảo — tối thiểu chỉ **50.000đ**, rút bất kỳ lúc nào.\n\n"
            f"Để dành {fmtm(amount)}/ngày → **{fmtm(yearly)}** sau 1 năm (chưa tính lãi!).\n\n"
            "Cừu hướng dẫn cách nạp tiền nhé! 👇",
            products=["ipower"],
            qr=["Cách nạp tiền vào TCBS","Lãi suất iPower bao nhiêu?","Lập mục tiêu tiết kiệm"]
        )

    if amount and 200_000 <= amount <= 2_000_000:
        return r(
            f"Với **{fmtm(amount)} mỗi tháng**, Cừu gợi ý bắt đầu với iPower hoặc iFund nhé!\n\n"
            f"🌱 **iPower:** Linh hoạt, sinh lời ổn định, rút tiền dễ dàng.\n\n"
            f"📊 **iFund:** Phù hợp mục tiêu dài hạn, lợi nhuận tốt hơn theo thời gian.\n\n"
            "Bạn muốn Cừu so sánh chi tiết hơn không? 😊",
            products=["ipower","ifund"],
            qr=["So sánh iPower và iFund","Đầu tư với 200k/tháng","Mục tiêu dài hạn","Tôi là người mới"]
        )

    if re.search(r"so sanh|ipower.*ifund|ifund.*ipower|quy dau tu", t):
        return r(
            "Cừu so sánh giúp bạn nhé! 📊\n\n"
            "🌱 **iPower** — Tối thiểu 50k · Rút bất kỳ lúc · Rủi ro thấp · Ngắn–trung hạn\n\n"
            "📊 **iFund** — Tối thiểu 100k · T+3 · Trung bình · Dài hạn 5–10 năm\n\n"
            "**Gợi ý của Cừu:** Chưa chắc thì bắt đầu iPower. Quen rồi phân bổ thêm vào iFund! 🌱",
            products=["ipower","ifund"],
            qr=["Bắt đầu với iPower","Tìm hiểu iFund","Cần bao nhiêu để bắt đầu?"]
        )

    if re.search(r"muc tieu|tiet kiem|mua xe|mua nha|du lich|ke hoach|gom tien", t):
        return r(
            "Đặt mục tiêu tài chính — bước thông minh nhất hôm nay! 🎯\n\n"
            "Cừu giúp bạn tính:\n"
            "- Cần tiết kiệm bao nhiêu **mỗi tháng**?\n"
            "- **Sản phẩm nào** phù hợp nhất?\n"
            "- Theo dõi tiến độ **mỗi ngày**.\n\n"
            "Mục tiêu của bạn là gì? 😊",
            qr=["Mua xe","Du lịch nước ngoài","Mua nhà","Quỹ dự phòng"]
        )

    if re.search(r"co phieu|chung khoan|stock|zero fee", t):
        return r(
            "Cổ phiếu — kênh đầu tư tiềm năng cao! 📈\n\n"
            "TCBS có **Zero Fee** — giao dịch cổ phiếu **miễn phí hoàn toàn** từ 01/01/2023.\n\n"
            "Bạn đã có kinh nghiệm giao dịch chưa?",
            products=["zerofee"],
            qr=["Chưa có kinh nghiệm","Đã giao dịch rồi","Muốn dùng margin"]
        )

    if re.search(r"moi bat dau|nguoi moi|chua biet|lan dau|newbie|moi\b", t):
        return r(
            "Chào mừng bạn đến với hành trình đầu tư! 🌱 Cừu đồng hành từng bước.\n\n"
            "**3 bước đơn giản để bắt đầu:**\n\n"
            "**1.** Mở tài khoản TCBS miễn phí (3 phút · TCInvest App)\n\n"
            "**2.** Nạp tiền tối thiểu **50.000đ**\n\n"
            "**3.** Bắt đầu với **iPower** — an toàn, linh hoạt, không kỳ hạn\n\n"
            "Bạn muốn Cừu hướng dẫn bước nào?",
            products=["ipower"],
            qr=["Cách mở tài khoản TCBS","Cách nạp tiền","Lãi suất iPower là bao nhiêu?"]
        )

    if re.search(r"nap tien|chuyen tien|deposit|nap vao", t):
        return r(
            "Nạp tiền vào TCBS — 3 bước, dưới 2 phút! 💰\n\n"
            "**Qua TCInvest App:**\n"
            "1. Mở TCInvest App → Tài khoản → Nạp tiền\n"
            "2. Chọn ngân hàng nguồn (20+ ngân hàng)\n"
            "3. Nhập số tiền (tối thiểu **50.000đ**) → Xác nhận\n\n"
            "**Qua TCB Mobile:** Đầu tư → Tài khoản CK → Chuyển tiền vào",
            qr=["Mở TCInvest App","Tôi dùng TCB Mobile","Hỗ trợ ngân hàng nào?"]
        )

    if re.search(r"margin|vay|ky quy", t):
        return r(
            "Vay ký quỹ tăng sức mua — nhưng cũng tăng rủi ro. Hãy hiểu rõ trước khi quyết định. 💡\n\n"
            "- **Lần đầu:** Margin 789 — lãi suất ưu đãi **7.89%/năm**\n"
            "- **Đã có KN:** Margin T+ — lãi từ **0%/năm**",
            products=["margin789"],
            qr=["Margin 789 là gì?","Điều kiện dùng margin","Không dùng margin"]
        )

    if re.search(r"chao|hello|hi\b|xin chao|bat dau|oi cuuu|oi cuu", t):
        return r(
            "Chào bạn thân mến! Cừu đây — người bạn đồng hành tài chính AI tại TCBS! ✨\n\n"
            "Cừu muốn **thực sự hiểu** và đồng hành trên hành trình tài chính của bạn.\n\n"
            "Hôm nay bạn đang cảm thấy thế nào?",
            qr=["Tôi đang khá stress","Ngày hôm nay ổn","Tôi có 500k/tháng muốn đầu tư","Giúp tôi lập mục tiêu"]
        )

    return r(
        "Cừu đang lắng nghe bạn đây. 💙\n\n"
        "Để tư vấn chính xác nhất, bạn cho Cừu biết:\n"
        "- Số tiền muốn đầu tư?\n"
        "- Mục tiêu tài chính của bạn?\n"
        "- Thời gian đầu tư ngắn hay dài hạn?",
        qr=QR_DEFAULT
    )

def process(text: str):
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role":"user","content":text,"time":now})
    resp = get_resp(text)
    st.session_state.messages.append({"role":"ai","content":resp["content"],
                                       "time":resp["time"],"products":resp["products"]})
    st.session_state.qr = resp["qr"]

# ── QR TRIGGER (trước render) ─────────────────────────
if st.session_state.qr_trigger:
    process(st.session_state.qr_trigger)
    st.session_state.qr_trigger = None
    st.rerun()

# ── LAYOUT ───────────────────────────────────────────
col_left, col_main = st.columns([1.05, 4.5])

# ═══ LEFT PANEL ═══
nav_items = [
    ("💬","Chat cùng Cừu",True),
    ("🔍","Tìm sản phẩm",False),
    ("🎯","Kế hoạch tiết kiệm",False),
    ("❤️","Nhật ký cảm xúc",False),
    ("🕐","Lịch sử hội thoại",False),
    ("⚙️","Cài đặt",False),
]
nav_html = "".join(
    f'<div class="nav-item {"active" if a else ""}"><span class="nav-icon">{ic}</span>{lb}</div>'
    for ic,lb,a in nav_items
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
    # Welcome banner
    tip = DAILY_TIPS[datetime.now().weekday() % len(DAILY_TIPS)]
    st.markdown(f"""
<div class="welcome-banner">
  <div class="wb-left">
    <h2>👋 Xin chào!</h2>
    <p>Mình là <strong>Cừu Cần Cù</strong>, người bạn đồng hành tài chính của bạn.</p>
    <p class="wb-red">Cùng Cừu bắt đầu hành trình tích tiểu thành đại nhé!</p>
  </div>
  <div class="tip-yellow">
    <div class="ty-label">💡 Tip của Cừu</div>
    <div class="ty-text">{tip}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CHAT MESSAGES — dùng components.html để tránh Streamlit parse HTML ──
    chat_iframe_html = build_chat_html(st.session_state.messages)
    # Tính chiều cao: mỗi message ~110px + cards, tối thiểu 240px
    n = len(st.session_state.messages)
    estimated_h = max(240, min(n * 120 + 80, 480))
    components.html(chat_iframe_html, height=estimated_h, scrolling=True)

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
