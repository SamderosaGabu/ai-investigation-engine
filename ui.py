import os
from pathlib import Path
import time
import requests
import streamlit as st
import secrets
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "")

LOGO_PATH = Path(__file__).resolve().parent / "investigation_logo.png"
st.set_page_config(page_title="AI Investigation Engine", page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🔎", layout="wide", initial_sidebar_state="expanded")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=88)
    st.toggle("🌙 Dark mode", key="dark_mode")

dark = st.session_state.dark_mode
bg = "#0B1020" if dark else "#F5F7FB"
panel = "#151E33" if dark else "#FFFFFF"
text = "#EDF2FF" if dark else "#172033"
muted = "#A7B4CD" if dark else "#5C677B"
border = "#2B3852" if dark else "#DDE3EE"
input_bg = "#101A2D" if dark else "#F8FAFE"

st.markdown(f"""
<style>
/* Streamlit's stock header is hidden; the dashboard contains its own title. */
[data-testid="stHeader"] {{ background: {bg} !important; }}
[data-testid="stToolbar"] {{ background: {bg} !important; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stSidebar"] [data-testid="stImage"] img {{ border-radius: 12px; }}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
    background: {input_bg} !important;
    border: 1px dashed #38BDF8 !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] button,
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
    background: #FF3B49 !important;
    color: white !important;
    border: 1px solid #FF3B49 !important;
}}
[data-testid="stSidebar"] button:hover {{ filter: brightness(1.08); }}
[data-testid="stTextInput"] input {{
    color: {text} !important;
    caret-color: #38BDF8 !important;
    background: {input_bg} !important;
    border: 1px solid #38BDF8 !important;
    box-shadow: none !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: {muted} !important; opacity: 1; }}
[data-testid="stTextInput"] input:focus {{
    border-color: #7DD3FC !important;
    box-shadow: 0 0 0 1px #38BDF8 !important;
}}
[data-testid="stTextArea"] textarea::placeholder {{ color: {muted} !important; }}
[data-testid="stFormSubmitButton"] button {{
    background: #FF3B49 !important;
    border: 0 !important;
    color: white !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] button {{
    background: transparent !important;
    border-color: transparent !important;
    color: {text} !important;
}}

.stApp {{ background: {bg}; color: {text}; }}
[data-testid="stSidebar"] {{ background: {panel}; border-right: 1px solid {border}; }}
[data-testid="stSidebar"] * {{ color: {text}; }}
h1, h2, h3, p, label {{ color: {text}; }}
[data-testid="stCaptionContainer"] {{ color: {muted}; }}
[data-testid="stMetric"] {{ background: {panel}; border: 1px solid {border}; border-radius: 14px; padding: 15px; }}
[data-testid="stMetricLabel"] {{ color: {muted}; }}
[data-testid="stMetricValue"] {{ color: {text}; }}
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {{ background: {input_bg}; color: {text}; border-color: {border}; }}
[data-testid="stExpander"] {{ border: 1px solid {border}; border-radius: 10px; background: {panel}; }}
[data-testid="stForm"] {{ background: {panel}; border: 1px solid {border}; border-radius: 16px; padding: 18px; }}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {{ background: #FF3B49; color: white; border: 0; }}
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button[kind="primary"]:hover {{ background: #E72F40; }}
.hero {{ background: linear-gradient(120deg, #19254A, #242052); border: 1px solid #39457B; border-radius: 18px; padding: 22px 26px; margin: 10px 0 22px; color: #F5F7FF; }}
.hero h2 {{ color: #F5F7FF; margin: 0 0 6px; }}
.hero p {{ color: #C5CCEA; margin: 0; }}
</style>
""", unsafe_allow_html=True)



def call(method, path, **kwargs):
    try:
        headers = kwargs.pop("headers", {})
        if ADMIN_KEY:
            headers["X-Admin-Key"] = ADMIN_KEY

        response = requests.request(
            method,
            BASE + path,
            headers=headers,
            timeout=180,
            **kwargs,
        )

        response.raise_for_status()
        return response.json()

    except requests.HTTPError as exc:
        try:
            payload = exc.response.json()
            detail = (
                payload.get("detail", payload)
                if isinstance(payload, dict)
                else payload
            )
        except ValueError:
            detail = exc.response.text

        raise RuntimeError(
            f"API error {exc.response.status_code}: {detail}"
        ) from exc

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Cannot reach backend at {BASE}: {exc}"
        ) from exc


if not ADMIN_KEY:
    st.error("ADMIN_API_KEY is not configured.")
    st.stop()

if not st.session_state.get("authenticated", False):
    st.title("🔐 AI Investigation Engine")
    st.write("Enter your access key to open the investigation workspace.")

    entered_key = st.text_input(
        "Access key",
        type="password",
    )

    if st.button("Unlock workspace", type="primary"):
        if secrets.compare_digest(entered_key, ADMIN_KEY):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid access key.")

    st.stop()


