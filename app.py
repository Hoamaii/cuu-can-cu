import streamlit as st
import anthropic
import json
import random
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Cừu Cần Cù 🐑", page_icon="🐑", layout="wide")

MASCOT_URL = "https://raw.githubusercontent.com/Hoamaii/cuu-can-cu/main/mascot.png"

# ─────────────────────────────────────────────
# PASTEL STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stApp"] {
    background: linear-gradient(135deg, #FFF0F5 0%, #F0F8FF 60%, #F5FFF8 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFF5F8 0%, #F0F8FF 100%) !important;
    border-right: 2px solid #FFD6E8 !important;
}
h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #C75B8A !important; }
h2 { font-size: 1.25rem !important; font-weight: 600 !important; color: #5B8AC7 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #555 !important; }
p, .stMarkdown p, label { font-size: 0.9rem !important; }
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
[data-testid="stChatMessage"] { border-radius: 16px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────
SYSTEM_PROMPT_ATTACHMENT = """Bạn là Cừu Cần Cù – người bạn đồng hành cảm xúc, KHÔNG phải chuyên gia tài chính.
Xưng hô: Mình (Cừu Cần Cù) – Bạn (người dùng). KHÔNG xưng "em" hay "Cừu Mai".

TUYỆT ĐỐI KHÔNG đề cập: chứng khoán cụ thể, lợi nhuận, NAV, khuyến nghị mua bán.
Nhiệm vụ: Lắng nghe như người bạn thân, ấm áp, không phán xét.

Phát hiện Life Event và gắn tag:
- học hành, thi cử → Education
- chia tay, buồn, cô đơn → Emotional
- mua xe, mua nhà, mua đồ → Consumption Goal
- hết tiền, thiếu tiền, nợ, khó khăn tài chính → Cashflow Problem
- nghỉ việc, chuyển việc, thất nghiệp, sự nghiệp → Career Change
- du lịch, đi Nhật, đi Hàn, đi Mỹ, đi nước ngoài → Travel Dream
- cưới, gia đình, sinh con → Life Milestone

Phát hiện giấc mơ/mục tiêu cụ thể nếu có.

Output JSON thuần túy:
{
  "message": "Phản hồi ấm áp như người bạn, dùng emoji nhẹ nhàng, KHÔNG nhắc tài chính hay quỹ đầu tư",
  "nudge_action": "Gợi ý hành động nhỏ về cảm xúc, không liên quan tài chính",
  "memory_update": "Thông tin mới cần ghi nhớ về người dùng",
  "life_event_tag": "Tag phát hiện hoặc chuỗi rỗng",
  "dream_detected": "Tên giấc mơ cụ thể hoặc chuỗi rỗng",
  "dream_amount": 0
}"""

SYSTEM_PROMPT_ADVANCED = """Bạn là Cừu Cần Cù – người bạn đồng hành tài chính, nhớ rõ lịch sử và mục tiêu của bạn.
Xưng hô: Mình (Cừu Cần Cù) – Bạn. KHÔNG xưng "em" hay "Cừu Mai".
Tone: Ấm áp, đồng cảm – không phán xét, không phải chuyên gia tài chính khô khan.

Khi người dùng chia sẻ mục tiêu/giấc mơ:
- Tính savings math đơn giản
- Gợi ý đầu tư quỹ TCBF (ngắn hạn <1 năm), TCFF (1-3 năm), TCEF (>3 năm)
- Nhấn mạnh: đầu tư quỹ từ 10.000đ, vừa tiết kiệm vừa sinh lãi

Output JSON thuần túy:
{
  "message": "Phản hồi ấm áp, có thể nhắc nhẹ đến việc nuôi quỹ",
  "nudge_action": "Hành động cụ thể nhỏ",
  "memory_update": "Thông tin mới về người dùng",
  "life_event_tag": "Tag hoặc chuỗi rỗng",
  "dream_detected": "Tên giấc mơ hoặc chuỗi rỗng",
  "dream_amount": 0,
  "savings_suggestion": "Gợi ý tiết kiệm + quỹ phù hợp hoặc chuỗi rỗng"
}"""

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
DREAM_AMOUNTS = {
    "nhật bản": 25_000_000, "nhật": 25_000_000,
    "hàn quốc": 20_000_000, "hàn": 20_000_000,
    "châu âu": 50_000_000,
    "mỹ": 60_000_000,
    "thái lan": 15_000_000, "thái": 15_000_000,
    "singapore": 18_000_000,
    "macbook": 30_000_000,
    "iphone": 25_000_000,
    "xe máy": 20_000_000, "xe": 20_000_000,
    "vespa": 50_000_000,
    "ô tô": 500_000_000,
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
    ("Mình đang lo về chuyện học hành 📚", "Education"),
    ("Mình có một giấc mơ muốn thực hiện ✨", "Travel Dream"),
    ("Mình vừa trải qua chuyện không vui 🌧️", "Emotional"),
    ("Mình đang gặp khó khăn về tiền bạc 💸", "Cashflow Problem"),
    ("Mình muốn có điều gì đó cho riêng mình 🎯", "Consumption Goal"),
    ("Mình đang nghĩ lại về con đường sự nghiệp 🌱", "Career Change"),
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
    "TCBF": {
        "tên": "Quỹ Trái Phiếu TCBF",
        "mô_tả": "An toàn & ổn định – lý tưởng cho mục tiêu ngắn hạn",
        "lãi_suất": 0.08,
        "rủi_ro": "Thấp 🛡️",
        "phù_hợp": "Dưới 1 năm",
        "emoji": "🔵",
    },
    "TCFF": {
        "tên": "Quỹ Linh Hoạt TCFF",
        "mô_tả": "Cân bằng & linh hoạt – kết hợp cổ phiếu & trái phiếu",
        "lãi_suất": 0.10,
        "rủi_ro": "Trung bình ⚖️",
        "phù_hợp": "1 – 3 năm",
        "emoji": "🟡",
    },
    "TCEF": {
        "tên": "Quỹ Cổ Phiếu TCEF",
        "mô_tả": "Tăng trưởng mạnh – đầu tư cổ phiếu dài hạn",
        "lãi_suất": 0.14,
        "rủi_ro": "Cao 🚀",
        "phù_hợp": "Trên 3 năm",
        "emoji": "🟢",
    },
}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
MEMORY_DEFAULT = {
    "name": "", "streak": 0, "sentiment": "neutral",
    "notes": [], "life_events": [], "dreams": [],
    "total_saved": 0, "last_updated": "",
    "selected_fund": "TCBF",
    "wealth_genome": {
        "dream_type": "", "emotion_type": "", "risk_type": "", "reward_type": "",
    },
}

for key, val in {
    "messages": [], "api_key": "",
    "user_memory": MEMORY_DEFAULT.copy(),
    "current_stage": 1, "active_dream_idx": 0, "_quick_reply": None,
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
    if 5 <= h < 12: return "☀️ Chào buổi sáng!", "Hôm nay mình được ăn chưa? Kể cho mình nghe chuyện của bạn nhé 🌱"
    if 12 <= h < 18: return "🌤️ Buổi chiều vui!", "Nhớ nghỉ ngơi một chút nhé – mình luôn ở đây lắng nghe bạn 🐑"
    return "🌙 Tối bình yên!", "Hôm nay bạn thế nào? Kể cho mình nghe nhé, mình không phán xét đâu 🐑"

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
    if mem["total_saved"] > 0 and st.session_state.current_stage < 5:
        st.session_state.current_stage = max(st.session_state.current_stage, 5)
    if mem["total_saved"] >= 100_000 and st.session_state.current_stage < 6:
        st.session_state.current_stage = max(st.session_state.current_stage, 6)

# ─────────────────────────────────────────────
# CLAUDE API
# ─────────────────────────────────────────────
def chat_with_sheep(user_message: str) -> dict:
    EMPTY = {"message": "", "nudge_action": "", "memory_update": "",
             "life_event_tag": "", "dream_detected": "", "dream_amount": 0, "savings_suggestion": ""}
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        mem = st.session_state.user_memory
        stage = st.session_state.current_stage
        system = SYSTEM_PROMPT_ATTACHMENT if stage <= 2 else SYSTEM_PROMPT_ADVANCED
        context = f"""=== THÔNG TIN NGƯỜI DÙNG ===
Tên: {mem['name'] or 'Chưa biết'}
Tâm trạng: {mem['sentiment']}
Streak: {mem['streak']} ngày
Sự kiện cuộc sống: {', '.join(mem['life_events'][-5:]) or 'Chưa có'}
Giấc mơ: {', '.join(d['name'] for d in mem['dreams']) or 'Chưa chia sẻ'}
Ghi chú: {'; '.join(mem['notes'][-3:]) or 'Chưa có'}

=== TIN NHẮN ===
{user_message}"""
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:]]
        history.append({"role": "user", "content": context})
        resp = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=1024, system=system, messages=history)
        raw = resp.content[0].text.strip()
        if raw.startswith("```"): raw = "\n".join(raw.split("\n")[1:-1])
        return {**EMPTY, **json.loads(raw)}
    except json.JSONDecodeError:
        return {**EMPTY, "message": "Bê bê 🐑 Cừu Cần Cù bị lạc... Bạn nói lại được không?"}
    except anthropic.AuthenticationError:
        return {**EMPTY, "message": "🔑 API key chưa đúng! Kiểm tra lại ở thanh bên nhé."}
    except Exception as e:
        return {**EMPTY, "message": f"Ối, mình gặp lỗi: {e}"}

