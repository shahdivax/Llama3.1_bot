import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

models = ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"]

class ChatBot:
    def __init__(self, model="llama-3.1-8b-instant", system_message="You are a helpful assistant."):
        self.model = model
        self.system_message = system_message
        self.context = []
        self.client = Groq()
        self.reset_context()

    def chat(self, message):
        self.context.append({"role": "user", "content": message})
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.context,
            temperature=1,
            max_tokens=8000,
            top_p=1,
            stream=True,
            stop=None,
        )
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
            yield response
        self.context.append({"role": "assistant", "content": response})

    def reset_context(self):
        self.context = [{"role": "system", "content": self.system_message}]

    def set_model(self, model):
        self.model = model

    def set_system_message(self, system_message):
        self.system_message = system_message
        self.reset_context()

# Custom CSS for better UI
st.markdown("""
<style>
    .stTextInput>div>div>input {
        background-color: var(--input-bg);
        color: var(--text-color);
    }
    .stTextArea textarea {
        background-color: var(--input-bg);
        color: var(--text-color);
    }
    .stSelectbox>div>div>div {
        background-color: var(--input-bg);
        color: var(--text-color);
    }
    .stChatMessage {
        background-color: var(--message-bg);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    /* Custom color variables */
    :root {
        --primary-color: #4CAF50;
        --secondary-color: #FFA500;
        --text-color: #333;
        --bg-color: #f0f0f0;
        --input-bg: #ffffff;
        --message-bg: #e6e6e6;
    }
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #45a049;
            --secondary-color: #FFD700;
            --text-color: #f0f0f0;
            --bg-color: #2b2b2b;
            --input-bg: #3a3a3a;
            --message-bg: #3a3a3a;
        }
    }
    body {
        color: var(--text-color);
        background-color: var(--bg-color);
    }
</style>
""", unsafe_allow_html=True)

# Streamlit app
st.title("🤖 AI Chatbot")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")

    # Model selection
    selected_model = st.selectbox("Choose a model", models)

    # System message input
    default_system_message = "You are a helpful assistant."
    system_message = st.text_area("System Message", value=default_system_message, height=100)

    # Apply settings button
    if st.button("Apply Settings", key="apply_settings"):
        st.session_state.chatbot = ChatBot(selected_model, system_message)
        st.success("Settings applied successfully!")

    # Reset conversation button
    if st.button("Reset Conversation", key="reset_conversation"):
        st.session_state.conversation = []
        st.session_state.chatbot.reset_context()
        st.success("Conversation reset successfully!")
        st.experimental_rerun()

# Initialize the chatbot
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = ChatBot(selected_model, system_message)

# Session state to store the conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Function to update the conversation history
def update_conversation(role, content):
    st.session_state.conversation.append({"role": role, "content": content})

# Render the conversation history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to conversation
    update_conversation("user", user_input)

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get the chat response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in st.session_state.chatbot.chat(user_input):
            full_response = chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Add assistant response to conversation
    update_conversation("assistant", full_response)

# Display a welcome message if the conversation is empty
if not st.session_state.conversation:
    st.info("👋 Welcome! Type a message to start chatting with the AI.")
