"""
╔══════════════════════════════════════════════════════════════╗
║        CỪU CẦN CÙ — v2.0 Production-Ready                  ║
║        Principal AI Engineer + Product Designer              ║
║        4 Tabs · Mascot Engine · Investment Coach             ║
╚══════════════════════════════════════════════════════════════╝

ASSETS NAMING GUIDE (đặt vào thư mục assets/):
  mascot.png              → cừu đội băng đỏ "CỪU CẦN CÙ" (default)
  sheep_listening.png     → cừu chống cằm lắng nghe
  sheep_happy.png         → cừu cười bắn tim
  sheep_sad.png           → cừu khóc, bát rỗng
  sheep_miss_you.png      → cừu nhớ bạn
  sheep_saving.png        → cừu bên heo đất
  sheep_celebrate.png     → cừu ăn mừng "ĐẠT MỤC TIÊU"
  sheep_determined.png    → cừu băng đỏ "QUYẾT TÂM"

  Nhiều ảnh cùng mood? → đặt tên: sheep_happy_1.png, sheep_happy_2.png ...
  Hệ thống tự random chọn 1 ảnh khi render.
"""

# ══════════════════════════════════════════════
# SECTION 1: IMPORTS & PAGE CONFIG
# ══════════════════════════════════════════════
import streamlit as st
import anthropic
import json
import random
import re
import base64
import glob
import os
import urllib.request
from datetime import datetime, timedelta
from copy import deepcopy

st.set_page_config(
    page_title="Cừu Cần Cù 🐑",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
# SECTION 2: MASCOT ENGINE (PHASE 2)
# Auto-scan assets/, random per mood, base64 embed
# ══════════════════════════════════════════════
_HERE       = os.path.dirname(os.path.abspath(__file__))
_ASSETS_DIR = os.path.join(_HERE, "assets")
_ROOT_MASCOT = os.path.join(_HERE, "mascot.png")

# Fallback SVG khi không có file nào
_SVG_SHEEP = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'%3E"
    "%3Ccircle cx='50' cy='50' r='48' fill='%23FFE4F0'/%3E"
    "%3Ctext y='.9em' x='10' font-size='72'%3E%F0%9F%90%91%3C/text%3E"
    "%3C/svg%3E"
)

# Mood → pattern list (ưu tiên theo thứ tự)
_MOOD_PATTERNS: dict[str, list[str]] = {
    "default":    ["mascot", "sheep_default", "sheep_happy"],
    "listening":  ["sheep_listening", "listening"],
    "happy":      ["sheep_happy", "happy"],
    "sad":        ["sheep_sad", "sad"],
    "miss_you":   ["sheep_miss_you", "miss_you"],
    "goal":       ["sheep_goal", "sheep_determined", "determined", "sheep_happy"],
    "saving":     ["sheep_saving", "saving"],
    "celebrate":  ["sheep_celebrate", "celebrate", "sheep_happy"],
    "determined": ["sheep_determined", "determined", "sheep_goal", "sheep_happy"],
}

@st.cache_data(ttl=300, show_spinner=False)
def _scan_assets() -> dict[str, list[str]]:
    """Scan assets/ + root, map mood → [filepath]. Cached 5 min."""
    if not os.path.exists(_ASSETS_DIR):
        os.makedirs(_ASSETS_DIR, exist_ok=True)

    all_files: list[str] = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        all_files += glob.glob(os.path.join(_ASSETS_DIR, ext))
    if os.path.exists(_ROOT_MASCOT):
        all_files.append(_ROOT_MASCOT)

    result: dict[str, list[str]] = {}
    for mood, patterns in _MOOD_PATTERNS.items():
        matched: list[str] = []
        for fp in all_files:
            fname = os.path.splitext(os.path.basename(fp))[0].lower()
            for p in patterns:
                if fname == p.lower() or fname.startswith(p.lower() + "_"):
                    matched.append(fp)
                    break
        result[mood] = matched
    return result


def _pick_mascot(mood: str = "default") -> str | None:
    """Return a random local path for the mood, with fallback chain."""
    assets = _scan_assets()
    files  = assets.get(mood, [])
    if not files:
        # Fallback cascade
        for fb in ("happy", "default"):
            files = assets.get(fb, [])
            if files:
                break
    if not files:
        return None
    return random.choice(files)


@st.cache_data(ttl=7200, show_spinner=False)
def _b64(path: str) -> str:
    """Local file → base64 data URI. Cached 2h."""
    if not path or not os.path.exists(path):
        return _SVG_SHEEP
    try:
        with open(path, "rb") as f:
            raw = f.read()
        ext  = path.rsplit(".", 1)[-1].lower()
        mime = {"png":"image/png","jpg":"image/jpeg",
                "jpeg":"image/jpeg","webp":"image/webp"}.get(ext,"image/png")
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except Exception:
        return _SVG_SHEEP


def show_sheep(mood: str | None = None, width: int = 160, caption: bool = True):
    """Render sheep avatar — base64 embedded, no CSP issues."""
    m    = mood or st.session_state.get("sheep_mood", "default")
    path = _pick_mascot(m)
    src  = _b64(path)
    badge_text = {
        "listening":  "👂 Cừu đang lắng nghe bạn...",
        "happy":      "😊 Cừu vui lắm! Bê bê~",
        "sad":        "🥺 Cừu hơi buồn... nhưng vẫn ở đây",
        "miss_you":   "💙 Cừu nhớ bạn lắm...",
        "goal":       "🎯 Cừu cùng bạn đặt mục tiêu!",
        "saving":     "💰 Tích tiểu thành đại!",
        "celebrate":  "🎉 Cừu ăn mừng cùng bạn! Bê bê~",
        "determined": "💪 Cùng nhau chinh phục mục tiêu!",
    }.get(m, "")
    st.markdown(
        f'<div style="text-align:center;margin:8px 0 6px;">'
        f'<img src="{src}" width="{width}" '
        f'style="border-radius:50%;border:4px solid #FFB5C8;'
        f'box-shadow:0 10px 32px rgba(255,140,190,0.5),'
        f'0 0 0 8px rgba(255,182,193,0.18);" /></div>',
        unsafe_allow_html=True,
    )
    if caption and badge_text:
        st.caption(badge_text)


def set_mood(mood: str):
    st.session_state.sheep_mood = mood


def get_avatar_src(mood: str | None = None) -> str:
    """Return base64 src for st.chat_message avatar=."""
    m    = mood or st.session_state.get("sheep_mood", "default")
    path = _pick_mascot(m)
    return _b64(path)


