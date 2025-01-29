# crawlgpt/src/crawlgpt/ui/login.py
import streamlit as st
from src.crawlgpt.core.database import create_user, authenticate_user

def show_login():
    """Displays login/registration interface"""
    if 'user' in st.session_state:
        del st.session_state.user
    if 'messages' in st.session_state:
        del st.session_state.messages
        
    st.title("CrawlGPT Login 🔐")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    
    
    with tab1:
        with st.form("Login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        with st.form("Register"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            email = st.text_input("Email")
            if st.form_submit_button("Register"):
                if create_user(new_user, new_pass, email):
                    st.success("Registration successful! Please login")
                else:
                    st.error("Username already exists")