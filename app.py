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
    # Nhật ký
    "diary":  ["sheep_diary",  "diary"],
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
        "diary":      "📔 Cừu đang giữ nhật ký cho bạn...",
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
        _remaining = next_threshold - total_saved
        _next_stage = next((s for s in GROWTH_STAGES if s[0] == next_threshold), None)
        _next_name  = _next_stage[2] if _next_stage else "giai đoạn tiếp theo"
        prog = min(1.0, total_saved / next_threshold) if next_threshold > 0 else 1.0
        st.progress(prog, text=f"🎯 Chỉ cần thêm {fmt(_remaining)} để trở thành {_next_name}!")


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
    "last_fed_date":   "",
    "last_visit_date": "",
    "sentiment":       "neutral",
    "wealth_genome": {
        "risk_type":   "",
        "personality": "",
        "stage":       "",
    },
    "diary_entries": [],
    "last_fed_amount": 0,
    "last_fed_food":   "",
    "just_leveled_up": False,
    "prev_stage_key": "baby",
}

MICRO_AMOUNTS = [10_000, 20_000, 50_000, 100_000]

FEED_OPTIONS = [
    (10_000,  "🥕", "Bữa ăn nhỏ"),
    (20_000,  "🍎", "Bữa ăn đủ no"),
    (50_000,  "🎂", "Tiệc nhỏ"),
    (100_000, "🎉", "Đại tiệc"),
]