# ══════════════════════════════════════════════
# SECTION 3: KNOWLEDGE BASE (PHASE 7 + 8)
# TCEF / TCBF / TCFF + Investment Coach
# (Không hứa lợi nhuận, không khuyến nghị mua bán)
# ══════════════════════════════════════════════
FUNDS = {
    "TCEF": {
        "emoji":    "🚀",
        "tên":      "TCEF — Quỹ Cổ Phiếu Tăng Trưởng",
        "mô_tả":    "Thiên về cổ phiếu tăng trưởng — phù hợp ai muốn vốn lớn dài hạn",
        "chi_tiết": (
            "📈 **Thiên về cổ phiếu** — đầu tư chủ yếu vào cổ phiếu doanh nghiệp tăng trưởng.\n\n"
            "🎯 **Phù hợp với bạn nếu:** Chấp nhận lên xuống ngắn hạn, mục tiêu 3-5 năm+.\n\n"
            "⚖️ **Rủi ro:** Cao — giá trị có thể giảm mạnh trong ngắn hạn.\n\n"
            "💡 **Ý tưởng đơn giản:** Như trồng cây ăn trái — chờ được thì quả ngọt."
        ),
        "rủi_ro":   "⚡ Cao",
        "phù_hợp":  "Dài hạn 3-5 năm+, chấp nhận biến động",
        "màu":      "#FF6B6B",
    },
    "TCBF": {
        "emoji":    "🛡️",
        "tên":      "TCBF — Quỹ Trái Phiếu Ổn Định",
        "mô_tả":    "Thiên về trái phiếu — ổn định, ít biến động, phù hợp mục tiêu ngắn-trung hạn",
        "chi_tiết": (
            "🏦 **Thiên về trái phiếu** — đầu tư chủ yếu vào trái phiếu doanh nghiệp và chính phủ.\n\n"
            "🎯 **Phù hợp với bạn nếu:** Muốn tăng trưởng ổn định hơn gửi tiết kiệm, ít lo biến động.\n\n"
            "⚖️ **Rủi ro:** Thấp hơn — ít lên xuống bất ngờ.\n\n"
            "💡 **Ý tưởng đơn giản:** Như gửi tiết kiệm nâng cấp — ổn định hơn, linh hoạt hơn."
        ),
        "rủi_ro":   "🌿 Thấp-Trung",
        "phù_hợp":  "Ngắn-trung hạn 1-3 năm, muốn ổn định",
        "màu":      "#4ECDC4",
    },
    "TCFF": {
        "emoji":    "⚖️",
        "tên":      "TCFF — Quỹ Linh Hoạt Cân Bằng",
        "mô_tả":    "Cân bằng giữa cổ phiếu và trái phiếu — linh hoạt theo thị trường",
        "chi_tiết": (
            "🔄 **Cân bằng linh hoạt** — phân bổ giữa cổ phiếu và trái phiếu tùy diễn biến thị trường.\n\n"
            "🎯 **Phù hợp với bạn nếu:** Chưa chắc chắn về khẩu vị rủi ro, muốn cân bằng.\n\n"
            "⚖️ **Rủi ro:** Trung bình — nhỏ hơn TCEF, lớn hơn TCBF.\n\n"
            "💡 **Ý tưởng đơn giản:** Như bữa ăn đủ chất — không quá cay, không quá nhạt."
        ),
        "rủi_ro":   "🌊 Trung bình",
        "phù_hợp":  "Trung hạn 2-4 năm, muốn cân bằng",
        "màu":      "#A8E6CF",
    },
}

INVESTMENT_PRINCIPLES = {
    "DCA": {
        "tên":   "Đầu tư đều đặn (Dollar Cost Averaging)",
        "giải_thích": (
            "Thay vì cố chọn 'thời điểm vàng' mua một lần, "
            "bạn đầu tư một số tiền cố định đều đặn mỗi tháng/tuần.\n\n"
            "**Lợi ích:** Giảm rủi ro mua đúng lúc giá cao. "
            "Khi giá giảm, bạn tự động mua được nhiều hơn.\n\n"
            "**Ví dụ thực tế:** Bỏ 500k mỗi tháng vào quỹ — không cần quan tâm thị trường đang lên hay xuống."
        ),
    },
    "DIVERSIFICATION": {
        "tên":   "Đa dạng hóa danh mục",
        "giải_thích": (
            "Không bỏ tất cả trứng vào một giỏ.\n\n"
            "**Ý nghĩa:** Phân bổ vốn vào nhiều loại tài sản khác nhau "
            "để khi một loại giảm, loại khác có thể bù đắp.\n\n"
            "**Đơn giản hóa:** Có quỹ cổ phiếu (TCEF) lẫn quỹ trái phiếu (TCBF) "
            "= đã đa dạng hóa cơ bản."
        ),
    },
    "LONG_TERM": {
        "tên":   "Đầu tư dài hạn",
        "giải_thích": (
            "Thị trường ngắn hạn luôn biến động — nhưng dài hạn thường đi lên theo tăng trưởng kinh tế.\n\n"
            "**Nguyên tắc:** Đừng lo nếu giá giảm 1 tuần hay 1 tháng. "
            "Nhìn vào 3-5 năm.\n\n"
            "**Warren Buffett nói:** 'Thị trường chứng khoán là cỗ máy chuyển tiền "
            "từ người thiếu kiên nhẫn sang người kiên nhẫn.'"
        ),
    },
    "RISK_PROFILE": {
        "tên":   "Hiểu khẩu vị rủi ro của bạn",
        "giải_thích": (
            "Không có danh mục đầu tư 'tốt nhất cho tất cả mọi người'.\n\n"
            "**3 câu hỏi tự hỏi:**\n"
            "1. Nếu đầu tư 10 triệu và giảm còn 8 triệu, bạn có bán không?\n"
            "2. Mục tiêu của bạn là 1 năm hay 5 năm?\n"
            "3. Bạn cần tiền này gấp không?\n\n"
            "**Nếu hay lo lắng về số dư:** TCBF phù hợp hơn.\n"
            "**Nếu chấp nhận chờ đợi:** TCEF có tiềm năng cao hơn."
        ),
    },
}

FUND_RECOMMENDER = {
    # (thời_gian_năm, risk_tolerance) → fund_key
    (1, "low"):    "TCBF",
    (1, "medium"): "TCBF",
    (1, "high"):   "TCFF",
    (2, "low"):    "TCBF",
    (2, "medium"): "TCFF",
    (2, "high"):   "TCFF",
    (3, "low"):    "TCFF",
    (3, "medium"): "TCFF",
    (3, "high"):   "TCEF",
    (5, "low"):    "TCFF",
    (5, "medium"): "TCEF",
    (5, "high"):   "TCEF",
}


def recommend_fund(years: int, risk: str) -> str:
    """Simple rule-based fund recommendation. No financial promises."""
    y = min([k[0] for k in FUND_RECOMMENDER if k[0] >= years], default=5)
    return FUND_RECOMMENDER.get((y, risk), "TCFF")


