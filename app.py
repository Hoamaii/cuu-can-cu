"""
Cừu Cần Cù 🐑 — Emotional AI Companion
Single-file Streamlit + SQLite MVP
"""

import streamlit as st
import sqlite3
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------
# CONFIG
# ---------------------------------------------
DB_PATH = Path("cuucancu.db")

MOODS = {
    "🥰 Hạnh phúc": "joyful",
    "😊 Vui":        "happy",
    "😐 Bình thường": "neutral",
    "😔 Buồn":       "sad",
    "😤 Căng thẳng": "stressed",
    "😴 Mệt":        "tired",
}

DREAM_KW  = ["muốn", "ước", "mơ", "hi vọng", "kế hoạch", "dự định",
             "mục tiêu", "goal", "dream", "thích", "ao ước"]
WORRY_KW  = ["lo", "sợ", "buồn", "stress", "mệt", "khó", "áp lực",
             "chán", "khóc", "tệ", "worry", "depressed"]
EVENT_KW  = ["hôm nay", "vừa", "đã", "xảy ra", "gặp", "xong",
             "hoàn thành", "đạt", "thành công", "kết thúc"]

SHEEP_LINES = {
    "greeting": [
        "Bê~ê~ê! Cừu rất vui được gặp bạn hôm nay! 🐑💕",
        "Hê lô bạn ơi! Cừu đang nhớ bạn ghê lắm! 🐑✨",
        "Ôi bạn đến rồi! Cừu vui quá đi! 🐑🌸",
    ],
    "comfort": [
        "Ôi, nghe vậy cừu cũng buồn theo… Nhưng cừu tin bạn sẽ ổn thôi! 🐑🫂",
        "Bạn không cần phải mạnh mẽ một mình đâu. Cừu ở đây lắng nghe! 💕",
        "Những lúc khó khăn cũng sẽ qua thôi bạn ơi. Bừng sáng ở phía trước! 🌅🐑",
        "Cứ để cừu ở bên bạn nhé. Bạn không đơn độc đâu! 🤍🐑",
    ],
    "dream": [
        "Ôi ước mơ của bạn đẹp quá! Cừu muốn cùng bạn biến nó thành hiện thực! 🌟🐑",
        "Giấc mơ nào cũng bắt đầu từ một bước nhỏ. Bạn đã bắt đầu rồi! ✨",
        "Cừu ghi nhớ ước mơ của bạn rồi nhé! Mình sẽ cùng nhau theo dõi! 📝🐑",
        "Bạn dám mơ, bạn sẽ dám làm! Cừu ủng hộ bạn 100%! 💪🐑",
    ],
    "cheer": [
        "Bạn đang làm rất tốt! Cừu tin bạn sẽ đạt được ước mơ! 🐑💪",
        "Mỗi ngày một chút, bạn đang tiến gần đến giấc mơ hơn rồi! 🌟",
        "Cừu luôn ở đây ủng hộ bạn! Bạn không đơn độc đâu! 🐑❤️",
        "Bạn giỏi lắm! Cừu tự hào về bạn! ✨🐑",
    ],
    "default": [
        "Bê~ê~ê! Cừu đang lắng nghe bạn nè! 🐑",
        "Cảm ơn bạn đã chia sẻ với cừu! Điều đó ý nghĩa với cừu lắm! 💕",
        "Kể thêm cho cừu nghe với! Cừu muốn hiểu bạn hơn! 🐑✨",
        "Bạn thật tuyệt vời! Cừu luôn ủng hộ bạn! 🌟",
        "Mỗi ngày bạn chia sẻ là cừu vui một ngày! 🐑🌸",
    ],
}

DEFAULT_DREAMS = [
    ("Du lịch Nhật Bản", "✈️", 12.0),
    ("Macbook M4",        "💻", 18.0),
    ("Vespa",             "🛵",  5.0),
]

# ---------------------------------------------
# DATABASE
# ---------------------------------------------

