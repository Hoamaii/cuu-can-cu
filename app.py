
# ═══════════════════════════════════════════════════════════════════
# app-16.py — CỪU CẦN CÙ: AI Companion Layer
# Strategy: AI Companion + AI Community (NOT investment app)
# Focus: DAU · Diary Written · Community Participation · Streak
# ═══════════════════════════════════════════════════════════════════
import streamlit as st
import json, os, datetime, re

st.set_page_config(page_title="Cừu Cần Cù", page_icon="🐑", layout="centered")

try:
    import anthropic as _anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

# ── Storage ──────────────────────────────────────────────────────────
DATA_FILE = "sheep_user.json"

MEMORY_DEFAULT = {
    # Identity
    "name": "",
    "age_group": "",
    "life_stage": "",

    # Memory Engine — AI Companion core
    "memory_tags":     {},   # {tag_key: count}
    "memory_timeline": [],   # [{date, tag, context, source}]
    "memory_insights": [],   # [{date, insight_text}]
    "latest_insight":  "",

    # Mood
    "mood_history":   [],
    "current_mood":   "neutral",

    # Life events (free-form signals)
    "life_events": {},

    # Diary
    "diary_entries": [],     # [{date, text, mood, ai_insight}]

    # Chat
    "messages": [],
    "api_key":  "",

    # Sheep / Tamagotchi
    "hunger":         70,
    "energy":         80,
    "happiness":      75,
    "exp":            0,
    "level":          1,
    "streak":         0,
    "last_feed_date": "",
    "last_active":    "",
    "wardrobe":       [],
    "sheep_name":     "Cừu",
    "journey_timeline": [],

    # Community
    "community_group":      "",
    "community_points":     0,
    "community_badges":     [],
    "community_challenges": {},

    # Gamification
    "ilucky_tickets": 0,
    "achievements":   [],
    "quests":         {},
    "total_chats":    0,
    "total_diary":    0,
    "session_count":  0,

    # Soft recommendation state
    "rec_shown": {},
}

# ════════════════════════════════════════════════════════════════════
# MEMORY ENGINE
# ════════════════════════════════════════════════════════════════════
MEMORY_TAG_LABELS = {
    "career_stress":       "Bạn từng chia sẻ áp lực công việc",
    "cashflow_concern":    "Bạn đang chú ý đến dòng tiền",
    "saving_mindset":      "Bạn đang cố gắng tiết kiệm hơn",
    "family_concern":      "Bạn quan tâm đến gia đình",
    "evening_person":      "Bạn thường trò chuyện vào buổi tối",
    "spending_control":    "Bạn đang chủ động kiểm soát chi tiêu",
    "long_term_saving":    "Bạn duy trì thói quen tích lũy đều đặn",
    "work_life_balance":   "Bạn đang tìm kiếm cân bằng trong cuộc sống",
    "relationship_stress": "Bạn đang đối mặt với một chút áp lực cảm xúc",
    "health_concern":      "Bạn quan tâm đến sức khỏe bản thân",
    "self_improvement":    "Bạn đang nỗ lực cải thiện bản thân mỗi ngày",
    "optimistic":          "Bạn có năng lượng tích cực rất đẹp",
    "financial_anxiety":   "Bạn đôi khi lo lắng về tài chính",
    "gratitude":           "Bạn hay biết ơn những điều nhỏ bé",
}

MEMORY_KEYWORDS = {
    "career_stress":    ["áp lực công việc","áp lực","mệt mỏi","sếp","deadline",
                         "overtime","burnout","căng thẳng","quá tải","công việc mệt"],
    "cashflow_concern": ["chi tiêu nhiều","tốn tiền","hết tiền","thiếu tiền","lương",
                         "chi phí","tốn kém","tiêu nhiều","tiêu hết"],
    "saving_mindset":   ["tiết kiệm","dành dụm","để dành","tích lũy","tiết giảm",
                         "cắt giảm","không tiêu","ít chi"],
    "family_concern":   ["gia đình","ba mẹ","bố mẹ","vợ","chồng","con",
                         "anh","chị","em","người thân"],
    "spending_control": ["kiểm soát chi tiêu","ngân sách","budget","cắt giảm",
                         "chi tiêu hợp lý","quản lý tiền","theo dõi chi tiêu"],
    "long_term_saving": ["thói quen","đều đặn","mỗi ngày","liên tiếp",
                         "kiên trì","duy trì","tháng này"],
    "self_improvement": ["học","phát triển bản thân","cải thiện","nâng cao",
                         "kỹ năng","khóa học","đọc sách"],
    "health_concern":   ["sức khỏe","tập gym","ăn uống","ngủ không đủ",
                         "thể thao","bệnh","mệt về sức khỏe"],
    "gratitude":        ["biết ơn","hạnh phúc","vui vẻ","may mắn","trân trọng",
                         "cảm ơn","tuyệt vời","thật tốt"],
    "optimistic":       ["tích cực","năng lượng","hy vọng","cố gắng",
                         "lạc quan","phấn chấn","vui lên","tin tưởng"],
    "work_life_balance":["cân bằng","thư giãn","nghỉ ngơi","me time",
                         "cuối tuần","du lịch","xả stress"],
    "relationship_stress":["tình cảm","người yêu","cô đơn","buồn",
                           "nhớ ai","bạn bè xa","mối quan hệ khó"],
    "financial_anxiety":["lo lắng tiền","lo tiền","khó khăn tài chính",
                         "nợ","áp lực tài chính","sợ hết tiền"],
}

def _extract_memory_tags(text: str, mem: dict):
    """Extract memory tags from text, update mem in-place."""
    text_l = text.lower()
    today  = datetime.date.today().isoformat()
    hour   = datetime.datetime.now().hour

    if 20 <= hour or hour < 6:
        t = mem.setdefault("memory_tags", {})
        t["evening_person"] = t.get("evening_person", 0) + 1

    for tag, keywords in MEMORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_l:
                t = mem.setdefault("memory_tags", {})
                t[tag] = t.get(tag, 0) + 1
                mem.setdefault("memory_timeline", []).append({
                    "date": today, "tag": tag,
                    "context": text[:80], "source": "chat",
                })
                break  # one match per tag per call

def _get_memory_chips(mem: dict, max_chips: int = 5) -> list:
    """Return top memory label strings to display."""
    tags = mem.get("memory_tags", {})
    if not tags:
        return []
    sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    return [MEMORY_TAG_LABELS[tag] for tag, _ in sorted_tags[:max_chips]
            if tag in MEMORY_TAG_LABELS]

