import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from session import persist_session

API_BASE_URL = "http://localhost:8000"


def render_auth_forms(cookies: EncryptedCookieManager) -> None:
    """Render the Login and Register tabs for unauthenticated users."""
    st.title("🎙️ VoiceMemo AI")
    st.caption("Sign in or create an account to start transcribing your voice memos.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        _render_login_form(cookies)

    with register_tab:
        _render_register_form()


def _render_login_form(cookies: EncryptedCookieManager) -> None:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

    if not submitted:
        return

    if not username or not password:
        st.error("Please enter both a username and a password.")
        return

    try:
        token_response = requests.post(
            f"{API_BASE_URL}/auth/token",
            data={"username": username, "password": password},
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not connect to the API: {exc}")
        return

    if token_response.status_code != 200:
        st.error("Invalid username or password.")
        return

    access_token = token_response.json()["access_token"]

    try:
        profile_response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not connect to the API: {exc}")
        return

    if profile_response.status_code != 200:
        st.error("Logged in, but failed to fetch user profile.")
        return

    st.session_state.token = access_token
    st.session_state.user = profile_response.json()
    persist_session(cookies, access_token)
    st.rerun()


def _render_register_form() -> None:
    with st.form("register_form"):
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        submitted = st.form_submit_button("Register", type="primary", use_container_width=True)

    if not submitted:
        return

    if not username or not email or not password:
        st.error("Please fill in all fields.")
        return

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not connect to the API: {exc}")
        return

    if response.status_code == 201:
        st.success("Registration successful! Please switch to the Login tab to sign in.")
    else:
        try:
            detail = response.json().get("detail", "Registration failed.")
        except ValueError:
            detail = "Registration failed."
        st.error(detail)
