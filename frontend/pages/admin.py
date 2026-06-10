import requests
import streamlit as st

from session import API_BASE_URL, get_cookie_manager, restore_session

st.set_page_config(page_title="Admin Panel - VoiceMemo AI", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }

    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

cookies = get_cookie_manager()
if not cookies.ready():
    st.stop()

restore_session(cookies)

user = st.session_state.get("user")
token = st.session_state.get("token")

if not user or not user.get("is_admin") or not token:
    st.error("Access Denied: You must be an admin to view this page.")
    st.stop()


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


st.title("🛡️ Admin Panel")

with st.sidebar:
    st.title("🎙️ VoiceMemo AI")
    st.write(f"Signed in as **{user['username']}**")
    st.page_link("app.py", label="⬅️ Back to App")

st.subheader("Registered Users")

try:
    users_response = requests.get(
        f"{API_BASE_URL}/admin/users", headers=_auth_headers(), timeout=10
    )
except requests.exceptions.RequestException as exc:
    st.error(f"Could not connect to the API: {exc}")
    st.stop()

if users_response.status_code == 200:
    users = users_response.json()
    if users:
        st.dataframe(users, use_container_width=True, hide_index=True)
    else:
        st.info("No users found.")
else:
    st.error("Failed to load users.")

st.subheader("All Voice Memos")

try:
    memos_response = requests.get(
        f"{API_BASE_URL}/admin/memos", headers=_auth_headers(), timeout=10
    )
except requests.exceptions.RequestException as exc:
    st.error(f"Could not connect to the API: {exc}")
    st.stop()

if memos_response.status_code == 200:
    memos = memos_response.json()
    if memos:
        st.dataframe(memos, use_container_width=True, hide_index=True)
    else:
        st.info("No voice memos found.")
else:
    st.error("Failed to load voice memos.")