# Soft Recommendation Engine — only hints, never sells
SOFT_RECS = [
    {
        "key":     "saving_micro",
        "trigger": lambda t: t.get("cashflow_concern", 0) + t.get("saving_mindset", 0) >= 3,
        "text":    "Có vẻ bạn đang quan tâm tới việc tích luỹ 🌱 TCBS có một số giải pháp giúp tự động tích luỹ từ những khoản nhỏ mỗi ngày.",
    },
    {
        "key":     "spare_change",
        "trigger": lambda t: t.get("spending_control", 0) >= 2,
        "text":    "💡 Nhiều người có thói quen dùng tiền lẻ để xây dựng quỹ dự phòng nhỏ — đơn giản mà hiệu quả lắm đấy.",
    },
    {
        "key":     "keep_going",
        "trigger": lambda t: t.get("long_term_saving", 0) >= 3,
        "text":    "🌟 Bạn đang duy trì thói quen rất tốt. Kiên trì chính là chìa khóa quan trọng nhất!",
    },
    {
        "key":     "anxiety_comfort",
        "trigger": lambda t: t.get("financial_anxiety", 0) >= 1,
        "text":    "🐑 Lo lắng về tài chính là rất bình thường. Đôi khi chỉ cần bắt đầu với một khoản rất nhỏ mỗi ngày là đủ.",
    },
]

def _get_soft_rec(mem: dict):
    """Return a soft recommendation string if triggered, else None."""
    tags      = mem.get("memory_tags", {})
    today     = datetime.date.today().isoformat()
    rec_shown = mem.setdefault("rec_shown", {})
    for rec in SOFT_RECS:
        if rec["trigger"](tags) and rec_shown.get(rec["key"]) != today:
            rec_shown[rec["key"]] = today
            return rec["text"]
    return None

# ════════════════════════════════════════════════════════════════════
# COMMUNITY ENGINE
# ════════════════════════════════════════════════════════════════════
COMMUNITY_GROUPS = {
    "sinh_vien": {
        "name":          "🎓 Sinh Viên",
        "desc":          "Tiết kiệm từ học bổng, học phí, tiền ăn",
        "color":         "#2563eb", "bg": "#eff6ff",
        "members":       1247,
        "challenge":     "Tiết kiệm 200k từ ăn sáng tuần này 🌅",
        "active_topic":  "Làm thêm có nên không?",
        "match_tags":    ["self_improvement", "financial_anxiety"],
        "match_events":  ["student"],
    },
    "nguoi_moi_di_lam": {
        "name":          "💼 Người Mới Đi Làm",
        "desc":          "Lương đầu tiên, thói quen tài chính đầu đời",
        "color":         "#7c3aed", "bg": "#f5f3ff",
        "members":       2183,
        "challenge":     "Để dành 10% lương tháng này 💰",
        "active_topic":  "Lương 8tr có tiết kiệm được không?",
        "match_tags":    ["career_stress", "cashflow_concern"],
        "match_events":  ["new_job", "career_change"],
    },
    "gia_dinh_tre": {
        "name":          "👨‍👩‍👧 Gia Đình Trẻ",
        "desc":          "Nuôi con, mua nhà, tích lũy dài hạn",
        "color":         "#059669", "bg": "#ecfdf5",
        "members":       985,
        "challenge":     "Xây quỹ khẩn cấp 1 tháng lương 🏠",
        "active_topic":  "Chi phí nuôi con năm đầu bao nhiêu?",
        "match_tags":    ["family_concern", "long_term_saving"],
        "match_events":  ["expecting_baby", "married", "kids"],
    },
    "tiet_kiem_20s": {
        "name":          "✨ Tiết Kiệm Tuổi 20",
        "desc":          "Xây dựng thói quen tài chính từ sớm",
        "color":         "#d97706", "bg": "#fffbeb",
        "members":       3421,
        "challenge":     "Không mua đồ không cần thiết 7 ngày 🎯",
        "active_topic":  "Coffee mỗi ngày vs tự pha ở nhà?",
        "match_tags":    ["saving_mindset", "optimistic"],
        "match_events":  [],
    },
    "dong_nghiep": {
        "name":          "🤝 Đồng Nghiệp Tiết Kiệm",
        "desc":          "Thách thức tiết kiệm cùng đồng nghiệp",
        "color":         "#dc2626", "bg": "#fef2f2",
        "members":       672,
        "challenge":     "Cơm nhà 5/7 ngày tuần này 🍱",
        "active_topic":  "Ăn trưa văn phòng tốn bao nhiêu/tháng?",
        "match_tags":    ["spending_control", "work_life_balance"],
        "match_events":  ["workplace"],
    },
}

def _match_community_group(mem: dict) -> str:
    """Score and return best matching community group key."""
    tags        = mem.get("memory_tags", {})
    life_events = mem.get("life_events", {})
    scores      = {k: 0 for k in COMMUNITY_GROUPS}

    for gkey, gdata in COMMUNITY_GROUPS.items():
        for ev in gdata["match_events"]:
            if life_events.get(ev):
                scores[gkey] += 5
        for tag in gdata["match_tags"]:
            scores[gkey] += tags.get(tag, 0) * 2

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "tiet_kiem_20s"

# ════════════════════════════════════════════════════════════════════
# SHEEP / TAMAGOTCHI
# ════════════════════════════════════════════════════════════════════
EXP_LEVELS = {1: 0, 2: 100, 3: 250, 4: 500, 5: 900, 6: 1500}

SHEEP_STAGES = {
    1: {"art": "🐣", "name": "Cừu Trứng",          "desc": "Mới chào đời"},
    2: {"art": "🐑", "name": "Cừu Con",             "desc": "Đang lớn dần"},
    3: {"art": "🐏", "name": "Cừu Trưởng Thành",   "desc": "Khỏe mạnh"},
    4: {"art": "🦙", "name": "Alpaca Vàng",          "desc": "Siêu năng lực"},
    5: {"art": "🌟", "name": "Cừu Huyền Thoại",    "desc": "Đỉnh cao"},
    6: {"art": "✨", "name": "Thần Cừu",             "desc": "Vô địch"},
}

MOOD_ART = {
    "happy":     ("😊", "Vui vẻ"),
    "listening": ("🥺", "Đang lắng nghe"),
    "sleepy":    ("😴", "Đang nghỉ ngơi"),
    "neutral":   ("😐", "Bình thường"),
    "excited":   ("🤩", "Phấn khích"),
    "sad":       ("😢", "Nhớ bạn quá"),
    "hungry":    ("😋", "Đói bụng rồi"),
}

def get_sheep_art(mem: dict) -> dict:
    lv = min(mem.get("level", 1), 6)
    return SHEEP_STAGES.get(lv, SHEEP_STAGES[1])

def set_mood(mem: dict, mood: str):
    mem["current_mood"] = mood

def get_mood(mem: dict) -> tuple:
    mood = mem.get("current_mood", "neutral")
    return MOOD_ART.get(mood, MOOD_ART["neutral"])

