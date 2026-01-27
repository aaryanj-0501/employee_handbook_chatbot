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
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "upload_status" not in st.session_state:
    st.session_state.upload_status = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "login_error" not in st.session_state:
    st.session_state.login_error = None

def get_api_url():
    """Get the current API URL from session state or default"""
    return st.session_state.get("api_url", API_BASE_URL)

def get_auth_headers():
    """Get authorization headers with token if available"""
    headers = {}
    if st.session_state.get("access_token"):
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    return headers

def check_api_connection():
    """Check if API is available"""
    try:
        api_url = get_api_url()
        response = requests.get(f"{api_url}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def login(username: str, password: str):
    """Login user and store token"""
    try:
        api_url = get_api_url()
        # OAuth2PasswordRequestForm expects form data
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(
            f"{api_url}/login",
            data=data,
            timeout=10
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.access_token = token_data.get("access_token")
            st.session_state.is_authenticated = True
            st.session_state.login_error = None
            return True, "Login successful!"
        else:
            error_detail = response.json().get('detail', 'Login failed')
            st.session_state.login_error = error_detail
            return False, error_detail
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        st.session_state.login_error = error_msg
        return False, error_msg

def logout():
    """Logout user and clear session"""
    st.session_state.access_token = None
    st.session_state.is_authenticated = False
    st.session_state.login_error = None
    st.session_state.messages = []
    st.session_state.upload_status = None

def upload_handbook(file):
    """Upload handbook PDF to API"""
    try:
        api_url = get_api_url()
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        headers = get_auth_headers()
        response = requests.post(
            f"{api_url}/upload-handbook",
            files=files,
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            return True, "Handbook uploaded successfully! Processing in background..."
        elif response.status_code == 401:
            # Token expired or invalid
            logout()
            return False, "Session expired. Please login again."
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
        headers = get_auth_headers()
        response = requests.post(
            f"{api_url}/chat",
            json=payload,
            params=params,
            headers=headers,
            timeout=timeout
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        elif response.status_code == 401:
            # Token expired or invalid
            logout()
            return False, "Session expired. Please login again."
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

# Login Modal - Show if not authenticated
if not st.session_state.is_authenticated:
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align: center; color: #1f77b4;">📚 Employee Handbook Bot</h1>', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; margin-bottom: 2rem;">Login Required</h2>', unsafe_allow_html=True)
        
        # Display login error if any
        if st.session_state.login_error:
            st.error(f"❌ {st.session_state.login_error}")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit_button:
                if username and password:
                    with st.spinner("Logging in..."):
                        success, message = login(username, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stop execution here - don't show main page
    st.stop()

# Main application - only shown after authentication
# Sidebar for configuration
with st.sidebar:
    # Logout button at the top
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()
    
    st.divider()
    st.header("⚙️ Configuration")
    
    # Connection status
    st.subheader("🔌 Connection Status")
    connection_status = check_api_connection()
    if connection_status:
        st.success("✅ Connected to API")
    else:
        st.error("❌ Cannot connect to API")
        st.info("**To fix:**\n1. Verify the API server is running\n2. Check server configuration\n3. Contact administrator if issue persists")
    
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
                    # If session expired, rerun to show login page
                    if not st.session_state.is_authenticated:
                        st.warning("Please login again.")
                        st.rerun()
    
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
        st.warning("Cannot connect to API server. Please check the connection status in the sidebar or contact administrator.")
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
                
                # If session expired, rerun to show login page
                if not st.session_state.is_authenticated:
                    st.warning("Please login again.")
                    st.rerun()
                
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
                    st.markdown("""
                    - Verify the API server is running
                    - Check the connection status in the sidebar
                    - Make sure the server started without errors
                    - Contact administrator if issue persists
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