import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"

STATUS_BADGES = {
    "processing": "🟡 Processing",
    "completed": "🟢 Completed",
    "failed": "🔴 Failed",
}

LANGUAGE_OPTIONS = {
    "Auto-detect": "",
    "English": "en",
    "Arabic": "ar",
}


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def render_upload_page() -> None:
    """Render the audio upload and transcription trigger page."""
    st.header("🎙️ Upload & Transcribe")
    st.write("Upload an audio file to transcribe it locally using Whisper.")

    uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])

    language_label = st.selectbox("Audio language", list(LANGUAGE_OPTIONS.keys()))

    if uploaded_file is None:
        return

    st.audio(uploaded_file)

    if st.button("Transcribe", type="primary"):
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        data = {"language": LANGUAGE_OPTIONS[language_label]}

        try:
            with st.spinner("Uploading file..."):
                response = requests.post(
                    f"{API_BASE_URL}/memos/upload",
                    headers=_auth_headers(),
                    files=files,
                    data=data,
                    timeout=60,
                )
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not connect to the API: {exc}")
            return

        if response.status_code == 202:
            st.info(
                "File uploaded successfully! Processing locally via Whisper... "
                "Visit the History page and click Refresh to check progress."
            )
        else:
            st.error(f"Upload failed: {response.text}")


def render_history_page() -> None:
    """Render the list of the current user's voice memos and their status."""
    st.header("📜 History")

    if st.button("🔄 Refresh"):
        st.rerun()

    try:
        response = requests.get(
            f"{API_BASE_URL}/memos/history",
            headers=_auth_headers(),
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not connect to the API: {exc}")
        return

    if response.status_code != 200:
        st.error("Failed to load history.")
        return

    memos = response.json()

    if not memos:
        st.info("You haven't uploaded any voice memos yet.")
        return

    for memo in memos:
        badge = STATUS_BADGES.get(memo["status"], memo["status"])

        with st.expander(f"{memo['filename']}  —  {badge}"):
            st.caption(f"Uploaded: {memo['created_at']}")

            if memo["status"] == "completed" and memo["transcription"]:
                st.write("**Transcription:**")
                st.write(memo["transcription"])
            elif memo["status"] == "processing":
                st.write("Transcription is still processing — click Refresh to check again.")
            elif memo["status"] == "failed":
                st.write("Transcription failed for this memo.")