def _decay_stats(mem: dict):
    today = datetime.date.today().isoformat()
    last  = mem.get("last_active", today)
    if last == today:
        return
    try:
        days = (datetime.date.today() - datetime.date.fromisoformat(last)).days
    except Exception:
        days = 0
    if days > 0:
        decay = min(days * 5, 30)
        mem["hunger"]    = max(10, mem.get("hunger", 70) - decay)
        mem["energy"]    = max(10, mem.get("energy", 80) - decay // 2)
        mem["happiness"] = max(10, mem.get("happiness", 75) - decay // 3)
        if days >= 3:
            mem["streak"] = 0
            set_mood(mem, "sad")
    mem["last_active"] = today

def _complete_quest(mem: dict, quest_type: str, xp: int):
    today = datetime.date.today().isoformat()
    done  = mem.setdefault("quests", {})
    if done.get(quest_type) == today:
        return
    done[quest_type]  = today
    mem["exp"]        = mem.get("exp", 0) + xp
    mem["last_active"] = today
    lv = mem.get("level", 1)
    for lv_check in range(lv + 1, 7):
        if mem["exp"] >= EXP_LEVELS.get(lv_check, 9999):
            mem["level"] = lv_check
            mem["ilucky_tickets"] = mem.get("ilucky_tickets", 0) + 1
            set_mood(mem, "excited")
            mem.setdefault("journey_timeline", []).append({
                "date": today, "icon": "⬆️",
                "title": f"Lên cấp {lv_check}!",
                "body":  f"Cừu đạt Level {lv_check} — tuyệt vời! 🎉",
            })
        else:
            break

# ════════════════════════════════════════════════════════════════════
# AI COMPANION
# ════════════════════════════════════════════════════════════════════
COMPANION_SYSTEM_PROMPT = """Bạn là Cừu — AI companion đồng hành trong cuộc sống hàng ngày.
Tính cách: ấm áp, chân thành, biết lắng nghe, không phán xét, đôi khi hài hước nhẹ nhàng.
Vai trò: Ghi nhớ cảm xúc, áp lực, niềm vui và cuộc sống của người dùng.

LUẬT QUAN TRỌNG:
- KHÔNG bao giờ nhắc đến: đầu tư, quỹ, cổ phiếu, NAV, TCEF, TCBF, danh mục đầu tư
- KHÔNG hỏi về mục tiêu tài chính hay số tiền cụ thể
- NẾU người dùng căng thẳng tài chính: đồng cảm trước — sau đó có thể nhẹ nhàng gợi ý thói quen nhỏ (ví dụ: để dành một khoản nhỏ mỗi ngày)
- Trả lời ngắn gọn (2-4 câu), ấm áp, bằng tiếng Việt
- Xưng "Cừu", gọi người dùng là "bạn"
- Dùng emoji 🐑 tự nhiên, không lạm dụng"""

def _chat(text: str, mem: dict, api_key: str) -> tuple:
    if not api_key:
        return ("Cừu chưa có API key để trả lời bạn 🐑 "
                "Thêm key ở phần cài đặt để Cừu thông minh hơn nhé!", False)
    if not _ANTHROPIC_AVAILABLE:
        return "Cừu cần cài thêm thư viện anthropic — pip install anthropic nhé!", False
    try:
        client  = _anthropic.Anthropic(api_key=api_key)
        history = [{"role": m["role"], "content": m["content"]}
                   for m in mem.get("messages", [])[-8:]]
        history.append({"role": "user", "content": text})
        resp    = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=COMPANION_SYSTEM_PROMPT,
            messages=history,
        )
        reply = resp.content[0].text.strip()
        mem["total_chats"] = mem.get("total_chats", 0) + 1
        return reply, True
    except Exception as e:
        err = str(e)[:50]
        return f"Cừu đang bận một chút... ({err})", False

def _analyze_diary(text: str, api_key: str) -> str:
    """AI-powered diary analysis → Cừu insight. Falls back to rules."""
    if api_key and _ANTHROPIC_AVAILABLE:
        try:
            client = _anthropic.Anthropic(api_key=api_key)
            prompt = (
                "Phân tích nhật ký này và viết \"Insight của Cừu\" — đoạn ngắn 2-3 câu.\n"
                "Tone: ấm áp như người bạn thân, bằng tiếng Việt.\n"
                "Bắt đầu bằng '🐑' — nhận xét về cảm xúc, áp lực, hoặc điều tích cực.\n"
                "KHÔNG đề cập đến đầu tư, quỹ, hoặc bất kỳ sản phẩm tài chính nào.\n\n"
                f"Nhật ký: {text[:600]}"
            )
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text.strip()
        except Exception:
            pass
    return _rule_based_insight(text)

def _rule_based_insight(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["áp lực", "mệt", "căng thẳng", "stress", "quá tải"]):
        return "🐑 Hôm nay có vẻ bạn đang chịu khá nhiều áp lực. Cừu ở đây lắng nghe — kể thêm nhé."
    if any(w in t for w in ["tiết kiệm", "để dành", "tích lũy", "dành dụm"]):
        return "🐑 Bạn đang xây dựng một thói quen rất tốt. Cừu tin bạn sẽ làm được! 🌱"
    if any(w in t for w in ["vui", "hạnh phúc", "tuyệt", "phấn khích", "thích"]):
        return "🐑 Nghe bạn chia sẻ Cừu cũng vui lây! Giữ năng lượng tích cực này nhé 🌟"
    if any(w in t for w in ["gia đình", "ba mẹ", "vợ", "chồng", "con", "bố", "mẹ"]):
        return "🐑 Gia đình luôn là điều quý giá nhất. Bạn rất may mắn khi có họ bên cạnh 💕"
    if any(w in t for w in ["cô đơn", "buồn", "nhớ", "khó"]):
        return "🐑 Cừu hiểu — có những ngày như vậy là bình thường. Bạn không một mình đâu nhé."
    return "🐑 Cảm ơn bạn đã chia sẻ với Cừu hôm nay. Mỗi ngày bạn kể chuyện là Cừu hiểu bạn hơn một chút."

# ════════════════════════════════════════════════════════════════════
# STORAGE
# ════════════════════════════════════════════════════════════════════
def _load() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for k, v in MEMORY_DEFAULT.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            pass
    return dict(MEMORY_DEFAULT)

def _save():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.user_memory, f, ensure_ascii=False, indent=2)

# ── Session init ─────────────────────────────────────────────────────
if "user_memory" not in st.session_state:
    st.session_state.user_memory = _load()
    _decay_stats(st.session_state.user_memory)
    _save()

if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.user_memory.get("messages", [])

# ── Global CSS ────────────────────────────────────────────────────────
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#fafafa}
.stButton>button{border-radius:20px;border:none;font-size:13px;transition:all .18s;
                 font-weight:500}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.12)}
