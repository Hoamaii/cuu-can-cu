"""
Cừu Cần Cù — AI Financial Companion · TCBS
Streamlit Demo  |  streamlit run app.py
"""

import streamlit as st
from datetime import datetime
import re

# ─────────────────────────────────────────────────
# PAGE CONFIG — gọi đầu tiên, trước mọi st.*
# ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Cừu Cần Cù — AI Financial Companion",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────
# CSS — ẩn sidebar mặc định của Streamlit,
#       kiểm soát hoàn toàn layout bằng columns
# ─────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Ẩn toàn bộ Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
.stDeployButton { display: none !important; }

/* ── Reset container padding ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── App background ── */
.stApp { background: #F5F7FA; }

/* ── LEFT PANEL ── */
.left-panel {
    background: #FFFFFF;
    min-height: 100vh;
    border-right: 1px solid #EEEEEE;
    box-shadow: 2px 0 12px rgba(0,0,0,0.06);
    display: flex;
    flex-direction: column;
    padding-bottom: 20px;
}

/* Sheep header */
.sheep-header {
    text-align: center;
    padding: 28px 16px 16px;
    border-bottom: 1px solid #F5F5F5;
}
.sheep-img {
    font-size: 72px;
    line-height: 1;
    display: block;
    margin-bottom: 10px;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15));
}
.sheep-name {
    font-size: 20px;
    font-weight: 800;
    color: #1A1A2E;
    letter-spacing: -.3px;
}
.sheep-sub {
    font-size: 12.5px;
    color: #999;
    margin-top: 3px;
}

