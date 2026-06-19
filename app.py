import streamlit as st
from groq import Groq

client = Groq(
api_key=st.secrets["GROQ_API_KEY"]
)

st.title("🐑 Cừu Cần Cù")

prompt = st.chat_input("Hãy trò chuyện với Cừu...")

if prompt:

```
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role":"system",
            "content":"Bạn là Cừu Cần Cù, người bạn đồng hành tài chính."
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
)

st.write(response.choices[0].message.content)
```