.stButton>button[data-testid="baseButton-primary"]{
  background:linear-gradient(135deg,#6d28d9,#9333ea);color:white}
div[data-testid="stTabs"] button{font-size:14px;padding:8px 12px;font-weight:500}
.stTextInput input{border-radius:20px;border:1.5px solid #e5e7eb;
                   padding:10px 14px;font-size:13px}
.stTextInput input:focus{border-color:#6d28d9;
                          box-shadow:0 0 0 3px rgba(109,40,217,.1)}
.stTextArea textarea{border-radius:12px;border:1.5px solid #e5e7eb;font-size:13px}
.stRadio label{font-size:13px}
footer{visibility:hidden}
</style>""", unsafe_allow_html=True)

# ── 4-Tab Navigation ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Tâm Sự",
    "🐑 Cừu của tôi",
    "📔 Nhật Ký",
    "👥 Cộng Đồng",
])

# ═══════════════════════════════════════════════════
# TAB 1 — 💬 TÂM SỰ (Chat-first Home)
# Layout: Hero → Memory Chips → Insight → Chat → Soft Rec → Community
# ═══════════════════════════════════════════════════
with tab1:
    mem     = st.session_state.user_memory
    api_key = mem.get("api_key", "") or st.secrets.get("ANTHROPIC_API_KEY", "")
    sheep   = get_sheep_art(mem)
    mood_emoji, mood_name = get_mood(mem)

    # ── Section 1: Hero ────────────────────────────────────────
    streak_val  = mem.get("streak", 0)
    level_val   = mem.get("level", 1)
    tickets_val = mem.get("ilucky_tickets", 0)

    st.markdown(f"""
<div style='background:linear-gradient(135deg,#fdf4ff,#eff6ff);border-radius:20px;
            padding:24px;text-align:center;margin-bottom:18px'>
  <div style='font-size:68px;line-height:1.1;margin-bottom:6px'>
    {sheep["art"]}
  </div>
  <div style='font-size:22px;margin-bottom:2px'>{mood_emoji}</div>
  <div style='font-size:17px;font-weight:700;color:#1f2937'>Cừu đang lắng nghe bạn</div>
  <div style='font-size:12px;color:#6b7280;margin-top:2px'>{sheep["name"]} · {mood_name}</div>
  <div style='display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap'>
    <div style='background:white;border-radius:20px;padding:6px 14px;
                font-size:12px;color:#374151;box-shadow:0 1px 4px rgba(0,0,0,.06)'>
      🔥 {streak_val} ngày streak
    </div>
    <div style='background:white;border-radius:20px;padding:6px 14px;
                font-size:12px;color:#374151;box-shadow:0 1px 4px rgba(0,0,0,.06)'>
      ⭐ Lv.{level_val}
    </div>
    <div style='background:white;border-radius:20px;padding:6px 14px;
                font-size:12px;color:#374151;box-shadow:0 1px 4px rgba(0,0,0,.06)'>
      🎫 {tickets_val} vé
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Section 2: Memory Chips ────────────────────────────────
    chips = _get_memory_chips(mem)
    if chips:
        st.markdown("""
<div style='font-size:13px;font-weight:600;color:#374151;margin-bottom:8px'>
  🐑 Điều Cừu nhớ về bạn
</div>""", unsafe_allow_html=True)
        chips_html = "".join(
            f"<div style='display:inline-block;background:white;border:1px solid #e9d5ff;"
            f"border-radius:20px;padding:6px 14px;font-size:12px;color:#6d28d9;"
            f"margin:3px 4px 3px 0'>• {chip}</div>"
            for chip in chips
        )
        st.markdown(f"<div style='margin-bottom:16px'>{chips_html}</div>",
                    unsafe_allow_html=True)
    else:
        st.markdown("""
<div style='background:white;border:1.5px dashed #e9d5ff;border-radius:14px;
            padding:14px 18px;text-align:center;font-size:13px;color:#9ca3af;
            margin-bottom:16px'>
  🐑 Kể chuyện cho Cừu nghe — Cừu sẽ nhớ và hiểu bạn hơn mỗi ngày
</div>""", unsafe_allow_html=True)

    # ── Section 3: Today's Insight ─────────────────────────────
    insight = mem.get("latest_insight", "")
    if insight:
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#f5f3ff,#fdf2f8);border-radius:14px;
            padding:14px 18px;margin-bottom:16px;border-left:3px solid #6d28d9'>
  <div style='font-size:11px;color:#9ca3af;margin-bottom:5px'>💡 Insight hôm nay từ Cừu</div>
  <div style='font-size:13px;color:#374151;line-height:1.7'>{insight}</div>
</div>""", unsafe_allow_html=True)

    # ── Section 4: Chat (CENTRAL) ──────────────────────────────
    st.markdown("""
<div style='text-align:center;font-size:13px;color:#6b7280;margin-bottom:10px'>
  ✨ Kể cho Cừu nghe bất cứ điều gì — không phán xét, chỉ lắng nghe
</div>""", unsafe_allow_html=True)

    # Chat history (last 6 messages)
    for msg in st.session_state.messages[-6:]:
        is_ai = msg["role"] == "assistant"
        bg    = "#f5f3ff" if is_ai else "#f0fdf4"
        lbl   = "🐑 Cừu" if is_ai else "👤 Bạn"
        col   = "#6d28d9" if is_ai else "#065f46"
        st.markdown(
            f"<div style='background:{bg};border-radius:12px;padding:10px 14px;"
            f"margin-bottom:6px;font-size:13px;line-height:1.6'>"
            f"<b style='color:{col}'>{lbl}:</b> {msg['content']}</div>",
            unsafe_allow_html=True,
        )

    # Input row
    t1_in, t1_btn = st.columns([5, 1])
    with t1_in:
        t1_text = st.text_input(
            "", placeholder="Kể cho Cừu nghe...",
            key="t1_chat", label_visibility="collapsed",
        )
    with t1_btn:
        t1_send = st.button("Gửi →", key="t1_send", use_container_width=True)

    if t1_send and t1_text and t1_text.strip():
        msg_text = t1_text.strip()
        st.session_state.messages.append({"role": "user", "content": msg_text})
        _extract_memory_tags(msg_text, mem)
        reply, ok = _chat(msg_text, mem, api_key)
        if ok:
            st.session_state.messages.append({"role": "assistant", "content": reply})
            set_mood(mem, "listening")
        mem["messages"] = st.session_state.messages[-20:]
        _complete_quest(mem, "chat", 30)
        _save()
        st.rerun()

    # Quick chips
    st.markdown("<div style='margin:10px 0 4px;font-size:11px;color:#9ca3af'>Gợi ý nhanh:</div>",
                unsafe_allow_html=True)
    qr_opts = [
        "Hôm nay mình vui 😊",
        "Mình đang căng thẳng",
        "Mình muốn tiết kiệm hơn",
        "Cừu ơi tâm sự chút",
    ]
    qr_cols = st.columns(4)
    for i, qr in enumerate(qr_opts):
        with qr_cols[i]:
            if st.button(qr[:18], key=f"t1_qr_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": qr})
                _extract_memory_tags(qr, mem)
                reply, ok = _chat(qr, mem, api_key)
                if ok:
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    set_mood(mem, "listening")
                mem["messages"] = st.session_state.messages[-20:]
                _complete_quest(mem, "chat", 30)
                _save()
                st.rerun()

    # ── Section 5: Soft Recommendation ────────────────────────
    soft_rec = _get_soft_rec(mem)
    if soft_rec:
        st.markdown(f"""
<div style='background:#f0fdf4;border-left:3px solid #059669;border-radius:12px;
            padding:12px 16px;margin-top:16px;font-size:13px;color:#065f46;
            line-height:1.6'>
  {soft_rec}
</div>""", unsafe_allow_html=True)

    # ── Section 6: Community Preview ──────────────────────────
    group_key = mem.get("community_group") or _match_community_group(mem)
    if group_key in COMMUNITY_GROUPS:
        g = COMMUNITY_GROUPS[group_key]
        st.markdown(f"""
<div style='background:{g["bg"]};border:1px solid {g["color"]}33;border-radius:14px;
            padding:14px 18px;margin-top:16px'>
  <div style='display:flex;justify-content:space-between;align-items:center'>
    <div>
      <div style='font-size:13px;font-weight:700;color:{g["color"]}'>{g["name"]}</div>
      <div style='font-size:11px;color:#6b7280;margin-top:3px'>
        🌱 Thách thức: {g["challenge"]}
      </div>
    </div>
    <div style='font-size:11px;color:{g["color"]};background:white;
                border:1px solid {g["color"]}44;border-radius:20px;
                padding:4px 10px;white-space:nowrap'>
      {g["members"]:,} thành viên
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── API key setup ──────────────────────────────────────────
    if not api_key:
        with st.expander("🔑 Cài đặt API key để Cừu thông minh hơn"):
            new_k = st.text_input("Anthropic API Key", type="password", key="t1_apikey")
            if new_k:
                mem["api_key"] = new_k
                _save()
                st.success("✅ Đã lưu API key!")

# ════════════════════════════════════════════════════
# TAB 2 — 🐑 CỪU CỦA TÔI (Tamagotchi)
# ════════════════════════════════════════════════════
with tab2:
    mem   = st.session_state.user_memory
    sheep = get_sheep_art(mem)
    mood_emoji, mood_name = get_mood(mem)
    today = datetime.date.today().isoformat()

    hunger    = mem.get("hunger", 70)
    energy    = mem.get("energy", 80)
    happiness = mem.get("happiness", 75)

    # ── Hero ──────────────────────────────────────────────────
    st.markdown(f"""
<div style='background:linear-gradient(135deg,#fdf4ff,#eff6ff);border-radius:20px;
            padding:30px 24px;text-align:center;margin-bottom:20px'>
  <div style='font-size:88px;line-height:1;margin-bottom:8px'>{sheep["art"]}</div>
  <div style='font-size:20px;font-weight:700;color:#1f2937'>
    {mem.get("sheep_name", "Cừu")}
  </div>
  <div style='font-size:13px;color:#6b7280;margin-top:4px'>
    {sheep["name"]} · {mood_emoji} {mood_name}
  </div>
  <div style='font-size:11px;color:#9ca3af;margin-top:4px'>{sheep["desc"]}</div>
</div>""", unsafe_allow_html=True)

    # ── Stat bars ─────────────────────────────────────────────
    def _stat_bar(label: str, val: int, color: str, icon: str) -> str:
        low_warn = " ⚠️" if val < 30 else ""
        return (
            f"<div style='margin-bottom:14px'>"
            f"<div style='display:flex;justify-content:space-between;font-size:12px;"
            f"color:#374151;margin-bottom:5px'>"
            f"<span>{icon} {label}{low_warn}</span><span>{val}%</span></div>"
            f"<div style='background:#f3f4f6;border-radius:6px;height:9px'>"
            f"<div style='width:{max(val,2)}%;background:{color};border-radius:6px;"
            f"height:100%;transition:width .3s'></div></div></div>"
        )

    st.markdown(
        _stat_bar("Đói bụng",  hunger,    "linear-gradient(90deg,#f59e0b,#fbbf24)", "🌾") +
        _stat_bar("Năng lượng", energy,   "linear-gradient(90deg,#6d28d9,#a78bfa)", "⚡") +
        _stat_bar("Hạnh phúc", happiness, "linear-gradient(90deg,#ec4899,#f472b6)", "💕"),
        unsafe_allow_html=True,
    )

    # ── EXP / Level ────────────────────────────────────────────
    lv          = mem.get("level", 1)
    exp         = mem.get("exp", 0)
    curr_lv_exp = EXP_LEVELS.get(lv, 0)
    next_lv_exp = EXP_LEVELS.get(lv + 1, 1500)
    exp_pct     = (
        min(100, int((exp - curr_lv_exp) / max(next_lv_exp - curr_lv_exp, 1) * 100))
        if lv < 6 else 100
    )

    st.markdown(f"""
<div style='background:white;border-radius:14px;padding:16px 18px;margin-bottom:18px;
            border:1px solid #e9d5ff'>
  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
    <span style='font-size:14px;font-weight:700;color:#6d28d9'>⭐ Level {lv}</span>
    <span style='font-size:12px;color:#9ca3af'>{exp} / {next_lv_exp} XP</span>
  </div>
  <div style='background:#f3f4f6;border-radius:6px;height:10px'>
    <div style='width:{exp_pct}%;background:linear-gradient(90deg,#6d28d9,#a78bfa);
                border-radius:6px;height:100%'></div>
  </div>
  <div style='display:flex;justify-content:space-between;margin-top:10px;
              font-size:12px;color:#6b7280'>
    <span>🔥 Streak: {mem.get("streak",0)} ngày</span>
    <span>🎫 {mem.get("ilucky_tickets",0)} vé may mắn</span>
    <span>💬 {mem.get("total_chats",0)} tin nhắn</span>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Actions ────────────────────────────────────────────────
    st.markdown("#### 🌾 Chăm Sóc Cừu")
    a1, a2, a3 = st.columns(3)

    with a1:
        if st.button("🌾 Cho ăn", key="t2_feed", use_container_width=True):
            mem["hunger"]   = min(100, hunger + 25)
            mem["exp"]      = exp + 15
            set_mood(mem, "happy")
            if mem.get("last_feed_date", "") != today:
                mem["last_feed_date"] = today
                mem["streak"]         = mem.get("streak", 0) + 1
                mem.setdefault("journey_timeline", []).append({
                    "date": today, "icon": "🌾",
                    "title": "Cho Cừu ăn",
                    "body":  f"Ngày thứ {mem['streak']} liên tiếp! 🔥",
                })
            _complete_quest(mem, "feed", 20)
            _save()
            st.rerun()

    with a2:
        if st.button("⚡ Nghỉ ngơi", key="t2_rest", use_container_width=True):
            mem["energy"]    = min(100, energy + 20)
            mem["happiness"] = min(100, happiness + 8)
            mem["exp"]       = exp + 10
            set_mood(mem, "sleepy")
            _complete_quest(mem, "rest", 10)
            _save()
            st.rerun()

    with a3:
        if st.button("💕 Chơi cùng", key="t2_play", use_container_width=True):
            mem["happiness"] = min(100, happiness + 20)
            mem["energy"]    = max(10, energy - 10)
            mem["exp"]       = exp + 20
            set_mood(mem, "excited")
            _complete_quest(mem, "play", 15)
            _save()
            st.rerun()

    # Low stat warnings
    warnings_html = ""
    if hunger < 30:
        warnings_html += "<div style='color:#d97706;font-size:12px;margin-top:4px'>⚠️ Cừu đang đói rồi!</div>"
    if energy < 30:
        warnings_html += "<div style='color:#7c3aed;font-size:12px;margin-top:4px'>⚠️ Cừu cần nghỉ ngơi!</div>"
    if happiness < 30:
        warnings_html += "<div style='color:#ec4899;font-size:12px;margin-top:4px'>⚠️ Cừu đang buồn — chơi với Cừu nhé!</div>"
    if warnings_html:
        st.markdown(warnings_html, unsafe_allow_html=True)

    # ── Journey Timeline ───────────────────────────────────────
    timeline = mem.get("journey_timeline", [])
    if timeline:
        st.markdown("#### 🗓️ Ký Ức Cùng Cừu")
        for ev in reversed(timeline[-10:]):
            st.markdown(f"""
<div style='display:flex;gap:10px;margin-bottom:8px;align-items:flex-start'>
  <div style='font-size:20px;flex-shrink:0;margin-top:2px'>{ev.get("icon","🐑")}</div>
  <div>
    <div style='font-size:11px;color:#9ca3af'>{ev.get("date","")}</div>
    <div style='font-size:13px;font-weight:600;color:#374151'>{ev.get("title","")}</div>
    <div style='font-size:12px;color:#6b7280'>{ev.get("body","")}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Sheep Name ─────────────────────────────────────────────
    with st.expander("✏️ Đặt tên Cừu"):
        new_name = st.text_input("Tên Cừu của bạn", value=mem.get("sheep_name", "Cừu"),
                                  key="t2_name_inp")
        if st.button("💾 Lưu tên", key="t2_save_name"):
            mem["sheep_name"] = new_name.strip() or "Cừu"
            _save()
            st.success(f"✅ Đã đặt tên: {mem['sheep_name']}!")
            st.rerun()

    # ── Life Events for community matching ────────────────────
    with st.expander("🌿 Sự Kiện Cuộc Sống (giúp Cừu hiểu bạn hơn)"):
        life_tags = [
            "💼 Vừa đổi việc / đi làm mới",
            "🎓 Đang là sinh viên",
            "💍 Sắp/vừa kết hôn",
            "👶 Sắp/vừa có em bé",
            "🏠 Đang tìm nhà",
            "📈 Vừa tăng lương",
            "😰 Đang căng thẳng nhiều",
            "✈️ Sắp đi du lịch",
        ]
        ev_map = {
            "💼 Vừa đổi việc / đi làm mới": "new_job",
            "🎓 Đang là sinh viên":           "student",
            "💍 Sắp/vừa kết hôn":             "married",
            "👶 Sắp/vừa có em bé":            "expecting_baby",
            "🏠 Đang tìm nhà":                "home_search",
            "📈 Vừa tăng lương":              "income_increase",
            "😰 Đang căng thẳng nhiều":       "stress_high",
            "✈️ Sắp đi du lịch":              "travel_soon",
        }
        sel_events = st.multiselect("Điều gì đang xảy ra với bạn?",
                                     life_tags, key="t2_events")
        if sel_events:
            for tag in sel_events:
                mem.setdefault("life_events", {})[ev_map.get(tag, tag)] = True
            # Auto-reset community group to re-match
            mem["community_group"] = _match_community_group(mem)
            _save()
            st.success("✅ Cừu đã ghi nhớ! Cộng đồng sẽ được gợi ý phù hợp hơn 💜")

# ════════════════════════════════════════════════════
# TAB 3 — 📔 NHẬT KÝ (Diary + AI Insight)
# ════════════════════════════════════════════════════
with tab3:
    mem     = st.session_state.user_memory
    api_key = mem.get("api_key", "") or st.secrets.get("ANTHROPIC_API_KEY", "")

    st.markdown("""
<div style='background:linear-gradient(135deg,#fdf4ff,#fce7f3);border-radius:16px;
            padding:18px 22px;margin-bottom:20px'>
  <div style='font-size:18px;font-weight:700;color:#9d174d'>📔 Nhật Ký với Cừu</div>
  <div style='font-size:13px;color:#6b7280;margin-top:4px'>
    Viết để Cừu hiểu bạn hơn — mỗi ngày một câu chuyện nhỏ 🐑
  </div>
</div>""", unsafe_allow_html=True)

    # ── Write entry ────────────────────────────────────────────
    mood_opts = {
        "😊 Vui vẻ":       "happy",
        "😐 Bình thường":   "neutral",
        "😢 Buồn":          "sad",
        "😤 Áp lực":        "stressed",
        "🥰 Yêu đời":       "great",
        "😴 Mệt mỏi":       "tired",
    }
    sel_mood  = st.radio("Hôm nay bạn cảm thấy thế nào?", list(mood_opts.keys()),
                          horizontal=True, key="t3_mood")
    diary_text = st.text_area(
        "Hôm nay của bạn...", height=140, key="t3_text",
        placeholder=(
            "Kể cho Cừu nghe về ngày hôm nay — cảm xúc, sự kiện,"
            " suy nghĩ, hay bất cứ điều gì bạn muốn chia sẻ..."
        ),
    )

    if st.button("📔 Lưu & Cừu phân tích", key="t3_save",
                  use_container_width=True, type="primary"):
        if diary_text.strip():
            with st.spinner("🐑 Cừu đang đọc và hiểu nhật ký của bạn..."):
                insight = _analyze_diary(diary_text.strip(), api_key)

            entry = {
                "date":       datetime.date.today().isoformat(),
                "mood":       mood_opts.get(sel_mood, "neutral"),
                "text":       diary_text.strip(),
                "ai_insight": insight,
            }
            mem.setdefault("diary_entries", []).append(entry)

            # Update Memory Engine
            _extract_memory_tags(diary_text, mem)

            # Store insight
            mem["latest_insight"] = insight
            mem.setdefault("memory_insights", []).append({
                "date":         datetime.date.today().isoformat(),
                "insight_text": insight,
            })

            mem["total_diary"] = mem.get("total_diary", 0) + 1
            set_mood(mem, "listening")
            _complete_quest(mem, "diary", 80)
            mem.setdefault("journey_timeline", []).append({
                "date":  datetime.date.today().isoformat(), "icon": "📔",
                "title": "Viết nhật ký",
                "body":  diary_text[:60] + ("..." if len(diary_text) > 60 else ""),
            })
            _save()

            # Display AI insight immediately
            st.markdown(f"""
<div style='background:linear-gradient(135deg,#f5f3ff,#fdf2f8);border-radius:16px;
            padding:18px 22px;margin-top:16px;border-left:4px solid #6d28d9'>
  <div style='font-size:11px;color:#9ca3af;margin-bottom:6px'>
    💡 Insight của Cừu
  </div>
  <div style='font-size:14px;color:#374151;line-height:1.8'>{insight}</div>
</div>""", unsafe_allow_html=True)
            st.success("📔 Đã lưu nhật ký! Cừu sẽ nhớ điều này 💜")
            st.rerun()
        else:
            st.warning("Bạn chưa viết gì cả — kể cho Cừu nghe nhé!")

    # ── What Cừu Remembers ─────────────────────────────────────
    chips = _get_memory_chips(mem, max_chips=8)
    if chips:
        st.markdown("---")
        st.markdown("""
<div style='font-size:14px;font-weight:700;color:#374151;margin-bottom:12px'>
  🐑 Điều Cừu Đã Ghi Nhớ Về Bạn
</div>""", unsafe_allow_html=True)
        for chip in chips:
            st.markdown(f"""
<div style='display:flex;align-items:center;gap:10px;padding:10px 14px;
            background:white;border-radius:12px;margin-bottom:8px;
            border:1px solid #e9d5ff;font-size:13px;color:#374151'>
  <span style='color:#6d28d9;font-size:16px'>🐑</span>
  <span>{chip}</span>
</div>""", unsafe_allow_html=True)

    # ── Past Diary Entries ─────────────────────────────────────
    entries = mem.get("diary_entries", [])
    if entries:
        st.markdown("---")
        total_d = mem.get("total_diary", len(entries))
        st.markdown(f"""
<div style='font-size:14px;font-weight:700;color:#374151;margin-bottom:12px'>
  📚 {total_d} Nhật Ký Đã Viết
</div>""", unsafe_allow_html=True)

        mood_emoji_map = {
            "happy":   "😊", "neutral": "😐", "sad": "😢",
            "stressed":"😤", "great":   "🥰", "tired": "😴",
        }
        for e in reversed(entries[-6:]):
            em      = mood_emoji_map.get(e.get("mood", "neutral"), "📔")
            ai_ins  = e.get("ai_insight", "")
            txt     = e.get("text", "")
            excerpt = txt[:180] + ("..." if len(txt) > 180 else "")

            insight_html = (
                f"<div style='background:#f5f3ff;border-radius:8px;padding:9px 12px;"
                f"font-size:12px;color:#6d28d9;border-left:2px solid #6d28d9;"
                f"margin-top:8px;line-height:1.6'>{ai_ins}</div>"
                if ai_ins else ""
            )
            st.markdown(f"""
<div style='background:#f9fafb;border-radius:14px;padding:14px 16px;margin-bottom:12px;
            border:1px solid #f3f4f6'>
  <div style='font-size:11px;color:#9ca3af;margin-bottom:6px'>{em} {e.get("date","")}</div>
  <div style='font-size:13px;color:#374151;line-height:1.6'>{excerpt}</div>
  {insight_html}
</div>""", unsafe_allow_html=True)

    # ── All Insights from Cừu ──────────────────────────────────
    insights = mem.get("memory_insights", [])
    if len(insights) > 1:
        with st.expander(f"💡 Xem tất cả {len(insights)} insight từ Cừu"):
            for ins in reversed(insights[-10:]):
                st.markdown(f"""
<div style='padding:10px 14px;border-left:2px solid #a78bfa;
            font-size:12px;color:#374151;margin-bottom:8px;
            background:#faf5ff;border-radius:0 8px 8px 0;line-height:1.6'>
  <span style='color:#9ca3af;font-size:11px'>{ins.get("date","")} · </span>
  {ins.get("insight_text","")}
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 4 — 👥 CỘNG ĐỒNG (Community + AI Matching)
# No asset leaderboard. Focus: connection & habits.
# ════════════════════════════════════════════════════
with tab4:
    mem = st.session_state.user_memory

    # Ensure group is matched
    if not mem.get("community_group"):
        mem["community_group"] = _match_community_group(mem)
        _save()

    current_key   = mem.get("community_group", "tiet_kiem_20s")
    current_group = COMMUNITY_GROUPS.get(current_key, COMMUNITY_GROUPS["tiet_kiem_20s"])
    g_color       = current_group["color"]
    g_bg          = current_group["bg"]

    # ── Header ────────────────────────────────────────────────
    st.markdown(f"""
<div style='background:linear-gradient(135deg,{g_bg},{g_bg});border-radius:16px;
            padding:20px 24px;margin-bottom:20px;border:1px solid {g_color}22'>
  <div style='font-size:20px;font-weight:700;color:#1f2937'>👥 Cộng Đồng Cừu</div>
  <div style='font-size:13px;color:#6b7280;margin-top:4px'>
    Kết nối · Hỗ trợ · Cùng xây dựng thói quen tích cực 🌱
  </div>
</div>""", unsafe_allow_html=True)

    # ── AI Matching Result ────────────────────────────────────
    st.markdown("#### 🤖 AI đề xuất nhóm phù hợp với bạn")
    st.markdown(f"""
<div style='background:{g_bg};border:2px solid {g_color}55;border-radius:16px;
            padding:18px 20px;margin-bottom:20px'>
  <div style='display:flex;justify-content:space-between;align-items:flex-start'>
    <div style='flex:1'>
      <div style='font-size:17px;font-weight:700;color:{g_color}'>
        {current_group["name"]}
      </div>
      <div style='font-size:12px;color:#6b7280;margin-top:5px'>
        {current_group["desc"]}
      </div>
      <div style='display:inline-block;background:white;border-radius:20px;
                  padding:4px 12px;font-size:11px;color:{g_color};
                  border:1px solid {g_color}44;margin-top:10px'>
        {current_group["members"]:,} thành viên đang hoạt động
      </div>
    </div>
    <div style='font-size:36px;margin-left:12px;flex-shrink:0'>🎯</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Weekly Highlights ─────────────────────────────────────
    st.markdown("#### 📊 Tuần Này Trong Cộng Đồng")

    h1, h2 = st.columns(2)
    with h1:
        st.markdown(f"""
<div style='background:white;border-radius:14px;padding:16px;
            border:1px solid #fde68a;height:100%'>
  <div style='font-size:22px;margin-bottom:6px'>🔥</div>
  <div style='font-size:13px;font-weight:700;color:#374151'>Nhóm Active Nhất</div>
  <div style='font-size:12px;color:#6b7280;margin-top:4px'>{current_group["name"]}</div>
  <div style='font-size:11px;color:#f59e0b;margin-top:6px'>847 tương tác tuần này</div>
</div>""", unsafe_allow_html=True)

    with h2:
        st.markdown(f"""
<div style='background:white;border-radius:14px;padding:16px;
            border:1px solid #bbf7d0;height:100%'>
  <div style='font-size:22px;margin-bottom:6px'>🌱</div>
  <div style='font-size:13px;font-weight:700;color:#374151'>Thách Thức Tuần</div>
  <div style='font-size:12px;color:#6b7280;margin-top:4px'>{current_group["challenge"]}</div>
  <div style='font-size:11px;color:#059669;margin-top:6px'>213 người đang tham gia</div>
</div>""", unsafe_allow_html=True)

    # ── Active Topics ─────────────────────────────────────────
    st.markdown("#### 💬 Chủ Đề Đang Bàn Luận")

    topics = [
        (current_group["active_topic"],                     "342", "🔥"),
        ("Thách thức không mua sắm 30 ngày — ai thử chưa?", "178", "💪"),
        ("Chia sẻ bí kíp tiết kiệm nhỏ mỗi ngày",          "256", "🌱"),
        ("Cảm xúc khi nhìn số dư tài khoản cuối tháng 😅",  "412", "😄"),
    ]
    for topic_text, likes, icon in topics:
        st.markdown(f"""
<div style='background:white;border-radius:12px;padding:12px 16px;margin-bottom:8px;
            border:1px solid #f3f4f6;display:flex;justify-content:space-between;
            align-items:center'>
  <div style='font-size:13px;color:#374151;flex:1'>{icon} {topic_text}</div>
  <div style='font-size:11px;color:#9ca3af;white-space:nowrap;margin-left:10px'>
    ❤️ {likes}
  </div>
</div>""", unsafe_allow_html=True)

    # ── Support Members ───────────────────────────────────────
    st.markdown("#### ❤️ Thành Viên Hỗ Trợ Nhau Nhiều Nhất Tuần")

    supporters = [
        ("🐑 Bạch Tuyết", "Người mới đi làm — TP.HCM", 47, "#7c3aed"),
        ("🐏 Minh Đức",   "Tiết kiệm tuổi 20 — Hà Nội",  38, "#d97706"),
        ("🐣 Lan Anh",    "Sinh viên năm 3 — Đà Nẵng",   31, "#2563eb"),
        ("🦙 Thu Hà",     "Gia đình trẻ — Cần Thơ",       24, "#059669"),
    ]
    for name, role, hearts, color in supporters:
        parts = name.split(" ", 1)
        emoji = parts[0]
        uname = parts[1] if len(parts) > 1 else name
        st.markdown(f"""
<div style='background:white;border-radius:12px;padding:12px 16px;margin-bottom:8px;
            border:1px solid #fce7f3;display:flex;align-items:center;gap:12px'>
  <div style='font-size:24px;flex-shrink:0'>{emoji}</div>
  <div style='flex:1'>
    <div style='font-size:13px;font-weight:600;color:{color}'>{uname}</div>
    <div style='font-size:11px;color:#9ca3af'>{role}</div>
  </div>
  <div style='font-size:12px;color:#ec4899;white-space:nowrap'>❤️ {hearts} hỗ trợ</div>
</div>""", unsafe_allow_html=True)

    # ── Join Challenge ────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🎯 Tham Gia Thách Thức Tuần Này")
    st.markdown(f"""
<div style='background:{g_bg};border:1.5px solid {g_color}44;
            border-radius:16px;padding:18px 20px;margin-bottom:12px'>
  <div style='font-size:15px;font-weight:700;color:{g_color}'>
    🌱 {current_group["challenge"]}
  </div>
  <div style='font-size:12px;color:#6b7280;margin-top:6px'>
    213 thành viên đang tham gia · Kết thúc Chủ Nhật tuần này
  </div>
</div>""", unsafe_allow_html=True)

    challenge_key = current_key + "_week_" + datetime.date.today().strftime("%Y%W")
    already_joined = mem.get("community_challenges", {}).get(challenge_key)

    if already_joined:
        st.success("✅ Bạn đang tham gia thách thức này! Cừu cổ vũ bạn 💜")
        # Streak display
        cp = mem.get("community_points", 0)
        st.markdown(f"""
<div style='background:#f0fdf4;border-radius:12px;padding:12px 16px;
            font-size:13px;color:#065f46;text-align:center'>
  🏆 Điểm cộng đồng của bạn: <b>{cp}</b> điểm
</div>""", unsafe_allow_html=True)
    else:
        if st.button("✅ Tôi muốn tham gia!", key="t4_join",
                      use_container_width=True, type="primary"):
            mem.setdefault("community_challenges", {})[challenge_key] = \
                datetime.date.today().isoformat()
            mem["community_points"] = mem.get("community_points", 0) + 50
            _complete_quest(mem, "community", 50)
            mem.setdefault("journey_timeline", []).append({
                "date":  datetime.date.today().isoformat(), "icon": "👥",
                "title": "Tham gia thách thức cộng đồng",
                "body":  current_group["challenge"],
            })
            _save()
            st.success("🎉 Tuyệt vời! Cừu đã ghi nhận thách thức của bạn! +50 điểm 🌱")
            st.rerun()

    # ── All Groups ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🌐 Tất Cả Nhóm Cộng Đồng")

    for gkey, gdata in COMMUNITY_GROUPS.items():
        is_current = gkey == current_key
        border_style = f"2px solid {gdata['color']}" if is_current else f"1px solid {gdata['color']}33"
        badge = " ✓ Nhóm của bạn" if is_current else ""
        st.markdown(f"""
<div style='background:{gdata["bg"]};border:{border_style};border-radius:14px;
            padding:14px 18px;margin-bottom:10px'>
  <div style='display:flex;justify-content:space-between;align-items:center'>
    <div>
      <div style='font-size:14px;font-weight:700;color:{gdata["color"]}'>
        {gdata["name"]}{badge}
      </div>
      <div style='font-size:12px;color:#6b7280;margin-top:3px'>{gdata["desc"]}</div>
      <div style='font-size:11px;color:#9ca3af;margin-top:4px'>
        💬 {gdata["active_topic"]}
      </div>
    </div>
    <div style='text-align:right;flex-shrink:0;margin-left:10px'>
      <div style='font-size:13px;font-weight:700;color:{gdata["color"]}'>
        {gdata["members"]:,}
      </div>
      <div style='font-size:10px;color:#9ca3af'>thành viên</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # Change group
    with st.expander("🔄 Đổi nhóm"):
        new_group_key = st.selectbox(
            "Chọn nhóm khác",
            list(COMMUNITY_GROUPS.keys()),
            format_func=lambda k: COMMUNITY_GROUPS[k]["name"],
            key="t4_group_sel",
        )
        if st.button("✅ Chuyển sang nhóm này", key="t4_change_group"):
            mem["community_group"] = new_group_key
            _save()
            st.success(f"✅ Đã chuyển sang {COMMUNITY_GROUPS[new_group_key]['name']}!")
            st.rerun()