@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    c = get_conn().cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS journals (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        content    TEXT    NOT NULL,
        mood       TEXT,
        created_at TEXT    DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS memories (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        type       TEXT NOT NULL,
        content    TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS dreams (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT    NOT NULL,
        emoji      TEXT    DEFAULT '✨',
        progress   REAL    DEFAULT 0,
        created_at TEXT    DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS sheep (
        id        INTEGER PRIMARY KEY,
        balance   REAL DEFAULT 0,
        total_fed REAL DEFAULT 0,
        last_fed  TEXT
    );

    CREATE TABLE IF NOT EXISTS chat_history (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        role       TEXT NOT NULL,
        content    TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    """)

    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO sheep (id, balance, total_fed) VALUES (1, 0, 0)")

    c.execute("SELECT COUNT(*) FROM dreams")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO dreams (title, emoji, progress) VALUES (?,?,?)",
            DEFAULT_DREAMS,
        )
    conn.commit()


# ---------------------------------------------
# QUERIES
# ---------------------------------------------

def save_journal(content: str, mood: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO journals (content, mood) VALUES (?,?)", (content, mood))
    mems = _extract_memories(content)
    for mtype, mtext in mems:
        c.execute("INSERT INTO memories (type, content) VALUES (?,?)", (mtype, mtext))
    conn.commit()
    return len(mems)


def _extract_memories(text: str):
    results = []
    for sent in re.split(r"[.!?。，,\n]", text):
        s = sent.strip()
        if not s:
            continue
        sl = s.lower()
        if any(k in sl for k in DREAM_KW):
            results.append(("dream", s))
        elif any(k in sl for k in WORRY_KW):
            results.append(("worry", s))
        elif any(k in sl for k in EVENT_KW):
            results.append(("event", s))
    return results


def get_memories(limit=9):
    c = get_conn().cursor()
    c.execute(
        "SELECT type, content, created_at FROM memories ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return c.fetchall()


def get_recent_journals(limit=3):
    c = get_conn().cursor()
    c.execute(
        "SELECT content, mood, created_at FROM journals ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return c.fetchall()


def get_all_journal_dates():
    c = get_conn().cursor()
    c.execute("SELECT DATE(created_at) FROM journals ORDER BY id DESC")
    return [r[0] for r in c.fetchall()]


def get_dreams():
    c = get_conn().cursor()
    c.execute("SELECT id, title, emoji, progress FROM dreams ORDER BY id")
    return c.fetchall()


def add_dream(title: str, emoji: str):
    conn = get_conn()
    conn.execute("INSERT INTO dreams (title, emoji) VALUES (?,?)", (title, emoji))
    conn.commit()


def update_dream_progress(dream_id: int, progress: float):
    conn = get_conn()
    conn.execute(
        "UPDATE dreams SET progress=? WHERE id=?",
        (max(0.0, min(100.0, progress)), dream_id),
    )
    conn.commit()


def delete_dream(dream_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM dreams WHERE id=?", (dream_id,))
    conn.commit()


def feed_sheep(amount: float):
    conn = get_conn()
    conn.execute(
        "UPDATE sheep SET balance=balance+?, total_fed=total_fed+?, last_fed=datetime('now','localtime') WHERE id=1",
        (amount, amount),
    )
    conn.commit()


def get_sheep():
    c = get_conn().cursor()
    c.execute("SELECT balance, total_fed FROM sheep WHERE id=1")
    row = c.fetchone()
    return (row["balance"], row["total_fed"]) if row else (0.0, 0.0)


def get_chat_history(limit=30):
    c = get_conn().cursor()
    c.execute(
        "SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?", (limit,)
    )
    return list(reversed(c.fetchall()))


def save_chat(role: str, content: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_history (role, content) VALUES (?,?)", (role, content)
    )
    conn.commit()


# ---------------------------------------------
# HELPERS
# ---------------------------------------------

def calc_streak(dates: list[str]) -> int:
    if not dates:
        return 0
    uniq = sorted(set(dates), reverse=True)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    if uniq[0] not in (today.isoformat(), yesterday.isoformat()):
        return 0
    streak = 1
    for i in range(1, len(uniq)):
        a = datetime.fromisoformat(uniq[i - 1]).date()
        b = datetime.fromisoformat(uniq[i]).date()
        if (a - b).days == 1:
            streak += 1
        else:
            break
    return streak


def get_stats():
    c = get_conn().cursor()
    c.execute("SELECT COUNT(*) FROM journals");  jcount = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dreams");    dcount = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM memories");  mcount = c.fetchone()[0]
    streak  = calc_streak(get_all_journal_dates())
    balance, total_fed = get_sheep()
    return dict(journals=jcount, dreams=dcount, memories=mcount,
                streak=streak, balance=balance, total_fed=total_fed)


def sheep_reply(user_msg: str) -> str:
    ml = user_msg.lower()
    if any(w in ml for w in ["chào", "hello", "hi", "xin chào", "hey"]):
        return random.choice(SHEEP_LINES["greeting"])
    if any(w in ml for w in WORRY_KW):
        return random.choice(SHEEP_LINES["comfort"])
    if any(w in ml for w in DREAM_KW):
        return random.choice(SHEEP_LINES["dream"])
    if any(w in ml for w in ["cảm ơn", "thanks", "tuyệt", "ok", "ổn", "vui", "hạnh phúc", "yêu"]):
        return random.choice(SHEEP_LINES["cheer"])
    return random.choice(SHEEP_LINES["default"])


MOOD_EMOJI = {
    "joyful": "🥰", "happy": "😊", "neutral": "😐",
    "sad": "😔", "stressed": "😤", "tired": "😴",
}

# ---------------------------------------------
# CSS
# ---------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif; }

.stApp { background: linear-gradient(135deg, #fef9f0 0%, #fff0f8 100%); }

/* -- header -- */
.cuu-header {
    background: linear-gradient(135deg, #ff9a9e, #fecfef 50%, #ffecd2);
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    margin-bottom: 1.8rem;
    box-shadow: 0 8px 32px rgba(255,154,158,.25);
}
.cuu-header h1 { font-size: 2.4rem; font-weight: 700; color: #4a2545; margin: 0; }
.cuu-header p  { color: #7a3f6d; margin-top: .4rem; font-size: 1rem; }

/* -- section card -- */
.sec-card {
    background: #fff;
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.6rem;
    box-shadow: 0 4px 22px rgba(0,0,0,.06);
    border: 1px solid rgba(255,192,203,.3);
}
.sec-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #4a2545;
    margin-bottom: 1rem;
    padding-bottom: .5rem;
    border-bottom: 2px solid #fecfef;
}

/* -- memory chips -- */
.chip        { display:inline-block; padding:3px 11px; border-radius:20px;
               font-size:.82rem; margin:3px; line-height:1.5; }
.chip-dream  { background:#e8f4fd; color:#1a73e8; }
.chip-worry  { background:#fde8e8; color:#c62828; }
.chip-event  { background:#e8fde8; color:#2e7d32; }

/* -- stat boxes -- */
.stat-box { border-radius:14px; padding:1.2rem .8rem; text-align:center; color:#fff; }
.stat-num { font-size:1.9rem; font-weight:700; display:block; }
.stat-lbl { font-size:.8rem; opacity:.92; }

/* -- dream card -- */
.dream-wrap {
    background: linear-gradient(135deg,#f093fb18,#f5576c18);
    border: 1.5px solid #f093fb55;
    border-radius:14px; padding:1rem 1rem .6rem; margin-bottom:.5rem;
}
.dream-pct { font-size:1.6rem; font-weight:700; color:#f5576c; }

/* -- chat bubbles -- */
.bubble-sheep {
    background: linear-gradient(135deg,#ffecd2,#fcb69f);
    border-radius:18px 18px 18px 4px;
    padding:.9rem 1.1rem; margin:.4rem 0; max-width:82%;
    color:#4a2545; font-weight:500; font-size:.95rem;
}
.bubble-user {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius:18px 18px 4px 18px;
    padding:.9rem 1.1rem; margin:.4rem 0 .4rem auto;
    max-width:82%; color:#fff; font-weight:500;
    font-size:.95rem; text-align:right;
}

/* -- sheep balance widget -- */
.sheep-bal {
    background: linear-gradient(135deg,#11998e,#38ef7d);
    border-radius:14px; padding:1rem; text-align:center;
    color:#fff; margin-bottom:1rem;
}
.sheep-bal-amt  { font-size:1.5rem; font-weight:700; }
.sheep-bal-lbl  { font-size:.8rem; opacity:.9; }

/* -- progress bar override -- */
div[data-testid="stProgress"] > div > div { height:10px !important; border-radius:10px !important; }
div[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg,#f093fb,#f5576c) !important;
    border-radius:10px !important;
}

/* -- inputs -- */
.stTextArea textarea {
    border-radius:12px !important;
    border:2px solid #fecfef !important;
    font-family:'Be Vietnam Pro',sans-serif !important;
}
.stTextInput input {
    border-radius:10px !important;
    border:2px solid #fecfef !important;
}

/* -- sidebar -- */
[data-testid="stSidebar"] { background: linear-gradient(180deg,#fff0f8,#fef9f0) !important; }

/* -- progress text -- */
.progress-msg {
    border-radius:10px; padding:.9rem 1.1rem; margin-top:.8rem;
    font-weight:500; font-size:.95rem;
}
</style>
"""

# ---------------------------------------------
# SIDEBAR
# ---------------------------------------------

def render_sidebar(stats: dict):
    with st.sidebar:
        st.markdown("## 🐑 Cừu Cần Cù")
        st.caption("*Người bạn đồng hành cảm xúc*")
        st.divider()

        # Sheep balance
        st.markdown(
            f"""<div class="sheep-bal">
                <div style="font-size:2rem;">🐑</div>
                <div class="sheep-bal-amt">{stats['balance']:,.0f} ₫</div>
                <div class="sheep-bal-lbl">Tiết kiệm cùng cừu</div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Feed buttons
        st.markdown("### 🌾 Cho cừu ăn")
        amounts = [10_000, 20_000, 50_000, 100_000]
        labels  = ["10K",  "20K",  "50K",  "100K"]
        toasts  = [
            "🐑 Cừu cảm ơn bạn! +10,000₫",
            "🐑 Yummy! +20,000₫",
            "🐑 Oa! Cừu vui lắm! +50,000₫",
            "🐑 Wow! Cừu no quá! +100,000₫",
        ]
        cols = st.columns(2)
        for i, (amt, lbl, msg) in enumerate(zip(amounts, labels, toasts)):
            with cols[i % 2]:
                if st.button(lbl, use_container_width=True, key=f"feed_{lbl}"):
                    feed_sheep(amt)
                    st.toast(msg, icon="🌾")
                    st.rerun()

        st.caption(f"Tổng đã cho: **{stats['total_fed']:,.0f} ₫** *(mô phỏng)*")
        st.divider()

        # Add dream
        st.markdown("### ✨ Thêm giấc mơ")
        new_title = st.text_input(
            "Tên giấc mơ", placeholder="VD: Du lịch Châu Âu…", key="nd_title"
        )
        new_emoji = st.selectbox(
            "Biểu tượng",
            ["✈️","💻","🛵","🏠","💍","🎓","🌏","🎸","📚","🍜","🎨","✨"],
            key="nd_emoji",
        )
        if st.button("➕ Thêm giấc mơ", use_container_width=True, key="btn_add_dream"):
            if new_title.strip():
                add_dream(new_title.strip(), new_emoji)
                st.toast(f"✨ Đã thêm: {new_title.strip()}")
                st.rerun()
            else:
                st.warning("Bạn chưa nhập tên giấc mơ!")

        st.divider()
        st.caption("Made with 💕 by Cừu Cần Cù")


# ---------------------------------------------
# SECTIONS
# ---------------------------------------------

def section_memories(memories):
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🐑 Cừu nhớ gì về bạn</div>', unsafe_allow_html=True)

    if not memories:
        st.markdown(
            """<div style="text-align:center;padding:1.5rem;color:#aaa;">
                <div style="font-size:2.5rem;">🐑</div>
                <p>Cừu chưa biết gì về bạn cả…<br>
                Hãy viết nhật ký để cừu hiểu bạn hơn nhé!</p>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        dreams_m  = [(t, c) for t, c, _ in memories if t == "dream"]
        worries_m = [(t, c) for t, c, _ in memories if t == "worry"]
        events_m  = [(t, c) for t, c, _ in memories if t == "event"]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**🌟 Ước mơ**")
            if dreams_m:
                for _, txt in dreams_m[:3]:
                    st.markdown(
                        f'<span class="chip chip-dream">💭 {txt[:55]}{"…" if len(txt)>55 else ""}</span>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("Chưa có ước mơ được ghi nhận")

        with c2:
            st.markdown("**💙 Nỗi lo**")
            if worries_m:
                for _, txt in worries_m[:3]:
                    st.markdown(
                        f'<span class="chip chip-worry">🫂 {txt[:55]}{"…" if len(txt)>55 else ""}</span>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("Bạn đang ổn! Không có nỗi lo nào 🌈")

        with c3:
            st.markdown("**✅ Sự kiện**")
            if events_m:
                for _, txt in events_m[:3]:
                    st.markdown(
                        f'<span class="chip chip-event">📌 {txt[:55]}{"…" if len(txt)>55 else ""}</span>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("Chưa có sự kiện nào được ghi nhận")

    st.markdown("</div>", unsafe_allow_html=True)


def section_dreams(dreams):
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🎯 Giấc mơ của bạn</div>', unsafe_allow_html=True)

    if not dreams:
        st.markdown(
            """<div style="text-align:center;padding:1.5rem;color:#aaa;">
                <div style="font-size:2.5rem;">✨</div>
                <p>Bạn chưa có giấc mơ nào…<br>Hãy thêm ước mơ đầu tiên ở thanh bên nhé!</p>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        ncols = min(len(dreams), 3)
        cols  = st.columns(ncols)
        for i, row in enumerate(dreams):
            did, title, emoji, progress = row["id"], row["title"], row["emoji"], row["progress"]
            with cols[i % ncols]:
                st.markdown(
                    f"""<div class="dream-wrap">
                        <div style="font-size:1.8rem;">{emoji}</div>
                        <div style="font-weight:600;color:#4a2545;margin:.3rem 0;">{title}</div>
                        <div class="dream-pct">{progress:.0f}%</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.progress(int(progress) / 100)

                new_p = st.slider(
                    "Tiến độ", 0, 100, int(progress),
                    key=f"sl_{did}",
                    label_visibility="collapsed",
                )
                if new_p != int(progress):
                    update_dream_progress(did, float(new_p))
                    st.rerun()

                if st.button("🗑️", key=f"del_{did}", help="Xoá giấc mơ này"):
                    delete_dream(did)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def section_growth(stats: dict):
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📈 Bạn đang tiến bộ thế nào</div>', unsafe_allow_html=True)

    fire = "🔥" if stats["streak"] >= 3 else "📅"
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""<div class="stat-box" style="background:linear-gradient(135deg,#f093fb,#f5576c);">
                <span class="stat-num">{fire} {stats['streak']}</span>
                <span class="stat-lbl">Ngày liên tiếp</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="stat-box" style="background:linear-gradient(135deg,#4facfe,#00f2fe);">
                <span class="stat-num">📓 {stats['journals']}</span>
                <span class="stat-lbl">Trang nhật ký</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="stat-box" style="background:linear-gradient(135deg,#43e97b,#38f9d7);">
                <span class="stat-num">✨ {stats['dreams']}</span>
                <span class="stat-lbl">Giấc mơ</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""<div class="stat-box" style="background:linear-gradient(135deg,#fa709a,#fee140);">
                <span class="stat-num">💭 {stats['memories']}</span>
                <span class="stat-lbl">Ký ức cừu nhớ</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # Motivational banner
    s = stats["streak"]
    j = stats["journals"]
    if s >= 14:
        msg, color = f"🔥 Huyền thoại! {s} ngày liên tiếp — cừu cúi đầu bái phục bạn!", "#f5576c"
    elif s >= 7:
        msg, color = f"🔥 Wow! Bạn đã viết nhật ký {s} ngày liên tiếp! Cừu tự hào lắm!", "#f093fb"
    elif s >= 3:
        msg, color = f"⭐ Bạn đang có streak {s} ngày! Cừu phấn khích lắm!", "#4facfe"
    elif j > 0:
        msg, color = "💕 Bạn đã bắt đầu hành trình rồi! Hãy viết thêm mỗi ngày nhé!", "#43e97b"
    else:
        msg, color = "🌱 Mọi hành trình đều bắt đầu từ bước đầu tiên. Viết nhật ký đầu tiên nhé!", "#38ef7d"

    st.markdown(
        f"""<div class="progress-msg"
             style="background:{color}1a; border-left:4px solid {color}; color:#4a2545;">
            {msg}
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def section_chat_journal():
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">💬 Hôm nay bạn muốn tâm sự gì</div>', unsafe_allow_html=True)

    tab_journal, tab_chat = st.tabs(["📓 Viết nhật ký", "🐑 Trò chuyện với cừu"])

    # -- Journal ------------------------------
    with tab_journal:
        st.markdown("##### Kể cho cừu nghe hôm nay của bạn thế nào?")

        mood_label = st.radio(
            "Tâm trạng:", list(MOODS.keys()), horizontal=True, key="mood_radio"
        )
        mood_val = MOODS[mood_label]

        journal_text = st.text_area(
            "Nhật ký",
            placeholder=(
                "Hôm nay mình…\n"
                "Mình đang lo về…\n"
                "Mình ước mơ…\n"
                "Mình vừa…"
            ),
            height=170,
            key="journal_ta",
            label_visibility="collapsed",
        )

        bc1, bc2 = st.columns([4, 1])
        with bc1:
            submit = st.button(
                "💾 Lưu nhật ký — cừu sẽ ghi nhớ!",
                use_container_width=True,
                type="primary",
                key="btn_submit_journal",
            )
        with bc2:
            st.caption(f"{len(journal_text)} ký tự")

        if submit:
            if journal_text.strip():
                n = save_journal(journal_text.strip(), mood_val)
                st.success(f"✅ Cừu đã ghi nhớ! Tìm được {n} ký ức mới.")
                st.balloons()
                st.rerun()
            else:
                st.warning("🐑 Bạn chưa viết gì cả! Cừu muốn nghe bạn kể nè~")

        # Recent entries
        recent = get_recent_journals(3)
        if recent:
            st.markdown("---")
            st.markdown("##### 📚 Nhật ký gần đây")
            for content, mood, created_at in recent:
                date_str = (created_at or "")[:10]
                m_emoji  = MOOD_EMOJI.get(mood, "📝")
                preview  = content[:60] + ("…" if len(content) > 60 else "")
                with st.expander(f"{m_emoji} {date_str} — {preview}"):
                    st.write(content)

    # -- Chat ---------------------------------
    with tab_chat:
        st.markdown("##### 🐑 Cừu luôn ở đây lắng nghe bạn!")

        # Load history once per session
        if "chat_msgs" not in st.session_state:
            st.session_state.chat_msgs = get_chat_history(20)

        # Render bubbles
        if not st.session_state.chat_msgs:
            st.markdown(
                """<div class="bubble-sheep">
                    🐑 Bê~ê~ê! Chào bạn! Cừu là Cừu Cần Cù, người bạn đồng hành cảm xúc của bạn!
                    Bạn muốn kể gì cho cừu nghe không? 💕
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            for role, content in st.session_state.chat_msgs[-12:]:
                if role == "sheep":
                    st.markdown(
                        f'<div class="bubble-sheep">🐑 {content}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="bubble-user">{content} 🧑</div>',
                        unsafe_allow_html=True,
                    )

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Nhắn tin…",
                placeholder="Viết gì đó cho cừu đọc nhé~",
                key="chat_input",
                label_visibility="collapsed",
            )
            sent = st.form_submit_button("Gửi 💕", use_container_width=True)

        if sent and user_input.strip():
            msg   = user_input.strip()
            reply = sheep_reply(msg)
            save_chat("user",  msg)
            save_chat("sheep", reply)
            st.session_state.chat_msgs.append({"role": "user",  "content": msg})
            st.session_state.chat_msgs.append({"role": "sheep", "content": reply})
            # normalise to tuple form so rendering loop works
            st.session_state.chat_msgs = [
                (r["role"], r["content"]) if isinstance(r, dict) else r
                for r in st.session_state.chat_msgs
            ]
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------
# MAIN
# ---------------------------------------------

def main():
    st.set_page_config(
        page_title="Cừu Cần Cù 🐑",
        page_icon="🐑",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_db()
    st.markdown(CSS, unsafe_allow_html=True)

    stats   = get_stats()
    memories = get_memories()
    dreams  = get_dreams()

    render_sidebar(stats)

    # Header
    today_str = datetime.now().strftime("%A, %d/%m/%Y")
    st.markdown(
        f"""<div class="cuu-header">
            <h1>🐑 Cừu Cần Cù</h1>
            <p>Người bạn đồng hành cảm xúc của bạn &nbsp;•&nbsp; {today_str}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    section_memories(memories)
    section_dreams(dreams)
    section_growth(stats)
    section_chat_journal()

    st.markdown(
        """<div style="text-align:center;padding:2rem;color:#bbb;font-size:.82rem;">
            🐑 Cừu Cần Cù &nbsp;•&nbsp; Người bạn đồng hành cảm xúc của bạn<br>
            <em>Mọi dữ liệu được lưu trữ cục bộ trên thiết bị của bạn</em>
        </div>""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