# ══════════════════════════════════════════════
# SECTION 4: MEMORY ENGINE (PHASE 4+9)
# ══════════════════════════════════════════════
LIFE_EVENT_LABELS = {
    "education":      "📚 Học hành/Thi cử",
    "emotional":      "💙 Cảm xúc/Tình cảm",
    "career":         "💼 Công việc/Sự nghiệp",
    "family":         "👨‍👩‍👧 Gia đình",
    "health":         "🌱 Sức khỏe",
    "dream_travel":   "✈️ Mơ được đi du lịch",
    "dream_house":    "🏠 Mơ có ngôi nhà",
    "dream_car":      "🚗 Mơ có xe riêng",
    "dream_business": "🏪 Mơ khởi nghiệp",
    "cashflow":       "💸 Lo về tiền bạc",
    "milestone":      "🎯 Cột mốc cuộc sống",
    "stress":         "😓 Áp lực/Stress",
}

MEMORY_DEFAULT: dict = {
    "name":          "",
    "notes":         [],          # list of str
    "life_events":   [],          # list of tag strings
    "dreams":        [],          # list of {name, amount, saved, tags}
    "total_saved":   0,
    "streak":        0,
    "last_fed_date": "",
    "sentiment":     "neutral",   # positive / neutral / concerned
    "level":         1,
    "wealth_genome": {
        "dream_type":    "",
        "risk_type":     "",
        "saving_habit":  "",
        "personality":   "",
        "stage":         "",
    },
    "diary_entries": [],          # moved here from session_state
}

LEVELS = [
    (0,        1, "🌱 Chồi xanh",          "Mới bắt đầu hành trình!"),
    (100_000,  2, "🌿 Mầm xanh",           "Thói quen đang hình thành!"),
    (500_000,  3, "🌳 Cây nhỏ",            "Nhìn cừu lớn lên rồi!"),
    (1_000_000,4, "🌲 Cây trưởng thành",   "Nền tảng vững chắc!"),
    (5_000_000,5, "🌴 Rừng xanh",          "Tương lai vững vàng!"),
]

def get_level(total: int) -> tuple[int, str, str]:
    level, label, desc = 1, "🌱 Chồi xanh", "Mới bắt đầu hành trình!"
    for threshold, lv, lb, d in LEVELS:
        if total >= threshold:
            level, label, desc = lv, lb, d
    return level, label, desc


def fmt(n: int) -> str:
    return f"{n:,.0f}đ".replace(",", ".")


MICRO_AMOUNTS = [10_000, 20_000, 50_000, 100_000]


