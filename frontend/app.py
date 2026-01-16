import streamlit as st
import requests
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Employee Handbook Bot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4CAF50;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "upload_status" not in st.session_state:
    st.session_state.upload_status = None

def get_api_url():
    """Get the current API URL from session state or default"""
    return st.session_state.get("api_url", API_BASE_URL)

def check_api_connection():
    """Check if API is available"""
    try:
        api_url = get_api_url()
        response = requests.get(f"{api_url}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_handbook(file):
    """Upload handbook PDF to API"""
    try:
        api_url = get_api_url()
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = requests.post(
            f"{api_url}/upload-handbook",
            files=files,
            timeout=30
        )
        if response.status_code == 200:
            return True, "Handbook uploaded successfully! Processing in background..."
        else:
            return False, f"Error: {response.json().get('detail', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def query_handbook(question: str, limit: int = 5, timeout: int = 120):
    """Query the handbook"""
    try:
        api_url = get_api_url()
        
        # First check if API is reachable
        try:
            health_check = requests.get(f"{api_url}/", timeout=3)
            if health_check.status_code != 200:
                return False, f"API server is not responding correctly. Status: {health_check.status_code}"
        except requests.exceptions.RequestException:
            return False, f"Cannot connect to API server at {api_url}. Make sure the server is running."
        
        payload = {"question": question}
        params = {"limit": limit}
        response = requests.post(
            f"{api_url}/chat",
            json=payload,
            params=params,
            timeout=timeout
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = response.text
            return False, error_detail
    except requests.exceptions.Timeout:
        return False, f"Request timed out after {timeout} seconds. The query may be too complex or the server is slow. Try:\n- Simplifying your question\n- Reducing the result limit\n- Checking server logs for errors"
    except requests.exceptions.ConnectionError:
        return False, f"Connection error: Cannot reach API server at {get_api_url()}. Make sure:\n- The API server is running\n- The URL is correct\n- There are no firewall issues"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)}"

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API URL input
    if "api_url" not in st.session_state:
        st.session_state.api_url = API_BASE_URL
    
    api_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_url,
        help="Enter the base URL of your FastAPI server"
    )
    if api_url != st.session_state.api_url:
        st.session_state.api_url = api_url
        API_BASE_URL = api_url
    
    st.divider()
    
    # Connection status
    st.subheader("🔌 Connection Status")
    connection_status = check_api_connection()
    if connection_status:
        st.success("✅ Connected to API")
    else:
        st.error("❌ Cannot connect to API")
        st.warning(f"**API URL**: `{get_api_url()}`")
        st.info("**To fix:**\n1. Start the API server: `uvicorn main:app --reload`\n2. Verify the URL is correct\n3. Check if the server is running on the correct port")
    
    st.divider()
    
    # Upload handbook section
    st.subheader("📤 Upload Handbook")
    uploaded_file = st.file_uploader(
        "Upload PDF Handbook",
        type=["pdf"],
        help="Upload your employee handbook PDF file"
    )
    
    if uploaded_file is not None:
        if st.button("Upload & Process", type="primary"):
            with st.spinner("Uploading handbook..."):
                success, message = upload_handbook(uploaded_file)
                if success:
                    st.session_state.upload_status = "success"
                    st.success(message)
                    st.info("⏳ Processing may take a few minutes. You can start asking questions once processing is complete.")
                else:
                    st.session_state.upload_status = "error"
                    st.error(message)
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Chat Settings")
    result_limit = st.slider(
        "Result Limit",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of relevant chunks to retrieve for answering"
    )
    
    timeout_seconds = st.slider(
        "Request Timeout (seconds)",
        min_value=30,
        max_value=300,
        value=120,
        step=30,
        help="Maximum time to wait for a response (increase if queries are slow)"
    )

# Main content area
st.markdown('<h1 class="main-header">📚 Employee Handbook Bot</h1>', unsafe_allow_html=True)
st.markdown("---")

# Chat interface
st.subheader("💬 Chat with Handbook")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the employee handbook..."):
    # Check API connection before processing
    if not check_api_connection():
        st.error("⚠️ **API Server Not Connected**")
        st.warning(f"Cannot connect to API at `{get_api_url()}`. Please:\n1. Start the API server\n2. Verify the URL in the sidebar\n3. Check the connection status indicator")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner(f"Thinking... (timeout: {timeout_seconds}s)"):
            success, response = query_handbook(prompt, result_limit, timeout_seconds)
            
            if success:
                # Format response (it's a list of strings from clean_output)
                if isinstance(response, list):
                    if response:
                        # Join list items with proper formatting
                        answer = "\n\n".join(response) if len(response) > 1 else response[0]
                    else:
                        answer = "I couldn't find a specific answer in the handbook. Please try rephrasing your question."
                elif isinstance(response, dict):
                    answer = response.get("answer", str(response))
                else:
                    answer = str(response) if response else "No answer available."
                
                # Display answer with better formatting
                st.markdown(answer)
                
                # Add bot response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = f"❌ **Error**: {response}"
                st.error(error_msg)
                
                # Provide specific troubleshooting based on error type
                if "timed out" in response.lower():
                    st.warning("**Timeout Troubleshooting:**")
                    st.markdown("""
                    - The query may be taking too long to process
                    - Try increasing the timeout in settings (sidebar)
                    - Simplify your question
                    - Reduce the result limit
                    - Check if the LLM service is responding
                    """)
                elif "cannot connect" in response.lower() or "connection error" in response.lower():
                    st.warning("**Connection Troubleshooting:**")
                    st.markdown(f"""
                    - Verify the API server is running at: `{get_api_url()}`
                    - Check the API URL in the sidebar
                    - Make sure the server started without errors
                    - Try accessing the API directly in your browser: `{get_api_url()}/`
                    """)
                else:
                    st.info("💡 **General Tips**:\n- Make sure the API server is running\n- Check if the handbook has been uploaded and processed\n- Verify your connection settings\n- Check server logs for detailed error messages")
                
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer with instructions
st.markdown("---")
with st.expander("ℹ️ How to use"):
    st.markdown("""
    ### Getting Started:
    1. **Upload Handbook**: Use the sidebar to upload your employee handbook PDF file
    2. **Wait for Processing**: The handbook will be processed in the background (this may take a few minutes)
    3. **Ask Questions**: Once processing is complete, you can ask questions about the handbook
    
    ### Example Questions:
    - "What is the leave policy?"
    - "How do I request time off?"
    - "What are the benefits for full-time employees?"
    - "What is the code of conduct?"
    - "What are the remote work policies?"
    
    ### Tips:
    - Be specific in your questions for better results
    - The bot only answers based on the uploaded handbook content
    - Adjust the result limit in the sidebar to get more or fewer relevant chunks
    """)

# Clear chat button
if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()