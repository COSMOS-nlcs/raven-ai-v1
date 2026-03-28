import streamlit as st
import google.generativeai as genai
import json
from google.api_core.exceptions import ResourceExhausted

# ================= CONFIG =================
apikey = st.secrets['API_KEY']
genai.configure(api_key=apikey)

generation_config = {
    "temperature": 0.4,
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 300,
}

model = genai.GenerativeModel(
    model_name="gemini-flash-lite-latest",
    generation_config=generation_config,
)

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# ================= UI =================
st.title("Larry AI")
st.text("Built By COSENTIAL: COSMOS AI DIVISION")

def right_aligned_message(msg):
    st.markdown(
        f'<div style="text-align: right; padding:10px;">{msg}</div>',
        unsafe_allow_html=True
    )

# ================= AI =================
def generate_response(prompt):
    try:
        system_prompt = f"""
Your name is Larry AI

NORMAL:
- Reply normally in plain text.

SPECIAL CASE (book recommendation):
- If user asks for a book, respond ONLY in JSON:
{{
  "type": "book",
  "title": "...",
  "author": "...",
  "description": "...",
  "image": "IMAGE_URL"
}}

User: {prompt}
"""

        response = st.session_state.chat.send_message(system_prompt)
        text = response.text.strip()

        # Try parse JSON
        try:
            data = json.loads(text)
            return data
        except:
            return {"type": "text", "content": text}

    except ResourceExhausted:
        return {"type": "error", "content": "⚠️ API quota exceeded."}

    except Exception as e:
        return {"type": "error", "content": str(e)}

# ================= RENDER =================
def render_response(data):
    if data["type"] == "book":
        st.markdown("### 📚 Book Recommendation")

        left, right = st.columns(2)

        with left:
            st.markdown(f"**{data['title']}**")
            # st.image(data["image"], use_container_width=True)
            st.markdown(f"✍️ *{data['author']}*")

        with right:
            st.markdown("**About this Book**")
            st.write(data["description"])

    else:
        st.chat_message("assistant").markdown(data.get("content", ""))

# ================= HISTORY =================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        right_aligned_message(msg["parts"])
    else:
        render_response(msg["data"])

# ================= INPUT =================
prompt = st.chat_input("Ask AI")

if prompt:
    right_aligned_message(prompt)

    st.session_state.messages.append({
        "role": "user",
        "parts": prompt
    })

    placeholder = st.chat_message("assistant").empty()
    placeholder.markdown("Thinking...")

    data = generate_response(prompt)

    placeholder.empty()
    render_response(data)

    st.session_state.messages.append({
        "role": "assistant",
        "data": data
    })
