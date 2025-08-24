import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Import our custom modules
from services.perplexity_service import PerplexityService
from services.data_service import DataService
from models.api_models import PerplexityRequest, PerplexityMessage
from utils.auth import authenticate_user
from pages import prompt_page, custom_page, statistics_page, responses_page

# Configure Streamlit page
st.set_page_config(
    page_title="Perplexity API Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize services with caching"""
    data_service = DataService()
    perplexity_service = PerplexityService()
    return data_service, perplexity_service

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Saved Prompts"
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate_user()
        return
    
    # Initialize services
    data_service, perplexity_service = init_services()
    
    # Store services in session state for access across pages
    st.session_state.data_service = data_service
    st.session_state.perplexity_service = perplexity_service
    
    # Sidebar navigation
    st.sidebar.title("🤖 Perplexity API Dashboard")
    st.sidebar.markdown(f"**Welcome, {st.session_state.username}!**")
    
    # Navigation
    pages = {
        "📝 Saved Prompts": prompt_page,
        "✍️ Custom Prompt": custom_page,
        "📊 API Statistics": statistics_page,
        "📋 Saved Responses": responses_page
    }
    
    selected_page = st.sidebar.selectbox(
        "Navigate to:",
        list(pages.keys()),
        index=list(pages.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages else 0
    )
    
    # Update current page
    st.session_state.current_page = selected_page
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    
    # API Status indicator
    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Status")
    
    # Test API connection
    if st.sidebar.button("Test Connection"):
        with st.spinner("Testing API connection..."):
            try:
                test_response = perplexity_service.test_connection()
                if test_response:
                    st.sidebar.success("✅ API Connected")
                else:
                    st.sidebar.error("❌ API Connection Failed")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    
    # Usage statistics in sidebar
    stats = data_service.get_usage_statistics()
    st.sidebar.markdown("### Quick Stats")
    st.sidebar.metric("Total Requests", stats.get('total_requests', 0))
    st.sidebar.metric("Total Tokens", stats.get('total_tokens', 0))
    st.sidebar.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
    
    # Render selected page
    try:
        pages[selected_page].render()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
