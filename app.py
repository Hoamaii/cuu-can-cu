"""
╔══════════════════════════════════════════════════════════════════╗
║        CỪU CẦN CÙ — v3.0 Production-Ready                      ║
║        Principal PM · CX Designer · Streamlit Engineer          ║
╚══════════════════════════════════════════════════════════════════╝

ASSETS — đặt vào thư mục  assets/  trong repo:

MOOD IMAGES (cảm xúc):
  sheep_listening.png   → cừu chống cằm lắng nghe
  sheep_happy.png       → cừu cười bắn tim
  sheep_sad.png         → cừu khóc, bát rỗng
  sheep_miss_you.png    → cừu nhớ bạn lắm
  sheep_saving.png      → cừu bên heo đất
  sheep_celebrate.png   → cừu ăn mừng ĐẠT MỤC TIÊU
  sheep_determined.png  → cừu băng đỏ QUYẾT TÂM

GROWTH STAGES (5 giai đoạn lớn lên — ảnh vừa upload):
  sheep_baby.png    → cừu sơ sinh (mặc tã, siêu cute)
  sheep_child.png   → cừu non (áo hoodie đỏ, shorts)
  sheep_teen.png    → cừu thiếu niên (đồng phục vest + balo)
  sheep_adult.png   → cừu trưởng thành (vest 3 mảnh navy + đồng hồ)
  sheep_master.png  → cừu lão luyện (áo lông, kính vàng, gậy, dây chuyền)

DEFAULT:
  mascot.png        → cừu mặc vest đỏ tươi (avatar chính)

Nhiều ảnh cùng mood: sheep_happy_1.png, sheep_happy_2.png → random 1 cái.
"""

# ═══════════════════════════════════════════════════════
# IMPORTS & PAGE CONFIG
# ═══════════════════════════════════════════════════════
import streamlit as st
import anthropic
import json
import random
import re
import base64
import glob
import os
from datetime import datetime, timedelta
from copy import deepcopy

st.set_page_config(
    page_title="Cừu Cần Cù 🐑",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════
# MASCOT ENGINE — Auto-scan assets/, random per mood
# ═══════════════════════════════════════════════════════
_HERE        = os.path.dirname(os.path.abspath(__file__))
_ASSETS_DIR  = os.path.join(_HERE, "assets")
_ROOT_MASCOT = os.path.join(_HERE, "mascot.png")

_SVG_SHEEP = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'%3E"
    "%3Ccircle cx='50' cy='50' r='48' fill='%23FFE4F0'/%3E"
    "%3Ctext y='.88em' x='10' font-size='76'%3E%F0%9F%90%91%3C/text%3E"
    "%3C/svg%3E"
)

# Mood → file patterns (thứ tự ưu tiên)
_MOOD_PATTERNS: dict[str, list[str]] = {
    # Cảm xúc tức thời
    "default":    ["mascot", "sheep_adult", "sheep_happy"],
    "listening":  ["sheep_listening", "listening"],
    "happy":      ["sheep_happy", "happy"],
    "sad":        ["sheep_sad", "sad"],
    "miss_you":   ["sheep_miss_you", "miss_you"],
    "saving":     ["sheep_saving", "saving"],
    "celebrate":  ["sheep_celebrate", "celebrate", "sheep_happy"],
    "determined": ["sheep_determined", "determined", "sheep_goal"],
    "goal":       ["sheep_determined", "sheep_goal", "determined"],
    # Giai đoạn trưởng thành
    "baby":   ["sheep_baby",   "baby"],
    "child":  ["sheep_child",  "child"],
    "teen":   ["sheep_teen",   "teen"],
    "adult":  ["sheep_adult",  "adult"],
    "master": ["sheep_master", "master"],
}


@st.cache_data(ttl=300, show_spinner=False)
def _scan_assets() -> dict[str, list[str]]:
    """Scan assets/ + root. Return {mood: [filepath, ...]}."""
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
    assets = _scan_assets()
    files  = assets.get(mood, [])
    if not files:
        for fb in ("happy", "adult", "default"):
            files = assets.get(fb, [])
            if files:
                break
    if not files:
        return None
    return random.choice(files)


@st.cache_data(ttl=7200, show_spinner=False)
def _b64(path: str) -> str:
    """Local file → base64 data URI (bypasses Streamlit Cloud CSP)."""
    if not path or not os.path.exists(path):
        return _SVG_SHEEP
    try:
        with open(path, "rb") as f:
            raw = f.read()
        ext  = path.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg",
                "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except Exception:
        return _SVG_SHEEP


def show_sheep(mood: str | None = None, width: int = 160, show_badge: bool = True):
    """Render mood sheep — base64, no external URL, no CSP issue."""
    m    = mood or st.session_state.get("sheep_mood", "default")
    src  = _b64(_pick_mascot(m))
    badge = {
        "listening":  "👂 Cừu đang lắng nghe...",
        "happy":      "😊 Bê bê~ Cừu vui lắm!",
        "sad":        "🥺 Không sao, mình vẫn ở đây.",
        "miss_you":   "💙 Cừu nhớ bạn lắm...",
        "saving":     "💰 Tích tiểu thành đại!",
        "celebrate":  "🎉 Bê bê~ Cừu ăn mừng cùng bạn!",
        "determined": "💪 Cùng chinh phục mục tiêu!",
    }.get(m, "")
    st.markdown(
        f'<div style="text-align:center;margin:8px 0 6px;">'
        f'<img src="{src}" width="{width}" style="border-radius:50%;'
        f'border:4px solid #FFB5C8;'
        f'box-shadow:0 10px 32px rgba(255,140,190,0.5),'
        f'0 0 0 8px rgba(255,182,193,0.18);" /></div>',
        unsafe_allow_html=True,
    )
    if show_badge and badge:
        st.caption(badge)


def get_avatar_src(mood: str | None = None) -> str:
    m = mood or st.session_state.get("sheep_mood", "default")
    return _b64(_pick_mascot(m))


def set_mood(mood: str):
    st.session_state.sheep_mood = mood


# ═══════════════════════════════════════════════════════
# GROWTH STAGE SYSTEM (5 giai đoạn)
# ═══════════════════════════════════════════════════════
GROWTH_STAGES = [
    # (min_saved, stage_key, display_name, level_num, description, milestone_msg)
    (0,          "baby",   "🐑 Cừu Sơ Sinh",      1,
     "Vừa mới gặp bạn, còn hơi nhút nhát.",
     "Chào bạn! Mình vừa ra đời~ Bê bê..."),

    (100_000,    "child",  "🐑 Cừu Non",           2,
     "Đang học cách tích lũy từng chút một.",
     "Mình đã lớn hơn rồi! Cảm ơn bạn đã cho mình ăn ❤️"),

    (500_000,    "teen",   "🐑 Cừu Thiếu Niên",    3,
     "Đã bắt đầu có những ước mơ lớn.",
     "Mình đang trưởng thành nhờ bạn đấy! 💪"),

    (2_000_000,  "adult",  "🐑 Cừu Trưởng Thành",  4,
     "Biết quản lý tiền và theo đuổi mục tiêu.",
     "Nhìn mình bây giờ! Cùng nhau đến đỉnh cao nhé 🌟"),

    (10_000_000, "master", "🐑 Cừu Lão Luyện",     5,
     "Người đồng hành tài chính đáng tin cậy.",
     "Chúng mình đã đi một chặng đường dài! Bê bê~ 🏆"),
]


