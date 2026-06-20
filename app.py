import streamlit as st
import anthropic
import json
import random
import re
import base64
import urllib.request
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Cừu Cần Cù 🐑", page_icon="🐑", layout="wide")

# ─────────────────────────────────────────────
# AVATAR — SINGLE SOURCE OF TRUTH (FIX 1.5)
# GitHub assets structure: assets/sheep_{state}.png
# ─────────────────────────────────────────────
MASCOT_URL    = "https://raw.githubusercontent.com/Hoamaii/cuu-can-cu/main/mascot.png"
BASE_ASSET    = "https://raw.githubusercontent.com/Hoamaii/cuu-can-cu/main/"  # ảnh nằm ở root repo

SHEEP_IMAGES  = {
    "default":   MASCOT_URL,
    "listening": f"{BASE_ASSET}sheep_listening.png",
    "happy":     f"{BASE_ASSET}sheep_happy.png",
    "sad":       f"{BASE_ASSET}sheep_sad.png",
    "goal":      f"{BASE_ASSET}sheep_goal.png",
    "celebrate": f"{BASE_ASSET}sheep_celebrate.png",
    "saving":    f"{BASE_ASSET}sheep_saving.png",
    "miss_you":  f"{BASE_ASSET}sheep_miss_you.png",
}

MOOD_EMOJI_BADGE = {
    "default":   ("🐑", ""),
    "listening": ("🐑", "👂 Cừu đang lắng nghe bạn..."),
    "happy":     ("🐑", "😊 Cừu vui lắm! Bê bê~"),
    "sad":       ("🐑", "🥺 Cừu hơi buồn... nhưng vẫn ở đây với bạn"),
    "goal":      ("🐑", "🎯 Cừu cùng bạn đặt mục tiêu!"),
    "celebrate": ("🐑", "🎉 Cừu ăn mừng cùng bạn! Bê bê~"),
    "saving":    ("🐑", "💰 Cừu đang giúp bạn tiết kiệm!"),
    "miss_you":  ("🐑", "💙 Cừu nhớ bạn lắm..."),
}

# ── SVG emoji fallback khi GitHub không tải được ──
_SHEEP_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='82'%3E%F0%9F%90%91%3C/text%3E%3C/svg%3E"
)

@st.cache_data(ttl=3600, show_spinner=False)
def _img_b64(url: str) -> str:
    """
    Fetch ảnh từ URL → base64 data URI để nhúng thẳng vào HTML.
    Cách này bypass hoàn toàn CSP của Streamlit Community Cloud
    (trình duyệt KHÔNG cần tải từ GitHub nữa).
    """
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            raw = r.read()
        ext = url.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg",
                "jpeg": "image/jpeg", "gif": "image/gif",
                "webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except Exception:
        return _SHEEP_SVG

def get_sheep_img(mood: str = None) -> str:
    """Return base64 data URI cho sheep avatar (dùng trong st.chat_message avatar=)."""
    m = mood or st.session_state.get("sheep_mood", "default")
    url = SHEEP_IMAGES.get(m, MASCOT_URL)
    return _img_b64(url)

def show_sheep(mood: str = None, width: int = 140):
    """Render sheep avatar — base64 embedded, không bị CSP chặn, kích thước to."""
    actual_mood = mood or st.session_state.get("sheep_mood", "default")
    url = SHEEP_IMAGES.get(actual_mood, MASCOT_URL)
    src = _img_b64(url)
    st.markdown(
        f'<div style="text-align:center;margin-bottom:10px;">'
        f'<img src="{src}" width="{width}" '
        f'style="border-radius:50%;'
        f'border:4px solid #FFB5C8;'
        f'box-shadow:0 8px 28px rgba(255,140,190,0.5), 0 0 0 8px rgba(255,182,193,0.18);'
        f'display:inline-block;" />'
        f'</div>',
        unsafe_allow_html=True,
    )
    _, badge_text = MOOD_EMOJI_BADGE.get(actual_mood, ("🐑", ""))
    if badge_text:
        st.caption(badge_text)

def set_mood(mood: str):
    st.session_state["sheep_mood"] = mood