# ─────────────────────────────────────────────
# CẬP NHẬT BỘ NHỚ
# ─────────────────────────────────────────────
def update_memory(result: dict, user_msg: str):
    mem = st.session_state.user_memory
    mu = result.get("memory_update", "")
    tag = result.get("life_event_tag", "")
    d_name = result.get("dream_detected", "")
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

    if any(k in ul for k in ["vui", "tốt", "tuyệt", "hào hứng", "phấn khởi", "thích", "mừng"]):
        mem["sentiment"] = "positive"
    elif any(k in ul for k in ["lo", "sợ", "buồn", "stress", "khó", "thiếu", "hết tiền",
                                "chia tay", "thất nghiệp", "nghỉ việc", "mất việc", "nợ",
                                "vay", "áp lực", "mệt", "không vui"]):
        mem["sentiment"] = "concerned"

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

    genome = mem["wealth_genome"]
    if "Travel Dream" in mem["life_events"]: genome["dream_type"] = "Du lịch & Trải nghiệm 🌏"
    elif "Consumption Goal" in mem["life_events"]: genome["dream_type"] = "Sở hữu & Vật chất 🛍️"
    elif "Education" in mem["life_events"]: genome["dream_type"] = "Học tập & Phát triển 📚"
    elif "Life Milestone" in mem["life_events"]: genome["dream_type"] = "Gia đình & Tổ ấm 💒"
    elif "Career Change" in mem["life_events"]: genome["dream_type"] = "Sự nghiệp & Tự do 💼"

    if mem["sentiment"] == "concerned":
        genome["emotion_type"] = "Thận trọng – bạn suy nghĩ kỹ trước khi hành động 🤔"
        genome["risk_type"] = "Ưu tiên an toàn – TCBF phù hợp nhất với bạn 🛡️"
    elif mem["sentiment"] == "positive":
        genome["emotion_type"] = "Lạc quan – bạn có năng lượng tích cực với tiền bạc 😊"
        genome["risk_type"] = "Cởi mở với rủi ro – TCEF/TCFF có thể phù hợp 🚀"

    if mem["streak"] >= 5: genome["reward_type"] = "Streak & Thành tích – bạn yêu thích chuỗi ngày liên tiếp 🏆"
    elif mem["streak"] >= 1: genome["reward_type"] = "Đang hình thành thói quen – mình cùng duy trì nhé! 🌱"
    elif mem["life_events"]: genome["reward_type"] = "Khám phá & Trải nghiệm – bạn thích thử những điều mới 🌟"

    mem["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.user_memory = mem

    stage = st.session_state.current_stage
    if stage == 1 and len(mem["notes"]) >= 1: st.session_state.current_stage = 2
    if stage <= 2 and mem["dreams"]: st.session_state.current_stage = max(stage, 3)
    if stage >= 5 and all(genome.values()): st.session_state.current_stage = max(stage, 7)

def send_message(text: str):
    if not st.session_state.api_key:
        st.error("🔑 Bạn chưa nhập API key! Vui lòng nhập ở thanh bên."); return
    st.session_state.messages.append({"role": "user", "content": text})
    with st.spinner("Cừu Cần Cù đang nghĩ... 🐑"):
        result = chat_with_sheep(text)
    msg = result.get("message", "Bê bê, mình không hiểu rồi...")
    st.session_state.messages.append({"role": "assistant", "content": msg,
                                       "nudge": result.get("nudge_action", ""),
                                       "savings": result.get("savings_suggestion", "")})
    update_memory(result, text)

# ─────────────────────────────────────────────
# THANH BÊN
# ─────────────────────────────────────────────
with st.sidebar:
    try: st.image(MASCOT_URL, width=90)
    except: st.markdown("# 🐑")
    st.title("Cừu Cần Cù")

    stage = st.session_state.current_stage
    st.caption(STAGE_LABELS.get(stage, ""))
    st.progress(stage / 7, text=f"Giai đoạn {stage} / 7")
    st.divider()

    key_in = st.text_input("🔑 Anthropic API Key", value=st.session_state.api_key,
                            type="password", placeholder="sk-ant-...")
    if key_in: st.session_state.api_key = key_in
    st.divider()

    st.subheader("🧠 Bộ Nhớ Cừu")
    mem = st.session_state.user_memory
    c1, c2 = st.columns(2)
    c1.metric("🔥 Streak", f"{mem['streak']} ngày")
    c2.metric("Tâm trạng", {"positive": "😊", "concerned": "😟", "neutral": "😐"}.get(mem["sentiment"], "😐"))

    if mem["name"]: st.info(f"👤 {mem['name']}")
    if mem["life_events"]:
        st.write("🏷️ **Sự kiện:**")
        for tag in mem["life_events"][-4:]:
            st.caption(f"{LIFE_EVENT_ICONS.get(tag,'🏷️')} {LIFE_EVENT_VI.get(tag, tag)}")
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
        if genome["risk_type"]: st.caption(f"🛡️ {genome['risk_type'].split(' – ')[0]}")

    st.divider()
    with st.expander("⚙️ Chuyển giai đoạn (demo)"):
        new_stage = st.selectbox("Giai đoạn:", list(range(1, 8)), index=stage - 1,
                                  format_func=lambda x: f"{x}. {STAGE_LABELS[x]}")
        if st.button("Chuyển →", use_container_width=True):
            st.session_state.current_stage = new_stage; st.rerun()
    if st.button("🗑️ Đặt lại tất cả", use_container_width=True):
        for k in ["messages", "user_memory", "current_stage", "active_dream_idx", "_quick_reply"]:
            if k == "user_memory": st.session_state[k] = MEMORY_DEFAULT.copy()
            elif k == "current_stage": st.session_state[k] = 1
            elif k == "active_dream_idx": st.session_state[k] = 0
            else: st.session_state[k] = [] if k == "messages" else None
        st.rerun()
    st.caption("Được tạo bởi Claude 💙")

# ─────────────────────────────────────────────
# NỘI DUNG CHÍNH
# ─────────────────────────────────────────────
stage = st.session_state.current_stage
mem = st.session_state.user_memory

if stage <= 2:
    greeting_title, greeting_msg = get_greeting()
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        try: st.image(MASCOT_URL, width=120)
        except: st.markdown("## 🐑")
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
    st.markdown("#### 🐑 Mình lắng nghe – không phán xét, không so sánh\n*Bạn đang cảm thấy thế nào? Chọn điều gần nhất với bạn hôm nay:*")
    qr_cols = st.columns(3)
    for i, (label, _) in enumerate(QUICK_REPLIES):
        if qr_cols[i % 3].button(label, use_container_width=True, key=f"qr_{i}"):
            st.session_state._quick_reply = label; st.rerun()
    if st.session_state._quick_reply:
        qr = st.session_state._quick_reply
        st.session_state._quick_reply = None
        send_message(qr); st.rerun()
    if st.session_state.messages:
        st.markdown("---")
        for m in st.session_state.messages[-8:]:
            with st.chat_message(m["role"], avatar="🐑" if m["role"] == "assistant" else "🧑"):
                st.markdown(m["content"])
                if m.get("nudge"): st.info(f"💡 {m['nudge']}")

elif stage == 3:
    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        try: st.image(MASCOT_URL, width=100)
        except: st.markdown("## 🐑")
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
                    st.markdown(f"**{fund['emoji']} Quỹ gợi ý:** {fund['tên']} – {fund['mô_tả']}\n\nLãi suất kỳ vọng ~**{fund['lãi_suất']*100:.0f}%/năm** | Rủi ro: {fund['rủi_ro']} | Phù hợp: {fund['phù_hợp']}")
                    st.markdown("---")
                    st.markdown("**💡 Nếu bạn đầu tư quỹ mỗi ngày:**")
                    c1, c2 = st.columns(2)
                    for col, daily in [(c1, 20_000), (c1, 50_000), (c2, 100_000), (c2, 200_000)]:
                        col.info(f"**{fmt(daily)}/ngày** → khoảng **{savings_timeline(d['amount'], daily)}**")
                    st.markdown("")
                    if st.button(f"🐑 Bắt đầu nuôi giấc mơ '{d['name'].title()}' ngay!", key=f"pick_{idx}", use_container_width=True, type="primary"):
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
        with st.chat_message(m["role"], avatar="🐑" if m["role"] == "assistant" else "🧑"):
            st.markdown(m["content"])
            if m.get("savings"): st.success(f"💡 {m['savings']}")

elif stage == 4:
    dream = active_dream()
    fund_key = mem.get("selected_fund", "TCBF")
    fund = FUNDS[fund_key]
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        try: st.image(MASCOT_URL, width=100)
        except: st.markdown("## 🐑")
        st.markdown("## ❤️ Nuôi Cừu Cần Cù hôm nay")
        st.caption("Mỗi lần cho Cừu ăn = bạn đang mua một phần quỹ đầu tư!")
        if dream and dream["amount"] > 0:
            pct = min(100, dream["saved"] / dream["amount"] * 100)
            st.markdown(f"### 🎯 {dream['name'].title()}")
            st.progress(pct / 100)
            st.caption(f"{pct:.1f}% hoàn thành · Đã đầu tư: {fmt(dream['saved'])} / {fmt(dream['amount'])}")
        st.markdown("---")
        st.markdown(f"**{fund['emoji']} Tiền của bạn đang vào:** {fund['tên']}\n\n📈 Lãi kỳ vọng ~{fund['lãi_suất']*100:.0f}%/năm · {fund['rủi_ro']}")
        st.markdown("")
        st.markdown("**Hôm nay bạn muốn đầu tư bao nhiêu?**")
        btn_cols = st.columns(4)
        for i, amt in enumerate(MICRO_AMOUNTS):
            if btn_cols[i].button(f"**{fmt(amt)}**", use_container_width=True, key=f"feed_{amt}", type="primary"):
                add_saved(amt); st.balloons()
                st.success(f"🐑 Cừu Cần Cù được ăn {fmt(amt)}! ❤️\n\nBạn vừa đầu tư {fmt(amt)} vào {fund['tên']}. Tích tiểu thành đại, mỗi ngày một ít là đủ rồi!")
                st.rerun()
        if mem["total_saved"] > 0:
            projected_1y = calc_fund_growth(max(mem["total_saved"] / max(1, mem["streak"] / 30), 50_000), 12, fund["lãi_suất"])
            st.markdown("---")
            st.markdown(f"💰 **Đã đầu tư:** {fmt(mem['total_saved'])}")
            st.markdown(f"🔥 **Streak:** {mem['streak']} ngày liên tiếp")
            st.markdown(f"📈 **Nếu tiếp tục 12 tháng**, quỹ của bạn có thể đạt ~**{fmt(int(projected_1y))}**")

elif stage == 5:
    fund_key = mem.get("selected_fund", "TCBF")
    fund = FUNDS[fund_key]
    st.title("🔄 Thói quen hàng ngày")
    st.caption("Tích tiểu thành đại – mỗi ngày một hành động nhỏ, tài chính lớn dần theo năm tháng 🐑")
    h = datetime.now().hour
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if 5 <= h < 12:
            with st.container(border=True):
                try: st.image(MASCOT_URL, width=90)
                except: st.markdown("## 🐑")
                st.markdown("### ☀️ Cừu Cần Cù chào buổi sáng!")
                st.markdown(f"🐑 *Hôm nay mình được ăn chưa?*\n\nMỗi lần bạn nuôi mình = bạn đang **mua một phần {fund['tên']}**.\n\nCừu Cần Cù lớn khoẻ → Tài chính của bạn cũng lớn mạnh theo! 🌱")
                st.markdown("")
                sc = st.columns(4)
                for i, amt in enumerate(MICRO_AMOUNTS):
                    if sc[i].button(f"❤️ {fmt(amt)}", use_container_width=True, key=f"morning_{amt}"):
                        add_saved(amt)
                        st.success(f"🌱 Cừu Cần Cù vui lắm!\n\nBạn vừa đầu tư {fmt(amt)} vào {fund['tên']}. Có một ngày tốt lành nhé! ☀️")
                        st.rerun()
        else:
            items = [("trà sữa", 35_000), ("cà phê", 45_000), ("ăn vặt", 25_000)]
            item, price = random.choice(items)
            with st.container(border=True):
                try: st.image(MASCOT_URL, width=90)
                except: st.markdown("## 🐑")
                st.markdown("### 🌙 Cừu Cần Cù chào buổi tối!")
                st.markdown(f"🐑 *Nếu hôm nay bớt 1 {item}, bạn có thêm **{fmt(price)}**.*\n\nSố tiền nhỏ đó, nếu đầu tư vào **{fund['tên']}** mỗi ngày,\nsau 1 năm có thể thành ~**{fmt(int(calc_fund_growth(price, 12, fund['lãi_suất'])))}** nhờ lãi kép! ✨")
                st.markdown("")
                if st.button(f"💰 Đầu tư {fmt(price)} ngay vào quỹ!", use_container_width=True, type="primary"):
                    add_saved(price)
                    st.success(f"🐑 Bạn vừa đầu tư {fmt(price)} vào {fund['tên']}!\n\nMỗi ngày một ít, Cừu Cần Cù ngày càng lớn khoẻ cùng tài chính của bạn ❤️")
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

elif stage == 6:
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
                    if pct_now < 25: icon, vibe = "🌱", "Hành trình mới bắt đầu..."
                    elif pct_now < 50: icon, vibe = "🌿", "Đang lớn dần rồi!"
                    elif pct_now < 75: icon, vibe = "🌸", "Đang nở rộ!"
                    elif pct_now < 100: icon, vibe = "🌟", "Sắp đến đích rồi!!!"
                    else: icon, vibe = "🎉", "Giấc mơ đã thành hiện thực!"
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
                        st.markdown(f"💡 **Tóm lại:** Bạn bỏ ra **{fmt(monthly_needed * last['tháng'])}** tiền gốc, quỹ sinh thêm **{fmt(int(last['giá_trị'] - monthly_needed * last['tháng']))}** tiền lãi.\n\nTháng {last['tháng']} bạn bán quỹ → nhận về ~**{fmt(int(last['giá_trị']))}** → mua {d['name'].title()} dư dả! 🎉")
                    st.markdown("")
                    if st.button("❤️ Tiếp tục nuôi quỹ!", key=f"vis_{d['name']}", use_container_width=True, type="primary"):
                        st.session_state.current_stage = 4; st.rerun()
                else:
                    st.info("Cừu Cần Cù sẽ giúp bạn tính toán chi phí cụ thể!")
    else:
        st.info("Bạn chưa có giấc mơ nào. Hãy quay lại và kể với Cừu Cần Cù! 🐑")

elif stage == 7:
    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        try: st.image(MASCOT_URL, width=100)
        except: st.markdown("## 🐑")
    st.title("🧬 Hồ Sơ Tài Chính Của Bạn")
    st.caption(f"Sau {len(mem['notes'])} cuộc trò chuyện, Cừu Cần Cù đã hiểu bạn hơn và xây dựng được bức chân dung tài chính riêng của bạn 🐑")
    genome = mem["wealth_genome"]
    GENOME_EXPLAIN = {
        "dream_type": ("💭 Kiểu Giấc Mơ", "Bạn đang hướng đến điều gì trong cuộc sống? Đây là động lực sâu nhất giúp bạn tiết kiệm và đầu tư."),
        "emotion_type": ("💓 Kiểu Cảm Xúc Tài Chính", "Cách bạn cảm nhận và phản ứng với tiền bạc. Hiểu được điều này giúp bạn đưa ra quyết định tài chính khôn ngoan hơn."),
        "risk_type": ("🛡️ Khẩu Vị Rủi Ro", "Mức độ rủi ro bạn thoải mái chấp nhận khi đầu tư. Cừu Cần Cù dùng điều này để gợi ý quỹ phù hợp nhất cho bạn."),
        "reward_type": ("🏆 Động Lực Của Bạn", "Điều gì thúc đẩy bạn hành động và duy trì thói quen tốt. Biết được động lực giúp Cừu Cần Cù khích lệ bạn đúng cách."),
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
        c2.metric("Mức rủi ro", fund["rủi_ro"])
        c3.metric("Phù hợp nhất", fund["phù_hợp"])
        st.markdown("💡 *Bạn có thể đầu tư từ **10.000đ** mỗi lần – không cần số tiền lớn*")
    st.divider()
    st.subheader("💌 Cừu Cần Cù nhắn riêng cho bạn")
    if mem["dreams"]:
        dream_name = mem["dreams"][0]["name"]
        with st.container(border=True):
            try: st.image(MASCOT_URL, width=80)
            except: st.markdown("🐑")
            st.markdown(f"### 🌏 **{random.randint(30_000,80_000):,} người** đang đầu tư quỹ để thực hiện **{dream_name.title()}** giống bạn!")
            st.markdown(f"Nhóm này đã đầu tư trung bình **{fmt(random.randint(8_000_000,15_000_000))}** rồi 💪")
            st.markdown(f"Còn bạn đã có **{fmt(mem['total_saved'])}** – mỗi ngày một ít, Cừu Cần Cù tin bạn sẽ đến đích! 🐑")
            st.markdown("")
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
# Ô NHẬP TIN NHẮN
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
        with st.chat_message("assistant", avatar="🐑"):
            st.markdown(last["content"])
            if last.get("savings"): st.success(f"💡 **Gợi ý đầu tư:** {last['savings']}")
            elif last.get("nudge"): st.info(f"💡 {last['nudge']}")
