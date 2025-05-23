import os

# Set environment variable for protobuf
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
from pdf_assistant import PDFAssistant
from utils import load_environment, get_example_queries, get_filename_from_url
import hashlib

# Disable logging from pdf_assistant or any noisy modules if present
import logging

logging.getLogger().setLevel(logging.WARNING)  # Set root logger level to WARNING

# Page configuration with clean layout
st.set_page_config(
    page_title="📚 Recipe PDF Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, above-the-fold sidebar layout
st.markdown("""
<style>
    /* Remove top padding for more space */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }

    /* Compact sidebar */
    .css-1d391kg {
        padding-top: 1rem;
    }

    /* Remove extra spacing from form elements */
    .stTextInput > div > div {
        margin-bottom: 0.5rem;
    }

    .stButton > button {
        width: 100%;
        margin-top: 0.25rem;
        margin-bottom: 0.25rem;
    }

    /* Compact headers */
    .sidebar .element-container h2 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }

    /* Hide streamlit branding for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Compact quick start buttons */
    .stButton button {
        padding: 0.25rem 0.5rem;
        font-size: 0.85rem;
    }

    /* Compact divider */
    hr {
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📖 Cookbook PDF Reader and Assistant")

# Load environment variables
db_url = load_environment()

# Default PDF URL
default_pdf_url = "https://reseaudumieuxetre.ca/wp-content/uploads/2021/01/French-Canadian-Recipes-.pdf"


def get_cookbook_description(pdf_url, assistant=None):
    """Generate a description using LLM analysis of the cookbook content."""
    if assistant and st.session_state.kb_loaded:
        try:
            # Use the assistant to analyze and describe the cookbook
            prompt = """Based on the cookbook content you have access to, provide a brief 1-2 sentence description of this cookbook. 
            Focus on: cuisine type, author/origin, main themes, and what makes it special. 
            Start with 'This cookbook...' and keep it concise and engaging. Maximum 150 characters."""

            description = assistant.chat(prompt)
            # Clean up the response and ensure it's properly formatted
            description = description.strip()

            # If it's too long, truncate at a sentence boundary
            if len(description) > 150:
                # Try to find the end of the first sentence
                sentence_end = description.find('. ')
                if sentence_end > 50 and sentence_end < 150:
                    description = description[:sentence_end + 1]
                else:
                    # Just truncate at word boundary
                    words = description[:147].split()
                    description = ' '.join(words[:-1]) + "..."

            return description
        except Exception as e:
            print(f"Error generating LLM description: {e}")
            # Fall back to filename-based description
            pass

    # Fallback: Simple filename-based description
    cookbook_name = get_filename_from_url(pdf_url).replace('.pdf', '').replace('-', ' ').replace('_', ' ')
    return f"This cookbook '{cookbook_name}' contains a collection of recipes and cooking instructions."


# Initialize session state
if 'pdf_url' not in st.session_state:
    st.session_state.pdf_url = default_pdf_url
    st.session_state.kb_loaded = False
    # Auto-generate initial collection name
    url_hash = hashlib.md5(default_pdf_url.encode()).hexdigest()[:12]
    filename = default_pdf_url.split('/')[-1].replace('.pdf', '').replace(' ', '_')[:20]
    st.session_state.collection_name = f"pdf_{filename}_{url_hash}"
    st.session_state.messages = []
    st.session_state.run_id = None
    st.session_state.assistant_initialized = False
    st.session_state.cookbook_description = None

# Compact Sidebar configuration - everything above the fold
with st.sidebar:
    st.title("📚 Recipe Assistant")

    # PDF Input Section - compact
    st.markdown("### 📁 Document Setup")
    pdf_url = st.text_input(
        "Cookbook PDF URL",
        value=st.session_state.pdf_url,
        placeholder="Enter PDF URL here...",
        label_visibility="collapsed"
    )

    load_clicked = st.button("📥 Load PDF", type="primary", use_container_width=True)

    if load_clicked:
        # Auto-generate collection name from PDF URL
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:12]
        filename = pdf_url.split('/')[-1].replace('.pdf', '').replace(' ', '_')[:20]

        # Add timestamp if force reload is enabled
        force_reload = st.session_state.get('force_reload', False)
        if force_reload:
            import time

            timestamp = int(time.time())
            auto_collection_name = f"pdf_{filename}_{url_hash}_{timestamp}"
        else:
            auto_collection_name = f"pdf_{filename}_{url_hash}"

        st.session_state.update({
            "pdf_url": pdf_url,
            "collection_name": auto_collection_name,
            "kb_loaded": False,
            "messages": [],
            "run_id": None,
            "assistant_initialized": False,
            "start_new": force_reload,  # Use force_reload flag
            "cookbook_description": None,  # Reset description when loading new PDF
        })
        st.success("✅ PDF loaded successfully!")

    # Document Status Section - compact
    st.markdown("### 📄 Current Cookbook")
    if st.session_state.get("pdf_url"):
        # Use cached description or generate new one
        if st.session_state.get("cookbook_description"):
            description = st.session_state.cookbook_description
        else:
            # Try to get description from assistant if available
            if st.session_state.get("assistant_initialized") and 'assistant' in locals():
                description = get_cookbook_description(st.session_state.pdf_url, assistant)
                st.session_state.cookbook_description = description  # Cache it
            else:
                description = get_cookbook_description(st.session_state.pdf_url)
        st.markdown(f"*{description}*")

        # Show a small indicator if it's AI-generated vs fallback
        if "This cookbook" in description and len(description) < 100:
            st.caption("🤖 AI-generated description")
        else:
            st.caption("📝 Filename-based description")
    else:
        st.markdown("*No cookbook loaded*")

    # Advanced Options - in expander to save space
    with st.expander("🔧 Advanced Options"):
        force_reload = st.checkbox("🔄 Force reload (clear existing)", value=False)
        if force_reload:
            st.warning("⚠️ Will clear existing data for this PDF")

        # Clear database button
        if st.button("🗑️ Clear Database", help="Remove all stored data"):
            st.session_state.clear()
            st.success("Database cleared! Please reload your PDF.")

    # Help Section
    with st.expander("ℹ️ Quick Help"):
        st.markdown("""
        **How to use:**
        1. **Paste** a PDF URL above
        2. **Click** 'Load PDF' to process  
        3. **Ask** questions about recipes

        **Tips:**
        - Try the quick start buttons below
        - Ask about specific ingredients
        - Request recipe modifications
        - Use 'Force reload' if you get duplicate errors
        """)

    # Session Info - compact (only show if active)
    if st.session_state.get("run_id"):
        st.caption(f"💬 Session: {st.session_state.run_id[:8]}...")


def initialize_assistant():
    with st.spinner("🔄 Initializing assistant..."):
        assistant = PDFAssistant(
            pdf_url=st.session_state.pdf_url,
            collection_name=st.session_state.collection_name,
            db_url=db_url,
            run_id=st.session_state.get("run_id")
        )

        if not st.session_state.kb_loaded:
            assistant.initialize_knowledge_base()
            st.session_state.kb_loaded = True

        if not st.session_state.get("run_id"):
            existing = assistant.get_existing_run_ids()
            if existing and not st.session_state.get("start_new", False):
                st.session_state.run_id = existing[0]
                st.sidebar.success(f"Resuming session: {st.session_state.run_id}")

        assistant.initialize_assistant()
        st.session_state.update({
            "assistant_initialized": True,
            "run_id": assistant.run_id
        })
        return assistant


# Display example queries - compact layout
st.subheader("💡 Quick Start")
cols = st.columns(3)
for i, query in enumerate(get_example_queries()):
    col_idx = i % 3
    if cols[col_idx].button(query, key=f"example_{i}", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.process_question = True
        st.rerun()

st.divider()

# Initialize assistant early if we have a PDF URL but no assistant yet
if st.session_state.pdf_url and not st.session_state.assistant_initialized:
    # Auto-initialize the assistant if we have a PDF
    assistant = initialize_assistant()
    # Generate cookbook description once assistant is ready - with error handling
    if assistant and st.session_state.kb_loaded and not st.session_state.get("cookbook_description"):
        try:
            st.session_state.cookbook_description = get_cookbook_description(st.session_state.pdf_url, assistant)
            st.sidebar.success("🤖 Generated AI description")
        except Exception as e:
            print(f"Failed to generate AI description: {e}")
            st.session_state.cookbook_description = get_cookbook_description(st.session_state.pdf_url)
elif st.session_state.assistant_initialized:
    # Recreate the assistant with the current settings
    assistant = PDFAssistant(
        pdf_url=st.session_state.pdf_url,
        collection_name=st.session_state.collection_name,
        db_url=db_url,
        run_id=st.session_state.run_id
    )
    assistant.initialize_assistant()
    # Generate description if we don't have one yet - with error handling
    if not st.session_state.get("cookbook_description") and st.session_state.kb_loaded:
        try:
            st.session_state.cookbook_description = get_cookbook_description(st.session_state.pdf_url, assistant)
        except Exception as e:
            print(f"Failed to generate AI description: {e}")
            st.session_state.cookbook_description = get_cookbook_description(st.session_state.pdf_url)
else:
    assistant = None

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check if we need to process the last message (from sample question or new input)
if 'process_question' not in st.session_state:
    st.session_state.process_question = False

if st.session_state.process_question and st.session_state.messages:
    # Process the last user message
    last_message = st.session_state.messages[-1]
    if last_message["role"] == "user":
        # Make sure assistant is ready
        if not assistant:
            assistant = initialize_assistant()

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = assistant.chat(last_message["content"])

                # Display assistant response
                st.markdown(response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

        # Clear the flag
        st.session_state.process_question = False

# Input for new messages - Always show if we have a PDF URL
if st.session_state.pdf_url:
    if prompt := st.chat_input("Ask a question about the cookbook content..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Make sure the assistant is initialized
        if not assistant:
            assistant = initialize_assistant()

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = assistant.chat(prompt)

                # Display assistant response
                st.markdown(response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("📌 Please enter a Cookbook PDF URL and click 'Load PDF' to begin.")