def refresh_documents():
    st.session_state.docs = call("GET", "/documents")


st.markdown('<div class="hero"><h2>🔎 AI Investigation Engine</h2><p>Evidence intelligence workspace · Search, investigate, and verify across your documents.</p></div>', unsafe_allow_html=True)

if "docs" not in st.session_state:
    try:
        refresh_documents()
    except Exception as exc:
        st.warning(f"Could not load documents: {exc}")
        st.session_state.docs = []

docs = st.session_state.docs
m1, m2, m3 = st.columns(3)
m1.metric("📚 Indexed documents", f"{len(docs):,}")
m2.metric("🔍 Retrieval", "Hybrid search")
m3.metric("🧠 AI reasoning", "Gemini")

st.write("")
st.subheader("New investigation")
with st.form("investigation_form", clear_on_submit=False):
    question = st.text_area(
        "Ask a question about your indexed evidence",
        placeholder="What happened, which sources support it, and do any sources disagree?",
        height=135,
    )
    submitted = st.form_submit_button("🔍 Investigate", type="primary", use_container_width=True)

if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving evidence and investigating..."):
            started = time.perf_counter()
            try:
                result = call("POST", "/investigate", json={"question": question.strip(), "k": 8})
                elapsed = time.perf_counter() - started
                st.session_state.history.insert(0, {"question": question.strip(), "result": result, "elapsed": elapsed})
                st.session_state.history = st.session_state.history[:20]
            except Exception as exc:
                st.error(f"Investigation failed: {exc}")

if st.session_state.history:
    current = st.session_state.history[0]
    result = current["result"]
    st.divider()
    st.subheader("Investigation result")
    st.caption(f"Status: {result.get('status', 'unknown')}  ·  {len(result.get('sources', []))} evidence sources  ·  {current['elapsed']:.1f}s")
    st.markdown(result.get("answer", "No answer returned."))
    sources = result.get("sources", [])
    if sources:
        st.subheader("Supporting evidence")
        for index, source in enumerate(sources, start=1):
            ref = source.get("ref", f"S{index}")
            name = source.get("name", "Untitled document")
            chunk = source.get("chunk", "?")
            with st.expander(f"[{ref}] {name} · Chunk {chunk}"):
                st.write(source.get("text", "No source text available."))
    st.download_button(
        "⬇️ Export answer as Markdown",
        data=(f"# Investigation\n\n**Question:** {current['question']}\n\n{result.get('answer', '')}\n\n## Sources\n" + "\n".join(f"- [{s.get('ref', '?')}] {s.get('name', 'Unknown')} (chunk {s.get('chunk', '?')})" for s in sources)),
        file_name="investigation.md",
        mime="text/markdown",
    )
    if len(st.session_state.history) > 1:
        with st.expander("🕘 Previous investigations (this session)"):
            for entry in st.session_state.history[1:]:
                st.markdown(f"**{entry['question']}**")
                st.caption(entry["result"].get("answer", "")[:350])

with st.sidebar:
    st.divider()
    st.header("📁 Document Manager")
    uploaded = st.file_uploader("Choose a document", type=["pdf", "docx", "txt", "md", "csv", "json", "jsonl"])
    if uploaded is not None and st.button("Upload & Index", type="primary", use_container_width=True):
        with st.spinner("Indexing document..."):
            try:
                result = call("POST", "/documents/upload", files={"file": (uploaded.name, uploaded.getvalue(), "application/octet-stream")})
                st.success(f"Indexed {result.get('name', uploaded.name)}")
                refresh_documents()
                st.rerun()
            except Exception as exc:
                st.error(f"Upload failed: {exc}")
    st.divider()
    st.subheader("Indexed documents")
    if st.button("🔄 Refresh list", use_container_width=True):
        try:
            refresh_documents()
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    docs = st.session_state.docs
    st.caption(f"{len(docs):,} documents indexed")
    filter_text = st.text_input("Find a document", placeholder="Search documents...")
    filtered = [doc for doc in docs if filter_text.casefold() in doc.get("name", "").casefold()]
    st.caption(f"Showing {min(20, len(filtered))} of {len(filtered):,} matches")
    for doc in filtered[:20]:
        with st.expander(f"📄 {doc.get('name', 'Untitled')}"):
            st.caption(f"Chunks: {doc.get('chunks', '?')}")
            st.code(doc.get("doc_id", ""))
            if st.button("🗑️ Delete document", key=f"delete_{doc['doc_id']}", use_container_width=True):
                try:
                    call("DELETE", f"/documents/{doc['doc_id']}")
                    refresh_documents()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Delete failed: {exc}")
