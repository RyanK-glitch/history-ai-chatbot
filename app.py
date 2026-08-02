import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="World History Vision Bot", page_icon="📜")
st.title("📜 World History Research Assistant")
st.caption("Now with Image Analysis! Specialized strictly in World, Korean, and Chinese history.")

# 2. Secure API Connection
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_API_KEY = st.sidebar.text_input("Enter Groq API Key:", type="password")

if not GROQ_API_KEY:
    st.info("Please add your Groq API key to continue.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 3. System Prompt Constraints
SPECIALIZED_TOPIC = "World History, specializing deeply in Korean and Chinese history."
SYSTEM_INSTRUCTION = f"""
You are a specialized AI history professor. Your core expertise is {SPECIALIZED_TOPIC}.
1. TOPIC RESTRICTION: You must only answer questions or analyze images directly related to World History. 
2. REFUSAL RULE: For any off-topic inputs (programming code, recipes, personal life, or non-historical images), say: 'I apologize, but I am programmed to only assist with questions regarding World History.'
3. MULTILINGUAL: Match the language of the user (English, සිංහල, 中文, 한국어, etc.).
"""

# Helper function to convert uploaded images to base64 string format
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode("utf-8")

# 4. Image Upload Field in the Sidebar Layout
st.sidebar.header("📸 Historical Photo Analyzer")
uploaded_image = st.sidebar.file_uploader("Upload a historical photo, map, or artifact...", type=["jpg", "jpeg", "png"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle User Prompts
if user_input := st.chat_input("Ask a history question or describe your uploaded photo..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Initialize messages payload with strict instructions
    messages_for_api = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    
    # Check if user added an image to analyze
    if uploaded_image:
        base64_image = encode_image(uploaded_image)
        # Format a specialized multimodal message payload block
        user_content = [
            {"type": "text", "text": user_input},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
        ]
        messages_for_api.append({"role": "user", "content": user_content})
    else:
        # Standard text loop fallback if no image is present
        for m in st.session_state.messages:
            messages_for_api.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Reviewing historical archives..."):
            # Switched to llama-3.2-11b-vision-preview to process images over API
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=messages_for_api,
                max_tokens=250 # 👈 Keeps responses short, crisp and punchy
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