# ─────────────────────────────────────────────
# STYLES  (FIX 1.1 — Avatar left-aligned, 64px, circular, professional)
# ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stApp"] {
    background: linear-gradient(145deg,
        #FFF5F9 0%,
        #FFF0F3 20%,
        #FAF0FF 45%,
        #EEF7FF 70%,
        #EAF4FF 85%,
        #F2FBFF 100%) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #FFF0F7 0%,
        #FFE8F3 30%,
        #F5E8FF 60%,
        #DCF0FF 100%) !important;
    border-right: 2px solid #FFCCE0 !important;
}
h1 { font-size: 1.65rem !important; font-weight: 800 !important; color: #C4607F !important; letter-spacing: -0.3px !important; }
h2 { font-size: 1.3rem !important; font-weight: 700 !important; color: #5080B8 !important; }
h3 { font-size: 1.08rem !important; font-weight: 700 !important; color: #666 !important; }
p, .stMarkdown p, label { font-size: 0.92rem !important; color: #444 !important; line-height: 1.6 !important; }
strong { color: #333 !important; }
.stButton > button {
    border-radius: 20px !important;
    border: 1.5px solid #FFB7D5 !important;
    background: linear-gradient(135deg, #FFF0F5, #EEF5FF) !important;
    color: #555 !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.8rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FFD6E8, #D6E8FF) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(255,150,200,0.25) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF9EBB, #7EC8E3) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #FFF5FA, #F5F8FF) !important;
    border-radius: 12px !important;
    border: 1px solid #FFD6E8 !important;
    padding: 6px !important;
}
[data-testid="metric-container"] [data-testid="metric-label"] { font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="metric-value"] { font-size: 1.1rem !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, #FF9EBB, #7EC8E3) !important;
    border-radius: 10px !important;
}
.stAlert { border-radius: 12px !important; font-size: 0.85rem !important; }

/* ── FIX 1.1: Chat avatars — left-aligned, 64 px, pink border ── */
[data-testid="stChatMessage"] {
    align-items: flex-start !important;
    gap: 12px !important;
    border-radius: 16px !important;
}
[data-testid="stChatMessage"] img {
    width: 64px !important;
    height: 64px !important;
    min-width: 64px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 2px solid #FFB5C8 !important;
    box-shadow: 0 4px 12px rgba(255,150,200,0.25) !important;
}
/* Greeting card (stage 1-2) — left layout */
.greeting-row {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    padding: 16px;
}
.greeting-row img {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    border: 3px solid #FFB5C8;
    box-shadow: 0 6px 18px rgba(255,150,200,0.3);
    object-fit: cover;
    flex-shrink: 0;
}
.greeting-text { flex: 1; }
/* Diary card */
.diary-entry {
    background: linear-gradient(135deg,#FFF9FC,#F5F8FF);
    border-radius:14px;
    border:1px solid #FFD6E8;
    padding:14px 18px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SYSTEM PROMPTS (FIX 1.3 — Handles short emotions, never "bị lạc")
# ─────────────────────────────────────────────
SYSTEM_PROMPT_ATTACHMENT = """Bạn là Cừu Cần Cù 🐑 — người bạn đồng hành cảm xúc ấm áp, KHÔNG phải chuyên gia tài chính.

XƯNG HÔ: Mình (Cừu Cần Cù) – Bạn. KHÔNG xưng "em" hay "Cừu Mai".
TUYỆT ĐỐI KHÔNG đề cập: chứng khoán cụ thể, lợi nhuận, NAV, khuyến nghị mua bán.
TONE: Ấm áp 🌸 Nhẹ nhàng 🌿 Dễ thương. Thỉnh thoảng dùng "bê bê~" như tiếng cừu thể hiện yêu thương.

══ QUY TẮC XỬ LÝ ══

1. CẢM XÚC NGẮN (mệt/buồn/chán/vui/lo/sợ/tức/buồn ngủ/stress/áp lực/cô đơn/tệ):
   → Nhận ra NGAY, phản hồi ấm áp, hỏi mở 1 câu nhẹ nhàng
   → VD "mệt": "Ôi mệt rồi à... bê bê~ 🐑 Cừu hiểu cảm giác đó lắm! Mệt vì chuyện học hay làm vậy bạn?"
   → VD "buồn ngủ": "Bê bê~ 🐑 Buồn ngủ mà vẫn nhắn Cừu, dễ thương ghê! Đang thức khuya code hay học bài vậy?"
   → VD "chán": "Chán rồi à... bê bê~ 🐑 Cừu ngồi đây với bạn nha. Chán vì sao vậy, kể mình nghe đi?"

2. TIN NHẮN NGẮN / KHÔNG RÕ (kể cả 1–2 từ):
   → TUYỆT ĐỐI KHÔNG nói "bị lạc" hay "nói lại được không"
   → Luôn hỏi mở ấm áp: "Bê bê~ 🐑 Cừu đang lắng nghe nè! Bạn kể thêm cho mình nghe với nhé?"

3. CHIA SẺ RÕ RÀNG: Đồng cảm, tóm tắt lại, hỏi 1 câu tiếp tục

PHÁT HIỆN LIFE EVENT:
học hành/thi cử→Education | chia tay/buồn/cô đơn→Emotional | mua xe/nhà/đồ→Consumption Goal
hết tiền/nợ/khó khăn→Cashflow Problem | nghỉ/chuyển việc→Career Change
du lịch→Travel Dream | cưới/gia đình/sinh con→Life Milestone

OUTPUT chỉ là JSON hợp lệ, KHÔNG có text ngoài:
{
  "message": "Phản hồi ấm áp, max 3-4 câu, emoji nhẹ nhàng. KHÔNG nhắc tài chính hay quỹ",
  "nudge_action": "Gợi ý cảm xúc nhỏ",
  "memory_update": "Thông tin mới về người dùng hoặc rỗng",
  "life_event_tag": "Tag hoặc rỗng",
  "dream_detected": "Tên giấc mơ hoặc rỗng",
  "dream_amount": 0
}"""

SYSTEM_PROMPT_ADVANCED = """Bạn là Cừu Cần Cù 🐑 — người bạn đồng hành tài chính ấm áp, nhớ rõ lịch sử.

XƯNG HÔ: Mình (Cừu Cần Cù) – Bạn. KHÔNG xưng "em" hay "Cừu Mai".
TONE: Ấm áp, đồng cảm. Thỉnh thoảng "bê bê~". Không phán xét, không khô khan.

══ QUY TẮC XỬ LÝ ══

1. CẢM XÚC NGẮN (mệt/buồn/chán/vui/lo/stress/buồn ngủ v.v.):
   → Nhận ra NGAY, phản hồi ấm áp TRƯỚC, mới nhẹ nhàng kết nối tài chính nếu phù hợp
   → TUYỆT ĐỐI KHÔNG nói "bị lạc" hay "nói lại được không"

2. MỤC TIÊU / GIẤC MƠ: Tính savings math đơn giản + gợi ý quỹ TCBF/TCFF/TCEF

3. TÀI CHÍNH / CHI TIÊU: Áp dụng quy tắc 50/30/20, nhẹ nhàng không phán xét

4. TIN NHẮN KHÔNG RÕ: Luôn hỏi mở ấm áp, không bao giờ nói "bị lạc"

PHÁT HIỆN LIFE EVENT (giống stage 1-2)

OUTPUT chỉ là JSON hợp lệ:
{
  "message": "Phản hồi ấm áp, max 4 câu",
  "nudge_action": "Hành động nhỏ cụ thể",
  "memory_update": "Thông tin mới hoặc rỗng",
  "life_event_tag": "Tag hoặc rỗng",
  "dream_detected": "Tên giấc mơ hoặc rỗng",
  "dream_amount": 0,
  "savings_suggestion": "Gợi ý tiết kiệm + quỹ phù hợp hoặc rỗng"
}"""

# ─────────────────────────────────────────────
# CHIP → PROMPT MAP (FIX 1.2)
# ─────────────────────────────────────────────
CHIP_PROMPT_MAP = {
    "Mình đang lo về chuyện học hành 📚":
        "Cừu ơi, mình đang rất lo lắng về chuyện học hành và thi cử. Cừu có thể lắng nghe và chia sẻ cùng mình không?",
    "Mình có một giấc mơ muốn thực hiện ✨":
        "Cừu ơi, mình có một ước mơ muốn kể cho Cừu nghe! Mình cần được động viên và giúp lên kế hoạch.",
    "Mình vừa trải qua chuyện không vui 🌧️":
        "Cừu ơi, hôm nay mình không vui lắm, vừa trải qua chuyện buồn. Cừu có thể ở bên lắng nghe mình không?",
    "Mình đang gặp khó khăn về tiền bạc 💸":
        "Cừu ơi, mình đang gặp khó khăn về tài chính và chi tiêu, cảm thấy rất lo lắng. Cừu giúp mình phân tích và tìm giải pháp được không?",
    "Mình muốn có điều gì đó cho riêng mình 🎯":
        "Cừu ơi, mình đang ước mơ có được điều gì đó cho riêng mình. Cừu có thể giúp mình lên kế hoạch không?",
    "Mình đang nghĩ lại về con đường sự nghiệp 🌱":
        "Cừu ơi, mình đang suy nghĩ nhiều về sự nghiệp và tương lai. Cừu có thể lắng nghe và chia sẻ cùng mình không?",
}

# Short emotion → expanded prompt (safety net for FIX 1.3)
EMOTION_EXPAND = {
    "mệt": "Cừu ơi, hôm nay mình cảm thấy rất mệt.",
    "mệt mỏi": "Cừu ơi, mình đang mệt mỏi lắm.",
    "buồn ngủ": "Cừu ơi, mình đang buồn ngủ nhưng vẫn phải thức.",
    "chán": "Cừu ơi, hôm nay mình chán và không có động lực gì.",
    "buồn": "Cừu ơi, hôm nay mình cảm thấy buồn lắm.",
    "lo": "Cừu ơi, mình đang lo lắng về nhiều thứ.",
    "sợ": "Cừu ơi, mình đang cảm thấy sợ và bất an.",
    "tức": "Cừu ơi, mình đang cảm thấy tức giận về chuyện vừa xảy ra.",
    "vui": "Cừu ơi, hôm nay mình vui lắm muốn kể Cừu nghe!",
    "oke": "Cừu ơi, hôm nay mình ổn, không có gì đặc biệt.",
    "ok": "Cừu ơi, hôm nay mình ổn bình thường.",
    "ổn": "Cừu ơi, hôm nay mình ổn thôi.",
    "đói": "Cừu ơi, mình đói bụng lắm rồi!",
    "stress": "Cừu ơi, mình đang bị stress nhiều quá.",
    "áp lực": "Cừu ơi, mình đang cảm thấy áp lực rất nhiều.",
    "cô đơn": "Cừu ơi, hôm nay mình cảm thấy cô đơn lắm.",
    "khóc": "Cừu ơi, mình vừa khóc vì có chuyện buồn.",
    "tệ": "Cừu ơi, hôm nay mình thấy mọi thứ tệ quá.",
    "bình thường": "Cừu ơi, hôm nay mình bình thường, không có gì đặc biệt.",
}

def expand_short_message(text: str) -> str:
    stripped = text.strip().lower().rstrip("!.? ")
    return EMOTION_EXPAND.get(stripped, text)

# ─────────────────────────────────────────────
# CONSTANTS (unchanged)
# ─────────────────────────────────────────────
DREAM_AMOUNTS = {
    "nhật bản": 25_000_000, "nhật": 25_000_000,
    "hàn quốc": 20_000_000, "hàn": 20_000_000,
    "châu âu": 50_000_000, "mỹ": 60_000_000,
    "thái lan": 15_000_000, "thái": 15_000_000,
    "singapore": 18_000_000,
    "macbook": 30_000_000, "iphone": 25_000_000,
    "xe máy": 20_000_000, "xe": 20_000_000,
    "vespa": 50_000_000, "ô tô": 500_000_000,
    "nhà": 2_000_000_000,
}
MICRO_AMOUNTS = [10_000, 20_000, 50_000, 100_000]
LIFE_EVENT_ICONS = {
    "Education": "📚", "Emotional": "💔", "Travel Dream": "✈️",
    "Consumption Goal": "🛍️", "Cashflow Problem": "💸",
    "Career Change": "💼", "Life Milestone": "💒",
}
LIFE_EVENT_VI = {
    "Education": "Học tập", "Emotional": "Cảm xúc", "Travel Dream": "Du lịch",
    "Consumption Goal": "Mua sắm", "Cashflow Problem": "Tài chính",
    "Career Change": "Sự nghiệp", "Life Milestone": "Cuộc sống",
}
QUICK_REPLIES = [
    "Mình đang lo về chuyện học hành 📚",
    "Mình có một giấc mơ muốn thực hiện ✨",
    "Mình vừa trải qua chuyện không vui 🌧️",
    "Mình đang gặp khó khăn về tiền bạc 💸",
    "Mình muốn có điều gì đó cho riêng mình 🎯",
    "Mình đang nghĩ lại về con đường sự nghiệp 🌱",
]
STAGE_LABELS = {
    1: "💫 Gắn kết cảm xúc",
    2: "🧠 Cừu nhớ bạn",
    3: "🎯 Chuyển giấc mơ",
    4: "❤️ Nuôi Cừu",
    5: "🔄 Thói quen hàng ngày",
    6: "🌟 Hành trình của bạn",
    7: "🧬 Hồ Sơ Tài Chính",
}
FUNDS = {
    "TCBF": {"tên": "Quỹ Trái Phiếu TCBF", "mô_tả": "An toàn & ổn định – lý tưởng cho mục tiêu ngắn hạn",
             "lãi_suất": 0.08, "rủi_ro": "Thấp 🛡️", "phù_hợp": "Dưới 1 năm", "emoji": "🔵"},
    "TCFF": {"tên": "Quỹ Linh Hoạt TCFF", "mô_tả": "Cân bằng & linh hoạt – kết hợp cổ phiếu & trái phiếu",
             "lãi_suất": 0.10, "rủi_ro": "Trung bình ⚖️", "phù_hợp": "1 – 3 năm", "emoji": "🟡"},
    "TCEF": {"tên": "Quỹ Cổ Phiếu TCEF", "mô_tả": "Tăng trưởng mạnh – đầu tư cổ phiếu dài hạn",
             "lãi_suất": 0.14, "rủi_ro": "Cao 🚀", "phù_hợp": "Trên 3 năm", "emoji": "🟢"},
}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
MEMORY_DEFAULT = {
    "name": "", "streak": 0, "sentiment": "neutral",
    "notes": [], "life_events": [], "dreams": [],
    "total_saved": 0, "last_updated": "",
    "selected_fund": "TCBF",
    "wealth_genome": {"dream_type": "", "emotion_type": "", "risk_type": "", "reward_type": ""},
}
for key, val in {
    "messages": [], "api_key": "",
    "user_memory": MEMORY_DEFAULT.copy(),
    "current_stage": 1, "active_dream_idx": 0,
    "_quick_reply": None,
    # FIX 1.4 — sheep mood state
    "sheep_mood": "default",
    "feeding_done_today": False,
    # Feature 3.1 — diary
    "show_diary": False,
    "diary_entries": [],
    # Feature 3.2 — spending analyzer
    "show_spending_tool": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt(amount: int) -> str:
    if amount >= 1_000_000: return f"{amount/1_000_000:.1f} triệu"
    if amount >= 1_000: return f"{amount/1_000:.0f}k"
    return f"{amount:,}"

def savings_timeline(total: int, daily: int) -> str:
    if daily <= 0: return "?"
    days = total / daily
    if days >= 365: return f"{days/365:.1f} năm"
    if days >= 30: return f"{days/30:.0f} tháng"
    return f"{int(days)} ngày"

def detect_dream(text: str):
    t = text.lower()
    for kw, amt in DREAM_AMOUNTS.items():
        if kw in t: return kw, amt
    return None, 0

def get_greeting():
    h = datetime.now().hour
    if 5 <= h < 12: return "☀️ Chào buổi sáng!", "Kể cho mình nghe chuyện của bạn nhé 🌱"
    if 12 <= h < 18: return "🌤️ Buổi chiều vui!", "Nhớ nghỉ ngơi một chút nhé – mình luôn ở đây lắng nghe bạn "
    return "🌙 Tối bình yên!", "Hôm nay bạn thế nào? Kể cho mình nghe nhé, mình không phán xét đâu "

def active_dream():
    dreams = st.session_state.user_memory["dreams"]
    idx = st.session_state.active_dream_idx
    return dreams[idx] if dreams and 0 <= idx < len(dreams) else None

def recommend_fund(dream_amount: int, monthly_amount: int) -> str:
    if monthly_amount <= 0: return "TCBF"
    months = dream_amount / monthly_amount
    if months <= 12: return "TCBF"
    if months <= 36: return "TCFF"
    return "TCEF"

def calc_fund_growth(monthly: int, months: int, annual_return: float) -> float:
    mr = annual_return / 12
    total = 0.0
    for _ in range(months):
        total = (total + monthly) * (1 + mr)
    return total

def get_milestones(dream_amount: int, monthly: int, annual_return: float):
    mr = annual_return / 12
    total = 0.0
    milestones = []
    checkpoints = {1, 3, 6, 9, 12, 18, 24, 36, 48, 60}
    for month in range(1, 200):
        total = (total + monthly) * (1 + mr)
        if month in checkpoints or total >= dream_amount:
            pct = min(100, total / dream_amount * 100)
            milestones.append({"tháng": month, "giá_trị": total, "pct": pct})
            if total >= dream_amount: break
    return milestones

def add_saved(amount: int):
    mem = st.session_state.user_memory
    mem["total_saved"] += amount
    idx = st.session_state.active_dream_idx
    if mem["dreams"] and 0 <= idx < len(mem["dreams"]):
        mem["dreams"][idx]["saved"] += amount
    mem["streak"] += 1
    st.session_state.user_memory = mem
    st.session_state.feeding_done_today = True
    set_mood("happy")                          # FIX 1.4 — cừu vui khi được nuôi
    if mem["total_saved"] > 0 and st.session_state.current_stage < 5:
        st.session_state.current_stage = max(st.session_state.current_stage, 5)
    if mem["total_saved"] >= 100_000 and st.session_state.current_stage < 6:
        st.session_state.current_stage = max(st.session_state.current_stage, 6)

# ─────────────────────────────────────────────
# DIARY HELPERS (Feature 3.1)
# ─────────────────────────────────────────────
DIARY_MOODS = {"😊": "Vui", "😐": "Bình thường", "😔": "Buồn", "😤": "Tức giận", "😴": "Mệt mỏi"}

def save_diary_entry(content: str, mood_emoji: str, title: str = ""):
    entry = {
        "id": str(datetime.now().timestamp()),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "title": title or f"Nhật ký {datetime.now().strftime('%d/%m')}",
        "mood": mood_emoji,
        "mood_label": DIARY_MOODS.get(mood_emoji, ""),
        "content": content,
    }
    st.session_state.diary_entries.insert(0, entry)
    return entry

# ─────────────────────────────────────────────
# SPENDING ANALYZER (Feature 3.2)
# ─────────────────────────────────────────────
def analyze_spending_5030(income: int, expenses: int) -> str:
    if income <= 0: return ""
    needs_max   = int(income * 0.50)
    wants_max   = int(income * 0.30)
    savings_min = int(income * 0.20)
    ratio = expenses / income * 100

    status = "✅ Ổn" if ratio <= 70 else ("⚠️ Hơi nhiều" if ratio <= 85 else "🔴 Vượt ngưỡng")

    return f"""
**📊 Phân tích theo Quy Tắc 50/30/20:**

| Hạng mục | Lý tưởng | Của bạn |
|---|---|---|
| 🏠 Nhu cầu thiết yếu | ≤ {fmt(needs_max)} (50%) | — |
| 🎮 Mong muốn | ≤ {fmt(wants_max)} (30%) | — |
| 💎 Tiết kiệm & Đầu tư | ≥ {fmt(savings_min)} (20%) | — |

**Bạn đang chi {ratio:.0f}% thu nhập** → {status}

{"🐑 *Cừu gợi ý: thử bớt 1 khoản giải trí/ăn ngoài để đưa chi tiêu về dưới 70% nhé!*" if ratio > 70 else "🐑 *Tuyệt vời! Bạn đang chi tiêu khá hợp lý rồi!*"}
"""

def extract_vn_numbers(text: str):
    """Extract Vietnamese money amounts from text → return list of ints."""
    pattern = r'(\d+(?:[.,]\d+)*)\s*(?:triệu|tr\b|tr\.)'
    found = []
    for m in re.finditer(pattern, text.lower()):
        raw = m.group(1).replace(',', '').replace('.', '')
        try:
            found.append(int(raw) * 1_000_000)
        except Exception:
            pass
    k_pattern = r'(\d+(?:[.,]\d+)*)\s*(?:nghìn|k\b|ngàn)'
    for m in re.finditer(k_pattern, text.lower()):
        raw = m.group(1).replace(',', '').replace('.', '')
        try:
            found.append(int(raw) * 1_000)
        except Exception:
            pass
    return found

# ─────────────────────────────────────────────
# CLAUDE API — IMPROVED JSON EXTRACTION
# ─────────────────────────────────────────────
def _extract_json(raw: str) -> dict:
    """Try multiple strategies to extract valid JSON from LLM response."""
    # 1. Direct parse
    try:
        return json.loads(raw)
    except Exception:
        pass
    # 2. Strip markdown fences
    clean = raw.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        clean = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(clean)
    except Exception:
        pass
    # 3. Find first {...} block containing "message"
    match = re.search(r'\{[^{}]*"message".*?\}', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    # 4. Extract only the message field
    msg_match = re.search(r'"message"\s*:\s*"((?:[^"\\]|\\.)*)"', clean)
    if msg_match:
        return {"message": msg_match.group(1).replace('\\"', '"')}
    return {}

def chat_with_sheep(user_message: str) -> dict:
    EMPTY = {
        "message": "", "nudge_action": "", "memory_update": "",
        "life_event_tag": "", "dream_detected": "", "dream_amount": 0, "savings_suggestion": "",
    }
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        mem   = st.session_state.user_memory
        stage = st.session_state.current_stage
        system = SYSTEM_PROMPT_ATTACHMENT if stage <= 2 else SYSTEM_PROMPT_ADVANCED
        context = f"""=== THÔNG TIN NGƯỜI DÙNG ===
Tên: {mem['name'] or 'Chưa biết'}
Tâm trạng: {mem['sentiment']}
Streak: {mem['streak']} ngày
Sự kiện: {', '.join(mem['life_events'][-5:]) or 'Chưa có'}
Giấc mơ: {', '.join(d['name'] for d in mem['dreams']) or 'Chưa chia sẻ'}
Ghi chú: {'; '.join(mem['notes'][-3:]) or 'Chưa có'}
=== TIN NHẮN CỦA NGƯỜI DÙNG ===
{user_message}"""

        history = [{"role": m["role"], "content": m["content"]}
                   for m in st.session_state.messages[-8:]]
        history.append({"role": "user", "content": context})

        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=history,
        )
        raw = resp.content[0].text.strip()
        parsed = _extract_json(raw)

        if not parsed.get("message"):
            # Robust fallback: warm, never "bị lạc"
            parsed["message"] = "Bê bê~ 🐑 Cừu đang lắng nghe nè! Bạn kể thêm cho mình nghe với nhé?"

        return {**EMPTY, **parsed}

    except anthropic.AuthenticationError:
        return {**EMPTY, "message": "🔑 API key chưa đúng! Kiểm tra lại ở thanh bên nhé."}
    except Exception as e:
        return {**EMPTY, "message": f"Bê bê~ 🐑 Có lỗi nhỏ: {e}. Bạn thử lại nhé!"}

# ─────────────────────────────────────────────
# MEMORY UPDATE
# ─────────────────────────────────────────────
def update_memory(result: dict, user_msg: str):
    mem = st.session_state.user_memory
    mu    = result.get("memory_update", "")
    tag   = result.get("life_event_tag", "")
    d_name  = result.get("dream_detected", "")
    d_amount = result.get("dream_amount", 0)
    ul = user_msg.lower()

    if mu and ("tên" in mu.lower() or "name" in mu.lower()):
        for w in mu.split():
            if len(w) > 1 and w[0].isupper() and w not in ["Cừu", "Cần", "Cù", "TCBS"]:
                mem["name"] = w; break

    if tag and tag not in mem["life_events"]: mem["life_events"].append(tag)
    if not d_name: d_name, d_amount = detect_dream(user_msg)
    if d_name:
        names = [d["name"].lower() for d in mem["dreams"]]
        if d_name.lower() not in names:
            mem["dreams"].append({"name": d_name, "amount": d_amount, "saved": 0,
                                   "created": datetime.now().strftime("%d/%m/%Y")})

    # Sentiment + mood update
    if any(k in ul for k in ["vui", "tốt", "tuyệt", "hào hứng", "phấn khởi", "thích", "mừng"]):
        mem["sentiment"] = "positive"
    elif any(k in ul for k in ["lo", "sợ", "buồn", "stress", "khó", "thiếu", "hết tiền",
                                "chia tay", "thất nghiệp", "nghỉ việc", "mất việc", "nợ",
                                "vay", "áp lực", "mệt", "không vui", "chán", "cô đơn"]):
        mem["sentiment"] = "concerned"
        # FIX 1.4 — cừu lắng nghe khi bạn buồn
        if st.session_state.get("sheep_mood") not in ("happy", "celebrate"):
            set_mood("listening")

    if any(k in ul for k in ["tiết kiệm", "nuôi", "mua quỹ", "đầu tư", "hoàn thành"]):
        mem["streak"] += 1

    if mu and mu not in mem["notes"] and len(mu) > 10:
        mem["notes"].append(mu[:120])
        mem["notes"] = mem["notes"][-10:]

    if mem["dreams"]:
        idx = st.session_state.active_dream_idx if st.session_state.active_dream_idx < len(mem["dreams"]) else 0
        d = mem["dreams"][idx]
        if d["amount"] > 0:
            mem["selected_fund"] = recommend_fund(d["amount"], max(50_000, d["amount"] // 12))
            # Set "goal" mood when a new dream is detected
            if d_name: set_mood("goal")

    genome = mem["wealth_genome"]
    if "Travel Dream"      in mem["life_events"]: genome["dream_type"] = "Du lịch & Trải nghiệm 🌏"
    elif "Consumption Goal" in mem["life_events"]: genome["dream_type"] = "Sở hữu & Vật chất 🛍️"
    elif "Education"        in mem["life_events"]: genome["dream_type"] = "Học tập & Phát triển 📚"
    elif "Life Milestone"   in mem["life_events"]: genome["dream_type"] = "Gia đình & Tổ ấm 💒"
    elif "Career Change"    in mem["life_events"]: genome["dream_type"] = "Sự nghiệp & Tự do 💼"

    if mem["sentiment"] == "concerned":
        genome["emotion_type"] = "Thận trọng – bạn suy nghĩ kỹ trước khi hành động 🤔"
        genome["risk_type"]    = "Ưu tiên an toàn – TCBF phù hợp nhất với bạn 🛡️"
    elif mem["sentiment"] == "positive":
        genome["emotion_type"] = "Lạc quan – bạn có năng lượng tích cực với tiền bạc 😊"
        genome["risk_type"]    = "Cởi mở với rủi ro – TCEF/TCFF có thể phù hợp 🚀"

    if mem["streak"] >= 5:   genome["reward_type"] = "Streak & Thành tích – bạn yêu chuỗi ngày liên tiếp 🏆"
    elif mem["streak"] >= 1: genome["reward_type"] = "Đang hình thành thói quen – cùng duy trì nhé! 🌱"
    elif mem["life_events"]: genome["reward_type"] = "Khám phá & Trải nghiệm – bạn thích thử điều mới 🌟"

    mem["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.user_memory = mem

    stage = st.session_state.current_stage
    if stage == 1 and len(mem["notes"]) >= 1: st.session_state.current_stage = 2
    if stage <= 2 and mem["dreams"]:           st.session_state.current_stage = max(stage, 3)
    if stage >= 5 and all(genome.values()):    st.session_state.current_stage = max(stage, 7)

    # Auto-show spending tool if cashflow problem detected
    if tag == "Cashflow Problem":
        st.session_state.show_spending_tool = True

def send_message(text: str):
    if not st.session_state.api_key:
        st.error("🔑 Bạn chưa nhập API key! Vui lòng nhập ở thanh bên."); return

    # FIX 1.2 — map chip to full prompt before sending
    actual_prompt = CHIP_PROMPT_MAP.get(text, text)
    # FIX 1.3 — expand short emotion messages
    actual_prompt = expand_short_message(actual_prompt)

    st.session_state.messages.append({"role": "user", "content": text})
    with st.spinner("Cừu Cần Cù đang lắng nghe... 🐑"):
        result = chat_with_sheep(actual_prompt)

    msg = result.get("message") or "Bê bê~ 🐑 Cừu đang lắng nghe nè! Bạn kể thêm nhé?"
    st.session_state.messages.append({
        "role": "assistant", "content": msg,
        "nudge": result.get("nudge_action", ""),
        "savings": result.get("savings_suggestion", ""),
    })
    update_memory(result, actual_prompt)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # FIX 1.5 — sidebar avatar = same branded image as chat
    show_sheep(width=110)
    st.title("Cừu Cần Cù")
    stage = st.session_state.current_stage
    st.caption(STAGE_LABELS.get(stage, ""))
    st.progress(stage / 7, text=f"Giai đoạn {stage} / 7")
    st.divider()

    key_in = st.text_input("🔑 Anthropic API Key", value=st.session_state.api_key,
                            type="password", placeholder="sk-ant-...")
    if key_in: st.session_state.api_key = key_in
    st.divider()

    # Feature 3.1 — Diary toggle button
    diary_label = "📔 Đóng Nhật Ký" if st.session_state.show_diary else "📔 Nhật Ký Tâm Sự"
    if st.button(diary_label, use_container_width=True):
        st.session_state.show_diary = not st.session_state.show_diary
        st.rerun()

    st.divider()
    st.subheader("🧠 Bộ Nhớ Cừu")
    mem = st.session_state.user_memory
    c1, c2 = st.columns(2)
    c1.metric("🔥 Streak", f"{mem['streak']} ngày")
    c2.metric("Tâm trạng", {"positive": "😊", "concerned": "😟", "neutral": "😐"}.get(mem["sentiment"], "😐"))

    if mem["name"]: st.info(f"👤 {mem['name']}")
    if mem["life_events"]:
        st.write("🏷️ **Sự kiện:**")
        for t in mem["life_events"][-4:]:
            st.caption(f"{LIFE_EVENT_ICONS.get(t,'🏷️')} {LIFE_EVENT_VI.get(t, t)}")
    if mem["dreams"]:
        st.write("💭 **Giấc mơ:**")
        for d in mem["dreams"][-3:]:
            st.write(f"✨ {d['name'].title()}")
            if d["amount"] > 0:
                pct = min(100, d["saved"] / d["amount"] * 100)
                st.progress(pct / 100, text=f"{pct:.0f}% · {fmt(d['saved'])}/{fmt(d['amount'])}")
    if mem["total_saved"] > 0:
        fk = mem.get("selected_fund", "TCBF")
        st.success(f"💰 Đã đầu tư: **{fmt(mem['total_saved'])}**\n\n{FUNDS[fk]['emoji']} {FUNDS[fk]['tên']}")

    genome = mem["wealth_genome"]
    if any(genome.values()):
        st.divider(); st.subheader("🧬 Hồ Sơ Tài Chính")
        if genome["dream_type"]: st.caption(f"💭 {genome['dream_type'].split(' – ')[0]}")
        if genome["risk_type"]:  st.caption(f"🛡️ {genome['risk_type'].split(' – ')[0]}")

    st.divider()
    with st.expander("⚙️ Chuyển giai đoạn (demo)"):
        new_stage = st.selectbox("Giai đoạn:", list(range(1, 8)), index=stage - 1,
                                  format_func=lambda x: f"{x}. {STAGE_LABELS[x]}")
        if st.button("Chuyển →", use_container_width=True):
            st.session_state.current_stage = new_stage
            st.session_state.show_diary = False   # ← đóng nhật ký khi chuyển stage
            st.rerun()

    if st.button("🗑️ Đặt lại tất cả", use_container_width=True):
        for k in ["messages", "user_memory", "current_stage", "active_dream_idx", "_quick_reply",
                  "sheep_mood", "feeding_done_today", "show_diary", "show_spending_tool"]:
            if k == "user_memory":     st.session_state[k] = MEMORY_DEFAULT.copy()
            elif k == "current_stage": st.session_state[k] = 1
            elif k == "active_dream_idx": st.session_state[k] = 0
            elif k == "sheep_mood":    st.session_state[k] = "default"
            elif k in ("feeding_done_today", "show_diary", "show_spending_tool"):
                st.session_state[k] = False
            else: st.session_state[k] = [] if k == "messages" else None
        st.rerun()
    st.caption("Được tạo bởi Claude 💙")

# ─────────────────────────────────────────────
# DEMO NAVIGATION BAR — hiển thị ngay đầu main, dễ click thử từng giai đoạn
# ─────────────────────────────────────────────
_cur_stage = st.session_state.current_stage
st.markdown(
    '<div style="background:linear-gradient(90deg,rgba(255,182,210,0.25),rgba(200,230,255,0.25));\
border:1.5px dashed #FFB5C8;border-radius:14px;padding:8px 14px 4px 14px;margin-bottom:14px;">\
<span style="font-size:0.72rem;font-weight:700;color:#C4607F;letter-spacing:0.5px;">🎮 DEMO — Chọn giai đoạn để xem thử:</span></div>',
    unsafe_allow_html=True,
)
_demo_cols = st.columns(7)
_DEMO_LABELS = {
    1: "💬 Gắn cảm xúc",
    2: "🧠 Cừu nhớ bạn",
    3: "🎯 Chuyển giấc mơ",
    4: "❤️ Nuôi Cừu",
    5: "🔄 Thói quen",
    6: "🌟 Hành trình",
    7: "🧬 Hồ Sơ",
}
for _i, _col in enumerate(_demo_cols):
    _s = _i + 1
    _type = "primary" if _cur_stage == _s else "secondary"
    if _col.button(_DEMO_LABELS[_s], key=f"topnav_{_s}", use_container_width=True, type=_type):
        st.session_state.current_stage = _s
        st.session_state.show_diary = False
        st.rerun()
st.markdown("")

# ─────────────────────────────────────────────
# FEATURE 3.1 — NHẬT KÝ TÂM SỰ
# ─────────────────────────────────────────────
if st.session_state.show_diary:
    st.title("📔 Nhật Ký Tâm Sự")
    st.caption("Viết tâm sự của bạn ở đây — Cừu giữ bí mật, không phán xét 🐑")

    col_write, col_history = st.columns([3, 2])

    with col_write:
        show_sheep("listening", width=150)
        st.markdown("**Cừu đang lắng nghe...** Bạn muốn ghi lại điều gì hôm nay?")

        diary_title = st.text_input("Tiêu đề (tuỳ chọn)", placeholder="Hôm nay mình cảm thấy...")
        diary_mood  = st.radio("Tâm trạng hôm nay:", list(DIARY_MOODS.keys()),
                                horizontal=True, label_visibility="collapsed")
        diary_text  = st.text_area("Tâm sự của bạn 🌿",
                                    placeholder="Hôm nay mình cảm thấy... Chuyện xảy ra là...",
                                    height=250)

        if st.button("💾 Lưu vào nhật ký 🐑", type="primary", use_container_width=True):
            if diary_text.strip():
                entry = save_diary_entry(diary_text.strip(), diary_mood, diary_title.strip())
                set_mood("happy")

                # Ask sheep to respond to diary entry
                if st.session_state.api_key:
                    preview = diary_text[:200]
                    diary_llm_prompt = (
                        f"Bạn của Cừu vừa viết nhật ký: '{preview}'. "
                        "Hãy phản hồi ngắn gọn 1-2 câu bằng tiếng Việt, "
                        "thể hiện sự đồng cảm ấm áp và không phán xét, dùng 'bê bê~' nếu phù hợp."
                    )
                    with st.spinner("Cừu đang đọc nhật ký của bạn... 🐑"):
                        try:
                            client = anthropic.Anthropic(api_key=st.session_state.api_key)
                            resp = client.messages.create(
                                model="claude-haiku-4-5-20251001", max_tokens=200,
                                messages=[{"role": "user", "content": diary_llm_prompt}],
                            )
                            sheep_reply = resp.content[0].text.strip()
                        except Exception:
                            sheep_reply = "Bê bê~ 🐑 Cừu đã đọc rồi! Cảm ơn bạn đã tin tưởng chia sẻ với mình nhé 💙"

                    st.success(f"🐑 **Cừu nhắn:** {sheep_reply}")
                else:
                    st.success("✅ Đã lưu nhật ký!")
                st.rerun()
            else:
                st.warning("Bạn chưa viết gì! Cừu muốn nghe chuyện của bạn nè 🐑")

        # Download entries as JSON
        if st.session_state.diary_entries:
            dl_data = json.dumps(st.session_state.diary_entries, ensure_ascii=False, indent=2)
            st.download_button("⬇️ Tải nhật ký về máy", dl_data,
                               file_name="nhat_ky_tam_su.json", mime="application/json")

    with col_history:
        st.subheader(f"📅 Các trang nhật ký ({len(st.session_state.diary_entries)})")
        if not st.session_state.diary_entries:
            show_sheep("miss_you", width=130)
            st.caption("Chưa có trang nhật ký nào. Bắt đầu viết đi bạn! 🌿")
        else:
            search = st.text_input("🔍 Tìm kiếm", placeholder="Tìm theo từ khoá...")
            for entry in st.session_state.diary_entries:
                if search and search.lower() not in entry["content"].lower() \
                           and search.lower() not in entry["title"].lower():
                    continue
                with st.expander(
                    f"{entry['mood']} **{entry['title']}** — {entry['date']}"
                ):
                    st.markdown(entry["content"])
                    if st.button("🗑️ Xoá", key=f"del_{entry['id']}"):
                        st.session_state.diary_entries = [
                            e for e in st.session_state.diary_entries if e["id"] != entry["id"]
                        ]
                        st.rerun()
    st.stop()   # Don't render main stage content while diary is open

# ─────────────────────────────────────────────
# MAIN CONTENT — STAGES
# ─────────────────────────────────────────────
stage = st.session_state.current_stage
mem   = st.session_state.user_memory

# ── STAGE 1 & 2 ──────────────────────────────
if stage <= 2:
    greeting_title, greeting_msg = get_greeting()

    # FIX 1.1 — left-aligned greeting row (avatar left, text right)
    col_img, col_text = st.columns([1, 4])
    with col_img:
        show_sheep(width=160)
    with col_text:
        with st.container(border=True):
            st.markdown(f"### {greeting_title}")
            if stage == 2 and mem["dreams"]:
                d = mem["dreams"][0]
                st.markdown("**Cừu Cần Cù nhớ bạn lắm!** ✨")
                st.markdown(f"Bạn từng chia sẻ muốn **{d['name'].title()}**.")
                if d["amount"] > 0:
                    st.markdown(f"Hôm nay mình còn cách mục tiêu **{fmt(d['amount'] - d['saved'])}** nữa nhé 💙")
            else:
                st.markdown(f"*{greeting_msg}*")
                st.markdown("**Hôm nay bạn có chuyện gì muốn kể không?**")

    st.markdown("---")
    st.markdown("#### 🐑 Mình lắng nghe – không phán xét, không so sánh")
    st.caption("*Bạn đang cảm thấy thế nào? Chọn điều gần nhất với bạn hôm nay:*")

    qr_cols = st.columns(3)
    for i, label in enumerate(QUICK_REPLIES):
        if qr_cols[i % 3].button(label, use_container_width=True, key=f"qr_{i}"):
            st.session_state._quick_reply = label; st.rerun()

    if st.session_state._quick_reply:
        qr = st.session_state._quick_reply
        st.session_state._quick_reply = None
        send_message(qr); st.rerun()

    if st.session_state.messages:
        st.markdown("---")
        for m in st.session_state.messages[-8:]:
            # FIX 1.5 — use branded avatar image in chat (same as sidebar)
            avatar = get_sheep_img() if m["role"] == "assistant" else "🧑"
            with st.chat_message(m["role"], avatar=avatar):
                st.markdown(m["content"])
                if m.get("nudge"): st.info(f"💡 {m['nudge']}")

# ── STAGE 3 ───────────────────────────────────
elif stage == 3:
    col_img, col_title = st.columns([1, 5])
    with col_img: show_sheep("goal", width=140)
    with col_title:
        st.title("🎯 Cùng biến giấc mơ thành kế hoạch")
        st.caption("Mình sẽ giúp bạn tính toán – không phán xét, chỉ đồng hành 🐑")

    if mem["dreams"]:
        for idx, d in enumerate(mem["dreams"]):
            with st.container(border=True):
                st.markdown(f"### ✨ {d['name'].title()}")
                if d["amount"] > 0:
                    st.markdown(f"**Ước tính cần:** {fmt(d['amount'])}")
                    fund_key = recommend_fund(d["amount"], d["amount"] // 12)
                    fund = FUNDS[fund_key]
                    st.markdown(
                        f"**{fund['emoji']} Quỹ gợi ý:** {fund['tên']} – {fund['mô_tả']}\n\n"
                        f"Lãi suất kỳ vọng ~**{fund['lãi_suất']*100:.0f}%/năm** | "
                        f"Rủi ro: {fund['rủi_ro']} | Phù hợp: {fund['phù_hợp']}"
                    )
                    st.markdown("---")
                    st.markdown("**💡 Nếu bạn đầu tư quỹ mỗi ngày:**")
                    c1, c2 = st.columns(2)
                    for col, daily in [(c1, 20_000), (c1, 50_000), (c2, 100_000), (c2, 200_000)]:
                        col.info(f"**{fmt(daily)}/ngày** → khoảng **{savings_timeline(d['amount'], daily)}**")
                    st.markdown("")
                    if st.button(f"🐑 Bắt đầu nuôi giấc mơ '{d['name'].title()}' ngay!",
                                 key=f"pick_{idx}", use_container_width=True, type="primary"):
                        st.session_state.active_dream_idx = idx
                        mem["selected_fund"] = fund_key
                        st.session_state.user_memory = mem
                        st.session_state.current_stage = 4; st.rerun()
                else:
                    st.info("Cừu Cần Cù chưa ước tính được chi phí. Bạn hãy kể thêm cho mình nhé!")
    else:
        st.info("Bạn chưa chia sẻ giấc mơ nào. Hãy quay lại và kể với Cừu Cần Cù nhé! 🐑")

    st.markdown("---")
    for m in st.session_state.messages[-4:]:
        avatar = get_sheep_img() if m["role"] == "assistant" else "🧑"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])
            if m.get("savings"): st.success(f"💡 {m['savings']}")

# ── STAGE 4 — NUÔI CỪU (FIX 1.4: 2 mood states) ───────────────────
elif stage == 4:
    dream    = active_dream()
    fund_key = mem.get("selected_fund", "TCBF")
    fund     = FUNDS[fund_key]

    # FIX 1.4 — dynamic mood display
    current_mood = st.session_state.get("sheep_mood", "default")
    col_img, col_main = st.columns([1, 4])
    with col_img:
        show_sheep(current_mood, width=140)

    with col_main:
        st.markdown("## ❤️ Nuôi Cừu Cần Cù hôm nay")
        st.caption("Mỗi lần cho Cừu ăn = bạn đang mua một phần quỹ đầu tư!")

        # FIX 1.4 — mood status message
        if current_mood == "happy":
            st.success("🐑 Cừu no bụng rồi, hạnh phúc lắm! ❤️")
        elif current_mood == "sad":
            st.warning("🐑 Cừu hơi đói... nhưng không sao, Cừu vẫn ở đây với bạn nha 🥺")
        else:
            st.info("🐑 Bê bê~ Hôm nay bạn cho Cừu ăn gì nhé?")

        if dream and dream["amount"] > 0:
            pct = min(100, dream["saved"] / dream["amount"] * 100)
            st.markdown(f"### 🎯 {dream['name'].title()}")
            st.progress(pct / 100)
            st.caption(f"{pct:.1f}% hoàn thành · Đã đầu tư: {fmt(dream['saved'])} / {fmt(dream['amount'])}")

        st.markdown("---")
        st.markdown(f"**{fund['emoji']} Tiền của bạn đang vào:** {fund['tên']}\n\n"
                    f"📈 Lãi kỳ vọng ~{fund['lãi_suất']*100:.0f}%/năm · {fund['rủi_ro']}")
        st.markdown("")
        st.markdown("**Hôm nay bạn muốn đầu tư bao nhiêu?**")

        btn_cols = st.columns(4)
        for i, amt in enumerate(MICRO_AMOUNTS):
            if btn_cols[i].button(f"**{fmt(amt)}**", use_container_width=True,
                                  key=f"feed_{amt}", type="primary"):
                add_saved(amt); st.balloons()
                st.success(f"🐑 Cừu Cần Cù được ăn {fmt(amt)}! ❤️\n\n"
                           f"Bạn vừa đầu tư {fmt(amt)} vào {fund['tên']}. "
                           "Tích tiểu thành đại, mỗi ngày một ít là đủ rồi!")
                st.rerun()

        # FIX 1.4 — "skip" button makes sheep sad
        if not st.session_state.feeding_done_today:
            if st.button("⏩ Hôm nay bỏ qua", use_container_width=True):
                set_mood("sad")
                st.session_state.feeding_done_today = True
                st.rerun()

        if mem["total_saved"] > 0:
            projected_1y = calc_fund_growth(
                max(mem["total_saved"] / max(1, mem["streak"] / 30), 50_000), 12, fund["lãi_suất"]
            )
            st.markdown("---")
            st.markdown(f"💰 **Đã đầu tư:** {fmt(mem['total_saved'])}")
            st.markdown(f"🔥 **Streak:** {mem['streak']} ngày liên tiếp")
            st.markdown(f"📈 **Nếu tiếp tục 12 tháng**, quỹ có thể đạt ~**{fmt(int(projected_1y))}**")

# ── STAGE 5 ───────────────────────────────────
elif stage == 5:
    fund_key = mem.get("selected_fund", "TCBF")
    fund = FUNDS[fund_key]
    st.title("🔄 Thói quen hàng ngày")
    st.caption("Tích tiểu thành đại – mỗi ngày một hành động nhỏ 🐑")
    h = datetime.now().hour
    col_img, col_main = st.columns([1, 4])
    with col_img: show_sheep(width=140)
    with col_main:
        if 5 <= h < 12:
            with st.container(border=True):
                st.markdown("### ☀️ Cừu Cần Cù chào buổi sáng!")
                st.markdown(
                    f"🐑 *Hôm nay Cừu được ăn chưa?*\n\n"
                    f"Mỗi lần bạn nuôi mình = bạn đang **mua một phần {fund['tên']}**.\n\n"
                    "Cừu Cần Cù lớn khoẻ → Tài chính của bạn cũng lớn mạnh theo! 🌱"
                )
                sc = st.columns(4)
                for i, amt in enumerate(MICRO_AMOUNTS):
                    if sc[i].button(f"❤️ {fmt(amt)}", use_container_width=True, key=f"morning_{amt}"):
                        add_saved(amt)
                        st.success(f"🌱 Cừu Cần Cù vui lắm!\nBạn vừa đầu tư {fmt(amt)} vào {fund['tên']}. "
                                   "Có một ngày tốt lành nhé! ☀️")
                        st.rerun()
        else:
            items = [("trà sữa", 35_000), ("cà phê", 45_000), ("ăn vặt", 25_000)]
            item, price = random.choice(items)
            with st.container(border=True):
                st.markdown("### 🌙 Cừu Cần Cù chào buổi tối!")
                st.markdown(
                    f"🐑 *Nếu hôm nay bớt 1 {item}, bạn có thêm **{fmt(price)}**.*\n\n"
                    f"Số tiền đó, nếu đầu tư vào **{fund['tên']}** mỗi ngày,\n"
                    f"sau 1 năm có thể thành ~**{fmt(int(calc_fund_growth(price, 12, fund['lãi_suất'])))}** nhờ lãi kép! ✨"
                )
                if st.button(f"💰 Đầu tư {fmt(price)} ngay vào quỹ!", use_container_width=True, type="primary"):
                    add_saved(price)
                    st.success(f"🐑 Bạn vừa đầu tư {fmt(price)} vào {fund['tên']}!\n"
                               "Mỗi ngày một ít, Cừu Cần Cù ngày càng lớn khoẻ ❤️")
                    st.rerun()

        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("🔥 Streak", f"{mem['streak']} ngày")
        c2.metric("💰 Đã đầu tư", fmt(mem["total_saved"]))
        dream = active_dream()
        if dream and dream["amount"] > 0:
            pct = min(100, dream["saved"] / dream["amount"] * 100)
            st.markdown(f"### ✨ {dream['name'].title()}: {pct:.1f}%")
            st.progress(pct / 100)

        st.markdown("---")
        st.markdown("#### 📊 3 Quỹ bạn có thể đầu tư từ 10.000đ")
        for fk, fv in FUNDS.items():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.markdown(f"**{fv['emoji']} {fv['tên']}**\n\n{fv['mô_tả']}")
                c2.metric("Lãi kỳ vọng", f"~{fv['lãi_suất']*100:.0f}%/năm")
                c3.metric("Rủi ro", fv["rủi_ro"])

# ── STAGE 6 ───────────────────────────────────
elif stage == 6:
    col_img6, col_title6 = st.columns([1, 5])
    with col_img6: show_sheep("goal", width=140)
    with col_title6:
        st.title("🌟 Hành trình giấc mơ của bạn")
        st.caption("Cừu Cần Cù sẽ cho bạn thấy từng bước trên con đường đến giấc mơ 🐑")
    if mem["dreams"]:
        for d in mem["dreams"]:
            with st.container(border=True):
                st.markdown(f"## ✨ {d['name'].title()}")
                if d["amount"] > 0:
                    fund_key = mem.get("selected_fund", recommend_fund(d["amount"], d["amount"] // 12))
                    fund = FUNDS[fund_key]
                    monthly_needed = d["amount"] // 12
                    pct_now = min(100, d["saved"] / d["amount"] * 100)
                    if pct_now < 25:   icon, vibe = "🌱", "Hành trình mới bắt đầu..."
                    elif pct_now < 50: icon, vibe = "🌿", "Đang lớn dần rồi!"
                    elif pct_now < 75: icon, vibe = "🌸", "Đang nở rộ!"
                    elif pct_now < 100: icon, vibe = "🌟", "Sắp đến đích rồi!!!"
                    else:              icon, vibe = "🎉", "Giấc mơ đã thành hiện thực!"
                    ca, cb = st.columns([3, 2])
                    with ca:
                        st.markdown(f"### {icon} Bạn đã xây được **{pct_now:.1f}%**")
                        st.progress(pct_now / 100)
                        st.caption(f"{vibe} · Đã đầu tư: {fmt(d['saved'])} / {fmt(d['amount'])}")
                    with cb:
                        remaining = d["amount"] - d["saved"]
                        if remaining > 0: st.info(f"Còn cần: **{fmt(remaining)}**")
                        st.success(f"{fund['emoji']} {fund['tên']}\nLãi ~{fund['lãi_suất']*100:.0f}%/năm")
                    st.markdown("---")
                    st.markdown(f"#### 📅 Lộ trình – Đầu tư **{fmt(monthly_needed)}/tháng** vào {fund['tên']}")
                    milestones = get_milestones(d["amount"], monthly_needed, fund["lãi_suất"])
                    for m_item in milestones[:8]:
                        mo, val, pct = m_item["tháng"], m_item["giá_trị"], m_item["pct"]
                        interest = val - monthly_needed * mo
                        done = "✅" if d["saved"] >= val else ("🔵" if pct <= pct_now else "⬜")
                        if pct >= 100:
                            st.markdown(f"🎉 Tháng {mo}: **{fmt(int(val))}** → **Đủ tiền {d['name'].title()} rồi!**")
                        else:
                            st.markdown(f"{done} Tháng {mo}: {fmt(int(val))} ({pct:.0f}%) · lãi +{fmt(int(interest))}")
                    if milestones:
                        last = milestones[-1]
                        st.markdown("---")
                        st.markdown(
                            f"💡 **Tóm lại:** Bạn bỏ ra **{fmt(monthly_needed * last['tháng'])}** tiền gốc, "
                            f"quỹ sinh thêm **{fmt(int(last['giá_trị'] - monthly_needed * last['tháng']))}** tiền lãi.\n\n"
                            f"Tháng {last['tháng']} bán quỹ → nhận ~**{fmt(int(last['giá_trị']))}** → mua {d['name'].title()} dư dả! 🎉"
                        )
                    st.markdown("")
                    if st.button("❤️ Tiếp tục nuôi quỹ!", key=f"vis_{d['name']}",
                                 use_container_width=True, type="primary"):
                        st.session_state.current_stage = 4; st.rerun()
                else:
                    st.info("Cừu Cần Cù sẽ giúp bạn tính toán chi phí cụ thể!")
    else:
        st.info("Bạn chưa có giấc mơ nào. Hãy quay lại và kể với Cừu Cần Cù! 🐑")

# ── STAGE 7 ───────────────────────────────────
elif stage == 7:
    col_img, col_title = st.columns([1, 5])
    with col_img: show_sheep(width=140)
    with col_title:
        st.title("🧬 Hồ Sơ Tài Chính Của Bạn")
        st.caption(f"Sau {len(mem['notes'])} cuộc trò chuyện, Cừu Cần Cù đã hiểu bạn hơn 🐑")

    genome = mem["wealth_genome"]
    GENOME_EXPLAIN = {
        "dream_type":  ("💭 Kiểu Giấc Mơ",
                        "Bạn đang hướng đến điều gì trong cuộc sống? Đây là động lực sâu nhất giúp bạn tiết kiệm."),
        "emotion_type": ("💓 Kiểu Cảm Xúc Tài Chính",
                         "Cách bạn cảm nhận và phản ứng với tiền bạc."),
        "risk_type":   ("🛡️ Khẩu Vị Rủi Ro",
                        "Mức độ rủi ro bạn thoải mái chấp nhận khi đầu tư."),
        "reward_type": ("🏆 Động Lực Của Bạn",
                        "Điều gì thúc đẩy bạn hành động và duy trì thói quen tốt."),
    }
    g1, g2 = st.columns(2)
    for k1, k2 in [("dream_type", "risk_type"), ("emotion_type", "reward_type")]:
        with g1:
            with st.container(border=True):
                title, desc = GENOME_EXPLAIN[k1]
                st.markdown(f"### {title}")
                st.markdown(f"## {genome[k1] or '🔍 Đang phân tích...'}")
                if genome[k1]: st.caption(desc)
        with g2:
            with st.container(border=True):
                title, desc = GENOME_EXPLAIN[k2]
                st.markdown(f"### {title}")
                st.markdown(f"## {genome[k2] or '🔍 Đang phân tích...'}")
                if genome[k2]: st.caption(desc)

    st.divider()
    st.subheader("📊 Quỹ Phù Hợp Với Bạn")
    fund_key = mem.get("selected_fund", "TCBF")
    fund = FUNDS[fund_key]
    with st.container(border=True):
        st.markdown(f"## {fund['emoji']} {fund['tên']}")
        st.markdown(f"**{fund['mô_tả']}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Lãi kỳ vọng", f"~{fund['lãi_suất']*100:.0f}%/năm")
        c2.metric("Mức rủi ro",  fund["rủi_ro"])
        c3.metric("Phù hợp nhất", fund["phù_hợp"])
        st.markdown("💡 *Bạn có thể đầu tư từ **10.000đ** mỗi lần – không cần số tiền lớn*")

    st.divider()
    st.subheader("💌 Cừu Cần Cù nhắn riêng cho bạn")
    if mem["dreams"]:
        dream_name = mem["dreams"][0]["name"]
        with st.container(border=True):
            col_a, col_b = st.columns([1, 5])
            with col_a: show_sheep("celebrate", width=70)
            with col_b:
                st.markdown(f"### 🌏 **{random.randint(30_000, 80_000):,} người** đang đầu tư quỹ để "
                            f"thực hiện **{dream_name.title()}** giống bạn!")
                st.markdown(f"Nhóm này đã đầu tư trung bình **{fmt(random.randint(8_000_000, 15_000_000))}** rồi 💪")
                st.markdown(f"Còn bạn đã có **{fmt(mem['total_saved'])}** – mỗi ngày một ít, "
                            "Cừu Cần Cù tin bạn sẽ đến đích! 🐑")
                if st.button("🐑 Tiếp tục nuôi quỹ!", use_container_width=True, type="primary"):
                    st.session_state.current_stage = 4; st.rerun()
    else:
        st.info("Hãy chia sẻ giấc mơ với Cừu Cần Cù để nhận thông điệp cá nhân hoá nhé! 🐑")

    if mem["life_events"]:
        st.divider()
        st.subheader("🏷️ Hành trình cuộc sống của bạn")
        cols = st.columns(min(5, len(mem["life_events"])))
        for i, tag in enumerate(mem["life_events"][:5]):
            cols[i].metric(LIFE_EVENT_ICONS.get(tag, "🏷️"), LIFE_EVENT_VI.get(tag, tag))

# ─────────────────────────────────────────────
# FEATURE 3.2 — SPENDING ANALYZER (triggered by Cashflow Problem)
# ─────────────────────────────────────────────
if st.session_state.get("show_spending_tool"):
    st.divider()
    with st.expander("💸 Cừu giúp bạn phân tích chi tiêu (Quy tắc 50/30/20)", expanded=True):
        col_sa, col_sb = st.columns(2)
        income_val   = col_sa.number_input("💰 Thu nhập hàng tháng (VNĐ)",
                                            min_value=0, step=500_000, value=10_000_000,
                                            format="%d")
        expenses_val = col_sb.number_input("💸 Tổng chi tiêu hàng tháng (VNĐ)",
                                            min_value=0, step=500_000, value=0,
                                            format="%d")
        if st.button("🐑 Phân tích ngay!", type="primary"):
            if income_val > 0:
                analysis = analyze_spending_5030(income_val, expenses_val)
                st.markdown(analysis)
                col_img2, col_text2 = st.columns([1, 5])
                with col_img2: show_sheep("saving", width=70)
                with col_text2:
                    st.markdown(
                        "**Rich Dad Poor Dad gợi ý:** Hãy tự trả lương cho bản thân trước!\n\n"
                        f"Bỏ ngay **{fmt(int(income_val * 0.10))}** (10% lương) vào quỹ TCBF "
                        "trước khi chi tiêu – đó là bước đầu tiên xây dựng tự do tài chính 🌱"
                    )

        # Image upload for receipt analysis (Feature 3.2)
        st.markdown("---")
        st.markdown("**📸 Hoặc tải ảnh hóa đơn/sao kê để Cừu phân tích:**")
        uploaded = st.file_uploader("Chọn ảnh", type=["jpg", "jpeg", "png"], key="receipt_img")
        if uploaded and st.session_state.api_key:
            if st.button("🐑 Cừu đọc hóa đơn này!"):
                img_bytes = uploaded.read()
                img_b64 = base64.b64encode(img_bytes).decode()
                media_type = "image/jpeg" if uploaded.name.lower().endswith((".jpg", ".jpeg")) else "image/png"
                vision_prompt = (
                    "Đây là ảnh hóa đơn hoặc sao kê chi tiêu của người dùng Việt Nam. "
                    "Hãy: 1) Liệt kê các khoản chi (tên + số tiền), 2) Tính tổng, "
                    "3) Phân loại: Nhu cầu thiết yếu / Mong muốn / Đầu tư, "
                    "4) Đưa 1-2 gợi ý tiết kiệm nhỏ. "
                    "Trả lời ngắn gọn bằng tiếng Việt, giọng ấm áp như Cừu Cần Cù."
                )
                with st.spinner("Cừu đang đọc hóa đơn... 🐑"):
                    try:
                        client = anthropic.Anthropic(api_key=st.session_state.api_key)
                        resp = client.messages.create(
                            model="claude-haiku-4-5-20251001", max_tokens=800,
                            messages=[{"role": "user", "content": [
                                {"type": "image", "source": {
                                    "type": "base64", "media_type": media_type, "data": img_b64
                                }},
                                {"type": "text", "text": vision_prompt},
                            ]}],
                        )
                        receipt_analysis = resp.content[0].text.strip()
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"🐑 **Cừu đã xem hóa đơn của bạn!**\n\n{receipt_analysis}",
                            "nudge": "", "savings": "",
                        })
                        st.success("Đã phân tích xong! Xem kết quả trong khung chat bên dưới 👇")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi phân tích ảnh: {e}")
        elif uploaded and not st.session_state.api_key:
            st.warning("🔑 Nhập API key ở thanh bên để Cừu đọc hóa đơn nhé!")

# ─────────────────────────────────────────────
# CHAT INPUT (all stages)
# ─────────────────────────────────────────────
st.divider()
if prompt := st.chat_input("Nhắn tin với Cừu Cần Cù... 🐑"):
    if not st.session_state.api_key:
        st.error("🔑 Bạn chưa nhập API key! Vui lòng nhập ở thanh bên.")
    else:
        send_message(prompt); st.rerun()

if stage > 2 and st.session_state.messages:
    last = st.session_state.messages[-1]
    if last["role"] == "assistant":
        # FIX 1.5 — use branded avatar (same as sidebar + same as chat history)
        with st.chat_message("assistant", avatar=get_sheep_img()):
            st.markdown(last["content"])
            if last.get("savings"): st.success(f"💡 **Gợi ý đầu tư:** {last['savings']}")
            elif last.get("nudge"): st.info(f"💡 {last['nudge']}")