def _init_state():
    defaults = {
        "api_key":        "",
        "messages":       [],
        "user_memory":    deepcopy(MEMORY_DEFAULT),
        "sheep_mood":     "default",
        "active_tab":     0,
        "_quick_reply":   None,
        "feeding_today":  False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()
mem: dict = st.session_state.user_memory


def save_state():
    st.session_state.user_memory = mem


# ══════════════════════════════════════════════
# SECTION 5: LLM ENGINE
# ══════════════════════════════════════════════
SYSTEM_EMOTION = """Bạn là Cừu Cần Cù 🐑 — người bạn đồng hành cảm xúc, KHÔNG phải chuyên gia tài chính.

XƯNG HÔ: Mình (Cừu Cần Cù) – Bạn.
TUYỆT ĐỐI KHÔNG: xưng "em", nhắc cổ phiếu/lợi nhuận/NAV/khuyến nghị đầu tư.
TONE: Ấm áp 🌸 Nhẹ nhàng 🌿 Thỉnh thoảng "bê bê~".

QUY TẮC:
1. CẢM XÚC NGẮN (mệt/buồn/chán/vui/lo/sợ/buồn ngủ/stress): phản hồi đồng cảm NGAY, hỏi thêm 1 câu nhẹ
2. TUYỆT ĐỐI KHÔNG nói "bị lạc" hay "nói lại được không"
3. Nếu KH nhắc giấc mơ → ghi nhận, hỏi thêm nhẹ nhàng
4. Nhớ thông tin đã kể → nhắc lại khi phù hợp để KH cảm thấy được nhớ

PHÁT HIỆN & TAG:
học/thi → "education" | chia tay/buồn → "emotional" | việc làm → "career"
nhà ở/mua nhà → "dream_house" | du lịch → "dream_travel" | xe → "dream_car"
khởi nghiệp → "dream_business" | hết tiền/nợ → "cashflow" | stress → "stress"
gia đình → "family" | sức khỏe → "health" | cưới/sinh con → "milestone"

OUTPUT (JSON hợp lệ, KHÔNG text ngoài):
{
  "message": "Phản hồi ấm áp, max 3-4 câu, emoji nhẹ",
  "nudge_action": "Gợi ý hành động nhỏ (hoặc rỗng)",
  "memory_note": "Thông tin quan trọng cần nhớ (hoặc rỗng)",
  "tags": ["tag1", "tag2"],
  "dream_name": "tên giấc mơ (hoặc rỗng)",
  "dream_amount": 0,
  "mood": "listening|happy|sad|goal|celebrate|determined|default"
}"""

SYSTEM_DIARY = """Bạn là Cừu Cần Cù 🐑 — đọc nhật ký tâm sự và phân tích nhẹ nhàng.

Phân tích:
- Cảm xúc chủ đạo
- Phát hiện giấc mơ/mục tiêu ẩn
- Phát hiện áp lực/stress
- Gợi ý 1 hành động nhỏ tích cực

OUTPUT (JSON):
{
  "sheep_reply": "Phản hồi ấm áp 2-3 câu, bê bê~ nếu phù hợp",
  "emotion": "vui|buồn|lo|bình_thường|stress|mơ_mộng",
  "tags": ["tag1"],
  "dream_detected": "tên giấc mơ (rỗng nếu không)",
  "mood": "listening|happy|sad|goal|celebrate|determined"
}"""


def _extract_json(raw: str) -> dict:
    """4-strategy JSON extractor."""
    # 1. Direct parse
    try:
        return json.loads(raw.strip())
    except Exception:
        pass
    # 2. Strip fences
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    # 3. Regex search
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    # 4. Field extraction fallback
    msg = re.search(r'"message"\s*:\s*"([^"]+)"', raw)
    reply = re.search(r'"sheep_reply"\s*:\s*"([^"]+)"', raw)
    return {
        "message":     msg.group(1)   if msg   else "Bê bê~ 🐑 Cừu đang lắng nghe nè!",
        "sheep_reply": reply.group(1) if reply else "Bê bê~ 🐑 Cừu đọc nhật ký rồi nhé!",
        "nudge_action": "", "memory_note": "", "tags": [],
        "dream_name": "", "dream_amount": 0,
        "mood": "listening", "emotion": "bình_thường",
    }


EMOTION_EXPAND = {
    "mệt": "Mình đang cảm thấy mệt mỏi, cần được lắng nghe.",
    "buồn": "Mình đang buồn, muốn chia sẻ với Cừu.",
    "chán": "Mình đang cảm thấy chán nản.",
    "vui": "Mình đang vui, muốn kể Cừu nghe!",
    "lo": "Mình đang lo lắng về điều gì đó.",
    "sợ": "Mình đang cảm thấy sợ hãi.",
    "stress": "Mình đang bị stress, cần được đồng cảm.",
    "áp lực": "Mình đang chịu rất nhiều áp lực.",
    "cô đơn": "Mình đang cảm thấy cô đơn.",
    "buồn ngủ": "Mình đang buồn ngủ nhưng muốn nói chuyện với Cừu.",
    "tệ": "Mình đang cảm thấy tệ, mọi thứ không ổn.",
    "ok": "Mình bình thường, muốn hỏi thăm Cừu.",
    "oke": "Mình ổn, muốn nói chuyện một chút.",
    "hi": "Xin chào Cừu, mình muốn nói chuyện!",
    "hello": "Xin chào Cừu, mình muốn chia sẻ.",
    "hey": "Hey Cừu, mình muốn nói chuyện một chút!",
}

QUICK_REPLIES = [
    "Mình đang lo về chuyện học hành 📚",
    "Mình có một giấc mơ muốn thực hiện ✨",
    "Mình vừa trải qua chuyện không vui 💔",
    "Mình đang gặp khó khăn về tiền bạc 💸",
    "Mình muốn có điều gì đó cho riêng mình 🎯",
    "Mình đang nghĩ lại về con đường sự nghiệp 🌱",
]

CHIP_PROMPTS = {
    "Mình đang lo về chuyện học hành 📚":
        "Cừu ơi, mình đang rất lo lắng về việc học và kỳ thi sắp tới. Cừu có thể lắng nghe không?",
    "Mình có một giấc mơ muốn thực hiện ✨":
        "Cừu ơi, mình có một ước mơ muốn kể cho Cừu nghe và cần được động viên.",
    "Mình vừa trải qua chuyện không vui 💔":
        "Cừu ơi, mình vừa trải qua chuyện buồn, muốn chia sẻ với Cừu.",
    "Mình đang gặp khó khăn về tiền bạc 💸":
        "Cừu ơi, mình đang gặp khó khăn tài chính, cảm thấy áp lực lắm.",
    "Mình muốn có điều gì đó cho riêng mình 🎯":
        "Cừu ơi, mình muốn thực hiện một điều gì đó cho bản thân, nhưng chưa biết bắt đầu từ đâu.",
    "Mình đang nghĩ lại về con đường sự nghiệp 🌱":
        "Cừu ơi, mình đang cân nhắc thay đổi công việc/sự nghiệp, cần được lắng nghe.",
}


def send_chat(user_text: str, system: str = SYSTEM_EMOTION) -> dict:
    """Call Anthropic API, return parsed JSON result."""
    if not st.session_state.api_key:
        return {
            "message": "Bê bê~ 🐑 Bạn cần nhập API Key ở sidebar để Cừu có thể trò chuyện nhé!",
            "nudge_action": "", "memory_note": "", "tags": [],
            "dream_name": "", "dream_amount": 0,
            "mood": "listening", "sheep_reply": "",
        }
    try:
        # Build history context (last 8 messages)
        hist = st.session_state.messages[-8:]
        history_ctx = "\n".join(
            f"{'KH' if m['role']=='user' else 'Cừu'}: {m['content'][:120]}"
            for m in hist
        )
        mem_ctx = (
            f"Tên: {mem['name'] or 'chưa biết'}. "
            f"Tags: {', '.join(mem['life_events'][-6:]) or 'chưa có'}. "
            f"Ghi chú: {', '.join(mem['notes'][-3:]) or 'chưa có'}."
        )
        full_prompt = (
            f"[Memory: {mem_ctx}]\n"
            f"[Lịch sử gần đây:\n{history_ctx}]\n\n"
            f"KH vừa nói: {user_text}"
        )
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": full_prompt}],
        )
        result = _extract_json(resp.content[0].text)
        # Update memory
        if result.get("memory_note"):
            note = result["memory_note"]
            if note and note not in mem["notes"]:
                mem["notes"].append(note)
        for tag in result.get("tags", []):
            if tag and tag not in mem["life_events"]:
                mem["life_events"].append(tag)
        if result.get("dream_name") and result.get("dream_amount", 0) > 0:
            existing = [d["name"] for d in mem["dreams"]]
            if result["dream_name"] not in existing:
                mem["dreams"].append({
                    "name":   result["dream_name"],
                    "amount": result["dream_amount"],
                    "saved":  0,
                    "tags":   result.get("tags", []),
                })
        if result.get("mood"):
            set_mood(result["mood"])
        save_state()
        return result
    except Exception as e:
        return {
            "message": f"Bê bê~ 🐑 Cừu gặp lỗi nhỏ: {str(e)[:60]}. Bạn thử lại nhé!",
            "nudge_action": "", "memory_note": "", "tags": [],
            "dream_name": "", "dream_amount": 0, "mood": "sad", "sheep_reply": "",
        }


