import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

API_BASE_URL = "http://localhost:8000"

# Used to encrypt the cookie that stores the JWT in the browser.
# Change this to a long random value for any real deployment.
COOKIE_PASSWORD = "voicememo-ai-cookie-secret-change-me"
COOKIE_NAME = "access_token"


def get_cookie_manager() -> EncryptedCookieManager:
    """Return the cookie manager used to persist the JWT across page reloads."""
    return EncryptedCookieManager(prefix="voicememo/", password=COOKIE_PASSWORD)


def init_session_state() -> None:
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None


def restore_session(cookies: EncryptedCookieManager) -> None:
    """Restore token/user into session_state from a persisted cookie.

    A browser refresh wipes Streamlit's in-memory session_state, so the JWT
    is also stored in an encrypted cookie and re-validated against the API
    on every fresh session.
    """
    init_session_state()

    if st.session_state.token:
        return

    token = cookies.get(COOKIE_NAME)
    if not token:
        return

    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except requests.exceptions.RequestException:
        return

    if response.status_code == 200:
        st.session_state.token = token
        st.session_state.user = response.json()


def persist_session(cookies: EncryptedCookieManager, token: str) -> None:
    """Save the JWT to a cookie so the session survives a browser refresh."""
    cookies[COOKIE_NAME] = token
    cookies.save()


def clear_session(cookies: EncryptedCookieManager) -> None:
    """Clear both the in-memory session and the persisted cookie.

    Note: this overwrites the cookie with an empty value rather than using
    `del cookies[...]`, since streamlit-cookies-manager's __delitem__ is
    broken when a `prefix` is configured (it checks the un-prefixed key
    against the prefixed cookie dict, so the deletion is silently dropped).
    """
    st.session_state.token = None
    st.session_state.user = None
    cookies[COOKIE_NAME] = ""
    cookies.save()