def _init():
    defs = {
        "api_key":      "",
        "messages":     [],
        "user_memory":  deepcopy(MEMORY_DEFAULT),
        "sheep_mood":   "default",
        "_quick_reply": None,
        "feeding_celebration": False,
        "feeding_refused":     False,
        "diary_mood_sel":      None,
        "diary_just_saved":    False,
        "diary_last_entry":    None,
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
# DIARY HELPERS
# ═══════════════════════════════════════════════════════
def _diary_streak(entries: list[dict]) -> int:
    """Consecutive days with diary entries (today counts; allow 1-day gap)."""
    if not entries:
        return 0
    today = datetime.now().date()
    dates = sorted(
        {datetime.fromisoformat(e["date_raw"]).date() for e in entries},
        reverse=True,
    )
    if not dates or dates[0] < today - timedelta(days=1):
        return 0
    streak, check = 0, today
    for d in dates:
        if d >= check - timedelta(days=1):
            streak += 1
            check   = d
        else:
            break
    return streak


def _top_diary_theme(entries: list[dict]) -> str:
    """Most common life-event tag across all diary entries."""
    from collections import Counter
    all_tags = [t for e in entries for t in e.get("tags", [])]
    return Counter(all_tags).most_common(1)[0][0] if all_tags else ""


def _top_diary_dream(entries: list[dict]) -> str:
    """Most frequently mentioned dream across diary entries."""
    from collections import Counter
    dreams = [e["dream"] for e in entries if e.get("dream")]
    return Counter(dreams).most_common(1)[0][0] if dreams else ""


def _build_diary_insights(mood: str, tags: list, dream: str, content: str) -> list[str]:
    """Return up to 4 human-readable insight bullets from a diary entry."""
    insights: list[str] = []
    mood_map = {
        "rất vui":        "Bạn đang trong trạng thái rất vui ✨",
        "áp lực":         "Bạn đang chịu một chút áp lực",
        "hơi mệt":        "Bạn đang cảm thấy mệt mỏi",
        "bực":            "Có điều gì đó đang làm bạn khó chịu",
        "quyết tâm":      "Bạn đang rất quyết tâm 💪",
        "được lắng nghe": "Bạn cần được lắng nghe hôm nay",
    }
    for k, v in mood_map.items():
        if k in mood.lower():
            insights.append(v)
            break
    tag_map = {
        "cashflow":       "Bạn đang áp lực công việc / tài chính",
        "stress":         "Bạn đang có stress cần giải tỏa",
        "dream_travel":   "Bạn muốn đi du lịch",
        "dream_house":    "Bạn mong có ngôi nhà riêng",
        "dream_car":      "Bạn mong có xe riêng",
        "dream_business": "Bạn đang ấp ủ khởi nghiệp",
        "education":      "Bạn đang lo về học hành / thi cử",
        "career":         "Bạn đang suy nghĩ về sự nghiệp",
        "emotional":      "Bạn đang có chuyện cảm xúc",
        "family":         "Bạn đang nghĩ về gia đình",
        "health":         "Bạn đang chú ý đến sức khỏe",
        "milestone":      "Bạn vừa trải qua một cột mốc quan trọng",
    }
    for tag in tags:
        if tag in tag_map and len(insights) < 3:
            insights.append(tag_map[tag])
    if dream and len(insights) < 4:
        insights.append(f"Bạn có giấc mơ: **{dream}** 💭")
    if not insights:
        insights.append("Bạn đã dành thời gian ghi lại hôm nay — đó là điều tuyệt vời 🌿")
    return insights[:4]


def _build_memory_card(mem: dict) -> list[tuple[str, str]]:
    """
    Build (emoji, text) pairs for the "Điều mình nhớ về bạn" card.
    Pulls from dreams, life_events, notes. Returns up to 5 items.
    """
    items: list[tuple[str, str]] = []

    # ── Tên người dùng ──
    if mem.get("name") and len(items) < 5:
        items.append(("👤", f"Tên bạn là {mem['name']}"))

    # ── Giấc mơ (ưu tiên nhất) ──
    for d in mem.get("dreams", [])[:2]:
        if len(items) >= 5:
            break
        name = d.get("name", "").strip()
        if name:
            items.append(("🎯", f"Muốn {name.lower()}"))

    # ── Tags cuộc sống ──
    _tag_display = {
        "dream_travel":   ("✈️",  "Muốn đi du lịch"),
        "dream_house":    ("🏠",  "Mơ có ngôi nhà riêng"),
        "dream_car":      ("🚗",  "Mơ có xe riêng"),
        "dream_business": ("🏪",  "Đang ấp ủ khởi nghiệp"),
        "cashflow":       ("💸",  "Đang cố gắng tiết kiệm"),
        "education":      ("📚",  "Quan tâm học tập"),
        "career":         ("💼",  "Đang suy nghĩ về công việc"),
        "family":         ("❤️",  "Muốn chăm sóc gia đình"),
        "health":         ("🌱",  "Quan tâm sức khỏe"),
        "stress":         ("😓",  "Đang có áp lực"),
        "emotional":      ("💙",  "Đang có chuyện cảm xúc"),
        "milestone":      ("🎊",  "Vừa qua một cột mốc"),
    }
    seen_tags: set[str] = set()
    for tag in reversed(mem.get("life_events", [])):    # most recent first
        if len(items) >= 5:
            break
        if tag in _tag_display and tag not in seen_tags:
            seen_tags.add(tag)
            items.append(_tag_display[tag])

    # ── Memory notes (tóm tắt ngắn) ──
    for note in reversed(mem.get("notes", [])[-3:]):
        if len(items) >= 5:
            break
        short = note.strip()[:38]
        if short:
            items.append(("📝", short + ("..." if len(note) > 38 else "")))

    return items[:5]


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

/* ── Diary-specific components ── */
.diary-prompt {
    background: rgba(255,240,200,0.45);
    border-left: 3px solid #FFB5C8;
    border-radius: 0 10px 10px 0;
    padding: 9px 14px;
    margin: 14px 0 5px;
    font-size: 0.93rem;
    font-weight: 700;
    color: #C4607F;
    line-height: 1.4;
}
.insight-card {
    background: linear-gradient(135deg, #FFF5FA, #F0F7FF);
    border: 2px solid #FFD6E8;
    border-radius: 20px;
    padding: 24px 20px;
    text-align: center;
    margin: 12px 0 16px;
    animation: pulse 0.8s ease-in-out;
}
.diary-stat-mini {
    background: white;
    border: 1.5px solid #FFD6E8;
    border-radius: 12px;
    padding: 10px 10px 8px;
    text-align: center;
    min-height: 62px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 2px;
}
.diary-entry-card {
    background: white;
    border: 1.5px solid #F0E6F0;
    border-radius: 14px;
    padding: 12px 14px;
    margin: 6px 0 4px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.diary-entry-card:hover {
    border-color: #FFB5C8;
    box-shadow: 0 2px 10px rgba(255,150,200,0.15);
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
# 5 TABS NAVIGATION
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chia sẻ cảm xúc",
    "📔 Nhật ký tâm sự",
    "❤️ Hành trình nuôi cừu",
    "🧬 Hồ sơ tài chính",
    "🎨 Xem Thiết Kế",
])


# ═══════════════════════════════════════════════════════
# TAB 1 — CHIA SẺ CẢM XÚC  v3.2
# UX: "Người bạn đồng hành — mở app vì muốn gặp Cừu"
# Hierarchy: Mascot → Mình đang nghe → Nhớ về bạn → Tiến bộ → Chips → Chat
# ═══════════════════════════════════════════════════════
with tab1:

    # ── Detect returning user ──
    _today_str   = datetime.now().strftime("%Y-%m-%d")
    _last_visit  = mem.get("last_visit_date", "")
    _is_returning = bool(_last_visit) and _last_visit != _today_str
    if mem.get("last_visit_date") != _today_str:
        mem["last_visit_date"] = _today_str
        _save()

    # ──────────────────────────────────────────────────
    # LEVEL 1: MASCOT — trung tâm màn hình, 300px
    # ──────────────────────────────────────────────────
    # Emotion Engine: chọn mood dựa trên context
    _hero_mood = st.session_state.get("sheep_mood", "default")
    if _is_returning and not st.session_state.messages:
        _hero_mood = "miss_you"       # Cừu nhớ bạn
    elif not st.session_state.messages:
        _hero_mood = "listening"      # Cừu đang sẵn sàng

    _hero_src = _b64(_pick_mascot(_hero_mood))
    st.markdown(
        f'<div style="text-align:center;padding:28px 0 10px;">'
        f'<img src="{_hero_src}" width="300" '
        f'style="border-radius:50%;'
        f'border:6px solid #FFB5C8;'
        f'box-shadow:0 20px 60px rgba(255,140,190,0.45),'
        f'0 0 0 16px rgba(255,182,193,0.13);" />'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ──────────────────────────────────────────────────
    # LEVEL 2: TAGLINE — "Mình đang nghe đây"
    # ──────────────────────────────────────────────────
    _name_str  = mem.get("name", "").strip()
    _return_line = ""
    if _is_returning and _name_str:
        _return_line = (
            f'<div style="color:#FF8FAF;font-size:0.92rem;font-weight:600;'
            f'margin-bottom:6px;">💙 {_name_str} ơi, mình nhớ bạn lắm!</div>'
        )
    elif _is_returning:
        _return_line = (
            '<div style="color:#FF8FAF;font-size:0.92rem;font-weight:600;'
            'margin-bottom:6px;">💙 Bạn quay lại rồi! Mình nhớ bạn lắm!</div>'
        )

    st.markdown(
        f'<div style="text-align:center;padding:4px 0 18px;">'
        f'{_return_line}'
        f'<div style="font-size:1.65rem;font-weight:800;color:#C4607F;margin-bottom:7px;">'
        f'🐑 Mình đang nghe đây</div>'
        f'<div style="font-size:0.97rem;color:#666;margin-bottom:4px;">'
        f'Có chuyện gì đang diễn ra với bạn hôm nay?</div>'
        f'<div style="font-size:0.88rem;color:#bbb;">'
        f'Bạn có thể kể cho mình bất cứ điều gì.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ──────────────────────────────────────────────────
    # PHẦN 6: HÀNH TRÌNH QUAY LẠI — streak card
    # ──────────────────────────────────────────────────
    if mem.get("streak", 0) > 1:
        _, _t1_sname, _, _, _ = get_growth_stage(mem["total_saved"])
        st.markdown(
            f'<div style="background:linear-gradient(135deg,'
            f'rgba(255,245,250,0.95),rgba(238,245,255,0.95));'
            f'border:1.5px solid #FFD6E8;border-radius:16px;'
            f'padding:11px 22px;text-align:center;margin:0 0 14px;">'
            f'🐑 Hôm nay là ngày thứ '
            f'<strong style="color:#C4607F;">{mem["streak"]}</strong>'
            f' bạn gặp mình &nbsp;·&nbsp; '
            f'🔥 Streak <strong>{mem["streak"]} ngày</strong>'
            f' &nbsp;·&nbsp; {_t1_sname}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ──────────────────────────────────────────────────
    # PHẦN 2: MEMORY CARD — "Điều mình đang nhớ về bạn"
    # ──────────────────────────────────────────────────
    _mem_items = _build_memory_card(mem)
    if _mem_items:
        _mem_chips = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:4px;'
            f'background:white;border:1.5px solid #FFD6E8;border-radius:20px;'
            f'padding:5px 13px;font-size:0.87rem;color:#444;'
            f'margin:3px 2px;white-space:nowrap;">{_e} {_t}</span>'
            for _e, _t in _mem_items
        )
        st.markdown(
            f'<div style="background:linear-gradient(135deg,'
            f'rgba(255,220,235,0.25),rgba(210,230,255,0.25));'
            f'border:1.5px solid #FFD6E8;border-radius:18px;'
            f'padding:16px 20px;margin:0 0 14px;">'
            f'<div style="font-size:0.88rem;font-weight:700;color:#C4607F;'
            f'margin-bottom:11px;">🐑 Điều mình đang nhớ về bạn</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:0;">{_mem_chips}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:rgba(255,220,235,0.1);'
            'border:1.5px solid #FFD6E8;border-radius:18px;'
            'padding:13px 20px;margin:0 0 12px;text-align:center;">'
            '<span style="color:#bbb;font-size:0.88rem;">'
            '🐑 Mình vẫn đang tìm hiểu thêm về bạn...</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ──────────────────────────────────────────────────
    # PHẦN 4: PROGRESS STRIP — chỉ khi có dữ liệu
    # ──────────────────────────────────────────────────
    _has_prog = (
        mem.get("streak", 0) > 0
        or mem.get("total_saved", 0) > 0
        or mem.get("dreams")
        or len(st.session_state.messages) >= 2
    )
    if _has_prog:
        _, _ps_name, _, _, _ = get_growth_stage(mem["total_saved"])
        _pd_dream = mem["dreams"][0]["name"].title() if mem.get("dreams") else "—"
        _pt_tag   = (
            LIFE_EVENT_LABELS.get(mem["life_events"][-1], "—")
            if mem.get("life_events") else "—"
        )
        _p_chats  = len(st.session_state.messages) // 2
        _pc1, _pc2, _pc3, _pc4 = st.columns(4)
        for _pcol, _pval, _plbl in [
            (_pc1, str(mem.get("streak", 0)), "🔥 Streak"),
            (_pc2, _ps_name,                  "🐑 Cừu lớn"),
            (_pc3, _pd_dream[:14],            "🎯 Giấc mơ"),
            (_pc4, str(_p_chats),             "💬 Lần chat"),
        ]:
            _pcol.markdown(
                f'<div class="diary-stat-mini">'
                f'<div style="font-size:0.88rem;font-weight:800;'
                f'color:#C4607F;line-height:1.3;">{_pval}</div>'
                f'<div style="font-size:0.73rem;color:#888;margin-top:2px;">{_plbl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div style="margin-bottom:14px;"></div>', unsafe_allow_html=True
        )

    # ──────────────────────────────────────────────────
    # PHẦN 3: CHIPS — ngắn, hội thoại, chỉ khi chưa chat
    # ──────────────────────────────────────────────────
    if not st.session_state.messages:
        _chips_v2 = [
            "📚 Em đang áp lực chuyện học",
            "💸 Em đang lo về tiền bạc",
            "💔 Hôm nay em không vui",
            "✨ Em có một giấc mơ",
            "🌱 Em muốn thay đổi cuộc sống",
            "💼 Em đang suy nghĩ về công việc",
        ]
        _chip_prompts_v2 = {
            "📚 Em đang áp lực chuyện học":
                "Cừu ơi, em đang rất áp lực về việc học và kỳ thi. Lắng nghe em với nhé?",
            "💸 Em đang lo về tiền bạc":
                "Cừu ơi, em đang lo lắng về tài chính và tiền bạc, áp lực lắm.",
            "💔 Hôm nay em không vui":
                "Cừu ơi, hôm nay em không vui, muốn chia sẻ với Cừu.",
            "✨ Em có một giấc mơ":
                "Cừu ơi, em có một ước mơ muốn kể! Em cần được động viên.",
            "🌱 Em muốn thay đổi cuộc sống":
                "Cừu ơi, em muốn thay đổi cuộc sống nhưng chưa biết bắt đầu từ đâu.",
            "💼 Em đang suy nghĩ về công việc":
                "Cừu ơi, em đang cân nhắc thay đổi hướng đi sự nghiệp, cần được lắng nghe.",
        }
        _qcols = st.columns(3)
        for _ci, _chip in enumerate(_chips_v2):
            if _qcols[_ci % 3].button(_chip, use_container_width=True, key=f"chip_{_ci}"):
                st.session_state._quick_reply = _chip_prompts_v2[_chip]
                st.session_state.messages.append({"role": "user", "content": _chip})
                st.rerun()

    # ── Handle quick reply ──
    if st.session_state._quick_reply:
        _qr = st.session_state._quick_reply
        st.session_state._quick_reply = None
        with st.spinner("Cừu đang nghĩ... 🐑"):
            _result_qr = _call_llm(_qr, _SYS_EMOTION)
        _reply_qr = _result_qr.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe!")
        st.session_state.messages.append({"role": "assistant", "content": _reply_qr})
        st.rerun()

    # ── Smart suggestion (contextual only) ──
    _suggestion = get_smart_suggestion(st.session_state.messages, mem)
    if _suggestion:
        st.markdown(
            f'<div class="suggestion-box">{_suggestion}</div>',
            unsafe_allow_html=True,
        )

    # ── LEVEL 5: Chat history ──
    if st.session_state.messages:
        st.markdown("---")
        for _m in st.session_state.messages[-12:]:
            _av = get_avatar_src("listening") if _m["role"] == "assistant" else "🧑"
            with st.chat_message(_m["role"], avatar=_av):
                st.markdown(_m["content"])

    # ── Chat input ──
    _user_msg = st.chat_input("Nhắn tin với Cừu Cần Cù... 🐑")
    if _user_msg:
        _expanded = _EMOTION_EXPAND.get(_user_msg.strip().lower(), _user_msg)
        st.session_state.messages.append({"role": "user", "content": _user_msg})
        with st.spinner("Cừu đang lắng nghe... 🐑"):
            _result_msg = _call_llm(_expanded, _SYS_EMOTION)
        _reply_msg = _result_msg.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe nè!")
        st.session_state.messages.append({"role": "assistant", "content": _reply_msg})
        st.rerun()


# ═══════════════════════════════════════════════════════
# TAB 2 — NHẬT KÝ TÂM SỰ  v3.1
# UX: "Mình đang viết cho Cừu" — KHÔNG phải "điền form"
# ═══════════════════════════════════════════════════════
with tab2:
    diary_entries: list[dict] = mem.get("diary_entries", [])

    # ── PHẦN 1: HERO — sheep_diary + tagline ──
    col_dimg, col_dhdr = st.columns([1, 4])
    with col_dimg:
        show_sheep("diary", width=180, show_badge=False)
    with col_dhdr:
        st.title("🐑 Nhật Ký Tâm Sự")
        st.markdown(
            '<div class="diary-framing">'
            '<strong style="color:#5A7A4A;font-size:1rem;">'
            '📖 Cừu sẽ giữ giúp bạn những điều của hôm nay.</strong><br/>'
            '<span style="color:#777;font-size:0.88rem;">'
            'Để sau này nhìn lại, bạn sẽ thấy mình đã trưởng thành như thế nào.<br/>'
            '<em>Không phải chat realtime — đây là không gian riêng tư của bạn.</em>'
            '</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── PHẦN 6: PROGRESS STATS — chỉ hiện khi có entries ──
    if diary_entries:
        d_streak  = _diary_streak(diary_entries)
        d_theme   = _top_diary_theme(diary_entries)
        d_dream   = _top_diary_dream(diary_entries)
        d_last_r  = diary_entries[0].get("reply", "") if diary_entries else ""
        top_lbl   = LIFE_EVENT_LABELS.get(d_theme, d_theme) if d_theme else "—"
        dream_lbl = d_dream.title() if d_dream else "—"

        st.markdown("---")
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sc1.markdown(
            f'<div class="diary-stat-mini">'
            f'<div style="font-size:1.3rem;font-weight:800;color:#C4607F;">{len(diary_entries)}</div>'
            f'<div style="font-size:0.76rem;color:#888;">📖 Tổng trang</div>'
            f'</div>', unsafe_allow_html=True,
        )
        sc2.markdown(
            f'<div class="diary-stat-mini">'
            f'<div style="font-size:1.3rem;font-weight:800;color:#C4607F;">{d_streak}</div>'
            f'<div style="font-size:0.76rem;color:#888;">🔥 Streak</div>'
            f'</div>', unsafe_allow_html=True,
        )
        sc3.markdown(
            f'<div class="diary-stat-mini">'
            f'<div style="font-size:0.85rem;font-weight:700;color:#4E7DB8;">{top_lbl[:16]}</div>'
            f'<div style="font-size:0.76rem;color:#888;">💙 Hay tâm sự</div>'
            f'</div>', unsafe_allow_html=True,
        )
        sc4.markdown(
            f'<div class="diary-stat-mini">'
            f'<div style="font-size:0.85rem;font-weight:700;color:#4E7DB8;">{dream_lbl[:16]}</div>'
            f'<div style="font-size:0.76rem;color:#888;">🎯 Giấc mơ thường</div>'
            f'</div>', unsafe_allow_html=True,
        )
        preview_r = f'"{d_last_r[:36]}..."' if len(d_last_r) > 36 else f'"{d_last_r}"'
        sc5.markdown(
            f'<div class="diary-stat-mini">'
            f'<div style="font-size:0.78rem;color:#666;font-style:italic;">{preview_r}</div>'
            f'<div style="font-size:0.76rem;color:#888;">🐑 Cừu nhớ nhất</div>'
            f'</div>', unsafe_allow_html=True,
        )

    st.markdown("---")

    DIARY_MOODS_V2 = [
        ("😊", "Mình rất vui"),
        ("😔", "Có chút áp lực"),
        ("😴", "Hơi mệt"),
        ("😡", "Bực một chuyện"),
        ("💪", "Đang quyết tâm"),
        ("🥹", "Muốn được lắng nghe"),
    ]

    col_write, col_history = st.columns([3, 2])

    # ─────────────────────────────────────────────────────
    # LEFT: WRITING SECTION
    # ─────────────────────────────────────────────────────
    with col_write:

        # ── PHẦN 4: INSIGHT CARD — hiển thị sau khi lưu ──
        if st.session_state.get("diary_just_saved") and st.session_state.get("diary_last_entry"):
            last_e   = st.session_state.diary_last_entry
            insights = _build_diary_insights(
                last_e.get("mood", ""),
                last_e.get("tags", []),
                last_e.get("dream", ""),
                last_e.get("content", ""),
            )
            diary_src = _b64(_pick_mascot("diary"))

            insight_html = "".join(
                f'<div style="display:flex;align-items:flex-start;gap:8px;margin:5px 0;text-align:left;">'
                f'<span style="color:#FF8FAF;font-weight:700;flex-shrink:0;">•</span>'
                f'<span style="font-size:0.9rem;color:#444;line-height:1.5;">{ins}</span>'
                f'</div>'
                for ins in insights
            )
            st.markdown(
                f'<div class="insight-card">'
                f'<img src="{diary_src}" width="88" '
                f'style="border-radius:50%;border:4px solid #FFB5C8;margin-bottom:12px;" /><br/>'
                f'<strong style="color:#C4607F;font-size:1.08rem;">'
                f'🐑 Hôm nay mình hiểu thêm về bạn</strong>'
                f'<div style="margin:14px 0 10px;padding:0 4px;">{insight_html}</div>'
                f'<div style="color:#4E7DB8;font-size:0.92rem;font-style:italic;">'
                f'💙 Mình sẽ nhớ điều này giúp bạn.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if last_e.get("reply"):
                st.markdown(
                    f'<div style="background:rgba(255,182,210,0.15);border-radius:14px;'
                    f'padding:12px 16px;margin:6px 0 14px;font-style:italic;color:#C4607F;">'
                    f'🐑 Cừu nhắn: <strong>{last_e["reply"]}</strong>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if last_e.get("dream"):
                st.markdown(
                    f'<div style="background:rgba(200,240,200,0.3);border-radius:12px;'
                    f'padding:10px 14px;margin:6px 0;">'
                    f'✨ Cừu phát hiện giấc mơ: <strong>{last_e["dream"]}</strong>!'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if st.button("✏️ Viết thêm hôm nay", type="primary", use_container_width=True):
                st.session_state.diary_just_saved = False
                st.session_state.diary_last_entry = None
                for k in ("dq1", "dq2", "dq3"):
                    st.session_state.pop(k, None)
                st.session_state.diary_mood_sel = None
                st.rerun()

        else:
            # ── PHẦN 2: CHỌN CẢM XÚC — mood chips ──
            st.markdown(
                '<div style="font-size:1rem;font-weight:700;color:#C4607F;margin-bottom:10px;">'
                '🐑 Hôm nay bạn thế nào?</div>',
                unsafe_allow_html=True,
            )
            mood_cols = st.columns(3)
            for i, (emoji, label) in enumerate(DIARY_MOODS_V2):
                full_label = f"{emoji} {label}"
                is_sel     = (st.session_state.get("diary_mood_sel") == full_label)
                if mood_cols[i % 3].button(
                    full_label,
                    key=f"dmood_{i}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary",
                ):
                    st.session_state.diary_mood_sel = full_label
                    st.rerun()

            current_mood = st.session_state.get("diary_mood_sel") or ""

            # ── PHẦN 3: 3 KHUNG VIẾT CÓ GỢI MỞ ──
            st.markdown(
                '<div class="diary-prompt">🐑 Hôm nay điều gì khiến bạn nhớ nhất?</div>',
                unsafe_allow_html=True,
            )
            q1 = st.text_area(
                "",
                placeholder="Kể cho mình nghe... (không cần viết nhiều)",
                height=100, key="dq1", label_visibility="collapsed",
            )

            st.markdown(
                '<div class="diary-prompt">🐑 Có điều gì khiến bạn vui, buồn hoặc lo lắng không?</div>',
                unsafe_allow_html=True,
            )
            q2 = st.text_area(
                "",
                placeholder="Vài dòng thôi cũng được...",
                height=100, key="dq2", label_visibility="collapsed",
            )

            st.markdown(
                '<div class="diary-prompt">🐑 Có điều gì bạn muốn nhắn cho chính mình trong tương lai?</div>',
                unsafe_allow_html=True,
            )
            q3 = st.text_area(
                "",
                placeholder="Ghi lại điều bạn muốn nhớ...",
                height=100, key="dq3", label_visibility="collapsed",
            )

            # ── PHẦN 4: SAVE CTA ──
            has_content = any([q1.strip(), q2.strip(), q3.strip()])
            if st.button(
                "💾 Lưu vào nhật ký của Cừu",
                type="primary",
                use_container_width=True,
                disabled=not has_content,
            ):
                combined = "\n\n".join(filter(None, [
                    f"Điều nhớ nhất: {q1.strip()}"       if q1.strip() else "",
                    f"Cảm xúc hôm nay: {q2.strip()}"     if q2.strip() else "",
                    f"Nhắn cho tương lai: {q3.strip()}"   if q3.strip() else "",
                ]))
                sheep_reply  = "Bê bê~ 🐑 Cừu đã đọc rồi! Cảm ơn bạn đã tin tưởng 💙"
                emotion_tag  = "bình_thường"
                dream_det    = ""
                entry_tags: list[str] = []

                if st.session_state.api_key:
                    with st.spinner("Cừu đang đọc nhật ký... 📖"):
                        r = _call_llm(
                            f"Nhật ký hôm nay:\nTâm trạng: {current_mood}\n{combined[:600]}",
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
                    "title":    f"Ngày {datetime.now().strftime('%d/%m')}",
                    "mood":     current_mood or "🐑 Bình thường",
                    "content":  combined,
                    "emotion":  emotion_tag,
                    "tags":     entry_tags,
                    "dream":    dream_det,
                    "reply":    sheep_reply,
                }
                diary_entries.insert(0, entry)
                mem["diary_entries"] = diary_entries
                _save()

                st.session_state.diary_just_saved = True
                st.session_state.diary_last_entry = entry
                st.rerun()

            if not has_content:
                st.caption("Viết ít nhất một điều để Cừu có thể lưu giúp bạn 🌿")

            if diary_entries:
                dl = json.dumps(diary_entries, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ Tải nhật ký về máy", dl,
                    "nhat_ky_tam_su.json", "application/json",
                )

    # ─────────────────────────────────────────────────────
    # RIGHT: TIMELINE — PHẦN 5 & 7
    # ─────────────────────────────────────────────────────
    with col_history:
        if not diary_entries:
            # Empty state: emotional hook
            st.markdown(
                '<div style="text-align:center;padding:40px 16px 20px;">'
                '<div style="font-size:2.4rem;margin-bottom:8px;">🌱</div>'
                '<div style="font-weight:800;color:#5A7A4A;font-size:1.05rem;margin-bottom:10px;">'
                'Trang đầu tiên đang chờ bạn.</div>'
                '<div style="color:#888;font-size:0.88rem;line-height:1.7;font-style:italic;">'
                '"Mọi giấc mơ lớn đều bắt đầu<br/>từ một dòng nhật ký nhỏ."'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-weight:800;color:#4E7DB8;font-size:1.05rem;margin-bottom:6px;">'
                '📖 Hành trình trưởng thành</div>',
                unsafe_allow_html=True,
            )
            now = datetime.now()
            filter_opt = st.radio(
                "Xem:",
                ["Hôm nay", "Tuần này", "Tháng này", "Tất cả"],
                horizontal=True,
                label_visibility="collapsed",
                key="d_filter",
            )
            filtered = diary_entries
            if filter_opt == "Hôm nay":
                filtered = [e for e in diary_entries
                            if e["date_raw"][:10] == now.strftime("%Y-%m-%d")]
            elif filter_opt == "Tuần này":
                ago = (now - timedelta(days=7)).isoformat()
                filtered = [e for e in diary_entries if e["date_raw"] >= ago]
            elif filter_opt == "Tháng này":
                ms = now.strftime("%Y-%m")
                filtered = [e for e in diary_entries if e["date_raw"][:7] == ms]

            search = st.text_input(
                "🔍", placeholder="Tìm kiếm...", key="d_search",
                label_visibility="collapsed",
            )
            if search:
                sl = search.lower()
                filtered = [e for e in filtered
                            if sl in e["content"].lower() or sl in e["title"].lower()]

            st.caption(f"{len(filtered)} trang nhật ký")

            for entry in filtered:
                preview = entry["content"][:110] + ("..." if len(entry["content"]) > 110 else "")
                dream_line = (
                    f'<div style="color:#5A7A4A;font-size:0.82rem;margin-top:4px;">✨ {entry["dream"]}</div>'
                    if entry.get("dream") else ""
                )
                tags_line = " ".join(
                    LIFE_EVENT_LABELS.get(t, t)
                    for t in entry.get("tags", [])[:2]
                )
                reply_preview = ""
                if entry.get("reply"):
                    rp = entry["reply"]
                    reply_preview = (
                        f'<div style="color:#C4607F;font-size:0.82rem;'
                        f'margin-top:6px;font-style:italic;">'
                        f'🐑 {rp[:55]}{"..." if len(rp)>55 else ""}</div>'
                    )

                tags_div = (
                    f'<div style="font-size:0.76rem;color:#aaa;margin-top:3px;">{tags_line}</div>'
                    if tags_line else ""
                )
                st.markdown(
                    f'<div class="diary-entry-card">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                    f'<span style="font-weight:700;color:#444;font-size:0.88rem;">{entry["mood"]}</span>'
                    f'<span style="font-size:0.76rem;color:#bbb;">{entry["date"][:8]}</span>'
                    f'</div>'
                    f'<div style="font-size:0.85rem;color:#666;margin:6px 0 2px;line-height:1.55;">'
                    f'{preview}</div>'
                    f'{dream_line}'
                    f'{tags_div}'
                    f'{reply_preview}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button("🗑️", key=f"del_{entry['id']}", help="Xoá trang này"):
                    mem["diary_entries"] = [e for e in diary_entries if e["id"] != entry["id"]]
                    _save()
                    st.rerun()


# ═══════════════════════════════════════════════════════
# TAB 3 — HÀNH TRÌNH NUÔI CỪU
# UX: Food metaphors, unlock rewards, Moment of Joy/Kindness, dream linkage
# ═══════════════════════════════════════════════════════
with tab3:
    total_saved = mem.get("total_saved", 0)
    stage_key, stage_name, lv_num, stage_desc, stage_msg = get_growth_stage(total_saved)

    _STAGE_REWARDS = {
        "baby":   "🌱 Được gặp bạn lần đầu",
        "child":  "💌 Cừu nhớ tên bạn rồi",
        "teen":   "🌙 Cừu kể chuyện buổi tối",
        "adult":  "✨ Cừu đặt tên theo giấc mơ",
        "master": "🏆 Cừu Lão Luyện — đồng hành mãi mãi",
    }

    col_left, col_right = st.columns([2, 3])

    # ── LEFT: Sheep + unlock roadmap ──
    with col_left:
        show_growth_sheep(total_saved, width=200)

        st.markdown(
            '<p style="font-size:0.85rem;font-weight:700;color:#C4607F;margin:14px 0 6px;">'
            '🗺️ Hành trình của Cừu</p>',
            unsafe_allow_html=True,
        )
        for i, (thresh, skey, sname, slv, sdesc, _) in enumerate(GROWTH_STAGES):
            is_current  = skey == stage_key
            is_unlocked = total_saved >= thresh
            _reward     = _STAGE_REWARDS.get(skey, "")
            if is_current:
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#FFF0F5,#FFE4F0);'
                    f'border:2px solid #FFB5C8;border-radius:12px;padding:10px 12px;margin:4px 0;">'
                    f'<div style="font-size:0.8rem;font-weight:800;color:#C4607F;">▶ {sname}</div>'
                    f'<div style="font-size:0.72rem;color:#999;margin-top:2px;">{_reward}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            elif is_unlocked:
                st.markdown(
                    f'<div style="background:#F8F8F8;border:1.5px solid #E0E0E0;'
                    f'border-radius:12px;padding:8px 12px;margin:4px 0;opacity:0.72;">'
                    f'<div style="font-size:0.78rem;font-weight:700;color:#AAA;text-decoration:line-through;">{sname}</div>'
                    f'<div style="font-size:0.7rem;color:#CCC;">✅ Đã mở khóa · {_reward}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:#FAFAFA;border:1.5px dashed #E0CCF0;'
                    f'border-radius:12px;padding:8px 12px;margin:4px 0;">'
                    f'<div style="font-size:0.78rem;font-weight:700;color:#C0A8D8;">🔒 {sname}</div>'
                    f'<div style="font-size:0.7rem;color:#CCC;margin-top:2px;">'
                    f'Cần {fmt(thresh)} · {_reward}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ── RIGHT: Main interaction ──
    with col_right:

        # PHẦN 1: Hero in Cừu's first-person voice
        _hero_lines = {
            "baby":   ("🥕", f"\"Mình vừa ra đời... còn bé lắm 🐑<br/>Cho mình ăn bữa đầu tiên nhé?\""),
            "child":  ("🍎", f"\"Mình lớn hơn rồi nhờ {mem.get('name','bạn')} đấy!<br/>Hôm nay cho mình ăn tiếp không?\""),
            "teen":   ("🎂", f"\"Mình đang lớn nhanh lắm~<br/>Cùng nhau đến đích thôi {mem.get('name','bạn')} ơi!\""),
            "adult":  ("🎉", f"\"Chúng mình đã đi được nửa đường rồi.<br/>Mình tự hào về {mem.get('name','bạn')} lắm ❤️\""),
            "master": ("🌟", f"\"Nhìn chúng mình đến đây...<br/>Cảm ơn {mem.get('name','bạn')} đã không bỏ cuộc 🏆\""),
        }
        _hfood, _htxt = _hero_lines.get(stage_key, _hero_lines["baby"])
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
            f'border-radius:16px;padding:16px 20px;text-align:center;margin-bottom:14px;">'
            f'<div style="font-size:2.2rem;">{_hfood}</div>'
            f'<div style="font-size:0.97rem;color:#C4607F;font-style:italic;margin-top:8px;line-height:1.6;">'
            f'{_htxt}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # PHẦN 5: Moment of Joy (celebration after feeding)
        if st.session_state.get("feeding_celebration"):
            fed_amt   = mem.get("last_fed_amount", 0)
            fed_food  = mem.get("last_fed_food", "")
            leveled   = mem.get("just_leveled_up", False)
            cur_key, cur_name, *_ = get_growth_stage(total_saved)
            cel_src   = _b64(_pick_mascot("celebrate"))

            _dream_link_html = ""
            if mem["dreams"]:
                _top_d      = mem["dreams"][0]
                _top_d_name = _top_d.get("name", "").title()
                _dream_link_html = (
                    f'<div style="background:rgba(255,215,0,0.15);border-radius:10px;'
                    f'padding:8px 14px;margin-top:10px;font-size:0.87rem;color:#B8860B;">'
                    f'✨ Giấc mơ <strong>{_top_d_name}</strong> vừa tiến thêm '
                    f'<strong>{fmt(fed_amt)}</strong>~</div>'
                )

            _leveled_html = ""
            if leveled:
                _leveled_html = (
                    f'<div style="font-size:1.1rem;font-weight:800;color:#C4607F;margin-top:12px;">'
                    f'🎊 Cừu vừa lớn thêm một giai đoạn! Chào mừng đến với {cur_name}!</div>'
                )

            _food_label = fed_food if fed_food else fmt(fed_amt)
            st.markdown(
                f'<div class="celebration-box" style="text-align:center;">'
                f'<img src="{cel_src}" width="100" style="border-radius:50%;border:4px solid #FFB5C8;" />'
                f'<div style="font-size:1.4rem;margin:6px 0;">🎉</div>'
                f'<strong style="font-size:1.05rem;color:#C4607F;">'
                f'Cừu được ăn {_food_label} rồi — bê bê cảm ơn bạn ❤️</strong>'
                f'{_dream_link_html}'
                f'{_leveled_html}'
                f'</div>',
                unsafe_allow_html=True,
            )
            mem["just_leveled_up"] = False
            mem["last_fed_amount"] = 0
            mem["last_fed_food"]   = ""
            st.session_state.feeding_celebration = False
            _save()
            st.balloons()

        # PHẦN 6: Moment of Kindness (skip — zero guilt)
        if st.session_state.get("feeding_refused"):
            kind_src = _b64(_pick_mascot("listening"))
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#F0F8FF,#EAF4FF);'
                f'border-radius:16px;padding:16px 20px;text-align:center;margin-bottom:12px;">'
                f'<img src="{kind_src}" width="76" style="border-radius:50%;border:3px solid #B5D8FF;" />'
                f'<div style="font-size:1rem;font-weight:700;color:#5B8DB8;margin-top:8px;">'
                f'Không sao cả 🌙</div>'
                f'<div style="font-size:0.88rem;color:#6A9BBF;margin-top:5px;">'
                f'Mình vẫn ở đây. Hôm nào sẵn sàng thì mình vẫn đợi~ 🐑</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.session_state.feeding_refused = False

        # PHẦN 2: Feed buttons — food metaphors
        st.markdown(
            '<p style="font-size:0.97rem;font-weight:700;color:#C4607F;margin:10px 0 6px;">'
            '🍽️ Hôm nay cho Cừu ăn gì?</p>',
            unsafe_allow_html=True,
        )
        _feed_cols = st.columns(4)
        for i, (amt, food_emoji, food_name) in enumerate(FEED_OPTIONS):
            if _feed_cols[i].button(
                f"{food_emoji} {food_name}\n{fmt(amt)}",
                use_container_width=True,
                key=f"feed_{amt}",
                type="primary",
            ):
                _prev_key = stage_key
                mem["total_saved"]     += amt
                mem["streak"]          += 1
                mem["last_fed_amount"]  = amt
                mem["last_fed_food"]    = f"{food_emoji} {food_name}"
                mem["last_fed_date"]    = datetime.now().strftime("%Y-%m-%d")
                _new_key, *_ = get_growth_stage(mem["total_saved"])
                if _new_key != _prev_key:
                    mem["just_leveled_up"] = True
                set_mood("happy")
                st.session_state.feeding_celebration = True
                st.session_state.feeding_refused     = False
                _save()
                st.rerun()

        with st.expander("🔢 Nhập số tiền khác"):
            custom = st.number_input(
                "Số tiền:", min_value=1_000, max_value=100_000_000,
                step=10_000, value=30_000, key="custom_amt",
            )
            if st.button(f"🐑 Đầu tư {fmt(int(custom))}", type="primary", use_container_width=True):
                _prev_key = stage_key
                mem["total_saved"]    += int(custom)
                mem["streak"]         += 1
                mem["last_fed_amount"] = int(custom)
                mem["last_fed_food"]   = fmt(int(custom))
                _new_key, *_ = get_growth_stage(mem["total_saved"])
                if _new_key != _prev_key:
                    mem["just_leveled_up"] = True
                set_mood("happy")
                st.session_state.feeding_celebration = True
                _save()
                st.rerun()

        # PHẦN 9: Dream linkage cards
        if mem["dreams"]:
            st.markdown("---")
            st.markdown(
                '<p style="font-size:0.97rem;font-weight:700;color:#C4607F;margin-bottom:8px;">'
                '🎯 Giấc mơ đang được nuôi</p>',
                unsafe_allow_html=True,
            )
            for d in mem["dreams"][:3]:
                with st.container(border=True):
                    da, db = st.columns([3, 2])
                    with da:
                        st.markdown(f"**✨ {d['name'].title()}**")
                        if d["amount"] > 0:
                            pct = min(100, d["saved"] / d["amount"] * 100)
                            st.progress(pct / 100, text=f"{pct:.1f}% — còn {fmt(d['amount'] - d['saved'])}")
                    with db:
                        if d["amount"] > 0 and d["saved"] < d["amount"]:
                            if st.button("❤️ +50k", key=f"dream_{d['name']}", type="primary"):
                                d["saved"]             = min(d["amount"], d["saved"] + 50_000)
                                mem["total_saved"]    += 50_000
                                mem["last_fed_amount"] = 50_000
                                mem["last_fed_food"]   = f"❤️ cho {d['name'].title()}"
                                set_mood("celebrate" if d["saved"] >= d["amount"] else "happy")
                                st.session_state.feeding_celebration = True
                                _save()
                                st.rerun()
                        elif d["amount"] > 0:
                            st.success("🎉 Hoàn thành!")
        else:
            st.markdown("---")
            st.info("💭 Kể với Cừu về giấc mơ của bạn ở tab **💬 Chia sẻ cảm xúc** nhé!")

        # Skip for today
        st.markdown("---")
        if st.button("🌙 Hôm nay chưa sẵn sàng", use_container_width=True):
            set_mood("sad")
            st.session_state.feeding_refused     = True
            st.session_state.feeding_celebration = False
            _save()
            st.rerun()

    # ── PHẦN 7+8: Plain-language fund cards + Cừu's voice recommender ──
    st.markdown("---")
    st.markdown(
        '<p style="font-size:1.05rem;font-weight:800;color:#C4607F;margin-bottom:2px;">'
        '🐑 Cừu Giải Thích Quỹ Đầu Tư</p>'
        '<p style="font-size:0.8rem;color:#AAA;margin-bottom:14px;">'
        'Kiến thức đơn giản · Không hứa lợi nhuận · Không khuyến nghị mua bán</p>',
        unsafe_allow_html=True,
    )

    _FUND_ANALOGIES = {
        "TCEF": (
            "🌳 Trồng cây ăn quả",
            "Cần kiên nhẫn 3–5 năm, nhưng khi cây ra trái thì ngọt lắm. "
            "Giá trị lên xuống theo thị trường — nhưng dài hạn thường đi lên.",
        ),
        "TCBF": (
            "🪣 Bình nước dự phòng",
            "Không sinh lời nhanh, nhưng ổn định và ít biến động. "
            "Phù hợp khi bạn cần dùng tiền trong 1–3 năm tới.",
        ),
        "TCFF": (
            "🎒 Balo cân bằng",
            "Vừa cổ phiếu vừa trái phiếu — không quá cay, không quá nhạt. "
            "Lý tưởng cho ai chưa chắc về khẩu vị rủi ro của mình.",
        ),
    }

    _fc1, _fc2, _fc3 = st.columns(3)
    for _fcol, _fkey in zip([_fc1, _fc2, _fc3], ["TCEF", "TCBF", "TCFF"]):
        _f = FUNDS[_fkey]
        _a_title, _a_desc = _FUND_ANALOGIES[_fkey]
        with _fcol:
            st.markdown(
                f'<div style="background:white;border:2px solid #FFD6E8;border-radius:16px;'
                f'padding:16px;min-height:190px;">'
                f'<div style="font-size:1.5rem;text-align:center;">{_f["emoji"]}</div>'
                f'<div style="font-size:0.83rem;font-weight:800;color:#C4607F;'
                f'text-align:center;margin-top:6px;">{_a_title}</div>'
                f'<div style="font-size:0.77rem;color:#555;margin-top:8px;line-height:1.55;">'
                f'{_a_desc}</div>'
                f'<div style="font-size:0.68rem;color:#CCC;margin-top:10px;">'
                f'{_f["tên"]} · {_f["rủi_ro"]} · {_f["phù_hợp"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Cừu's voice recommender (uses user memory)
    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.95rem;font-weight:700;color:#C4607F;margin-bottom:8px;">'
        '🤔 Hỏi Cừu — Quỹ nào phù hợp với mình?</p>',
        unsafe_allow_html=True,
    )
    _ry1, _ry2 = st.columns(2)
    with _ry1:
        y_opt = st.selectbox(
            "Mục tiêu bao lâu?", [1, 2, 3, 5],
            format_func=lambda x: f"{x} năm", key="rec_y",
        )
    with _ry2:
        r_opt = st.selectbox(
            "Khẩu vị rủi ro?",
            ["low", "medium", "high"],
            format_func=lambda x: {
                "low":    "🌿 Thấp — hay lo lắng",
                "medium": "🌊 Trung bình — cân bằng",
                "high":   "⚡ Cao — chấp nhận biến động",
            }[x],
            key="rec_r",
        )

    rf_key = recommend_fund(y_opt, r_opt)
    rf     = FUNDS[rf_key]
    _rf_a_title, _rf_a_desc = _FUND_ANALOGIES[rf_key]

    _user_name_rec = mem.get("name", "bạn")
    _risk_label    = {"low": "thấp", "medium": "trung bình", "high": "cao"}[r_opt]
    _dream_ctx_rec = ""
    if mem["dreams"]:
        _dream_ctx_rec = (
            f'Mình biết {_user_name_rec} đang mơ đến '
            f'<strong>{mem["dreams"][0]["name"].title()}</strong> — '
        )

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
        f'border-radius:16px;padding:18px 20px;margin-top:8px;">'
        f'<div style="font-size:0.88rem;color:#C4607F;font-style:italic;margin-bottom:8px;">'
        f'🐑 Cừu nói với {_user_name_rec}:</div>'
        f'<div style="font-size:0.93rem;color:#444;line-height:1.7;">'
        f'{_dream_ctx_rec}với mục tiêu <strong>{y_opt} năm</strong> và khẩu vị '
        f'<strong>{_risk_label}</strong>, mình nghĩ <strong>{rf["emoji"]} {_rf_a_title}</strong> '
        f'hợp với {_user_name_rec} nhất.<br/><br/>'
        f'<span style="font-size:0.84rem;color:#777;">{_rf_a_desc}</span><br/><br/>'
        f'<span style="font-size:0.73rem;color:#BBB;">'
        f'⚠️ Đây chỉ là gợi ý tham khảo, không phải tư vấn đầu tư chuyên nghiệp.</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    with st.expander("📚 Kiến thức đầu tư cơ bản"):
        for _pk, _pp in INVESTMENT_PRINCIPLES.items():
            st.markdown(f"**{_pp['tên']}**")
            st.markdown(_pp["nội_dung"])
            st.markdown("---")


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

    # ── TAB 5: Interactive Design Demo ──────────────────────────────────
    with tab5:
        st.markdown("""<div style='text-align:center; padding:16px 0 4px;'>
            <span style='font-size:1.8rem;'>🐑</span>
            <h2 style='color:#C4607F; margin:4px 0 2px; font-size:1.5rem;'>Cừu Cần Cù — Interactive Prototype</h2>
            <p style='color:#999; font-size:0.85rem; margin:0;'>Click vào từng màn hình trong sidebar để khám phá · Dữ liệu minh hoạ</p>
        </div>""", unsafe_allow_html=True)

        _PROTO_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif;}
body{background:#f5f0ff;display:flex;height:780px;overflow:hidden;}

/* ── Sidebar ── */
.sidebar{width:180px;background:linear-gradient(180deg,#fff5f8 0%,#fff 100%);
  border-right:1px solid #f0d6e0;display:flex;flex-direction:column;padding:12px 0;flex-shrink:0;}
.profile{text-align:center;padding:12px 8px 16px;}
.avatar{width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#ffb3c6,#c4607f);
  margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:1.8rem;}
.profile-name{font-size:.78rem;font-weight:700;color:#c4607f;}
.profile-sub{font-size:.65rem;color:#aaa;margin-top:2px;}
.xp-bar{height:5px;background:#f0e0e8;border-radius:3px;margin:6px 12px 0;}
.xp-fill{height:100%;width:65%;background:linear-gradient(90deg,#ff8fab,#c4607f);border-radius:3px;}
.nav-item{display:flex;align-items:center;gap:8px;padding:9px 16px;cursor:pointer;
  font-size:.8rem;color:#666;border-radius:0;transition:all .15s;position:relative;}
.nav-item:hover{background:#fff0f5;color:#c4607f;}
.nav-item.active{background:linear-gradient(90deg,#ffe0eb,#fff5f8);color:#c4607f;font-weight:700;
  border-left:3px solid #c4607f;}
.nav-icon{font-size:1rem;width:20px;text-align:center;}
.badge{background:#ff4d6d;color:#fff;font-size:.6rem;border-radius:10px;
  padding:1px 5px;position:absolute;right:12px;}

/* ── Main ── */
.main{flex:1;overflow-y:auto;background:#f8f0ff;}
.screen{display:none;padding:0;height:100%;}
.screen.active{display:block;}

/* ── Top bar ── */
.topbar{background:linear-gradient(135deg,#c4607f,#a03060);color:#fff;
  padding:10px 16px;display:flex;align-items:center;justify-content:space-between;}
.topbar-title{font-size:1rem;font-weight:700;}
.topbar-coins{display:flex;gap:10px;align-items:center;font-size:.78rem;}
.coin{background:rgba(255,255,255,.2);border-radius:12px;padding:3px 8px;
  display:flex;align-items:center;gap:4px;}

/* ── Farm Screen ── */
.farm-bg{background:linear-gradient(180deg,#87CEEB 0%,#98FB98 60%,#90EE90 100%);
  height:200px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
.farm-sheep{font-size:4rem;animation:bounce 2s infinite;}
@keyframes bounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-8px);}}
.farm-grass{position:absolute;bottom:0;left:0;right:0;height:70px;
  background:linear-gradient(180deg,#7ec850,#5a9e30);border-radius:50% 50% 0 0 / 20px 20px 0 0;}
.farm-label{position:absolute;top:10px;left:50%;transform:translateX(-50%);
  background:rgba(255,255,255,.85);border-radius:20px;padding:3px 12px;
  font-size:.7rem;font-weight:700;color:#c4607f;}

.chat-area{padding:12px;background:#fff;margin:8px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);}
.chat-bubble{background:#fff5f8;border:1px solid #f0d6e0;border-radius:12px 12px 12px 4px;
  padding:8px 12px;font-size:.78rem;color:#444;margin-bottom:8px;max-width:85%;}
.chat-bubble.user{background:linear-gradient(135deg,#c4607f,#a03060);color:#fff;
  border-radius:12px 12px 4px 12px;margin-left:auto;}
.chat-input{display:flex;gap:8px;margin-top:8px;}
.chat-input input{flex:1;border:1px solid #f0d0e0;border-radius:20px;padding:6px 12px;
  font-size:.75rem;outline:none;}
.chat-input button{background:#c4607f;color:#fff;border:none;border-radius:20px;
  padding:6px 14px;cursor:pointer;font-size:.75rem;}

.mood-row{display:flex;gap:8px;padding:8px 8px 0;overflow-x:auto;}
.mood-btn{background:#fff;border:1.5px solid #f0d0e0;border-radius:20px;
  padding:5px 10px;font-size:.7rem;cursor:pointer;white-space:nowrap;transition:all .15s;}
.mood-btn:hover,.mood-btn.active{background:#c4607f;color:#fff;border-color:#c4607f;}

/* ── Stats ── */
.stats-row{display:flex;gap:8px;padding:8px;overflow-x:auto;}
.stat-card{background:#fff;border-radius:12px;padding:10px 14px;min-width:100px;
  box-shadow:0 2px 8px rgba(0,0,0,.06);flex-shrink:0;}
.stat-val{font-size:1.1rem;font-weight:800;color:#c4607f;}
.stat-lbl{font-size:.65rem;color:#aaa;margin-top:2px;}

/* ── Friends Screen ── */
.section-title{padding:12px 12px 6px;font-size:.85rem;font-weight:700;color:#444;}
.friends-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:0 8px 8px;}
.friend-card{background:#fff;border-radius:14px;padding:10px 8px;text-align:center;
  box-shadow:0 2px 8px rgba(0,0,0,.06);cursor:pointer;transition:transform .15s;}
.friend-card:hover{transform:translateY(-2px);}
.friend-sheep{font-size:2rem;margin-bottom:4px;}
.friend-name{font-size:.68rem;font-weight:700;color:#333;}
.friend-level{font-size:.6rem;color:#888;margin:2px 0;}
.friend-badge{font-size:.55rem;border-radius:8px;padding:2px 6px;background:#e8f5e9;color:#388e3c;
  display:inline-block;margin-top:2px;}
.friend-badge.blue{background:#e3f2fd;color:#1565c0;}
.progress-sm{height:4px;background:#f0e0e8;border-radius:2px;margin-top:6px;}
.progress-sm-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,#ff8fab,#c4607f);}
.leaderboard{margin:8px;background:#fff;border-radius:14px;padding:12px;
  box-shadow:0 2px 8px rgba(0,0,0,.06);}
.lb-row{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #f5f5f5;
  font-size:.75rem;}
.lb-row:last-child{border:none;}
.lb-rank{width:20px;font-weight:700;color:#c4607f;}
.lb-name{flex:1;color:#333;}
.lb-amount{color:#888;font-size:.7rem;}

/* ── Missions Screen ── */
.mission-card{background:#fff;border-radius:14px;padding:12px;margin:8px;
  box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;align-items:center;gap:10px;cursor:pointer;}
.mission-card:hover{box-shadow:0 4px 12px rgba(196,96,127,.2);}
.mission-icon{font-size:1.6rem;width:40px;text-align:center;}
.mission-info{flex:1;}
.mission-title{font-size:.8rem;font-weight:700;color:#333;}
.mission-desc{font-size:.68rem;color:#888;margin-top:2px;}
.mission-reward{font-size:.7rem;color:#c4607f;font-weight:700;}
.progress-bar{height:5px;background:#f0e0e8;border-radius:3px;margin-top:6px;}
.progress-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,#ffb3c6,#c4607f);}
.mission-tag{font-size:.6rem;background:#fff0f5;color:#c4607f;border:1px solid #f0c0d0;
  border-radius:8px;padding:2px 6px;float:right;}

/* ── Community Screen ── */
.chat-msg{display:flex;gap:8px;padding:8px 12px;}
.msg-avatar{font-size:1.4rem;flex-shrink:0;}
.msg-body{}
.msg-name{font-size:.68rem;font-weight:700;color:#c4607f;}
.msg-text{font-size:.76rem;color:#333;margin-top:2px;background:#fff;
  border-radius:0 12px 12px 12px;padding:6px 10px;display:inline-block;max-width:260px;}
.msg-time{font-size:.6rem;color:#bbb;margin-top:2px;}
.community-input{display:flex;gap:8px;padding:10px 12px;background:#fff;
  border-top:1px solid #f0e0e8;position:sticky;bottom:0;}
.community-input input{flex:1;border:1px solid #f0d0e0;border-radius:20px;
  padding:7px 14px;font-size:.75rem;outline:none;}
.community-input button{background:#c4607f;color:#fff;border:none;border-radius:20px;
  padding:7px 16px;cursor:pointer;font-size:.75rem;}

/* ── Crowdfund Screen ── */
.dream-card{background:#fff;border-radius:16px;margin:8px;padding:14px;
  box-shadow:0 2px 8px rgba(0,0,0,.08);}
.dream-header{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
.dream-sheep{font-size:1.8rem;}
.dream-meta{flex:1;}
.dream-title{font-size:.85rem;font-weight:700;color:#333;}
.dream-user{font-size:.68rem;color:#888;}
.dream-amount{font-size:1.1rem;font-weight:800;color:#c4607f;}
.dream-target{font-size:.68rem;color:#aaa;}
.dream-bar{height:8px;background:#f0e0e8;border-radius:4px;margin:8px 0;}
.dream-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,#ffb3c6,#c4607f);}
.dream-actions{display:flex;gap:8px;margin-top:10px;}
.btn-cheer{flex:1;background:#fff0f5;color:#c4607f;border:1.5px solid #f0c0d0;
  border-radius:20px;padding:8px;font-size:.75rem;cursor:pointer;text-align:center;}
.btn-invest{flex:1;background:linear-gradient(135deg,#c4607f,#a03060);color:#fff;
  border:none;border-radius:20px;padding:8px;font-size:.75rem;cursor:pointer;text-align:center;}
.btn-invest:hover,.btn-cheer:hover{opacity:.9;transform:translateY(-1px);}

.tag-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;}
.tag{font-size:.6rem;background:#f5f0ff;color:#7c3aed;border-radius:8px;padding:2px 7px;}
</style>
</head>
<body>

<!-- SIDEBAR -->
<div class="sidebar">
  <div class="profile">
    <div class="avatar">🐑</div>
    <div class="profile-name">Bông Cần Cù</div>
    <div class="profile-sub">Cừu Kiến Tri · Cấp 5</div>
    <div class="xp-bar"><div class="xp-fill"></div></div>
    <div style="font-size:.62rem;color:#ccc;margin-top:4px;">65% → Cấp 6</div>
  </div>
  <div class="nav-item active" onclick="show('farm')">
    <span class="nav-icon">🏡</span> Trang trại
  </div>
  <div class="nav-item" onclick="show('missions')">
    <span class="nav-icon">📋</span> Nhiệm vụ
    <span class="badge">3</span>
  </div>
  <div class="nav-item" onclick="show('shop')">
    <span class="nav-icon">🛍️</span> Cửa hàng
  </div>
  <div class="nav-item" onclick="show('decor')">
    <span class="nav-icon">🎨</span> Trang trí
  </div>
  <div class="nav-item" onclick="show('friends')">
    <span class="nav-icon">👯</span> Bạn bè
  </div>
  <div class="nav-item" onclick="show('community')">
    <span class="nav-icon">💬</span> Hội nhóm
  </div>
  <div class="nav-item" onclick="show('diary')">
    <span class="nav-icon">📔</span> Nhật ký
  </div>
  <div class="nav-item" onclick="show('crowdfund')">
    <span class="nav-icon">🚀</span> Ước mơ
  </div>
</div>

<!-- SCREENS -->
<div class="main">

  <!-- FARM -->
  <div class="screen active" id="screen-farm">
    <div class="topbar">
      <span class="topbar-title">🏡 Trang Trại Cừu</span>
      <div class="topbar-coins">
        <div class="coin">🪙 128.450</div>
        <div class="coin">💎 320</div>
      </div>
    </div>
    <div class="farm-bg">
      <div class="farm-label">☀️ Hôm nay: Thứ Bảy</div>
      <div class="farm-sheep">🐑</div>
      <div class="farm-grass"></div>
    </div>
    <div class="mood-row">
      <div class="mood-btn active" onclick="selectMood(this,'😊 Vui')">😊 Vui vẻ</div>
      <div class="mood-btn" onclick="selectMood(this,'😟 Lo')">😟 Lo lắng</div>
      <div class="mood-btn" onclick="selectMood(this,'💪 Quyết tâm')">💪 Quyết tâm</div>
      <div class="mood-btn" onclick="selectMood(this,'😮 Bất ngờ')">😮 Bất ngờ</div>
      <div class="mood-btn" onclick="selectMood(this,'🤔 Phân vân')">🤔 Phân vân</div>
    </div>
    <div class="stats-row">
      <div class="stat-card"><div class="stat-val">2.450.000đ</div><div class="stat-lbl">💰 Đã tích lũy</div></div>
      <div class="stat-card"><div class="stat-val">7 ngày</div><div class="stat-lbl">🔥 Streak</div></div>
      <div class="stat-card"><div class="stat-val">Cấp 5</div><div class="stat-lbl">📈 Cừu Kiến Tri</div></div>
      <div class="stat-card"><div class="stat-val">85%</div><div class="stat-lbl">🎯 Mục tiêu</div></div>
    </div>
    <div class="chat-area">
      <div class="chat-bubble">🐑 Hôm nay tụi mình mua cà phê hết 45.000đ nha! Nếu tiết kiệm mỗi ngày thì 1 tháng dành được 1.350.000đ đó 💕</div>
      <div class="chat-bubble user">Ừ nhỉ, cừu ơi hôm nay mình lương rồi nên muốn để dành thêm</div>
      <div class="chat-bubble">🐑 Yayyy! Bông rất vui! Mình đề xuất để 30% = 3.000.000đ vào quỹ tiết kiệm nhé? Mình giữ hộ bạn 🌱</div>
      <div class="chat-input">
        <input type="text" placeholder="Kể cho cừu nghe..." id="chatInput"/>
        <button onclick="sendChat()">Gửi 💬</button>
      </div>
    </div>
  </div>

  <!-- MISSIONS -->
  <div class="screen" id="screen-missions">
    <div class="topbar">
      <span class="topbar-title">📋 Nhiệm Vụ Hôm Nay</span>
      <div class="topbar-coins"><div class="coin">⚡ 3 nhiệm vụ</div></div>
    </div>
    <div class="section-title">🌟 Nhiệm vụ ngày (reset lúc 00:00)</div>
    <div class="mission-card" onclick="completeTask(this)">
      <div class="mission-icon">☕</div>
      <div class="mission-info">
        <div class="mission-title">Ghi 1 khoản chi hôm nay <span class="mission-tag">Dễ</span></div>
        <div class="mission-desc">Ghi lại bất kỳ chi tiêu nào trong ngày</div>
        <div class="progress-bar"><div class="progress-fill" style="width:0%"></div></div>
        <div class="mission-reward">+50 🪙 · +10 XP</div>
      </div>
    </div>
    <div class="mission-card" onclick="completeTask(this)">
      <div class="mission-icon">💬</div>
      <div class="mission-info">
        <div class="mission-title">Chat với cừu 3 lần <span class="mission-tag">Thường</span></div>
        <div class="mission-desc">Chia sẻ cảm xúc tài chính với Bông</div>
        <div class="progress-bar"><div class="progress-fill" style="width:66%"></div></div>
        <div class="mission-reward">+80 🪙 · +15 XP</div>
      </div>
    </div>
    <div class="mission-card" onclick="completeTask(this)">
      <div class="mission-icon">👯</div>
      <div class="mission-info">
        <div class="mission-title">Cheer 1 người bạn <span class="mission-tag">Xã hội</span></div>
        <div class="mission-desc">Vào màn hình Bạn Bè và gửi cỏ cho ai đó</div>
        <div class="progress-bar"><div class="progress-fill" style="width:0%"></div></div>
        <div class="mission-reward">+60 🪙 · +20 XP</div>
      </div>
    </div>
    <div class="section-title">🏆 Nhiệm vụ tuần</div>
    <div class="mission-card">
      <div class="mission-icon">📈</div>
      <div class="mission-info">
        <div class="mission-title">Tích lũy 500.000đ trong tuần <span class="mission-tag">Khó</span></div>
        <div class="mission-desc">Streak tiết kiệm 7 ngày liên tiếp</div>
        <div class="progress-bar"><div class="progress-fill" style="width:78%"></div></div>
        <div class="mission-reward">+500 🪙 · Mũ nhà nông 🎩</div>
      </div>
    </div>
  </div>

  <!-- SHOP -->
  <div class="screen" id="screen-shop">
    <div class="topbar">
      <span class="topbar-title">🛍️ Cửa Hàng Cừu</span>
      <div class="topbar-coins"><div class="coin">🪙 128.450</div></div>
    </div>
    <div class="section-title">🎁 Phụ kiện cho Bông</div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:0 8px 8px;">
      <div style="background:#fff;border-radius:14px;padding:12px;text-align:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06);" onclick="buyItem(this,'🎩 Mũ nhà nông','2000')">
        <div style="font-size:2.2rem;margin-bottom:6px;">🎩</div>
        <div style="font-size:.75rem;font-weight:700;color:#333;">Mũ nhà nông</div>
        <div style="font-size:.68rem;color:#c4607f;margin-top:4px;">🪙 2.000</div>
      </div>
      <div style="background:#fff;border-radius:14px;padding:12px;text-align:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06);" onclick="buyItem(this,'🏠 Nhà mái lá','5000')">
        <div style="font-size:2.2rem;margin-bottom:6px;">🏠</div>
        <div style="font-size:.75rem;font-weight:700;color:#333;">Nhà mái lá</div>
        <div style="font-size:.68rem;color:#c4607f;margin-top:4px;">🪙 5.000</div>
      </div>
      <div style="background:#fff;border-radius:14px;padding:12px;text-align:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06);" onclick="buyItem(this,'🌳 Cây hiếm','8000')">
        <div style="font-size:2.2rem;margin-bottom:6px;">🌳</div>
        <div style="font-size:.75rem;font-weight:700;color:#333;">Cây hiếm</div>
        <div style="font-size:.68rem;color:#c4607f;margin-top:4px;">🪙 8.000</div>
      </div>
      <div style="background:#fff;border-radius:14px;padding:12px;text-align:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06);" onclick="buyItem(this,'🌸 Hoa anh đào','3500')">
        <div style="font-size:2.2rem;margin-bottom:6px;">🌸</div>
        <div style="font-size:.75rem;font-weight:700;color:#333;">Hoa anh đào</div>
        <div style="font-size:.68rem;color:#c4607f;margin-top:4px;">🪙 3.500</div>
      </div>
      <div style="background:#fff;border-radius:14px;padding:12px;text-align:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06);" onclick="buyItem(this,'🎀 Nơ hồng','1500')">
        <div style="font-size:2.2rem;margin-bottom:6px;">🎀</div>
        <div style="font-size:.75rem;font-weight:700;color:#333;">Nơ hồng</div>
        <div style="font-size:.68rem;color:#c4607f;margin-top:4px;">🪙 1.500</div>
      </div>
      <div style="background:#fff;border-radius:14px;padding:12px;text-align:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06);" onclick="buyItem(this,'☁️ Đám mây','6000')">
        <div style="font-size:2.2rem;margin-bottom:6px;">☁️</div>
        <div style="font-size:.75rem;font-weight:700;color:#333;">Đám mây</div>
        <div style="font-size:.68rem;color:#c4607f;margin-top:4px;">🪙 6.000</div>
      </div>
    </div>
  </div>

  <!-- DECOR -->
  <div class="screen" id="screen-decor">
    <div class="topbar">
      <span class="topbar-title">🎨 Trang Trí Trang Trại</span>
    </div>
    <div style="background:linear-gradient(180deg,#87CEEB,#98FB98);height:220px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;">
      <div style="font-size:4rem;" id="decorSheep">🐑</div>
      <div id="decorItems" style="position:absolute;top:10px;right:20px;font-size:1.6rem;display:flex;flex-direction:column;gap:4px;"></div>
      <div style="position:absolute;bottom:0;left:0;right:0;height:60px;background:linear-gradient(180deg,#7ec850,#5a9e30);border-radius:50% 50% 0 0/20px 20px 0 0;"></div>
    </div>
    <div class="section-title">🎒 Đồ đang mặc — click để gỡ</div>
    <div id="equippedList" style="padding:0 8px;display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
      <div style="background:#fff0f5;border:1.5px dashed #c4607f;border-radius:10px;padding:8px 14px;font-size:.75rem;color:#c4607f;">Chưa trang trí gì 🌿</div>
    </div>
    <div class="section-title">🎁 Kho đồ của bạn — click để mặc</div>
    <div style="display:flex;gap:8px;padding:0 8px;flex-wrap:wrap;">
      <div style="background:#fff;border-radius:12px;padding:8px 14px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.06);font-size:.78rem;" onclick="equipItem('🎩')">🎩 Mũ nhà nông</div>
      <div style="background:#fff;border-radius:12px;padding:8px 14px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.06);font-size:.78rem;" onclick="equipItem('🎀')">🎀 Nơ hồng</div>
      <div style="background:#fff;border-radius:12px;padding:8px 14px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.06);font-size:.78rem;" onclick="equipItem('🌸')">🌸 Hoa anh đào</div>
    </div>
  </div>

  <!-- FRIENDS -->
  <div class="screen" id="screen-friends">
    <div class="topbar">
      <span class="topbar-title">👯 Bạn Bè Đồng Hành</span>
      <div class="topbar-coins"><div class="coin">+8 bạn mới</div></div>
    </div>
    <div class="section-title">🐑 Bạn bè của tôi (6)</div>
    <div class="friends-grid">
      <div class="friend-card" onclick="cheerFriend(this,'Bông Mập')">
        <div class="friend-sheep">🐑</div>
        <div class="friend-name">Bông Mập</div>
        <div class="friend-level">Cấp 8</div>
        <div class="friend-badge">Cừu Non</div>
        <div class="progress-sm"><div class="progress-sm-fill" style="width:80%"></div></div>
      </div>
      <div class="friend-card" onclick="cheerFriend(this,'Cừu Nhanh Nhẹn')">
        <div class="friend-sheep">🐑</div>
        <div class="friend-name">Cừu Nhanh Nhẹn</div>
        <div class="friend-level">Cấp 12</div>
        <div class="friend-badge" style="background:#fff3e0;color:#e65100;">Cừu Thiếu Niên</div>
        <div class="progress-sm"><div class="progress-sm-fill" style="width:60%"></div></div>
      </div>
      <div class="friend-card" onclick="cheerFriend(this,'Máy Tích Lũy')">
        <div class="friend-sheep">🐑</div>
        <div class="friend-name">Máy Tích Lũy</div>
        <div class="friend-level">Cấp 7</div>
        <div class="friend-badge blue">Cừu Trưởng Thành</div>
        <div class="progress-sm"><div class="progress-sm-fill" style="width:75%"></div></div>
      </div>
      <div class="friend-card" onclick="cheerFriend(this,'Lúa Vàng')">
        <div class="friend-sheep">🐑</div>
        <div class="friend-name">Lúa Vàng</div>
        <div class="friend-level">Cấp 20</div>
        <div class="friend-badge" style="background:#f3e5f5;color:#6a1b9a;">Cừu Lão Luyện</div>
        <div class="progress-sm"><div class="progress-sm-fill" style="width:90%"></div></div>
      </div>
      <div class="friend-card" onclick="cheerFriend(this,'Bé Bông')">
        <div class="friend-sheep">🐑</div>
        <div class="friend-name">Bé Bông</div>
        <div class="friend-level">Cấp 4</div>
        <div class="friend-badge">Cừu Non</div>
        <div class="progress-sm"><div class="progress-sm-fill" style="width:45%"></div></div>
      </div>
      <div class="friend-card" onclick="cheerFriend(this,'Cừu Thịnh Vượng')">
        <div class="friend-sheep">🐑</div>
        <div class="friend-name">Cừu Thịnh Vượng</div>
        <div class="friend-level">Cấp 18</div>
        <div class="friend-badge blue">Cừu Trưởng Thành</div>
        <div class="progress-sm"><div class="progress-sm-fill" style="width:70%"></div></div>
      </div>
    </div>
    <div class="leaderboard">
      <div style="font-size:.82rem;font-weight:700;color:#333;margin-bottom:8px;">🏆 Top tiết kiệm tuần này</div>
      <div class="lb-row"><div class="lb-rank">🥇</div><div class="lb-name">Cừu Nhanh Nhẹn</div><div class="lb-amount">2.450.000đ</div></div>
      <div class="lb-row"><div class="lb-rank">🥈</div><div class="lb-name">Lúa Vàng</div><div class="lb-amount">2.150.000đ</div></div>
      <div class="lb-row"><div class="lb-rank">🥉</div><div class="lb-name">Máy Tích Lũy</div><div class="lb-amount">1.980.000đ</div></div>
      <div class="lb-row"><div class="lb-rank" style="color:#888">4</div><div class="lb-name">Cừu Thịnh Vượng</div><div class="lb-amount">1.750.000đ</div></div>
      <div class="lb-row"><div class="lb-rank" style="color:#888">5</div><div class="lb-name">Bông Mập</div><div class="lb-amount">1.320.000đ</div></div>
    </div>
  </div>

  <!-- COMMUNITY -->
  <div class="screen" id="screen-community">
    <div class="topbar">
      <span class="topbar-title">💬 Hội Nhóm Tiết Kiệm</span>
      <div class="topbar-coins"><div class="coin">👥 1.247</div></div>
    </div>
    <div class="section-title">🔥 Nhóm đang hot</div>
    <div style="display:flex;gap:8px;padding:0 8px 8px;overflow-x:auto;">
      <div style="background:linear-gradient(135deg,#ff8fab,#c4607f);color:#fff;border-radius:12px;padding:8px 14px;white-space:nowrap;cursor:pointer;font-size:.75rem;font-weight:700;" onclick="joinGroup(this,'🐑 Hội Tiết Kiệm 1tr/tháng')">🐑 Tiết kiệm 1tr/tháng<br><span style="font-weight:400;opacity:.8">892 thành viên</span></div>
      <div style="background:#fff;border-radius:12px;padding:8px 14px;white-space:nowrap;cursor:pointer;font-size:.75rem;font-weight:700;color:#333;box-shadow:0 2px 6px rgba(0,0,0,.08);" onclick="joinGroup(this,'💼 Nhóm Đầu Tư ETF')">💼 Đầu tư ETF<br><span style="color:#888;font-weight:400">234 thành viên</span></div>
      <div style="background:#fff;border-radius:12px;padding:8px 14px;white-space:nowrap;cursor:pointer;font-size:.75rem;font-weight:700;color:#333;box-shadow:0 2px 6px rgba(0,0,0,.08);" onclick="joinGroup(this,'🏠 Nhóm Mua Nhà 2026')">🏠 Mua nhà 2026<br><span style="color:#888;font-weight:400">567 thành viên</span></div>
    </div>
    <div id="chatMessages" style="padding:4px 0;max-height:350px;overflow-y:auto;">
      <div class="chat-msg">
        <div class="msg-avatar">🐑</div>
        <div class="msg-body">
          <div class="msg-name">Lúa Vàng</div>
          <div class="msg-text">Tháng này mình đã để dành được 3.2tr rồi 🎉 ai đang theo dõi mục tiêu cùng không?</div>
          <div class="msg-time">10:32</div>
        </div>
      </div>
      <div class="chat-msg">
        <div class="msg-avatar">🐑</div>
        <div class="msg-body">
          <div class="msg-name">Máy Tích Lũy</div>
          <div class="msg-text">Mình cũng vừa tới 2tr! Cùng cố lên nhé mọi người 💪</div>
          <div class="msg-time">10:35</div>
        </div>
      </div>
      <div class="chat-msg">
        <div class="msg-avatar">🐑</div>
        <div class="msg-body">
          <div class="msg-name">Cừu Nhanh Nhẹn</div>
          <div class="msg-text">Tip của mình: sáng dậy ghi ngay kế hoạch chi tiêu trước khi xài tiền 📝</div>
          <div class="msg-time">10:41</div>
        </div>
      </div>
    </div>
    <div class="community-input">
      <input type="text" placeholder="Nhắn gì đó cho hội nhóm..." id="groupInput"/>
      <button onclick="sendGroupMsg()">Gửi</button>
    </div>
  </div>

  <!-- DIARY -->
  <div class="screen" id="screen-diary">
    <div class="topbar">
      <span class="topbar-title">📔 Nhật Ký Tâm Sự</span>
    </div>
    <div style="padding:12px;">
      <div style="background:#fff;border-radius:14px;padding:14px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);">
        <div style="font-size:.7rem;color:#c4607f;font-weight:700;margin-bottom:6px;">📅 21/06/2026 · Thứ Bảy</div>
        <div style="font-size:.78rem;color:#444;line-height:1.6;">Hôm nay lương về rồi! Quyết định để 3 triệu vào quỹ tiết kiệm ngay. Cừu Bông rất vui và nói "Bạn đang xây tương lai đó!" 🌱</div>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
          <span style="background:#fff0f5;color:#c4607f;border-radius:8px;padding:2px 7px;font-size:.62rem;">😊 Vui vẻ</span>
          <span style="background:#e8f5e9;color:#388e3c;border-radius:8px;padding:2px 7px;font-size:.62rem;">💰 Tiết kiệm</span>
        </div>
      </div>
      <div style="background:#fff;border-radius:14px;padding:14px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);">
        <div style="font-size:.7rem;color:#c4607f;font-weight:700;margin-bottom:6px;">📅 20/06/2026 · Thứ Sáu</div>
        <div style="font-size:.78rem;color:#444;line-height:1.6;">Đi ăn với bạn hết 250k nhưng mình đã plan trước nên không cảm thấy tội 😄 Cừu bảo "Trải nghiệm cũng là đầu tư vào bản thân!"</div>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
          <span style="background:#fff0f5;color:#c4607f;border-radius:8px;padding:2px 7px;font-size:.62rem;">😊 Thoải mái</span>
          <span style="background:#fff3e0;color:#e65100;border-radius:8px;padding:2px 7px;font-size:.62rem;">🍽️ Ăn uống</span>
        </div>
      </div>
      <div style="background:linear-gradient(135deg,#fff0f5,#fce4ec);border:1.5px dashed #f0c0d0;border-radius:14px;padding:14px;text-align:center;cursor:pointer;" onclick="addDiary()">
        <div style="font-size:1.5rem;margin-bottom:4px;">✏️</div>
        <div style="font-size:.78rem;color:#c4607f;font-weight:700;">Thêm nhật ký hôm nay</div>
      </div>
    </div>
  </div>

  <!-- CROWDFUND -->
  <div class="screen" id="screen-crowdfund">
    <div class="topbar">
      <span class="topbar-title">🚀 Ước Mơ Cộng Đồng</span>
      <div class="topbar-coins"><div class="coin">+ Đăng ước mơ</div></div>
    </div>
    <div class="dream-card">
      <div class="dream-header">
        <div class="dream-sheep">🐑</div>
        <div class="dream-meta">
          <div class="dream-title">Mua xe máy đi làm không cần Grab 🛵</div>
          <div class="dream-user">bởi Cừu Nhanh Nhẹn · 23 người ủng hộ</div>
        </div>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:baseline;">
        <div><div class="dream-amount">18.500.000đ</div><div class="dream-target">/ 25.000.000đ mục tiêu</div></div>
        <div style="font-size:.75rem;color:#c4607f;font-weight:700;">74%</div>
      </div>
      <div class="dream-bar"><div class="dream-fill" style="width:74%"></div></div>
      <div class="tag-row">
        <div class="tag">🛵 Phương tiện</div>
        <div class="tag">💼 Đi làm</div>
        <div class="tag">⏰ 12 ngày còn lại</div>
      </div>
      <div class="dream-actions">
        <div class="btn-cheer" onclick="cheerDream(this)">🌿 Gửi cỏ ủng hộ</div>
        <div class="btn-invest" onclick="investDream(this)">💰 Góp vốn</div>
      </div>
    </div>
    <div class="dream-card">
      <div class="dream-header">
        <div class="dream-sheep">🐑</div>
        <div class="dream-meta">
          <div class="dream-title">Học khoá CFA cho sự nghiệp tài chính 📚</div>
          <div class="dream-user">bởi Lúa Vàng · 41 người ủng hộ</div>
        </div>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:baseline;">
        <div><div class="dream-amount">6.250.000đ</div><div class="dream-target">/ 15.000.000đ mục tiêu</div></div>
        <div style="font-size:.75rem;color:#c4607f;font-weight:700;">42%</div>
      </div>
      <div class="dream-bar"><div class="dream-fill" style="width:42%"></div></div>
      <div class="tag-row">
        <div class="tag">📚 Học tập</div>
        <div class="tag">💼 Tài chính</div>
        <div class="tag">⏰ 28 ngày còn lại</div>
      </div>
      <div class="dream-actions">
        <div class="btn-cheer" onclick="cheerDream(this)">🌿 Gửi cỏ ủng hộ</div>
        <div class="btn-invest" onclick="investDream(this)">💰 Góp vốn</div>
      </div>
    </div>
  </div>

</div><!-- end main -->

<!-- TOAST -->
<div id="toast" style="display:none;position:fixed;bottom:20px;left:50%;transform:translateX(-50%);
  background:rgba(50,50,50,.9);color:#fff;border-radius:20px;padding:8px 20px;
  font-size:.78rem;z-index:999;transition:opacity .3s;"></div>

<script>
function show(screen) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('screen-' + screen).classList.add('active');
  event.currentTarget.classList.add('active');
}

function toast(msg) {
  var t = document.getElementById('toast');
  t.textContent = msg; t.style.display = 'block'; t.style.opacity = '1';
  setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.style.display='none', 300); }, 2000);
}

function selectMood(el, mood) {
  document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  toast('Cừu Bông ghi nhận: ' + mood + ' 💕');
}

function sendChat() {
  var inp = document.getElementById('chatInput');
  if(!inp.value.trim()) return;
  var area = inp.closest('.chat-area');
  var userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user';
  userBubble.textContent = inp.value;
  area.insertBefore(userBubble, inp.closest('.chat-input'));
  var sheepBubble = document.createElement('div');
  sheepBubble.className = 'chat-bubble';
  sheepBubble.textContent = '🐑 Mình nghe bạn nói rồi! Cảm ơn bạn đã chia sẻ nhé 💕 Bạn đang làm rất tốt!';
  area.insertBefore(sheepBubble, inp.closest('.chat-input'));
  inp.value = '';
}

function completeTask(card) {
  var fill = card.querySelector('.progress-fill');
  var current = parseInt(fill.style.width) || 0;
  if(current >= 100) { toast('✅ Nhiệm vụ đã hoàn thành!'); return; }
  fill.style.width = Math.min(100, current + 50) + '%';
  if(current + 50 >= 100) {
    card.style.opacity = '.6';
    toast('🎉 Hoàn thành nhiệm vụ! +80 🪙');
  } else {
    toast('📈 Tiến độ cập nhật!');
  }
}

function buyItem(card, name, price) {
  card.style.background = 'linear-gradient(135deg,#fff0f5,#fce4ec)';
  card.style.border = '2px solid #c4607f';
  toast('🛍️ Đã mua: ' + name + ' (-' + price + ' 🪙)');
}

function equipItem(emoji) {
  var list = document.getElementById('equippedList');
  if(list.textContent.includes('Chưa trang trí')) list.innerHTML = '';
  var item = document.createElement('div');
  item.style.cssText = 'background:#fff0f5;border:1.5px solid #c4607f;border-radius:10px;padding:6px 12px;font-size:.75rem;color:#c4607f;cursor:pointer;';
  item.textContent = emoji + ' Đang mặc';
  item.onclick = function() { this.remove(); toast('Đã gỡ ' + emoji); };
  list.appendChild(item);
  document.getElementById('decorItems').innerHTML += '<div>' + emoji + '</div>';
  toast(emoji + ' Đã trang trí cho Bông!');
}

function cheerFriend(card, name) {
  card.style.boxShadow = '0 0 0 2px #c4607f';
  toast('🌿 Đã gửi cỏ cho ' + name + '!');
}

function joinGroup(el, name) {
  el.style.background = 'linear-gradient(135deg,#c4607f,#a03060)';
  el.style.color = '#fff';
  toast('✅ Đã tham gia: ' + name);
}

function sendGroupMsg() {
  var inp = document.getElementById('groupInput');
  if(!inp.value.trim()) return;
  var msgs = document.getElementById('chatMessages');
  var msg = document.createElement('div');
  msg.className = 'chat-msg';
  msg.innerHTML = '<div class="msg-avatar">🐑</div><div class="msg-body"><div class="msg-name" style="color:#a03060;">Bạn</div><div class="msg-text">' + inp.value + '</div><div class="msg-time">Vừa xong</div></div>';
  msgs.appendChild(msg);
  msgs.scrollTop = msgs.scrollHeight;
  inp.value = '';
  toast('💬 Đã gửi!');
}

function cheerDream(btn) {
  btn.textContent = '✅ Đã gửi cỏ!';
  btn.style.background = '#e8f5e9'; btn.style.color = '#388e3c'; btn.style.borderColor = '#388e3c';
  toast('🌿 Gửi cỏ ủng hộ thành công!');
}

function investDream(btn) {
  toast('💰 Tính năng Góp Vốn đang trong Phase 3 🚀');
}

function addDiary() {
  toast('✏️ Tính năng nhật ký đang mở trong tab Nhật ký!');
}
</script>
</body>
</html>
"""
        import streamlit.components.v1 as components
        components.html(_PROTO_HTML, height=800, scrolling=False)