/* Nav items */
.nav-section { padding: 14px 12px 6px; }
.nav-label {
    font-size: 10px;
    font-weight: 700;
    color: #BDBDBD;
    text-transform: uppercase;
    letter-spacing: .9px;
    padding: 0 8px;
    margin-bottom: 4px;
}
.nav-item {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 13.5px;
    font-weight: 500;
    color: #555;
    cursor: pointer;
    margin-bottom: 2px;
    transition: all .15s;
    text-decoration: none;
}
.nav-item:hover { background: #FFF0F0; color: #D0021B; }
.nav-item.active {
    background: #FDE8EA;
    color: #D0021B;
    font-weight: 700;
}
.nav-icon { font-size: 17px; width: 22px; text-align: center; }

/* Green tip card */
.tip-green {
    margin: auto 14px 0;
    background: linear-gradient(135deg, #E8F5E9, #F1F8E9);
    border: 1px solid #A5D6A7;
    border-radius: 14px;
    padding: 14px 15px;
    margin-top: 20px;
}
.tip-green-title {
    font-size: 13px;
    font-weight: 700;
    color: #2E7D32;
    margin-bottom: 6px;
}
.tip-green-text {
    font-size: 12px;
    line-height: 1.6;
    color: #388E3C;
}

/* ── RIGHT / MAIN PANEL ── */
.main-panel {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
    padding: 20px 24px;
    gap: 14px;
}

/* Welcome banner */
.welcome-banner {
    background: white;
    border-radius: 20px;
    padding: 20px 26px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-shrink: 0;
}
.wb-left h2 {
    font-size: 22px;
    font-weight: 800;
    color: #1A1A2E;
    margin: 0 0 5px;
}
.wb-left p { font-size: 13.5px; color: #555; margin: 0 0 3px; }
.wb-red { color: #D0021B !important; font-weight: 600; }
.tip-yellow {
    background: #FFFDE7;
    border: 1.5px solid #FDD835;
    border-radius: 14px;
    padding: 13px 17px;
    min-width: 200px;
    max-width: 240px;
    flex-shrink: 0;
}
.ty-label { font-size: 11.5px; font-weight: 700; color: #F57F17; margin-bottom: 5px; }
.ty-text { font-size: 12.5px; line-height: 1.6; color: #795548; }

/* Chat scroll area */
.chat-area {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding-right: 4px;
}
.chat-area::-webkit-scrollbar { width: 4px; }
.chat-area::-webkit-scrollbar-thumb { background: #E0E0E0; border-radius: 2px; }

/* Message rows */
.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
}
.msg-row.user { flex-direction: row-reverse; }

.av-sheep {
    width: 38px; height: 38px; border-radius: 50%;
    background: #FFF0F0;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.av-user {
    width: 36px; height: 36px; border-radius: 50%;
    background: #FCE4EC;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; flex-shrink: 0;
}

.bubble-ai {
    background: white;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    font-size: 14px; line-height: 1.7;
    color: #1A1A2E;
    max-width: 540px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.09);
    border: 1px solid #EEEEEE;
}
.bubble-user {
    background: #FCE4EC;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    font-size: 14px; line-height: 1.7;
    color: #1A1A2E;
    max-width: 420px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.09);
}
.msg-time {
    font-size: 11px; color: #BDBDBD;
    margin-top: 4px; padding: 0 4px;
}
.msg-row.user .msg-time { text-align: right; }

/* Product card */
.p-card {
    background: white;
    border-radius: 14px;
    border: 1px solid #EEEEEE;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    overflow: hidden;
    max-width: 280px;
    margin-top: 6px;
    font-size: 13px;
}
.p-card-header {
    padding: 11px 14px;
    border-bottom: 1px solid #F5F5F5;
    display: flex; align-items: center; gap: 10px;
}
.p-card-body { padding: 10px 14px; display: flex; flex-direction: column; gap: 6px; }
.p-row { display: flex; justify-content: space-between; align-items: center; }
.p-label { color: #9E9E9E; font-size: 12px; }
.p-val { font-weight: 600; font-size: 12.5px; }
.p-green { color: #27AE60; }
.p-red { color: #D0021B; }
.p-desc { font-size: 11.5px; color: #666; background: #F8FAFD; border-radius: 8px; padding: 7px 9px; border: 1px solid #EEF0F5; margin-top: 2px; }
.p-btn {
    background: #D0021B; color: white;
    text-align: center; padding: 10px;
    font-size: 13px; font-weight: 700;
    border-radius: 0 0 14px 14px;
    cursor: pointer;
}

/* Quick replies */
.qr-row { display: flex; flex-wrap: wrap; gap: 8px; flex-shrink: 0; }
.qr-pill {
    background: white;
    border: 1.5px solid #E0E0E0;
    border-radius: 20px;
    padding: 7px 15px;
    font-size: 13px; font-weight: 500; color: #333;
    cursor: pointer; white-space: nowrap;
    transition: all .15s;
}
.qr-pill:hover { background: #D0021B; color: white; border-color: #D0021B; }

/* Disclaimer */
.disclaimer {
    font-size: 11.5px; color: #BDBDBD;
    text-align: center; flex-shrink: 0;
    padding: 2px 0 4px;
}

/* ── Streamlit widget overrides ── */
/* st.chat_input */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
    border: 1.5px solid #E0E0E0 !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.10) !important;
    background: white !important;
    padding: 4px 8px !important;
}
[data-testid="stChatInput"] textarea {
    font-size: 14px !important;
}
[data-testid="stChatInput"] button {
    background: #D0021B !important;
    border-radius: 50% !important;
    width: 40px !important; height: 40px !important;
    box-shadow: 0 3px 10px rgba(208,2,27,0.35) !important;
}

/* Column spacing */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    align-items: stretch !important;
}
[data-testid="stHorizontalBlock"] > div:first-child {
    min-width: 240px;
    max-width: 260px;
}

/* Remove column padding */
[data-testid="stColumn"] > div {
    padding: 0 !important;
    height: 100%;
}

/* Quick reply buttons in columns */
.qr-col [data-testid="stButton"] button {
    background: white !important;
    border: 1.5px solid #E0E0E0 !important;
    border-radius: 20px !important;
    color: #333 !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
    white-space: nowrap !important;
    width: auto !important;
}
.qr-col [data-testid="stButton"] button:hover {
    background: #D0021B !important;
    color: white !important;
    border-color: #D0021B !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────────────
KB = {
    "ipower":    {"name":"iPower",        "min":50000,   "return":"Linh hoạt",   "liq":"Rút bất kỳ lúc","emoji":"🌱","desc":"Tài khoản tích lũy linh hoạt, không kỳ hạn, lãi cộng dồn hằng ngày."},
    "ifund":     {"name":"iFund / TCEF",  "min":100000,  "return":"~12–18%/năm", "liq":"T+3",           "emoji":"📊","desc":"Quỹ cổ phiếu đa dạng hóa, phù hợp tích lũy 5–10 năm."},
    "ibond":     {"name":"iBond",         "min":1000000, "return":"Cố định",     "liq":"Theo kỳ hạn",   "emoji":"📋","desc":"Trái phiếu doanh nghiệp, lãi suất cố định, rủi ro thấp."},
    "zerofee":   {"name":"Zero Fee Stock","min":0,       "return":"Tiềm năng cao","liq":"T+2",           "emoji":"🆓","desc":"Giao dịch cổ phiếu miễn phí hoàn toàn từ 01/01/2023."},
    "margin789": {"name":"Margin 789",    "min":0,       "return":"Vay 7.89%/năm","liq":"Theo hợp đồng","emoji":"📐","desc":"Lãi suất margin ưu đãi 7.89%/năm cho lần đầu dùng margin."},
}

DAILY_TIPS = [
    "Đầu tư thông minh từ số tiền nhỏ hôm nay, tương lai sẽ lớn hơn bạn nghĩ! ✨",
    "10.000đ mỗi ngày = 3.650.000đ sau một năm. Bắt đầu nhỏ thôi! 🌱",
    "Người giàu không tiết kiệm vì có nhiều tiền — họ có nhiều tiền vì tiết kiệm. 💡",
    "Mục tiêu rõ ràng giúp bạn tiết kiệm dễ hơn 3 lần so với không có mục tiêu. 🎯",
    "Đa dạng hóa danh mục — cách tốt nhất để ngủ ngon khi thị trường biến động. 😴",
    "Chiến lược DCA: đầu tư đều mỗi tháng, bất kể thị trường lên hay xuống. 📈",
    "Kỷ luật quan trọng hơn tài năng trong hành trình đầu tư dài hạn. 🏆",
]

QR_DEFAULT = ["So sánh iPower và iFund", "Đầu tư với 200k/tháng", "Mục tiêu dài hạn", "Tôi là người mới"]

# ─────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────
for key, default in [
    ("messages", []),
    ("quick_replies", QR_DEFAULT),
    ("active_nav", "chat"),
    ("qr_trigger", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────
def normalize(text: str) -> str:
    t = text.lower()
    for src, dst in [
        ("đ","d"),("á","a"),("à","a"),("ả","a"),("ã","a"),("ạ","a"),
        ("ă","a"),("ắ","a"),("ằ","a"),("ặ","a"),("â","a"),("ấ","a"),("ầ","a"),("ậ","a"),
        ("é","e"),("è","e"),("ẻ","e"),("ẹ","e"),("ê","e"),("ế","e"),("ề","e"),("ệ","e"),
        ("í","i"),("ì","i"),("ị","i"),("ó","o"),("ò","o"),("ọ","o"),
        ("ô","o"),("ố","o"),("ồ","o"),("ộ","o"),("ơ","o"),("ớ","o"),("ờ","o"),("ợ","o"),
        ("ú","u"),("ù","u"),("ụ","u"),("ư","u"),("ứ","u"),("ừ","u"),("ự","u"),
        ("ý","y"),("ỳ","y"),("ỵ","y"),
    ]:
        t = t.replace(src, dst)
    return t

def extract_amount(text: str):
    t = normalize(text)
    m = re.search(r'(\d[\d.,]*)[\s]*(k|tr|trieu|nghin)', t)
    if not m:
        m = re.search(r'(\d{3,})', t)
    if not m:
        return None
    raw = float(m.group(1).replace(",","").replace(".",""))
    unit = m.group(2) if m.lastindex and m.lastindex >= 2 else ""
    if unit in ("k","nghin"): raw *= 1000
    elif unit in ("tr","trieu"): raw *= 1_000_000
    if 1000 <= raw <= 9999: raw *= 1000
    return int(raw)

def fmt(n: int) -> str:
    if n >= 1_000_000:
        v = n/1_000_000
        return f"{v:.0f} triệu đ" if v==int(v) else f"{v:.1f} triệu đ"
    if n >= 1000: return f"{n//1000}.000đ"
    return f"{n}đ"

def to_html(text: str) -> str:
    """Markdown-lite → HTML"""
    text = text.replace("\n\n", "<br><br>").replace("\n", "<br>")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text

def product_card_html(pid: str) -> str:
    p = KB.get(pid)
    if not p: return ""
    min_row = f'<div class="p-row"><span class="p-label">Tối thiểu</span><span class="p-val p-red">{fmt(p["min"])}</span></div>' if p["min"] else ""
    return f"""
    <div class="p-card">
      <div class="p-card-header">
        <span style="font-size:22px">{p['emoji']}</span>
        <div>
          <div style="font-weight:700;font-size:13.5px">{p['name']}</div>
          <div style="font-size:11px;color:#9E9E9E">Sản phẩm TCBS</div>
        </div>
      </div>
      <div class="p-card-body">
        <div class="p-row"><span class="p-label">Sinh lời</span><span class="p-val p-green">{p['return']}</span></div>
        <div class="p-row"><span class="p-label">Thanh khoản</span><span class="p-val">{p['liq']}</span></div>
        {min_row}
        <div class="p-desc">✨ {p['desc']}</div>
      </div>
      <div class="p-btn">Tìm hiểu thêm →</div>
    </div>"""

def render_msg(msg: dict) -> str:
    content = to_html(msg["content"])
    cards = "".join(product_card_html(pid) for pid in msg.get("products",[]))
    if cards:
        cards = f'<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:6px">{cards}</div>'
    t = msg["time"]

    if msg["role"] == "user":
        return f"""
        <div class="msg-row user">
          <div><div class="bubble-user">{content}</div><div class="msg-time">{t}</div></div>
          <div class="av-user">👤</div>
        </div>"""
    else:
        return f"""
        <div class="msg-row">
          <div class="av-sheep">🐑</div>
          <div>
            <div class="bubble-ai">{content}</div>
            {cards}
            <div class="msg-time">{t}</div>
          </div>
        </div>"""

# ─────────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────────
def get_response(text: str) -> dict:
    t = normalize(text)
    amount = extract_amount(text)
    now = datetime.now().strftime("%H:%M")

    def r(content, products=None, qr=None):
        return {"content":content, "time":now, "products":products or [], "qr":qr or QR_DEFAULT}

    # Emotional negative
    if re.search(r"buon|stress|met|chan|lo lang|ap luc|so hai|that vong|tuyet vong", t):
        return r(
            "Cừu nghe thấy bạn rồi — áp lực kiểu đó nặng lắm, không ai muốn gánh một mình. 🤍\n\n"
            "Bạn không cần giải quyết hết ngay hôm nay. Đôi khi **một bước nhỏ** là đủ để cảm thấy nhẹ hơn.\n\n"
            "Bạn có thể kể thêm — điều gì đang khiến bạn lo nhất lúc này?",
            qr=["Áp lực tài chính", "Áp lực công việc", "Cứ nghe Cừu nói đi"]
        )

    # Emotional positive
    if re.search(r"vui|hanh phuc|tu hao|phan khich|tuyet voi|hom nay tot|ok roi|on roi", t):
        return r(
            "Cừu thấy vui lây rồi! 🎉 Ngày tốt xứng đáng được kỷ niệm!\n\n"
            "Kể Cừu nghe hôm nay có gì vui không? 😊",
            qr=["Kể chuyện vui", "Tôi muốn tiết kiệm để ăn mừng", "Tạo mục tiêu mới"]
        )

    # Micro saving ≤ 100k
    if amount and amount <= 100_000:
        daily = amount
        yearly = daily * 365
        return r(
            f"**{fmt(daily)}** — và bạn muốn nó sinh ra tiền. Cừu thích tư duy này lắm! ✨\n\n"
            f"🌱 **iPower** là lựa chọn hoàn hảo — tối thiểu chỉ **50.000đ**, rút bất kỳ lúc nào.\n\n"
            f"Nếu để dành {fmt(daily)}/ngày → bạn có **{fmt(yearly)}** sau 1 năm (chưa tính lãi!).\n\n"
            "Cừu hướng dẫn cách nạp tiền nhé! 👇",
            products=["ipower"],
            qr=["Cách nạp tiền vào TCBS", "Lãi suất iPower bao nhiêu?", "Tôi muốn lập mục tiêu"]
        )

    # Medium amount 200k-2M
    if amount and 200_000 <= amount <= 2_000_000:
        return r(
            f"Với **{fmt(amount)} mỗi tháng**, Cừu gợi ý bạn có thể bắt đầu với iPower hoặc iFund nhé!\n\n"
            f"🌱 **iPower:** Linh hoạt, phù hợp nếu bạn muốn sinh lời và rút tiền dễ dàng.\n\n"
            f"📊 **iFund:** Phù hợp cho mục tiêu dài hạn, lợi nhuận ổn định hơn theo thời gian.\n\n"
            "Bạn muốn Cừu giúp so sánh chi tiết hơn không? 😊",
            products=["ipower", "ifund"],
            qr=["So sánh iPower và iFund", "Đầu tư với 200k/tháng", "Mục tiêu dài hạn", "Tôi là người mới"]
        )

    # So sánh
    if re.search(r"so sanh|ipower|ifund|quy dau tu", t):
        return r(
            "Cừu so sánh giúp bạn nhé! 📊\n\n"
            "🌱 **iPower** — Tối thiểu 50k · Rút bất kỳ lúc · Rủi ro thấp · Ngắn–trung hạn\n\n"
            "📊 **iFund** — Tối thiểu 100k · T+3 · Trung bình · Dài hạn 5–10 năm\n\n"
            "**Cừu gợi ý:** Nếu chưa chắc, bắt đầu iPower. Quen rồi, phân bổ thêm vào iFund! 🌱",
            qr=["Bắt đầu với iPower", "Tìm hiểu iFund", "Cần bao nhiêu tiền để bắt đầu?"]
        )

    # Goal / tiết kiệm
    if re.search(r"muc tieu|tiet kiem|mua xe|mua nha|du lich|ke hoach|gom tien", t):
        return r(
            "Đặt mục tiêu tài chính là bước thông minh nhất hôm nay! 🎯\n\n"
            "Cừu giúp bạn tính:\n"
            "- Cần tiết kiệm bao nhiêu **mỗi tháng**?\n"
            "- **Sản phẩm nào** phù hợp nhất?\n"
            "- Theo dõi tiến độ **mỗi ngày**.\n\n"
            "Mục tiêu của bạn là gì? 😊",
            qr=["Mua xe", "Du lịch nước ngoài", "Mua nhà", "Quỹ dự phòng khẩn cấp"]
        )

    # Cổ phiếu
    if re.search(r"co phieu|chung khoan|stock|zero fee|giao dich", t):
        return r(
            "Cổ phiếu — kênh đầu tư tiềm năng! 📈\n\n"
            "Tin vui: TCBS có **Zero Fee** — giao dịch cổ phiếu **miễn phí hoàn toàn** từ 01/01/2023.\n\n"
            "Bạn đã có kinh nghiệm GD chưa, hay đang muốn bắt đầu?",
            products=["zerofee"],
            qr=["Chưa có kinh nghiệm", "Đã giao dịch rồi", "Muốn dùng margin"]
        )

    # Người mới
    if re.search(r"moi bat dau|nguoi moi|chua biet|lan dau|moi|newbie", t):
        return r(
            "Chào mừng bạn đến với hành trình đầu tư! 🌱 Cừu sẽ đồng hành từng bước.\n\n"
            "**3 bước đơn giản để bắt đầu:**\n\n"
            "**1.** Mở tài khoản TCBS miễn phí (3 phút · TCInvest App)\n"
            "**2.** Nạp tiền tối thiểu **50.000đ**\n"
            "**3.** Bắt đầu với **iPower** — an toàn, linh hoạt, không kỳ hạn\n\n"
            "Bạn muốn Cừu hướng dẫn bước nào? 😊",
            products=["ipower"],
            qr=["Cách mở tài khoản TCBS", "Cách nạp tiền", "Lãi suất iPower là bao nhiêu?"]
        )

    # Nạp tiền / deposit
    if re.search(r"nap tien|chuyen tien|deposit|nap vao", t):
        return r(
            "Nạp tiền vào TCBS — 3 bước, dưới 2 phút! 💰\n\n"
            "**Qua TCInvest App:**\n"
            "1. Mở TCInvest App → Tài khoản → Nạp tiền\n"
            "2. Chọn ngân hàng nguồn (hỗ trợ 20+ ngân hàng)\n"
            "3. Nhập số tiền (tối thiểu **50.000đ**) → Xác nhận\n\n"
            "**Qua TCB Mobile:** Đầu tư → Tài khoản CK → Chuyển tiền vào",
            qr=["Mở TCInvest App", "Tôi dùng TCB Mobile", "Hỗ trợ ngân hàng nào?"]
        )

    # Margin
    if re.search(r"margin|vay|ky quy", t):
        return r(
            "Vay ký quỹ giúp tăng sức mua — nhưng cũng tăng rủi ro. Cừu muốn bạn hiểu rõ trước khi quyết định. 💡\n\n"
            "- Lần đầu: **Margin 789** — lãi suất ưu đãi **7.89%/năm**\n"
            "- Đã có kinh nghiệm: **Margin T+** — lãi từ **0%/năm**",
            products=["margin789"],
            qr=["Margin 789 là gì?", "Điều kiện dùng margin", "Quay về không dùng margin"]
        )

    # Greeting
    if re.search(r"chao|hello|hi\b|xin chao|bat dau", t):
        return r(
            "Chào bạn thân mến! Cừu đây — người bạn đồng hành tài chính AI của bạn tại TCBS! 🐑✨\n\n"
            "Cừu muốn **thực sự hiểu** bạn và đồng hành trên hành trình tài chính.\n\n"
            "Hôm nay bạn đang cảm thấy thế nào?",
            qr=["Tôi đang khá stress", "Ngày hôm nay ổn", "Tôi có 500k/tháng muốn đầu tư", "Giúp tôi lập mục tiêu"]
        )

    # Default
    return r(
        "Cừu đang lắng nghe bạn đây. 🐑\n\n"
        "Để tư vấn chính xác, bạn cho Cừu biết:\n"
        "- Số tiền muốn đầu tư?\n"
        "- Mục tiêu (mua nhà, du lịch, hưu trí...)?\n"
        "- Thời gian đầu tư ngắn hay dài hạn?",
        qr=QR_DEFAULT
    )

def process_msg(text: str):
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role":"user","content":text,"time":now})
    resp = get_response(text)
    st.session_state.messages.append({
        "role":"ai","content":resp["content"],"time":resp["time"],"products":resp["products"]
    })
    st.session_state.quick_replies = resp["qr"]

# ─────────────────────────────────────────────────
# QR TRIGGER (trước khi render)
# ─────────────────────────────────────────────────
if st.session_state.qr_trigger:
    process_msg(st.session_state.qr_trigger)
    st.session_state.qr_trigger = None
    st.rerun()

# ─────────────────────────────────────────────────
# LAYOUT: col_left | col_main
# ─────────────────────────────────────────────────
col_left, col_main = st.columns([1.1, 4.2])

# ═══════════════════════════════════════
# LEFT PANEL — pure HTML, zero Streamlit
# ═══════════════════════════════════════
nav_items = [
    ("chat",     "💬", "Chat cùng Cừu",       True),
    ("search",   "🔍", "Tìm sản phẩm",        False),
    ("plan",     "🎯", "Kế hoạch tiết kiệm",  False),
    ("journal",  "❤️", "Nhật ký cảm xúc",     False),
    ("history",  "🕐", "Lịch sử hội thoại",   False),
    ("settings", "⚙️", "Cài đặt",             False),
]

nav_html = "".join(
    f'<div class="nav-item {"active" if active else ""}">'
    f'<span class="nav-icon">{icon}</span>{label}</div>'
    for _, icon, label, active in nav_items
)

with col_left:
    st.markdown(f"""
    <div class="left-panel">
      <div class="sheep-header">
        <span class="sheep-img">🐑</span>
        <div class="sheep-name">Cừu Cần Cù</div>
        <div class="sheep-sub">Người bạn đồng hành tài chính ❤️</div>
      </div>
      <div class="nav-section">
        <div class="nav-label">Tính năng</div>
        {nav_html}
      </div>
      <div class="tip-green" style="margin:auto 14px 0;">
        <div class="tip-green-title">🌱 Tích tiểu thành đại</div>
        <div class="tip-green-text">
          Bắt đầu từ những khoản nhỏ mỗi ngày,
          Cừu sẽ giúp bạn đầu tư thông minh để
          đạt được mục tiêu lớn! 🌱
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
# RIGHT / MAIN PANEL
# ═══════════════════════════════════════
with col_main:

    # Welcome banner
    today_tip = DAILY_TIPS[datetime.now().weekday() % len(DAILY_TIPS)]
    st.markdown(f"""
    <div class="welcome-banner">
      <div class="wb-left">
        <h2>👋 Xin chào!</h2>
        <p>Mình là <strong>Cừu Cần Cù</strong>, người bạn đồng hành tài chính của bạn.</p>
        <p class="wb-red">Cùng Cừu bắt đầu hành trình tích tiểu thành đại nhé!</p>
      </div>
      <div class="tip-yellow">
        <div class="ty-label">💡 Tip của Cừu</div>
        <div class="ty-text">{today_tip}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat messages
    messages_html = "".join(render_msg(m) for m in st.session_state.messages)
    st.markdown(
        f'<div class="chat-area" id="chat-area">{messages_html}</div>',
        unsafe_allow_html=True
    )

    # Quick replies — dùng columns để clickable
    qr_list = st.session_state.quick_replies
    if qr_list:
        st.markdown('<div class="qr-col">', unsafe_allow_html=True)
        qr_cols = st.columns(len(qr_list) + 1)
        for i, qr_text in enumerate(qr_list):
            with qr_cols[i]:
                if st.button(qr_text, key=f"qr_{i}_{qr_text[:8]}"):
                    st.session_state.qr_trigger = qr_text
                    st.rerun()
        with qr_cols[-1]:
            if st.button("🔄", key="qr_reset"):
                st.session_state.quick_replies = QR_DEFAULT
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat input — st.chat_input xuất hiện bottom-of-page
    user_input = st.chat_input("Nhắn tin cho Cừu...", key="chat_in")
    if user_input:
        process_msg(user_input)
        st.rerun()

    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
      🛡️ Cừu Cần Cù cung cấp thông tin, không phải lời khuyên đầu tư.
      Bạn nên cân nhắc kỹ trước khi đưa ra quyết định.
    </div>
    """, unsafe_allow_html=True)

# Auto-scroll chat to bottom
st.markdown("""
<script>
  window.addEventListener('load', () => {
    const el = document.getElementById('chat-area');
    if (el) el.scrollTop = el.scrollHeight;
  });
</script>
""", unsafe_allow_html=True)
