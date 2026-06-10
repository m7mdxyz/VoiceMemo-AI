import streamlit as st

from components.auth_forms import render_auth_forms
from components.memo_handlers import render_history_page, render_upload_page
from session import clear_session, get_cookie_manager, restore_session

st.set_page_config(
    page_title="VoiceMemo AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark, modern theme styling + hide Streamlit's default multipage nav
# (we render our own controlled sidebar navigation below).
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

    section[data-testid="stSidebar"] {
        background-color: #161a23;
        border-right: 1px solid #262730;
    }

    div[data-testid="stExpander"] {
        background-color: #161a23;
        border: 1px solid #262730;
        border-radius: 8px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    cookies = get_cookie_manager()
    if not cookies.ready():
        st.stop()

    restore_session(cookies)

    if not st.session_state.token:
        render_auth_forms(cookies)
        return

    user = st.session_state.user

    with st.sidebar:
        st.title("🎙️ VoiceMemo AI")
        st.write(f"Signed in as **{user['username']}**")

        st.divider()

        page = st.radio(
            "Navigation",
            ["🎙️ Upload & Transcribe", "📜 History"],
            label_visibility="collapsed",
        )

        if user.get("is_admin"):
            st.page_link("pages/admin.py", label="🛡️ Admin Panel")

        st.divider()

        if st.button("Logout", use_container_width=True):
            clear_session(cookies)
            st.rerun()

    if page == "🎙️ Upload & Transcribe":
        render_upload_page()
    elif page == "📜 History":
        render_history_page()


if __name__ == "__main__":
    main()
