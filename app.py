"""
CV Tailor - AI-Powered Resume and Cover Letter Generator
Uses local Ollama LLMs to tailor your CV and generate cover letters based on job postings
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project directories to path
sys.path.append(str(Path(__file__).parent))

from scrapers.job_scraper import JobScraper
from processors.cv_processor import CVProcessor
from processors.cover_letter_generator import CoverLetterGenerator
from processors.ollama_client import OllamaClient
from utils.file_handler import FileHandler

# Page configuration
st.set_page_config(
    page_title="CV Tailor - AI Resume & Cover Letter Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'job_description' not in st.session_state:
    st.session_state.job_description = None
if 'original_cv' not in st.session_state:
    st.session_state.original_cv = None
if 'tailored_cv' not in st.session_state:
    st.session_state.tailored_cv = None
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = None

def main():
    # Header
    st.markdown('<div class="main-header">📄 CV Tailor - AI-Powered Job Application Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tailor your CV and generate cover letters using local AI models</div>', unsafe_allow_html=True)

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Check Ollama connection
        ollama_client = OllamaClient()
        if ollama_client.check_connection():
            st.success("✅ Ollama is running")

            # Model selection
            available_models = ollama_client.list_models()
            if available_models:
                selected_model = st.selectbox(
                    "Select LLM Model",
                    available_models,
                    index=0
                )
                st.session_state.selected_model = selected_model
            else:
                st.warning("⚠️ No models found. Please pull a model using: ollama pull llama3")
                st.session_state.selected_model = "llama3"
        else:
            st.error("❌ Ollama is not running. Please start Ollama first.")
            st.info("Run: ollama serve")
            return

        st.divider()

        # Additional settings
        st.subheader("Settings")
        temperature = st.slider("AI Creativity", 0.0, 1.0, 0.7, 0.1)
        st.session_state.temperature = temperature

        st.divider()
        st.markdown("### 📚 How to Use")
        st.markdown("""
        1. **Enter Job URL** or paste job description
        2. **Upload your CV** (PDF or DOCX)
        3. Click **Generate** to tailor your CV
        4. **Download** tailored CV and cover letter
        """)

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📋 Job Posting")

        # Job input method
        input_method = st.radio(
            "Choose input method:",
            ["URL", "Paste Text"],
            horizontal=True
        )

        if input_method == "URL":
            job_url = st.text_input(
                "Job Posting URL",
                placeholder="https://www.linkedin.com/jobs/view/...",
                help="Enter job URL from LinkedIn, Indeed, StepStone, etc."
            )

            if st.button("🔍 Scrape Job Description", type="primary"):
                if job_url:
                    with st.spinner("Scraping job posting..."):
                        scraper = JobScraper()
                        job_data = scraper.scrape_job(job_url)

                        if job_data:
                            st.session_state.job_description = job_data
                            st.success("✅ Job description scraped successfully!")
                        else:
                            st.error("❌ Failed to scrape job. Try pasting the description manually.")
                else:
                    st.warning("⚠️ Please enter a job URL")
        else:
            job_text = st.text_area(
                "Paste Job Description",
                height=300,
                placeholder="Paste the full job description here..."
            )

            if st.button("📝 Use This Description", type="primary"):
                if job_text:
                    st.session_state.job_description = {
                        "title": "Manual Entry",
                        "company": "N/A",
                        "description": job_text,
                        "requirements": job_text
                    }
                    st.success("✅ Job description loaded!")
                else:
                    st.warning("⚠️ Please paste a job description")

        # Display job description
        if st.session_state.job_description:
            with st.expander("📄 View Job Description", expanded=True):
                job_data = st.session_state.job_description
                st.markdown(f"**Title:** {job_data.get('title', 'N/A')}")
                st.markdown(f"**Company:** {job_data.get('company', 'N/A')}")
                st.markdown(f"**Location:** {job_data.get('location', 'N/A')}")
                st.divider()
                st.markdown(job_data.get('description', 'No description available'))

    with col2:
        st.header("📂 Your CV")

        # CV upload
        uploaded_file = st.file_uploader(
            "Upload your CV",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format"
        )

        if uploaded_file:
            with st.spinner("Processing CV..."):
                file_handler = FileHandler()
                cv_text = file_handler.extract_text_from_file(uploaded_file)

                if cv_text:
                    st.session_state.original_cv = cv_text
                    st.success(f"✅ CV loaded ({len(cv_text)} characters)")

                    with st.expander("📄 View Original CV", expanded=False):
                        st.text_area("Your CV Content", cv_text, height=300, disabled=True)
                else:
                    st.error("❌ Failed to extract text from CV")

    # Generation section
    st.divider()
    st.header("🚀 Generate Tailored Application")

    col3, col4, col5 = st.columns([1, 1, 1])

    with col3:
        generate_cv = st.checkbox("Tailor CV", value=True)
    with col4:
        generate_cover_letter = st.checkbox("Generate Cover Letter", value=True)
    with col5:
        company_name = st.text_input("Company Name (optional)", placeholder="Google")

    if st.button("✨ Generate Tailored Application", type="primary", use_container_width=True):
        if not st.session_state.job_description:
            st.error("❌ Please load a job description first")
        elif not st.session_state.original_cv:
            st.error("❌ Please upload your CV first")
        else:
            # Initialize processors
            cv_processor = CVProcessor(st.session_state.selected_model, st.session_state.temperature)
            cover_letter_gen = CoverLetterGenerator(st.session_state.selected_model, st.session_state.temperature)

            # Generate tailored CV
            if generate_cv:
                with st.spinner("🔄 Tailoring your CV..."):
                    st.session_state.tailored_cv = cv_processor.tailor_cv(
                        st.session_state.original_cv,
                        st.session_state.job_description
                    )

            # Generate cover letter
            if generate_cover_letter:
                with st.spinner("✍️ Writing cover letter..."):
                    st.session_state.cover_letter = cover_letter_gen.generate_cover_letter(
                        st.session_state.original_cv,
                        st.session_state.job_description,
                        company_name if company_name else st.session_state.job_description.get('company', 'the company')
                    )

            st.success("🎉 Application materials generated successfully!")

    # Results section
    if st.session_state.tailored_cv or st.session_state.cover_letter:
        st.divider()
        st.header("📥 Your Tailored Application")

        result_col1, result_col2 = st.columns([1, 1])

        with result_col1:
            if st.session_state.tailored_cv:
                st.subheader("📄 Tailored CV")
                st.text_area("Tailored Resume", st.session_state.tailored_cv, height=400)

                file_handler = FileHandler()
                docx_cv = file_handler.create_docx(st.session_state.tailored_cv, "Tailored CV")

                st.download_button(
                    label="⬇️ Download Tailored CV (DOCX)",
                    data=docx_cv,
                    file_name="tailored_cv.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

        with result_col2:
            if st.session_state.cover_letter:
                st.subheader("✉️ Cover Letter")
                st.text_area("Cover Letter", st.session_state.cover_letter, height=400)

                file_handler = FileHandler()
                docx_cl = file_handler.create_docx(st.session_state.cover_letter, "Cover Letter")

                st.download_button(
                    label="⬇️ Download Cover Letter (DOCX)",
                    data=docx_cl,
                    file_name="cover_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
