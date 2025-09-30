import streamlit as st
from openai import OpenAI
import os

# Page configuration
st.set_page_config(
    page_title="Perplexity AI Chat",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Perplexity AI Chat Interface")
st.markdown("Chat with Perplexity's Sonar models for up-to-date, web-grounded responses")

# Sidebar for API key and model selection
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Perplexity API Key",
        type="password",
        help="Enter your Perplexity API key. Get one at https://perplexity.ai/account/api"
    )
    
    # Model selection
    model = st.selectbox(
        "Select Model",
        [
            "sonar",
            "sonar-pro",
            "sonar-reasoning"
        ],
        help="Choose the Perplexity model to use"
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Controls randomness in responses"
    )
    
    # Max tokens
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=100,
        max_value=4096,
        value=1024,
        step=100,
        help="Maximum length of response"
    )
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    **About Perplexity API:**
    - Sonar models provide real-time, web-grounded responses
    - Get your API key from the [Perplexity Portal](https://perplexity.ai/account/api)
    - [Documentation](https://docs.perplexity.ai/)
    """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Check if API key is provided
    if not api_key:
        st.error("⚠️ Please enter your Perplexity API key in the sidebar")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Initialize Perplexity client
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
            
            # Create streaming response
            with st.spinner("Thinking..."):
                stream = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                # Stream the response
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Make sure your API key is valid and you have sufficient credits")

# Display info about message count
if st.session_state.messages:
    st.sidebar.info(f"💬 Messages in conversation: {len(st.session_state.messages)}")