# ══════════════════════════════════════════════
# SECTION 6: CSS & THEME
# ══════════════════════════════════════════════
st.markdown("""
<style>
/* ── Background ── */
[data-testid="stApp"] {
    background: linear-gradient(145deg,
        #FFF8FB 0%, #FFF3F7 25%, #FAF0FF 55%,
        #F0F7FF 80%, #F5FBFF 100%) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #FFF5F9 0%, #FFECF4 35%, #F8EAFF 65%, #E8F4FF 100%) !important;
    border-right: 2px solid #FFCCE0 !important;
}

/* ── Typography ── */
h1 {
    font-size: 1.7rem !important; font-weight: 800 !important;
    color: #C4607F !important; letter-spacing: -0.3px !important;
}
h2 {
    font-size: 1.3rem !important; font-weight: 700 !important;
    color: #4E7DB8 !important;
}
h3 {
    font-size: 1.08rem !important; font-weight: 700 !important;
    color: #555 !important;
}
p, .stMarkdown p, label {
    font-size: 0.92rem !important; color: #444 !important;
    line-height: 1.65 !important;
}
strong { color: #333 !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 22px !important;
    border: 1.5px solid #FFB7D5 !important;
    background: linear-gradient(135deg, #FFF5FA, #EEF5FF) !important;
    color: #555 !important;
    font-size: 0.87rem !important;
    padding: 0.45rem 0.9rem !important;
    transition: all 0.2s ease !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FFD6E8, #D6E8FF) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(255,150,200,0.3) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF8FAF, #7EC8E3) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
    background: rgba(255,200,220,0.15) !important;
    border-radius: 16px !important;
    padding: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: #888 !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF8FAF, #7EC8E3) !important;
    color: white !important;
}

/* ── Chat ── */
[data-testid="stChatMessage"] {
    align-items: flex-start !important;
    gap: 12px !important;
    border-radius: 18px !important;
}
[data-testid="stChatMessage"] img {
    width: 56px !important; height: 56px !important;
    min-width: 56px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 2px solid #FFB5C8 !important;
    box-shadow: 0 4px 12px rgba(255,150,200,0.3) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #FFF8FC, #F5F8FF) !important;
    border-radius: 14px !important;
    border: 1px solid #FFD6E8 !important;
    padding: 8px !important;
}

/* ── Progress ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #FF8FAF, #7EC8E3) !important;
    border-radius: 10px !important;
}

/* ── Cards ── */
.sheep-card {
    background: linear-gradient(135deg, #FFF9FC, #F5F8FF);
    border-radius: 16px;
    border: 1px solid #FFD6E8;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.profile-card {
    background: white;
    border-radius: 20px;
    border: 2px solid #FFD6E8;
    padding: 20px 24px;
    box-shadow: 0 4px 20px rgba(255,150,200,0.15);
    margin-bottom: 16px;
}
.level-badge {
    display: inline-block;
    background: linear-gradient(135deg, #FF8FAF, #7EC8E3);
    color: white;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.85rem;
    font-weight: 700;
    margin: 4px 0;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# SECTION 7: SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    show_sheep(width=110)
    st.markdown("## Cừu Cần Cù 🐑")
    st.caption("Người bạn đồng hành tài chính ấm áp")

    st.divider()
    key_in = st.text_input(
        "🔑 Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-...",
    )
    if key_in:
        st.session_state.api_key = key_in

    st.divider()
    st.subheader("🧠 Bộ Nhớ Cừu")
    c1, c2 = st.columns(2)
    c1.metric("🔥 Streak", f"{mem['streak']} ngày")
    c2.metric("Cảm xúc", {"positive": "😊", "concerned": "😟", "neutral": "😐"}.get(
        mem["sentiment"], "😐"))

    if mem["name"]:
        st.info(f"👤 {mem['name']}")

    _, level_label, _ = get_level(mem["total_saved"])
    st.markdown(
        f'<div class="level-badge">{level_label}</div>',
        unsafe_allow_html=True,
    )
    if mem["total_saved"] > 0:
        st.caption(f"💰 Đã tích lũy: **{fmt(mem['total_saved'])}**")

    if mem["life_events"]:
        st.write("🏷️ **Tags:**")
        for t in mem["life_events"][-5:]:
            st.caption(LIFE_EVENT_LABELS.get(t, t))

    if mem["dreams"]:
        st.write("💭 **Giấc mơ:**")
        for d in mem["dreams"][-3:]:
            st.write(f"✨ {d['name'].title()}")
            if d["amount"] > 0:
                pct = min(100, d["saved"] / d["amount"] * 100)
                st.progress(pct / 100, text=f"{pct:.0f}%")

    st.divider()
    if st.button("🗑️ Đặt lại tất cả", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.caption("Được tạo bởi Claude 💙")


# ══════════════════════════════════════════════
# SECTION 8: 4-TAB DEMO NAVIGATION (PHASE 3)
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chia sẻ cảm xúc",
    "📔 Nhật ký tâm sự",
    "❤️ Hành trình nuôi cừu",
    "🧬 Hồ sơ tài chính",
])


# ══════════════════════════════════════════════
# SECTION 9: TAB 1 — CHIA SẺ CẢM XÚC (PHASE 4)
# Gộp stages 1+2: emotional chat + memory
# ══════════════════════════════════════════════
with tab1:
    # Header
    col_img, col_title = st.columns([1, 4])
    with col_img:
        show_sheep("listening", width=160)
    with col_title:
        st.title("💬 Chia Sẻ Cảm Xúc")
        st.markdown(
            "*Cừu ở đây lắng nghe — không phán xét, không so sánh* 🐑\n\n"
            "Bạn có thể kể về học hành, công việc, gia đình, tình cảm, hay bất cứ điều gì trong lòng."
        )

    st.markdown("---")

    # Quick reply chips
    if not st.session_state.messages:
        st.markdown("#### 🐑 Hôm nay bạn cảm thấy thế nào?")
        st.caption("Chọn điều gần nhất với bạn:")
        qcols = st.columns(3)
        for i, lbl in enumerate(QUICK_REPLIES):
            if qcols[i % 3].button(lbl, use_container_width=True, key=f"qr_{i}"):
                st.session_state._quick_reply = lbl
                st.rerun()

    # Handle quick reply
    if st.session_state._quick_reply:
        qr        = st.session_state._quick_reply
        full_text = CHIP_PROMPTS.get(qr, qr)
        st.session_state._quick_reply = None
        st.session_state.messages.append({"role": "user", "content": qr})
        with st.spinner("Cừu đang suy nghĩ... 🐑"):
            result = send_chat(full_text)
        reply = result.get("message") or "Bê bê~ 🐑 Cừu đang lắng nghe nè!"
        st.session_state.messages.append({
            "role": "assistant", "content": reply,
            "nudge": result.get("nudge_action", ""),
        })
        st.rerun()

    # Chat history
    if st.session_state.messages:
        st.markdown("---")
        for m in st.session_state.messages[-10:]:
            avatar = get_avatar_src() if m["role"] == "assistant" else "🧑"
            with st.chat_message(m["role"], avatar=avatar):
                st.markdown(m["content"])
                if m.get("nudge"):
                    st.info(f"💡 {m['nudge']}")

    # Chat input
    user_msg = st.chat_input("Nhắn tin với Cừu Cần Cù... 🐑")
    if user_msg:
        # Expand short emotions
        expanded = EMOTION_EXPAND.get(user_msg.strip().lower(), user_msg)
        st.session_state.messages.append({"role": "user", "content": user_msg})
        with st.spinner("Cừu đang lắng nghe... 🐑"):
            result = send_chat(expanded)
        reply = result.get("message") or "Bê bê~ 🐑 Cừu đang lắng nghe nè!"
        st.session_state.messages.append({
            "role": "assistant", "content": reply,
            "nudge": result.get("nudge_action", ""),
        })
        st.rerun()


# ══════════════════════════════════════════════
# SECTION 10: TAB 2 — NHẬT KÝ TÂM SỰ (PHASE 5)
# Timeline: Hôm nay / Tuần này / Tháng này
# ══════════════════════════════════════════════
with tab2:
    col_img2, col_title2 = st.columns([1, 4])
    with col_img2:
        show_sheep("listening", width=160)
    with col_title2:
        st.title("📔 Nhật Ký Tâm Sự")
        st.markdown("*Cừu giữ bí mật — viết ra để nhẹ lòng* 🌿")

    st.markdown("---")

    diary_entries: list[dict] = mem.get("diary_entries", [])

    DIARY_MOODS = {
        "😊 Vui": "positive",
        "😐 Bình thường": "neutral",
        "😔 Buồn": "sad",
        "😤 Bực": "stressed",
        "😴 Mệt": "tired",
        "🥺 Lo lắng": "anxious",
        "💪 Quyết tâm": "determined",
    }

    col_write, col_history = st.columns([3, 2])

    with col_write:
        st.subheader("✍️ Viết tâm sự hôm nay")
        diary_title = st.text_input(
            "Tiêu đề (tuỳ chọn)",
            placeholder="Hôm nay mình cảm thấy...",
            key="diary_title",
        )
        diary_mood_sel = st.radio(
            "Tâm trạng:",
            list(DIARY_MOODS.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key="diary_mood_sel",
        )
        diary_text = st.text_area(
            "Tâm sự của bạn 🌿",
            placeholder="Hôm nay mình cảm thấy... Chuyện xảy ra là...",
            height=220,
            key="diary_text",
        )

        if st.button("💾 Lưu vào nhật ký", type="primary", use_container_width=True):
            if diary_text.strip():
                # Analyze with LLM
                sheep_reply  = "Bê bê~ 🐑 Cừu đã đọc rồi! Cảm ơn bạn đã tin tưởng chia sẻ 💙"
                emotion_tag  = "bình_thường"
                dream_det    = ""
                entry_tags: list[str] = []

                if st.session_state.api_key:
                    with st.spinner("Cừu đang đọc nhật ký... 🐑"):
                        diary_prompt = (
                            f"Nhật ký của KH:\nTiêu đề: {diary_title or '(trống)'}\n"
                            f"Tâm trạng chọn: {diary_mood_sel}\n"
                            f"Nội dung: {diary_text[:500]}"
                        )
                        r = send_chat(diary_prompt, system=SYSTEM_DIARY)
                        sheep_reply = r.get("sheep_reply") or sheep_reply
                        emotion_tag = r.get("emotion", "bình_thường")
                        dream_det   = r.get("dream_detected", "")
                        entry_tags  = r.get("tags", [])
                        if r.get("mood"):
                            set_mood(r["mood"])

                entry = {
                    "id":       datetime.now().isoformat(),
                    "date":     datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "date_raw": datetime.now().isoformat(),
                    "title":    diary_title.strip() or f"Ngày {datetime.now().strftime('%d/%m')}",
                    "mood":     diary_mood_sel,
                    "content":  diary_text.strip(),
                    "emotion":  emotion_tag,
                    "tags":     entry_tags,
                    "dream":    dream_det,
                    "reply":    sheep_reply,
                }
                diary_entries.insert(0, entry)
                mem["diary_entries"] = diary_entries
                save_state()

                st.success(f"🐑 **Cừu nhắn:** {sheep_reply}")
                if dream_det:
                    st.info(f"✨ Cừu phát hiện giấc mơ: **{dream_det}**!")
                st.rerun()
            else:
                st.warning("Bạn chưa viết gì! Cừu muốn nghe chuyện của bạn nè 🐑")

        if diary_entries:
            dl_data = json.dumps(diary_entries, ensure_ascii=False, indent=2)
            st.download_button(
                "⬇️ Tải nhật ký về máy",
                dl_data,
                file_name="nhat_ky_tam_su.json",
                mime="application/json",
            )

    with col_history:
        st.subheader(f"📅 Timeline ({len(diary_entries)} trang)")

        if not diary_entries:
            show_sheep("miss_you", width=130, caption=True)
            st.caption("Chưa có trang nhật ký nào. Bắt đầu viết đi bạn! 🌿")
        else:
            # Filter tabs: Hôm nay / Tuần này / Tháng này
            filter_opt = st.radio(
                "Xem:",
                ["📅 Hôm nay", "📆 Tuần này", "🗓️ Tháng này", "📚 Tất cả"],
                horizontal=True,
                label_visibility="collapsed",
                key="diary_filter",
            )
            now = datetime.now()
            filtered = diary_entries
            if filter_opt == "📅 Hôm nay":
                filtered = [
                    e for e in diary_entries
                    if e["date_raw"][:10] == now.strftime("%Y-%m-%d")
                ]
            elif filter_opt == "📆 Tuần này":
                week_ago = (now - timedelta(days=7)).isoformat()
                filtered = [e for e in diary_entries if e["date_raw"] >= week_ago]
            elif filter_opt == "🗓️ Tháng này":
                month_start = now.strftime("%Y-%m")
                filtered = [e for e in diary_entries if e["date_raw"][:7] == month_start]

            search = st.text_input("🔍 Tìm kiếm", placeholder="Từ khoá...", key="diary_search")
            if search:
                filtered = [
                    e for e in filtered
                    if search.lower() in e["content"].lower()
                    or search.lower() in e["title"].lower()
                ]

            st.caption(f"Hiển thị {len(filtered)} trang")
            for entry in filtered:
                with st.expander(
                    f"{entry['mood']} **{entry['title']}** — {entry['date']}"
                ):
                    st.markdown(entry["content"])
                    if entry.get("reply"):
                        st.info(f"🐑 Cừu: {entry['reply']}")
                    if entry.get("dream"):
                        st.success(f"✨ Giấc mơ: {entry['dream']}")
                    tags_str = " ".join(
                        LIFE_EVENT_LABELS.get(t, t) for t in entry.get("tags", [])
                    )
                    if tags_str:
                        st.caption(tags_str)
                    if st.button("🗑️ Xoá", key=f"del_{entry['id']}"):
                        mem["diary_entries"] = [
                            e for e in diary_entries if e["id"] != entry["id"]
                        ]
                        save_state()
                        st.rerun()


# ══════════════════════════════════════════════
# SECTION 11: TAB 3 — HÀNH TRÌNH NUÔI CỪU (PHASE 6)
# Gộp stages 4+5+6: feeding + habit + journey
# ══════════════════════════════════════════════
with tab3:
    col_img3, col_title3 = st.columns([1, 4])
    with col_img3:
        current_sheep_mood = st.session_state.sheep_mood
        show_sheep(current_sheep_mood, width=160)
    with col_title3:
        st.title("❤️ Hành Trình Nuôi Cừu")
        st.markdown("*Mỗi đồng nhỏ hôm nay là nền móng cho ước mơ mai sau* 🌱")

    st.markdown("---")

    # Level display
    lv_num, lv_label, lv_desc = get_level(mem["total_saved"])
    c_lv1, c_lv2, c_lv3 = st.columns(3)
    c_lv1.metric("🐑 Level", lv_label)
    c_lv2.metric("💰 Đã tích lũy", fmt(mem["total_saved"]))
    c_lv3.metric("🔥 Streak", f"{mem['streak']} ngày")

    # Level progress bar
    thresholds = [t for t, *_ in LEVELS]
    next_idx   = min(lv_num, len(thresholds) - 1)
    curr_thresh = thresholds[lv_num - 1]
    next_thresh = thresholds[next_idx] if next_idx < len(thresholds) else thresholds[-1]
    if next_thresh > curr_thresh:
        progress_to_next = min(1.0, (mem["total_saved"] - curr_thresh) / (next_thresh - curr_thresh))
        st.progress(progress_to_next, text=f"Level {lv_num} → {lv_num+1}: {fmt(next_thresh - mem['total_saved'])} nữa")
    st.caption(lv_desc)

    st.markdown("---")

    # Feeding section
    col_feed, col_info = st.columns([3, 2])
    with col_feed:
        st.subheader("🍀 Hôm nay cho Cừu ăn gì?")
        st.caption("Mỗi lần cho ăn = bạn đang đầu tư vào tương lai của mình!")

        # Mood status
        if current_sheep_mood == "happy":
            st.success("🐑 Cừu no bụng rồi, hạnh phúc lắm! Bê bê~ ❤️")
        elif current_sheep_mood == "sad":
            st.warning("🐑 Cừu hơi đói... nhưng vẫn ở đây với bạn 🥺")
        else:
            st.info("🐑 Bê bê~ Hôm nay bạn cho Cừu ăn gì nhé?")

        # Feed buttons
        btn_cols = st.columns(4)
        for i, amt in enumerate(MICRO_AMOUNTS):
            if btn_cols[i].button(f"❤️ {fmt(amt)}", use_container_width=True, key=f"feed_{amt}", type="primary"):
                mem["total_saved"] += amt
                mem["streak"]      += 1
                mem["last_fed_date"] = datetime.now().strftime("%Y-%m-%d")
                set_mood("happy")
                save_state()
                st.balloons()
                st.success(
                    f"🐑 Cừu được ăn {fmt(amt)}! Bê bê~ ❤️\n\n"
                    f"Bạn vừa tích lũy {fmt(amt)} cho tương lai. Tích tiểu thành đại!"
                )
                st.rerun()

        # Custom amount
        custom = st.number_input(
            "Hoặc nhập số khác:",
            min_value=1_000, max_value=100_000_000,
            step=10_000, value=30_000,
            key="custom_feed",
        )
        if st.button(f"❤️ Đầu tư {fmt(int(custom))}", use_container_width=True, type="primary"):
            mem["total_saved"] += int(custom)
            mem["streak"]      += 1
            set_mood("happy")
            save_state()
            st.balloons()
            st.success(f"🐑 Tuyệt vời! {fmt(int(custom))} vừa được đầu tư vào tương lai của bạn!")
            st.rerun()

        if not st.session_state.feeding_today:
            if st.button("⏩ Hôm nay bỏ qua", use_container_width=True):
                set_mood("sad")
                st.session_state.feeding_today = True
                save_state()
                st.rerun()

    with col_info:
        st.subheader("🎯 Giấc mơ đang nuôi")
        if mem["dreams"]:
            for d in mem["dreams"][:3]:
                with st.container(border=True):
                    st.markdown(f"**✨ {d['name'].title()}**")
                    if d["amount"] > 0:
                        pct = min(100, d["saved"] / d["amount"] * 100)
                        st.progress(pct / 100, text=f"{pct:.1f}%")
                        st.caption(f"{fmt(d['saved'])} / {fmt(d['amount'])}")
                        remain = d["amount"] - d["saved"]
                        if remain > 0:
                            st.caption(f"Còn {fmt(remain)} nữa 💪")
                        if st.button(f"❤️ Nuôi '{d['name'].title()}'",
                                     key=f"dream_feed_{d['name']}", use_container_width=True):
                            d["saved"] = min(d["amount"], d["saved"] + 50_000)
                            set_mood("celebrate" if d["saved"] >= d["amount"] else "happy")
                            save_state()
                            st.rerun()
        else:
            st.info("Hãy kể với Cừu về giấc mơ của bạn ở tab 💬 nhé! 🌟")

    st.markdown("---")

    # Investment Coach section
    st.subheader("🎓 Cừu Giải Thích — Quỹ Đầu Tư Là Gì?")
    st.caption("Kiến thức tài chính đơn giản — không hứa lợi nhuận, không khuyến nghị mua bán")

    ic_tab1, ic_tab2, ic_tab3, ic_tab4 = st.tabs([
        "🚀 TCEF", "🛡️ TCBF", "⚖️ TCFF", "📚 Kiến thức"
    ])

    with ic_tab1:
        f = FUNDS["TCEF"]
        st.markdown(f"## {f['emoji']} {f['tên']}")
        st.markdown(f['chi_tiết'])
        st.error(f"**Rủi ro:** {f['rủi_ro']} | **Phù hợp:** {f['phù_hợp']}")

    with ic_tab2:
        f = FUNDS["TCBF"]
        st.markdown(f"## {f['emoji']} {f['tên']}")
        st.markdown(f['chi_tiết'])
        st.success(f"**Rủi ro:** {f['rủi_ro']} | **Phù hợp:** {f['phù_hợp']}")

    with ic_tab3:
        f = FUNDS["TCFF"]
        st.markdown(f"## {f['emoji']} {f['tên']}")
        st.markdown(f['chi_tiết'])
        st.info(f"**Rủi ro:** {f['rủi_ro']} | **Phù hợp:** {f['phù_hợp']}")

    with ic_tab4:
        for key, principle in INVESTMENT_PRINCIPLES.items():
            with st.expander(f"📖 {principle['tên']}"):
                st.markdown(principle['giải_thích'])

    # Fund recommender
    st.markdown("---")
    st.subheader("🤔 Quỹ nào phù hợp với bạn?")
    st.caption("Cừu gợi ý dựa trên thông tin bạn cung cấp — KHÔNG phải tư vấn đầu tư chuyên nghiệp")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        years_opt = st.selectbox(
            "Mục tiêu của bạn là bao lâu?",
            [1, 2, 3, 5],
            format_func=lambda x: f"{x} năm",
            key="rec_years",
        )
    with r_col2:
        risk_opt = st.selectbox(
            "Bạn chấp nhận rủi ro như thế nào?",
            ["low", "medium", "high"],
            format_func=lambda x: {"low":"🌿 Thấp — tôi hay lo lắng",
                                    "medium":"🌊 Trung bình — tôi cân bằng",
                                    "high":"⚡ Cao — tôi chấp nhận biến động"}[x],
            key="rec_risk",
        )
    rec_fund = recommend_fund(years_opt, risk_opt)
    rf       = FUNDS[rec_fund]
    st.info(
        f"🐑 **Cừu gợi ý:** {rf['emoji']} **{rf['tên']}**\n\n"
        f"{rf['mô_tả']}\n\n"
        f"⚠️ *Đây chỉ là gợi ý tham khảo, không phải tư vấn đầu tư chuyên nghiệp. "
        f"Bạn hãy tự nghiên cứu thêm trước khi quyết định.*"
    )


# ══════════════════════════════════════════════
# SECTION 12: TAB 4 — HỒ SƠ TÀI CHÍNH (PHASE 9)
# Financial profile card built from conversations
# ══════════════════════════════════════════════
with tab4:
    col_img4, col_title4 = st.columns([1, 4])
    with col_img4:
        show_sheep("determined", width=160)
    with col_title4:
        st.title("🧬 Hồ Sơ Tài Chính")
        st.markdown("*Cừu xây dựng hồ sơ dựa trên câu chuyện của bạn* 🌟")

    st.markdown("---")

    genome = mem.get("wealth_genome", {})
    has_data = any([
        mem["dreams"], mem["life_events"], mem["notes"],
        mem["total_saved"] > 0, genome.get("risk_type"),
    ])

    if not has_data:
        show_sheep("miss_you", width=130)
        st.info(
            "**Hồ sơ tài chính đang trống** 🌿\n\n"
            "Hãy chia sẻ chuyện của bạn ở tab **💬 Chia sẻ cảm xúc** "
            "hoặc viết **📔 Nhật ký tâm sự** — Cừu sẽ tự động xây dựng hồ sơ cho bạn!"
        )
    else:
        # ── Profile Card ──
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown("### 🐑 Hồ Sơ Tài Chính của Bạn")
        st.divider()

        pc1, pc2 = st.columns(2)

        with pc1:
            # Biggest dream
            st.markdown("#### 💭 Giấc mơ lớn nhất")
            if mem["dreams"]:
                top_dream = max(mem["dreams"], key=lambda d: d["amount"])
                st.markdown(f"**✨ {top_dream['name'].title()}**")
                if top_dream["amount"] > 0:
                    pct = min(100, top_dream["saved"] / top_dream["amount"] * 100)
                    st.progress(pct / 100, text=f"{pct:.0f}% tiến độ")
                    st.caption(f"Mục tiêu: {fmt(top_dream['amount'])}")
            else:
                st.caption("Chưa xác định — hãy kể với Cừu!")

            st.markdown("#### 🏷️ Sự kiện cuộc sống")
            if mem["life_events"]:
                for t in list(dict.fromkeys(mem["life_events"]))[:6]:
                    st.markdown(f"• {LIFE_EVENT_LABELS.get(t, t)}")
            else:
                st.caption("Chưa có thông tin")

            st.markdown("#### 💰 Thói quen tích lũy")
            lv_n, lv_l, lv_d = get_level(mem["total_saved"])
            st.markdown(
                f'<span class="level-badge">{lv_l}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"Đã tích lũy: **{fmt(mem['total_saved'])}** · Streak: **{mem['streak']} ngày**")

        with pc2:
            # Risk profile quiz
            st.markdown("#### 🛡️ Khẩu vị rủi ro")
            risk_quiz = st.radio(
                "Nếu đầu tư 10 triệu và còn 8 triệu, bạn:",
                ["😰 Bán ngay, không dám chờ",
                 "🤔 Chờ xem, phân vân",
                 "😎 Không lo, đầu tư thêm"],
                key="risk_quiz",
                label_visibility="collapsed",
            )
            risk_map = {
                "😰 Bán ngay, không dám chờ":  ("low",    "🌿 Ưa ổn định", "TCBF"),
                "🤔 Chờ xem, phân vân":          ("medium", "🌊 Cân bằng",   "TCFF"),
                "😎 Không lo, đầu tư thêm":      ("high",   "⚡ Dám rủi ro",  "TCEF"),
            }
            risk_val, risk_label, risk_fund = risk_map[risk_quiz]
            genome["risk_type"] = risk_label
            save_state()
            st.markdown(f"**{risk_label}**")
            st.caption(f"Quỹ phù hợp tham khảo: **{risk_fund}**")

            # Motivation
            st.markdown("#### 🔥 Động lực")
            motivation = st.selectbox(
                "Bạn tích lũy chủ yếu vì:",
                ["Muốn an tâm về tương lai", "Có giấc mơ muốn thực hiện",
                 "Trách nhiệm với gia đình", "Muốn tự do tài chính",
                 "Đang thử nghiệm, chưa chắc"],
                key="motivation_sel",
            )
            genome["personality"] = motivation
            save_state()
            st.markdown(f"*'{motivation}'*")

            # Saving habit
            st.markdown("#### 📈 Giai đoạn")
            stage_sel = st.selectbox(
                "Bạn đang ở giai đoạn:",
                ["🌱 Mới bắt đầu tích lũy", "🌿 Đang hình thành thói quen",
                 "🌳 Đã có nền tảng vững", "🌴 Tối ưu hóa danh mục"],
                key="stage_sel",
            )
            genome["stage"] = stage_sel
            save_state()
            st.markdown(f"**{stage_sel}**")

        st.markdown('</div>', unsafe_allow_html=True)

        # All dreams progress
        if len(mem["dreams"]) > 1:
            st.markdown("---")
            st.subheader("✨ Tất cả giấc mơ đang theo đuổi")
            for d in mem["dreams"]:
                with st.container(border=True):
                    dca, dcb = st.columns([3, 2])
                    with dca:
                        st.markdown(f"**{d['name'].title()}**")
                        if d["amount"] > 0:
                            pct = min(100, d["saved"] / d["amount"] * 100)
                            st.progress(pct / 100, text=f"{pct:.1f}%")
                    with dcb:
                        if d["amount"] > 0:
                            st.metric("Mục tiêu", fmt(d["amount"]))
                            st.caption(f"Đã: {fmt(d['saved'])}")

        # Investment Coach recommendation
        st.markdown("---")
        st.subheader("💡 Gợi ý từ Cừu Coach")
        rec_key  = recommend_fund(3, risk_val)
        rec_info = FUNDS[rec_key]

        coach_col1, coach_col2, coach_col3 = st.columns(3)
        with coach_col1:
            with st.container(border=True):
                st.markdown(f"### {rec_info['emoji']}")
                st.markdown(f"**{rec_key}**")
                st.caption(rec_info["mô_tả"])
                st.caption(f"Rủi ro: {rec_info['rủi_ro']}")
        with coach_col2:
            with st.container(border=True):
                st.markdown("### 🔄")
                st.markdown("**Đầu tư đều đặn**")
                st.caption(INVESTMENT_PRINCIPLES["DCA"]["giải_thích"][:120] + "...")
        with coach_col3:
            with st.container(border=True):
                st.markdown("### 📅")
                st.markdown("**Dài hạn**")
                st.caption(INVESTMENT_PRINCIPLES["LONG_TERM"]["giải_thích"][:120] + "...")

        st.warning(
            "⚠️ **Lưu ý quan trọng:** Tất cả thông tin trên chỉ mang tính tham khảo và giáo dục tài chính cơ bản. "
            "Cừu Cần Cù KHÔNG phải là công ty tư vấn đầu tư được cấp phép. "
            "Bạn hãy tự nghiên cứu kỹ và/hoặc tham khảo chuyên gia tài chính trước khi đưa ra quyết định đầu tư."
        )
