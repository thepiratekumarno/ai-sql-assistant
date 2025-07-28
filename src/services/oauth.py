import streamlit as st
import requests
from src.services.auth import set_auth_token
import extra_streamlit_components as stx

def handle_oauth_callback():
    cookie_manager = stx.CookieManager()
    query_params = st.experimental_get_query_params()
    
    # Handle Google OAuth callback
    if st.session_state.oauth_provider == "google":
        code = query_params.get("code", [None])[0]
        if not code:
            st.error("Missing authorization code")
            return
            
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": st.secrets["google"]["client_id"],
            "client_secret": st.secrets["google"]["client_secret"],
            "redirect_uri": st.secrets["google"]["redirect_uri"],
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if "access_token" not in token_json:
            st.error(f"Token exchange failed: {token_json}")
            return
        
        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        st.session_state.user_info = {
            "email": userinfo["email"],
            "name": userinfo.get("name", userinfo["email"]),
            "provider": "google"
        }
        set_auth_token(token_json["access_token"])
    
    # Handle GitHub OAuth callback
    elif st.session_state.oauth_provider == "github":
        code = query_params.get("code", [None])[0]
        if not code:
            st.error("Missing authorization code")
            return
            
        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            "code": code,
            "client_id": st.secrets["github"]["client_id"],
            "client_secret": st.secrets["github"]["client_secret"],
            "redirect_uri": st.secrets["github"]["redirect_uri"],
        }
        headers = {"Accept": "application/json"}
        token_response = requests.post(token_url, data=token_data, headers=headers)
        token_json = token_response.json()
        
        if "access_token" not in token_json:
            st.error(f"Token exchange failed: {token_json}")
            return
        
        # Get user info
        userinfo_url = "https://api.github.com/user"
        headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        # Get email (requires additional request)
        email_url = "https://api.github.com/user/emails"
        email_response = requests.get(email_url, headers=headers)
        emails = email_response.json()
        primary_email = next((e["email"] for e in emails if e["primary"]), None)
        
        st.session_state.user_info = {
            "email": primary_email or userinfo["login"] + "@github.com",
            "name": userinfo.get("name", userinfo["login"]),
            "provider": "github"
        }
        set_auth_token(token_json["access_token"])
    
    # Clear OAuth provider from session
    del st.session_state.oauth_provider
    st.experimental_set_query_params()
    st.experimental_rerun()
