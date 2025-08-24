import streamlit as st
import hashlib
import json
from pathlib import Path

def load_user_credentials():
    """Load user credentials from secrets or local file"""
    try:
        # Try to get from Streamlit secrets first
        if hasattr(st, 'secrets') and 'auth' in st.secrets:
            return {
                'username': st.secrets.auth.username,
                'password': st.secrets.auth.password_hash
            }
        
        # Fallback to local file
        creds_file = Path('data/credentials.json')
        if creds_file.exists():
            with open(creds_file, 'r') as f:
                return json.load(f)
        
        # Default credentials if none exist
        return create_default_credentials()
    except Exception as e:
        st.error(f"Error loading credentials: {e}")
        return create_default_credentials()

def create_default_credentials():
    """Create default credentials file"""
    default_creds = {
        'username': 'admin',
        'password': hash_password('admin123')  # Default password
    }
    
    # Save to local file
    Path('data').mkdir(exist_ok=True)
    with open('data/credentials.json', 'w') as f:
        json.dump(default_creds, f, indent=2)
    
    st.info("Default credentials created: username=admin, password=admin123")
    return default_creds

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username, password):
    """Verify user credentials"""
    creds = load_user_credentials()
    return (username == creds.get('username') and 
            hash_password(password) == creds.get('password'))

def authenticate_user():
    """Streamlit authentication interface"""
    st.title("🔐 Login to Perplexity API Dashboard")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### Enter your credentials")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if username and password:
                    if verify_credentials(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.warning("Please enter both username and password.")
        
        st.info("💡 Default credentials: admin / admin123")
        
        with st.expander("🔧 Setup Instructions"):
            st.markdown("""
            **For production use, set up Streamlit secrets:**
            
            1. Create `.streamlit/secrets.toml` file:
            ```
            [auth]
            username = "your_username"
            password_hash = "your_hashed_password"
            
            [perplexity]
            api_key = "your_perplexity_api_key"
            base_url = "https://api.perplexity.ai"
            ```
            
            2. Or use environment variables
            """)
