import streamlit as st
from groq import Groq

client = Groq(
api_key=st.secrets["GROQ_API_KEY"]
)

st.set_page_config(
page_title="🐑 Cừu Cần Cù",
layout="wide"
)

st.title("🐑 Cừu Cần Cù")

if "messages" not in st.session_state:
st.session_state.messages = []

for msg in st.session_state.messages:
with st.chat_message(msg["role"]):
st.write(msg["content"])

prompt = st.chat_input("Hãy trò chuyện với Cừu...")

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

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": """
```

Bạn là Cừu Cần Cù.
Người bạn đồng hành tài chính.
Trả lời thân thiện, ngắn gọn, dễ hiểu.
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
