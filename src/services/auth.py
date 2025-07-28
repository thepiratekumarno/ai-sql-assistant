import streamlit as st
import extra_streamlit_components as stx
import requests
from urllib.parse import urlencode
from src.database.mongodb import get_user_credentials, delete_user_credentials
import os

# OAuth providers configuration
OAUTH_PROVIDERS = {
    "google": {
        "client_id": "614110627327-9ap4vkf06d0moqt83snj1lg6ivilfiu3.apps.googleusercontent.com",
        "client_secret": "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",
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v1/userinfo",
        "scope": "openid email profile",
        "redirect_uri": "https://ai-sql-assistant.streamlit.app/oauth_callback"  # Update with your actual deployed URL
    },
    "github": {
        "client_id": "Ov23li2L2zUtFxmsZHkA",
        "client_secret": "2ce9d66ec5ec4b0b0009f8167e576b25276c67c0",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scope": "user:email",
        "redirect_uri": "https://ai-sql-assistant.streamlit.app/oauth_callback"  # Update with your actual deployed URL
    }
}

def get_cookie_manager():
    return stx.CookieManager()

def get_auth_token():
    cookie_manager = get_cookie_manager()
    return cookie_manager.get("auth_token")

def set_auth_token(token):
    cookie_manager = get_cookie_manager()
    cookie_manager.set("auth_token", token, expires_at=3600*24*7)  # Expires in 7 days

def clear_auth_token():
    cookie_manager = get_cookie_manager()
    cookie_manager.delete("auth_token")

def is_authenticated():
    # Check if we have user info in session state
    return "user_info" in st.session_state

def logout():
    if "user_info" in st.session_state:
        user_id = st.session_state.user_info["email"]
        delete_user_credentials(user_id)
        clear_auth_token()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    st.experimental_rerun()

def show_login_ui():
    st.title("🔒 Login to SQL Assistant")
    
    # Google Login
    google_params = {
        "client_id": OAUTH_PROVIDERS["google"]["client_id"],
        "redirect_uri": OAUTH_PROVIDERS["google"]["redirect_uri"],
        "response_type": "code",
        "scope": OAUTH_PROVIDERS["google"]["scope"],
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = f"{OAUTH_PROVIDERS['google']['authorize_url']}?{urlencode(google_params)}"
    
    if st.button("Sign in with Google", key="google_login"):
        st.session_state.oauth_provider = "google"
        st.write(f"Please [sign in with Google]({google_auth_url})")
    
    # GitHub Login
    github_params = {
        "client_id": OAUTH_PROVIDERS["github"]["client_id"],
        "redirect_uri": OAUTH_PROVIDERS["github"]["redirect_uri"],
        "scope": OAUTH_PROVIDERS["github"]["scope"],
    }
    github_auth_url = f"{OAUTH_PROVIDERS['github']['authorize_url']}?{urlencode(github_params)}"
    
    if st.button("Sign in with GitHub", key="github_login"):
        st.session_state.oauth_provider = "github"
        st.write(f"Please [sign in with GitHub]({github_auth_url})")
    
    # Mock login for development
    if os.getenv("ENV") == "development":
        st.divider()
        if st.button("Developer Login"):
            st.session_state.user_info = {
                "email": "dev@example.com",
                "name": "Developer",
                "provider": "dev"
            }
            set_auth_token("dev_token")
            st.experimental_rerun()
