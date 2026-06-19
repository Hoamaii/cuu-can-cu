import streamlit as st
from groq import Groq
import pandas as pd

client = Groq(
api_key=st.secrets["GROQ_API_KEY"]
)

# Giao diện

st.set_page_config(
page_title="🐑 Cừu Cần Cù",
layout="wide"
)

st.title("🐑 Cừu Cần Cù")

# Đọc prompt

with open("prompt.txt", "r", encoding="utf-8") as f:
SYSTEM_PROMPT = f.read()

# Đọc Excel

df = pd.read_excel("knowledge.xlsx")

# Tìm dữ liệu liên quan

def find_knowledge(question):

```
q = question.lower()

matched = []

for _, row in df.iterrows():

    row_text = " ".join(
        [str(x) for x in row.values]
    ).lower()

    score = 0

    for word in q.split():

        if word in row_text:
            score += 1

    if score > 0:
        matched.append((score, row))

matched.sort(
    key=lambda x: x[0],
    reverse=True
)

top_rows = matched[:5]

result = ""

for _, row in top_rows:
    result += str(row.to_dict())
    result += "\n\n"

return result
```

# Lưu lịch sử chat

if "messages" not in st.session_state:
st.session_state.messages = []

# Hiển thị lịch sử

for msg in st.session_state.messages:

```
with st.chat_message(msg["role"]):
    st.write(msg["content"])
```

# Ô nhập chat

prompt = st.chat_input(
"Hãy trò chuyện với Cừu..."
)

if prompt:

```
st.session_state.messages.append(
    {
        "role": "user",
        "content": prompt
    }
)

with st.chat_message("user"):
    st.write(prompt)

knowledge = find_knowledge(prompt)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"""
```

Dữ liệu TCBS:

{knowledge}

Chỉ sử dụng dữ liệu trên để trả lời.
Nếu không có dữ liệu phù hợp thì nói chưa có thông tin.
"""
},
{
"role": "user",
"content": prompt
}
]
)

```
answer = response.choices[0].message.content

st.session_state.messages.append(
    {
        "role": "assistant",
        "content": answer
    }
)

with st.chat_message("assistant"):
    st.write(answer)
```