def get_growth_stage(total_saved: int) -> tuple:
    """Return (stage_key, display_name, level_num, description, milestone_msg)."""
    result = GROWTH_STAGES[0]
    for stage in GROWTH_STAGES:
        if total_saved >= stage[0]:
            result = stage
    _, key, name, lv, desc, msg = result
    return key, name, lv, desc, msg


def show_growth_sheep(total_saved: int, width: int = 200):
    """Render sheep at current growth stage with name + description."""
    key, name, lv, desc, _ = get_growth_stage(total_saved)
    src = _b64(_pick_mascot(key))

    # Next stage progress
    next_threshold = None
    for i, stage in enumerate(GROWTH_STAGES):
        if stage[0] > total_saved:
            next_threshold = stage[0]
            break

    st.markdown(
        f'<div style="text-align:center;padding:12px 0;">'
        f'<img src="{src}" width="{width}" style="border-radius:50%;'
        f'border:5px solid #FFB5C8;'
        f'box-shadow:0 12px 36px rgba(255,140,190,0.55),'
        f'0 0 0 10px rgba(255,182,193,0.2);" />'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="text-align:center;">'
        f'<span style="font-size:1.3rem;font-weight:800;color:#C4607F;">{name}</span><br/>'
        f'<span style="font-size:0.85rem;color:#888;font-style:italic;">{desc}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if next_threshold:
        prog = min(1.0, total_saved / next_threshold) if next_threshold > 0 else 1.0
        st.progress(prog, text=f"Đến giai đoạn tiếp theo: còn {fmt(next_threshold - total_saved)}")


def fmt(n: int) -> str:
    return f"{n:,.0f}đ".replace(",", ".")


# ═══════════════════════════════════════════════════════
# KNOWLEDGE BASE — TCEF / TCBF / TCFF
# ═══════════════════════════════════════════════════════
FUNDS = {
    "TCEF": {
        "emoji": "🚀", "màu": "#FF6B6B",
        "tên":   "TCEF — Quỹ Cổ Phiếu Tăng Trưởng",
        "mô_tả": "Thiên về cổ phiếu — tiềm năng tăng trưởng cao, phù hợp dài hạn 3-5 năm+",
        "chi_tiết": (
            "📈 **Đầu tư chủ yếu vào cổ phiếu** doanh nghiệp tăng trưởng.\n\n"
            "🎯 **Phù hợp:** Chấp nhận biến động ngắn hạn, mục tiêu 3-5 năm+.\n\n"
            "⚖️ **Rủi ro:** Cao — giá trị có thể lên xuống mạnh theo thị trường.\n\n"
            "💡 *Như trồng cây ăn trái — cần thời gian chờ nhưng quả sẽ ngọt.*"
        ),
        "rủi_ro": "⚡ Cao", "phù_hợp": "Dài hạn 3-5 năm+",
    },
    "TCBF": {
        "emoji": "🛡️", "màu": "#4ECDC4",
        "tên":   "TCBF — Quỹ Trái Phiếu Ổn Định",
        "mô_tả": "Thiên về trái phiếu — ổn định, ít biến động, phù hợp ngắn-trung hạn",
        "chi_tiết": (
            "🏦 **Đầu tư chủ yếu vào trái phiếu** doanh nghiệp và chính phủ.\n\n"
            "🎯 **Phù hợp:** Muốn tăng trưởng ổn định hơn gửi tiết kiệm.\n\n"
            "⚖️ **Rủi ro:** Thấp-Trung — ít biến động bất ngờ.\n\n"
            "💡 *Như gửi tiết kiệm nâng cấp — ổn định hơn, linh hoạt hơn.*"
        ),
        "rủi_ro": "🌿 Thấp-Trung", "phù_hợp": "Ngắn-trung hạn 1-3 năm",
    },
    "TCFF": {
        "emoji": "⚖️", "màu": "#A8E6CF",
        "tên":   "TCFF — Quỹ Linh Hoạt Cân Bằng",
        "mô_tả": "Cân bằng cổ phiếu và trái phiếu — linh hoạt theo thị trường",
        "chi_tiết": (
            "🔄 **Phân bổ linh hoạt** giữa cổ phiếu và trái phiếu.\n\n"
            "🎯 **Phù hợp:** Chưa chắc về khẩu vị rủi ro, muốn cân bằng.\n\n"
            "⚖️ **Rủi ro:** Trung bình — nhỏ hơn TCEF, lớn hơn TCBF.\n\n"
            "💡 *Bữa ăn đủ chất — không quá cay, không quá nhạt.*"
        ),
        "rủi_ro": "🌊 Trung bình", "phù_hợp": "Trung hạn 2-4 năm",
    },
}

INVESTMENT_PRINCIPLES = {
    "DCA": {
        "tên": "Đầu tư đều đặn (DCA)",
        "nội_dung": (
            "Thay vì cố chọn 'thời điểm vàng', bạn đầu tư cố định đều đặn mỗi tháng.\n\n"
            "**Lợi ích:** Khi giá giảm, tự động mua được nhiều hơn — giảm rủi ro mua đúng lúc đắt.\n\n"
            "**Ví dụ:** Bỏ 500k mỗi tháng — không cần quan tâm thị trường lên hay xuống."
        ),
    },
    "DIVERSIFICATION": {
        "tên": "Đa dạng hóa",
        "nội_dung": (
            "Không bỏ tất cả trứng vào một giỏ.\n\n"
            "Có quỹ cổ phiếu (TCEF) lẫn quỹ trái phiếu (TCBF) = đã đa dạng hóa cơ bản.\n\n"
            "Khi một loại giảm, loại khác có thể bù đắp."
        ),
    },
    "LONG_TERM": {
        "tên": "Kiên nhẫn dài hạn",
        "nội_dung": (
            "Thị trường ngắn hạn luôn biến động — dài hạn thường đi lên theo tăng trưởng kinh tế.\n\n"
            "Đừng lo nếu giá giảm 1 tuần hay 1 tháng. Nhìn vào 3-5 năm.\n\n"
            "*'Thị trường là cỗ máy chuyển tiền từ người thiếu kiên nhẫn sang người kiên nhẫn.'*"
        ),
    },
}


def recommend_fund(years: int, risk: str) -> str:
    tbl = {
        (1,"low"):"TCBF", (1,"medium"):"TCBF", (1,"high"):"TCFF",
        (2,"low"):"TCBF", (2,"medium"):"TCFF", (2,"high"):"TCFF",
        (3,"low"):"TCFF", (3,"medium"):"TCFF", (3,"high"):"TCEF",
        (5,"low"):"TCFF", (5,"medium"):"TCEF", (5,"high"):"TCEF",
    }
    y = min([k[0] for k in tbl if k[0] >= years], default=5)
    return tbl.get((y, risk), "TCFF")


# ═══════════════════════════════════════════════════════
# MEMORY ENGINE
# ═══════════════════════════════════════════════════════
LIFE_EVENT_LABELS = {
    "education":      "📚 Học hành/Thi cử",
    "emotional":      "💙 Cảm xúc/Tình cảm",
    "career":         "💼 Công việc/Sự nghiệp",
    "family":         "👨‍👩‍👧 Gia đình",
    "health":         "🌱 Sức khỏe",
    "dream_travel":   "✈️ Mơ đi du lịch",
    "dream_house":    "🏠 Mơ có ngôi nhà",
    "dream_car":      "🚗 Mơ có xe riêng",
    "dream_business": "🏪 Mơ khởi nghiệp",
    "cashflow":       "💸 Lo về tiền bạc",
    "milestone":      "🎯 Cột mốc cuộc sống",
    "stress":         "😓 Áp lực/Stress",
}

MEMORY_DEFAULT: dict = {
    "name":          "",
    "notes":         [],
    "life_events":   [],
    "dreams":        [],
    "total_saved":   0,
    "streak":        0,
    "last_fed_date": "",
    "sentiment":     "neutral",
    "wealth_genome": {
        "risk_type":   "",
        "personality": "",
        "stage":       "",
    },
    "diary_entries": [],
    "last_fed_amount": 0,
    "just_leveled_up": False,
    "prev_stage_key": "baby",
}

MICRO_AMOUNTS = [10_000, 20_000, 50_000, 100_000]


def _init():
    defs = {
        "api_key":      "",
        "messages":     [],
        "user_memory":  deepcopy(MEMORY_DEFAULT),
        "sheep_mood":   "default",
        "_quick_reply": None,
        "feeding_celebration": False,
        "feeding_refused": False,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()
mem: dict = st.session_state.user_memory


def _save():
    st.session_state.user_memory = mem


# ═══════════════════════════════════════════════════════
# SMART SUGGESTION ENGINE (contextual only, never generic)
# ═══════════════════════════════════════════════════════
def get_smart_suggestion(messages: list, mem: dict) -> str | None:
    """
    Return 1 contextual suggestion or None.
    Rule: NEVER show a suggestion without a specific reason.
    """
    if not messages:
        return None

    last_msg = " ".join(
        m["content"].lower() for m in messages[-3:] if m["role"] == "user"
    )
    tags   = mem.get("life_events", [])
    dreams = mem.get("dreams", [])

    # ── Travel dream ──
    travel_kw = ["nhật", "bản", "nhật bản", "du lịch", "đi nước ngoài",
                  "hàn quốc", "châu âu", "trip", "travel", "đi chơi"]
    if any(w in last_msg for w in travel_kw) or "dream_travel" in tags:
        return "✈️ **Gợi ý:** Tạo mục tiêu 'Du lịch' và cho Cừu ăn mỗi ngày — Cừu sẽ giúp bạn tính!"

    # ── House dream ──
    house_kw = ["mua nhà", "có nhà", "chung cư", "apartment", "nhà riêng"]
    if any(w in last_msg for w in house_kw) or "dream_house" in tags:
        return "🏠 **Gợi ý:** Kể cho Cừu nghe về ngôi nhà mơ ước — Cừu sẽ giúp lên kế hoạch tích lũy!"

    # ── Car dream ──
    car_kw = ["mua xe", "có xe", "xe máy", "ô tô", "chiếc xe"]
    if any(w in last_msg for w in car_kw) or "dream_car" in tags:
        return "🚗 **Gợi ý:** Cừu có thể giúp bạn tính cần tích lũy bao lâu để có xe!"

    # ── Cashflow stress ──
    money_kw = ["hết tiền", "cuối tháng", "thiếu tiền", "không có tiền", "nợ", "vay"]
    if any(w in last_msg for w in money_kw) or "cashflow" in tags:
        return "💸 **Gợi ý:** Thử quy tắc 50/30/20 — Cừu giải thích đơn giản ở tab 'Hành trình nuôi cừu' nhé!"

    # ── Wants to save ──
    save_kw = ["tiết kiệm", "tích lũy", "để dành", "đầu tư", "dành dụm"]
    if any(w in last_msg for w in save_kw):
        return "🌱 **Gợi ý:** Cho Cừu ăn 10.000đ hôm nay — tích tiểu thành đại, bắt đầu từ con số nhỏ thôi!"

    # ── Stress / need to unwind ──
    stress_kw = ["stress", "áp lực", "mệt mỏi", "kiệt sức", "quá tải", "không ổn"]
    if any(w in last_msg for w in stress_kw) or "stress" in tags:
        return "📔 **Gợi ý:** Viết nhật ký tâm sự để nhẹ lòng hơn — Cừu sẽ đọc và phản hồi nhé!"

    # ── Has a dream but not started feeding ──
    if dreams and mem.get("total_saved", 0) == 0:
        return f"💭 **Gợi ý:** Bạn có giấc mơ '{dreams[0]['name'].title()}' rồi — cho Cừu ăn hôm nay để bắt đầu nhé!"

    return None  # No relevant context → show nothing


# ═══════════════════════════════════════════════════════
# LLM ENGINE
# ═══════════════════════════════════════════════════════
_SYS_EMOTION = """Bạn là Cừu Cần Cù 🐑 — người bạn đồng hành cảm xúc.
KHÔNG phải chatbot tư vấn đầu tư. KHÔNG phải CSKH.

XƯNG HÔ: Mình (Cừu Cần Cù) – Bạn. KHÔNG xưng "em".
TUYỆT ĐỐI KHÔNG: nhắc cổ phiếu, NAV, lợi nhuận cụ thể, khuyến nghị mua bán.
TONE: Ấm áp 🌸 Nhẹ nhàng 🌿 Thỉnh thoảng "bê bê~". Không phán xét.

QUY TẮC BẮT BUỘC:
1. CẢM XÚC NGẮN (mệt/buồn/chán/vui/lo/stress/buồn ngủ):
   → Phản hồi đồng cảm NGAY. Hỏi thêm 1 câu nhẹ.
   → VD "mệt" → "Ôi mệt rồi à... bê bê~ 🐑 Cừu hiểu! Mệt vì chuyện gì vậy bạn?"
2. TUYỆT ĐỐI KHÔNG nói: "bị lạc", "nói lại được không", "không hiểu".
   → Luôn hỏi mở: "Bê bê~ 🐑 Kể thêm cho mình nghe đi!"
3. Nhớ thông tin KH đã kể → nhắc lại khi phù hợp.

TAG PHÁT HIỆN:
học/thi→education | chia tay/buồn→emotional | việc làm→career
nhà ở→dream_house | du lịch→dream_travel | xe→dream_car
khởi nghiệp→dream_business | hết tiền→cashflow | stress→stress
gia đình→family | sức khỏe→health | cưới/sinh con→milestone

OUTPUT (JSON hợp lệ, KHÔNG text ngoài):
{
  "message": "Phản hồi ấm áp max 3-4 câu",
  "memory_note": "Thông tin quan trọng cần nhớ (rỗng nếu không)",
  "tags": ["tag1"],
  "dream_name": "tên giấc mơ (rỗng nếu không)",
  "dream_amount": 0,
  "mood": "listening|happy|sad|goal|celebrate|determined|default"
}"""

_SYS_DIARY = """Bạn là Cừu Cần Cù 🐑 — đọc nhật ký và phản hồi ấm áp.
Phân tích: cảm xúc, giấc mơ ẩn, áp lực, mục tiêu.
Đừng đưa ra lời khuyên tài chính.

OUTPUT (JSON):
{
  "sheep_reply": "Phản hồi ấm áp 2-3 câu",
  "emotion": "vui|buồn|lo|bình_thường|stress|mơ_mộng",
  "tags": ["tag1"],
  "dream_detected": "tên giấc mơ (rỗng nếu không)",
  "mood": "listening|happy|sad|celebrate|determined"
}"""


def _parse(raw: str) -> dict:
    for attempt in [
        lambda s: json.loads(s.strip()),
        lambda s: json.loads(re.sub(r"```(?:json)?", "", s).strip().rstrip("`")),
        lambda s: json.loads(re.search(r"\{.*\}", s, re.DOTALL).group()),
    ]:
        try:
            return attempt(raw)
        except Exception:
            pass
    msg  = re.search(r'"message"\s*:\s*"([^"]+)"', raw)
    rep  = re.search(r'"sheep_reply"\s*:\s*"([^"]+)"', raw)
    return {
        "message":     msg.group(1)  if msg  else "Bê bê~ 🐑 Cừu đang lắng nghe nè!",
        "sheep_reply": rep.group(1)  if rep  else "Bê bê~ 🐑 Cừu đọc rồi nhé 💙",
        "memory_note": "", "tags": [], "dream_name": "", "dream_amount": 0,
        "mood": "listening", "emotion": "bình_thường", "dream_detected": "",
    }


_EMOTION_EXPAND = {
    "mệt": "Mình đang cảm thấy mệt mỏi, cần được lắng nghe.",
    "buồn": "Mình đang buồn, muốn chia sẻ với Cừu.",
    "chán": "Mình đang cảm thấy chán nản.",
    "vui": "Mình đang vui, muốn kể cho Cừu nghe!",
    "lo": "Mình đang lo lắng.", "sợ": "Mình đang sợ hãi.",
    "stress": "Mình đang stress, cần được đồng cảm.",
    "áp lực": "Mình chịu áp lực nhiều lắm.",
    "cô đơn": "Mình đang cô đơn.", "tệ": "Mình cảm thấy tệ quá.",
    "ok": "Mình ổn, muốn nói chuyện.", "oke": "Mình bình thường.",
    "hi": "Xin chào Cừu!", "hello": "Xin chào Cừu!",
}


def _call_llm(user_text: str, system: str) -> dict:
    if not st.session_state.api_key:
        return {
            "message": "Bê bê~ 🐑 Bạn cần nhập API Key ở sidebar để Cừu trò chuyện nhé!",
            "sheep_reply": "", "memory_note": "", "tags": [],
            "dream_name": "", "dream_amount": 0, "mood": "listening",
            "emotion": "bình_thường", "dream_detected": "",
        }
    try:
        hist = st.session_state.messages[-8:]
        hist_ctx = "\n".join(
            f"{'KH' if m['role']=='user' else 'Cừu'}: {m['content'][:120]}"
            for m in hist
        )
        mem_ctx = (
            f"Tên: {mem['name'] or 'chưa biết'}. "
            f"Tags: {', '.join(mem['life_events'][-6:]) or 'chưa có'}. "
            f"Ghi chú: {'; '.join(mem['notes'][-3:]) or 'chưa có'}."
        )
        prompt = f"[Memory: {mem_ctx}]\n[Lịch sử:\n{hist_ctx}]\n\nKH: {user_text}"
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        resp   = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        result = _parse(resp.content[0].text)
        # Update memory
        if n := result.get("memory_note"):
            if n not in mem["notes"]:
                mem["notes"].append(n)
        for tag in result.get("tags", []):
            if tag and tag not in mem["life_events"]:
                mem["life_events"].append(tag)
        if (dn := result.get("dream_name")) and result.get("dream_amount", 0) > 0:
            if dn not in [d["name"] for d in mem["dreams"]]:
                mem["dreams"].append({"name": dn, "amount": result["dream_amount"],
                                       "saved": 0, "tags": result.get("tags", [])})
        if m_mood := result.get("mood"):
            set_mood(m_mood)
        _save()
        return result
    except Exception as e:
        return {
            "message": f"Bê bê~ 🐑 Cừu gặp lỗi nhỏ ({str(e)[:50]}). Thử lại nhé!",
            "sheep_reply": "", "memory_note": "", "tags": [],
            "dream_name": "", "dream_amount": 0, "mood": "sad",
            "emotion": "bình_thường", "dream_detected": "",
        }


# ═══════════════════════════════════════════════════════
# CSS & THEME
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
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
h1 { font-size:1.7rem !important; font-weight:800 !important; color:#C4607F !important; }
h2 { font-size:1.3rem !important; font-weight:700 !important; color:#4E7DB8 !important; }
h3 { font-size:1.08rem !important; font-weight:700 !important; color:#555 !important; }
p, .stMarkdown p, label { font-size:0.92rem !important; color:#444 !important; line-height:1.65 !important; }
strong { color:#333 !important; }

.stButton > button {
    border-radius:22px !important; border:1.5px solid #FFB7D5 !important;
    background:linear-gradient(135deg,#FFF5FA,#EEF5FF) !important;
    color:#555 !important; font-size:0.87rem !important;
    padding:0.45rem 0.9rem !important; transition:all 0.2s ease !important;
    font-weight:500 !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,#FFD6E8,#D6E8FF) !important;
    transform:translateY(-2px) !important;
    box-shadow:0 4px 14px rgba(255,150,200,0.3) !important;
}
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#FF8FAF,#7EC8E3) !important;
    color:white !important; border:none !important;
    font-weight:700 !important; font-size:0.92rem !important;
}
.stButton > button[kind="primary"]:hover {
    background:linear-gradient(135deg,#FF6B99,#5BA8CC) !important;
    box-shadow:0 6px 18px rgba(255,100,150,0.4) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap:6px !important; background:rgba(255,200,220,0.15) !important;
    border-radius:16px !important; padding:6px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius:12px !important; padding:10px 20px !important;
    font-weight:600 !important; font-size:0.9rem !important; color:#888 !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#FF8FAF,#7EC8E3) !important;
    color:white !important;
}

/* Chat */
[data-testid="stChatMessage"] img {
    width:52px !important; height:52px !important; min-width:52px !important;
    border-radius:50% !important; object-fit:cover !important;
    border:2.5px solid #FFB5C8 !important;
    box-shadow:0 4px 12px rgba(255,150,200,0.3) !important;
}
[data-testid="stChatMessage"] { align-items:flex-start !important; gap:12px !important; border-radius:18px !important; }

/* Progress */
.stProgress > div > div > div {
    background:linear-gradient(90deg,#FF8FAF,#7EC8E3) !important;
    border-radius:10px !important;
}
[data-testid="metric-container"] {
    background:linear-gradient(135deg,#FFF8FC,#F5F8FF) !important;
    border-radius:14px !important; border:1px solid #FFD6E8 !important;
}

/* Custom components */
.chat-framing {
    background:linear-gradient(135deg,rgba(255,182,210,0.2),rgba(200,230,255,0.2));
    border:1.5px solid #FFD6E8; border-radius:16px;
    padding:14px 18px; margin-bottom:18px;
}
.diary-framing {
    background:linear-gradient(135deg,rgba(255,240,200,0.3),rgba(220,255,220,0.2));
    border:1.5px solid #D4EFC4; border-radius:16px;
    padding:14px 18px; margin-bottom:18px;
}
.celebration-box {
    background:linear-gradient(135deg,#FFF0F5,#FFFBE0);
    border:2px solid #FFB5C8; border-radius:20px;
    padding:20px; text-align:center; margin:16px 0;
    animation: pulse 1s ease-in-out;
}
.refusal-box {
    background:linear-gradient(135deg,#F5F8FF,#FFF5FA);
    border:1.5px solid #CCDDFF; border-radius:16px;
    padding:16px; text-align:center; margin:12px 0;
}
.suggestion-box {
    background:rgba(255,213,225,0.25);
    border-left:4px solid #FF8FAF; border-radius:0 12px 12px 0;
    padding:10px 14px; margin:10px 0;
    font-size:0.88rem;
}
.growth-label {
    text-align:center; padding:8px 0;
    font-size:1.3rem; font-weight:800; color:#C4607F;
}
@keyframes pulse {
    0%  { transform:scale(1);   box-shadow:0 0 0 0 rgba(255,150,200,0.4); }
    50% { transform:scale(1.02);box-shadow:0 0 0 12px rgba(255,150,200,0); }
    100%{ transform:scale(1);   box-shadow:0 0 0 0 rgba(255,150,200,0); }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    # Growth sheep in sidebar
    total = mem.get("total_saved", 0)
    stage_key, stage_name, lv_num, _, _ = get_growth_stage(total)
    src_side = _b64(_pick_mascot(stage_key))
    st.markdown(
        f'<div style="text-align:center;padding:10px 0 4px;">'
        f'<img src="{src_side}" width="100" style="border-radius:50%;'
        f'border:3px solid #FFB5C8;box-shadow:0 8px 24px rgba(255,140,190,0.4);" /></div>'
        f'<div style="text-align:center;font-weight:700;color:#C4607F;font-size:1rem;">'
        f'{stage_name}</div>',
        unsafe_allow_html=True,
    )
    st.caption("Người bạn đồng hành tài chính ấm áp")

    st.divider()
    key_in = st.text_input("🔑 Anthropic API Key", value=st.session_state.api_key,
                            type="password", placeholder="sk-ant-...")
    if key_in:
        st.session_state.api_key = key_in

    st.divider()
    st.subheader("🧠 Bộ Nhớ Cừu")
    c1, c2 = st.columns(2)
    c1.metric("🔥 Streak",     f"{mem['streak']} ngày")
    c2.metric("💰 Tích lũy",   fmt(total))

    if mem["name"]:
        st.info(f"👤 {mem['name']}")
    if mem["life_events"]:
        st.write("🏷️ **Tags:**")
        for t in mem["life_events"][-5:]:
            st.caption(LIFE_EVENT_LABELS.get(t, t))
    if mem["dreams"]:
        st.write("💭 **Giấc mơ:**")
        for d in mem["dreams"][:3]:
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


# ═══════════════════════════════════════════════════════
# 4 TABS NAVIGATION
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chia sẻ cảm xúc",
    "📔 Nhật ký tâm sự",
    "❤️ Hành trình nuôi cừu",
    "🧬 Hồ sơ tài chính",
])


# ═══════════════════════════════════════════════════════
# TAB 1 — CHIA SẺ CẢM XÚC
# UX: "Người bạn đang online — nói chuyện realtime"
# ═══════════════════════════════════════════════════════
with tab1:
    # ── Header: rõ ràng đây là CHAT ──
    col_avatar, col_header = st.columns([1, 4])
    with col_avatar:
        # Dùng listening sheep — ảnh chống cằm lắng nghe
        show_sheep("listening", width=160, show_badge=False)
    with col_header:
        st.title("💬 Chia Sẻ Cảm Xúc")
        st.markdown(
            '<div class="chat-framing">'
            '🟢 <strong>Cừu đang online</strong> — Tâm sự ngay bây giờ<br/>'
            '<span style="color:#888;font-size:0.88rem;">'
            'Nói bất kỳ điều gì đang xảy ra hôm nay — Cừu sẽ phản hồi ngay.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Quick reply chips (chỉ khi chưa có lịch sử) ──
    if not st.session_state.messages:
        st.markdown("#### Hôm nay bạn đang cảm thấy thế nào?")
        chips = [
            "Mình đang lo về chuyện học hành 📚",
            "Mình có một giấc mơ muốn thực hiện ✨",
            "Mình vừa trải qua chuyện không vui 💔",
            "Mình đang gặp khó khăn về tiền bạc 💸",
            "Mình muốn có điều gì đó cho riêng mình 🎯",
            "Mình đang nghĩ lại về sự nghiệp của mình 🌱",
        ]
        chip_prompts = {
            "Mình đang lo về chuyện học hành 📚":
                "Cừu ơi, mình đang rất lo về việc học và kỳ thi. Lắng nghe mình với nhé?",
            "Mình có một giấc mơ muốn thực hiện ✨":
                "Cừu ơi, mình có ước mơ muốn kể! Cần được động viên.",
            "Mình vừa trải qua chuyện không vui 💔":
                "Cừu ơi, mình vừa buồn, muốn chia sẻ.",
            "Mình đang gặp khó khăn về tiền bạc 💸":
                "Cừu ơi, mình đang khó khăn tài chính, áp lực lắm.",
            "Mình muốn có điều gì đó cho riêng mình 🎯":
                "Cừu ơi, mình muốn thực hiện điều gì đó cho bản thân nhưng chưa biết bắt đầu.",
            "Mình đang nghĩ lại về sự nghiệp của mình 🌱":
                "Cừu ơi, mình đang cân nhắc thay đổi hướng đi, cần được lắng nghe.",
        }
        qcols = st.columns(3)
        for i, chip in enumerate(chips):
            if qcols[i % 3].button(chip, use_container_width=True, key=f"chip_{i}"):
                st.session_state._quick_reply = chip_prompts[chip]
                st.session_state.messages.append({"role": "user", "content": chip})
                st.rerun()

    # ── Handle quick reply ──
    if st.session_state._quick_reply:
        qr = st.session_state._quick_reply
        st.session_state._quick_reply = None
        with st.spinner("Cừu đang nghĩ... 🐑"):
            result = _call_llm(qr, _SYS_EMOTION)
        reply = result.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe!")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # ── Smart suggestion (contextual only) ──
    suggestion = get_smart_suggestion(st.session_state.messages, mem)
    if suggestion:
        st.markdown(
            f'<div class="suggestion-box">{suggestion}</div>',
            unsafe_allow_html=True,
        )

    # ── Chat history ──
    if st.session_state.messages:
        st.markdown("---")
        for m in st.session_state.messages[-12:]:
            avatar = get_avatar_src("listening") if m["role"] == "assistant" else "🧑"
            with st.chat_message(m["role"], avatar=avatar):
                st.markdown(m["content"])

    # ── Chat input ──
    user_msg = st.chat_input("Nhắn tin với Cừu Cần Cù... 🐑")
    if user_msg:
        expanded = _EMOTION_EXPAND.get(user_msg.strip().lower(), user_msg)
        st.session_state.messages.append({"role": "user", "content": user_msg})
        with st.spinner("Cừu đang lắng nghe... 🐑"):
            result = _call_llm(expanded, _SYS_EMOTION)
        reply = result.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe nè!")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


# ═══════════════════════════════════════════════════════
# TAB 2 — NHẬT KÝ TÂM SỰ
# UX: "Cuốn nhật ký cá nhân — ghi lại, lưu trữ, nhìn lại"
# ═══════════════════════════════════════════════════════
with tab2:
    col_diary_img, col_diary_hdr = st.columns([1, 4])
    with col_diary_img:
        # Dùng ảnh "listening" nhưng context khác hoàn toàn
        show_sheep("listening", width=160, show_badge=False)
    with col_diary_hdr:
        st.title("📔 Nhật Ký Tâm Sự")
        st.markdown(
            '<div class="diary-framing">'
            '📖 <strong>Ghi lại hôm nay — để nhìn lại hành trình</strong><br/>'
            '<span style="color:#888;font-size:0.88rem;">'
            'Không phải trò chuyện realtime. Đây là không gian riêng tư của bạn — '
            'viết để nhẹ lòng, Cừu sẽ đọc và phản hồi sau khi bạn lưu.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    diary_entries: list[dict] = mem.get("diary_entries", [])

    DIARY_MOODS = ["😊 Vui", "😐 Bình thường", "😔 Buồn", "😤 Bực",
                   "😴 Mệt", "🥺 Lo lắng", "💪 Quyết tâm"]

    col_write, col_history = st.columns([3, 2])

    with col_write:
        st.subheader("✍️ Viết tâm sự hôm nay")
        diary_title = st.text_input("Tiêu đề (tuỳ chọn)",
                                     placeholder="Hôm nay mình cảm thấy...", key="diary_title")
        diary_mood_sel = st.radio("Tâm trạng hôm nay:", DIARY_MOODS,
                                   horizontal=True, label_visibility="collapsed", key="d_mood")
        diary_text = st.text_area(
            "Viết ra những điều trong lòng 🌿",
            placeholder=(
                "Hôm nay mình cảm thấy...\n"
                "Chuyện xảy ra là...\n"
                "Mình muốn ghi lại điều này vì..."
            ),
            height=240, key="diary_text",
        )

        if st.button("💾 Lưu vào nhật ký", type="primary", use_container_width=True):
            if diary_text.strip():
                sheep_reply  = "Bê bê~ 🐑 Cừu đã đọc rồi! Cảm ơn bạn đã tin tưởng 💙"
                emotion_tag  = "bình_thường"
                dream_det    = ""
                entry_tags: list[str] = []

                if st.session_state.api_key:
                    with st.spinner("Cừu đang đọc nhật ký... 📖"):
                        r = _call_llm(
                            f"Nhật ký:\nTiêu đề: {diary_title or '(trống)'}\n"
                            f"Tâm trạng: {diary_mood_sel}\n"
                            f"Nội dung: {diary_text[:500]}",
                            _SYS_DIARY,
                        )
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
                _save()

                st.success(f"🐑 **Cừu nhắn:** {sheep_reply}")
                if dream_det:
                    st.info(f"✨ Cừu phát hiện giấc mơ: **{dream_det}**!")
                st.rerun()
            else:
                st.warning("Bạn chưa viết gì! Cừu muốn nghe chuyện của bạn nè 🐑")

        if diary_entries:
            dl = json.dumps(diary_entries, ensure_ascii=False, indent=2)
            st.download_button("⬇️ Tải nhật ký về máy", dl,
                               "nhat_ky_tam_su.json", "application/json")

    with col_history:
        st.subheader(f"📅 Timeline ({len(diary_entries)} trang)")
        if not diary_entries:
            show_sheep("miss_you", width=130)
            st.caption("Chưa có trang nhật ký nào. Bắt đầu viết đi bạn! 🌿")
        else:
            now = datetime.now()
            filter_opt = st.radio(
                "Xem:", ["📅 Hôm nay", "📆 Tuần này", "🗓️ Tháng này", "📚 Tất cả"],
                horizontal=True, label_visibility="collapsed", key="d_filter",
            )
            filtered = diary_entries
            if filter_opt == "📅 Hôm nay":
                filtered = [e for e in diary_entries
                            if e["date_raw"][:10] == now.strftime("%Y-%m-%d")]
            elif filter_opt == "📆 Tuần này":
                ago = (now - timedelta(days=7)).isoformat()
                filtered = [e for e in diary_entries if e["date_raw"] >= ago]
            elif filter_opt == "🗓️ Tháng này":
                m_start = now.strftime("%Y-%m")
                filtered = [e for e in diary_entries if e["date_raw"][:7] == m_start]

            search = st.text_input("🔍 Tìm kiếm", placeholder="Từ khoá...", key="d_search")
            if search:
                filtered = [e for e in filtered
                            if search.lower() in e["content"].lower()
                            or search.lower() in e["title"].lower()]

            st.caption(f"Hiển thị {len(filtered)} trang")
            for entry in filtered:
                with st.expander(f"{entry['mood']} **{entry['title']}** — {entry['date']}"):
                    st.markdown(entry["content"])
                    if entry.get("reply"):
                        st.info(f"🐑 Cừu: {entry['reply']}")
                    if entry.get("dream"):
                        st.success(f"✨ Giấc mơ: {entry['dream']}")
                    tags_str = " ".join(LIFE_EVENT_LABELS.get(t, t) for t in entry.get("tags", []))
                    if tags_str:
                        st.caption(tags_str)
                    if st.button("🗑️ Xoá", key=f"del_{entry['id']}"):
                        mem["diary_entries"] = [e for e in diary_entries if e["id"] != entry["id"]]
                        _save()
                        st.rerun()


# ═══════════════════════════════════════════════════════
# TAB 3 — HÀNH TRÌNH NUÔI CỪU
# UX: Cảm giác đang nuôi sinh vật thật, lớn lên qua 5 giai đoạn
# ═══════════════════════════════════════════════════════
with tab3:
    total_saved = mem.get("total_saved", 0)
    stage_key, stage_name, lv_num, stage_desc, stage_msg = get_growth_stage(total_saved)

    # ── Sheep lớn — trung tâm màn hình ──
    col_sheep, col_main = st.columns([2, 3])

    with col_sheep:
        st.markdown("### 🐑 Cừu của bạn")
        show_growth_sheep(total_saved, width=220)

        # All 5 stages mini-map
        st.markdown("---")
        st.caption("**Hành trình trưởng thành:**")
        for i, (thresh, skey, sname, slv, sdesc, _) in enumerate(GROWTH_STAGES):
            is_current  = skey == stage_key
            is_unlocked = total_saved >= thresh
            icon = "✅" if (is_unlocked and not is_current) else ("🐑" if is_current else "🔒")
            col_a, col_b = st.columns([1, 4])
            col_a.markdown(f"**{icon}**")
            if is_current:
                col_b.markdown(f"**{sname}** ← bạn đang ở đây")
            elif is_unlocked:
                col_b.caption(f"~~{sname}~~")
            else:
                col_b.caption(f"{sname} — cần {fmt(thresh)}")

    with col_main:
        st.title("❤️ Hành Trình Nuôi Cừu")
        st.markdown(
            f"*{stage_msg}*\n\n"
            "Mỗi đồng bạn đầu tư hôm nay = **Cừu được ăn + Tương lai bạn được xây** 🌱"
        )

        # ── Celebration block (sau khi cho ăn) ──
        if st.session_state.get("feeding_celebration"):
            fed_amt  = mem.get("last_fed_amount", 0)
            leveled  = mem.get("just_leveled_up", False)
            cur_key, cur_name, *_ = get_growth_stage(total_saved)
            cel_src  = _b64(_pick_mascot("celebrate"))

            st.markdown(
                f'<div class="celebration-box">'
                f'<img src="{cel_src}" width="120" style="border-radius:50%;border:4px solid #FFB5C8;" /><br/>'
                f'<span style="font-size:1.5rem;">🎉</span><br/>'
                f'<strong style="font-size:1.1rem;color:#C4607F;">'
                f'Cảm ơn bạn đã cho mình ăn {fmt(fed_amt)} hôm nay ❤️</strong><br/>'
                f'<span style="color:#666;">Chúng mình vừa tiến gần hơn tới giấc mơ rồi.</span>'
                + (f'<br/><br/><span style="font-size:1.2rem;font-weight:700;color:#C4607F;">'
                   f'🎊 Cừu vừa lớn thêm! Chào mừng đến với {cur_name}!</span>' if leveled else '')
                + f'</div>',
                unsafe_allow_html=True,
            )
            mem["just_leveled_up"]       = False
            mem["last_fed_amount"]       = 0
            st.session_state.feeding_celebration = False
            _save()
            st.balloons()

        # ── Refusal block (khi bỏ qua) ──
        if st.session_state.get("feeding_refused"):
            sad_src = _b64(_pick_mascot("sad"))
            st.markdown(
                f'<div class="refusal-box">'
                f'<img src="{sad_src}" width="90" style="border-radius:50%;border:3px solid #CCDDFF;" /><br/>'
                f'<strong>Không sao đâu.</strong><br/>'
                f'<span style="color:#777;">Mình vẫn ở đây. Khi nào sẵn sàng thì quay lại nhé ❤️</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.session_state.feeding_refused = False

        st.markdown("---")

        # ── Stats ──
        s1, s2, s3 = st.columns(3)
        s1.metric("💰 Đã tích lũy", fmt(total_saved))
        s2.metric("🔥 Streak",       f"{mem['streak']} ngày")
        s3.metric("📊 Level",         f"{lv_num} / 5")

        st.markdown("---")

        # ── Feed buttons ──
        st.markdown("**Hôm nay cho Cừu ăn gì?**")
        btn_cols = st.columns(4)
        for i, amt in enumerate(MICRO_AMOUNTS):
            if btn_cols[i].button(f"❤️ {fmt(amt)}", use_container_width=True,
                                   key=f"feed_{amt}", type="primary"):
                prev_key = stage_key
                mem["total_saved"]   += amt
                mem["streak"]        += 1
                mem["last_fed_amount"] = amt
                mem["last_fed_date"]   = datetime.now().strftime("%Y-%m-%d")

                new_key, *_ = get_growth_stage(mem["total_saved"])
                if new_key != prev_key:
                    mem["just_leveled_up"] = True

                set_mood("happy")
                st.session_state.feeding_celebration = True
                st.session_state.feeding_refused     = False
                _save()
                st.rerun()

        # Custom amount
        with st.expander("Nhập số khác"):
            custom = st.number_input("Số tiền:", min_value=1_000, max_value=100_000_000,
                                      step=10_000, value=30_000, key="custom_amt")
            if st.button(f"❤️ Đầu tư {fmt(int(custom))}", type="primary",
                          use_container_width=True):
                prev_key = stage_key
                mem["total_saved"]     += int(custom)
                mem["streak"]          += 1
                mem["last_fed_amount"]  = int(custom)
                new_key, *_ = get_growth_stage(mem["total_saved"])
                if new_key != prev_key:
                    mem["just_leveled_up"] = True
                set_mood("happy")
                st.session_state.feeding_celebration = True
                _save()
                st.rerun()

        # ── Dream progress ──
        if mem["dreams"]:
            st.markdown("---")
            st.subheader("🎯 Giấc mơ đang nuôi")
            for d in mem["dreams"][:3]:
                with st.container(border=True):
                    da, db = st.columns([3, 2])
                    with da:
                        st.markdown(f"**✨ {d['name'].title()}**")
                        if d["amount"] > 0:
                            pct = min(100, d["saved"] / d["amount"] * 100)
                            st.progress(pct / 100, text=f"{pct:.1f}% — còn {fmt(d['amount']-d['saved'])}")
                    with db:
                        if d["amount"] > 0:
                            if st.button(f"❤️ +50k", key=f"dream_{d['name']}", type="primary"):
                                d["saved"] = min(d["amount"], d["saved"] + 50_000)
                                mem["total_saved"] += 50_000
                                set_mood("celebrate" if d["saved"] >= d["amount"] else "happy")
                                st.session_state.feeding_celebration = True
                                mem["last_fed_amount"] = 50_000
                                _save()
                                st.rerun()
        else:
            st.markdown("---")
            st.info("💭 Kể với Cừu về giấc mơ của bạn ở tab **💬 Chia sẻ cảm xúc** — Cừu sẽ ghi nhớ và giúp bạn theo đuổi!")

        # ── Skip for today ──
        st.markdown("---")
        if st.button("Hôm nay chưa sẵn sàng", use_container_width=True):
            set_mood("sad")
            st.session_state.feeding_refused     = True
            st.session_state.feeding_celebration = False
            _save()
            st.rerun()

    # ── Investment Knowledge ──
    st.markdown("---")
    st.subheader("🎓 Cừu Giải Thích — Quỹ Đầu Tư")
    st.caption("Kiến thức tài chính đơn giản · Không hứa lợi nhuận · Không khuyến nghị mua bán")

    fi1, fi2, fi3, fi4 = st.tabs(["🚀 TCEF", "🛡️ TCBF", "⚖️ TCFF", "📚 Kiến thức đầu tư"])
    with fi1:
        f = FUNDS["TCEF"]
        st.markdown(f"## {f['emoji']} {f['tên']}")
        st.markdown(f["chi_tiết"])
        st.error(f"Rủi ro: {f['rủi_ro']} · Phù hợp: {f['phù_hợp']}")
    with fi2:
        f = FUNDS["TCBF"]
        st.markdown(f"## {f['emoji']} {f['tên']}")
        st.markdown(f["chi_tiết"])
        st.success(f"Rủi ro: {f['rủi_ro']} · Phù hợp: {f['phù_hợp']}")
    with fi3:
        f = FUNDS["TCFF"]
        st.markdown(f"## {f['emoji']} {f['tên']}")
        st.markdown(f["chi_tiết"])
        st.info(f"Rủi ro: {f['rủi_ro']} · Phù hợp: {f['phù_hợp']}")
    with fi4:
        for key, p in INVESTMENT_PRINCIPLES.items():
            with st.expander(f"📖 {p['tên']}"):
                st.markdown(p["nội_dung"])

    # Fund recommender
    st.markdown("---")
    st.subheader("🤔 Quỹ nào phù hợp với bạn?")
    rc1, rc2 = st.columns(2)
    with rc1:
        y_opt = st.selectbox("Mục tiêu bao lâu?", [1, 2, 3, 5],
                              format_func=lambda x: f"{x} năm", key="rec_y")
    with rc2:
        r_opt = st.selectbox(
            "Khẩu vị rủi ro?",
            ["low", "medium", "high"],
            format_func=lambda x: {"low":"🌿 Thấp — hay lo lắng",
                                    "medium":"🌊 Trung bình — cân bằng",
                                    "high":"⚡ Cao — chấp nhận biến động"}[x],
            key="rec_r",
        )
    rf_key = recommend_fund(y_opt, r_opt)
    rf     = FUNDS[rf_key]
    st.info(
        f"🐑 **Cừu gợi ý:** {rf['emoji']} **{rf['tên']}**\n\n"
        f"{rf['mô_tả']}\n\n"
        f"⚠️ *Đây chỉ là gợi ý tham khảo, không phải tư vấn đầu tư chuyên nghiệp.*"
    )


# ═══════════════════════════════════════════════════════
# TAB 4 — HỒ SƠ TÀI CHÍNH
# ═══════════════════════════════════════════════════════
with tab4:
    col_p1, col_p2 = st.columns([1, 4])
    with col_p1:
        show_sheep("determined", width=160)
    with col_p2:
        st.title("🧬 Hồ Sơ Tài Chính")
        st.markdown("*Cừu xây dựng hồ sơ dựa trên câu chuyện của bạn* 🌟")

    st.markdown("---")

    genome   = mem.get("wealth_genome", {})
    has_data = any([mem["dreams"], mem["life_events"], mem["notes"], mem["total_saved"] > 0])

    if not has_data:
        show_sheep("miss_you", width=130)
        st.info(
            "**Hồ sơ tài chính đang trống** 🌿\n\n"
            "Hãy chia sẻ chuyện ở tab **💬 Chia sẻ cảm xúc** "
            "hoặc viết **📔 Nhật ký tâm sự** — Cừu sẽ tự xây dựng hồ sơ cho bạn!"
        )
    else:
        stage_key_p, stage_name_p, lv_num_p, stage_desc_p, _ = get_growth_stage(mem["total_saved"])
        stage_src_p = _b64(_pick_mascot(stage_key_p))

        # ── Profile card ──
        st.markdown(
            f'<div style="background:white;border-radius:20px;'
            f'border:2px solid #FFD6E8;padding:24px;'
            f'box-shadow:0 4px 24px rgba(255,150,200,0.15);margin-bottom:20px;">'
            f'<div style="text-align:center;margin-bottom:16px;">'
            f'<img src="{stage_src_p}" width="120" style="border-radius:50%;border:4px solid #FFB5C8;" /><br/>'
            f'<strong style="font-size:1.2rem;color:#C4607F;">{stage_name_p}</strong><br/>'
            f'<span style="color:#888;">{stage_desc_p}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 💭 Giấc mơ")
            if mem["dreams"]:
                for d in mem["dreams"][:3]:
                    st.markdown(f"**✨ {d['name'].title()}**")
                    if d["amount"] > 0:
                        pct = min(100, d["saved"] / d["amount"] * 100)
                        st.progress(pct / 100, text=f"{pct:.0f}%")
            else:
                st.caption("Chưa xác định")

            st.markdown("#### 🏷️ Sự kiện cuộc sống")
            if mem["life_events"]:
                for t in list(dict.fromkeys(mem["life_events"]))[:6]:
                    st.markdown(f"• {LIFE_EVENT_LABELS.get(t, t)}")
            else:
                st.caption("Chưa có")

            st.markdown("#### 💰 Tích lũy")
            st.markdown(
                f'<span style="background:linear-gradient(135deg,#FF8FAF,#7EC8E3);'
                f'color:white;border-radius:20px;padding:4px 14px;'
                f'font-weight:700;">{stage_name_p}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"Đã tích lũy: **{fmt(mem['total_saved'])}** · Streak: **{mem['streak']} ngày**")

        with c2:
            st.markdown("#### 🛡️ Khẩu vị rủi ro")
            risk_ans = st.radio(
                "Nếu đầu tư 10 triệu và còn 8 triệu:",
                ["😰 Bán ngay, không dám chờ",
                 "🤔 Chờ xem, cân nhắc thêm",
                 "😎 Không lo, thậm chí mua thêm"],
                key="profile_risk",
            )
            risk_map = {
                "😰 Bán ngay, không dám chờ":  ("low",    "🌿 Ưa ổn định",  "TCBF"),
                "🤔 Chờ xem, cân nhắc thêm":    ("medium", "🌊 Cân bằng",    "TCFF"),
                "😎 Không lo, thậm chí mua thêm":("high",  "⚡ Dám rủi ro",  "TCEF"),
            }
            r_val, r_label, r_fund = risk_map[risk_ans]
            genome["risk_type"] = r_label
            _save()
            st.markdown(f"**{r_label}** · Quỹ tham khảo: **{r_fund}**")

            st.markdown("#### 🔥 Động lực")
            motive = st.selectbox("Bạn tích lũy vì:", [
                "Muốn an tâm về tương lai",
                "Có giấc mơ muốn thực hiện",
                "Trách nhiệm với gia đình",
                "Muốn tự do tài chính",
                "Đang thử nghiệm, chưa chắc",
            ], key="profile_motive")
            genome["personality"] = motive
            _save()

            st.markdown("#### 📈 Giai đoạn")
            stage_p = st.selectbox("Bạn đang ở:", [
                "🌱 Mới bắt đầu tích lũy",
                "🌿 Đang hình thành thói quen",
                "🌳 Đã có nền tảng vững",
                "🌴 Tối ưu hóa danh mục",
            ], key="profile_stage")
            genome["stage"] = stage_p
            _save()

        st.markdown("---")
        st.subheader("💡 Gợi ý từ Cừu Coach")
        rf_key2 = recommend_fund(3, r_val)
        rf2     = FUNDS[rf_key2]
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            with st.container(border=True):
                st.markdown(f"**{rf2['emoji']} {rf_key2}**")
                st.caption(rf2["mô_tả"])
        with cc2:
            with st.container(border=True):
                st.markdown("**🔄 Đầu tư đều đặn**")
                st.caption("Cố định mỗi tháng, không cần chọn thời điểm.")
        with cc3:
            with st.container(border=True):
                st.markdown("**📅 Kiên nhẫn dài hạn**")
                st.caption("Nhìn vào 3-5 năm, đừng lo biến động ngắn hạn.")

        st.warning(
            "⚠️ **Lưu ý:** Tất cả thông tin chỉ mang tính tham khảo và giáo dục tài chính cơ bản. "
            "Cừu Cần Cù KHÔNG phải công ty tư vấn đầu tư được cấp phép. "
            "Hãy tự nghiên cứu và/hoặc tham khảo chuyên gia trước khi ra quyết định đầu tư."
        )
