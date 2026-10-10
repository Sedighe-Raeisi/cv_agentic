import requests
import streamlit as st

# Set page title and layout
st.set_page_config(
    page_title="Agentic CV Web Engine",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 End-to-End Agentic CV Engine")
st.markdown(
    "Upload your PDF CV, provide your GitHub handle, and let our multi-agent workflow "
    "parse your CV via Vision LLMs, enrich it with live repository data, and generate tailored LaTeX/PDF output."
)

# Backend Endpoint configuration (Default: local running FastAPI server)
BACKEND_URL = st.sidebar.text_input("Backend Endpoint", "http://127.0.0.1:8000/api/enrich")

# Input Form
with st.form("cv_enrichment_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your CV (.tex, .txt, .pdf, .png, .jpg)", 
            type=["tex", "txt", "pdf", "png", "jpg", "jpeg"]
            )
        github_username = st.text_input("GitHub Username", placeholder="e.g., Sedighe-Raeisi")
        
    with col2:
        output_format = st.selectbox("Output Format", ["latex", "pdf"])
        custom_prompt = st.text_area(
            "Custom Instructions / Targeted Role",
            placeholder="e.g., Tailor my CV for a Data Scientist role focusing on Graph Neural Networks and LLMs.",
            height=120
        )

    submit_button = st.form_submit_button("Enrich CV 🚀", use_container_width=True)

# Form Submission Processing
if submit_button:
    if not uploaded_file:
        st.error("Please upload a CV file.")
    elif not github_username.strip():
        st.error("Please provide your GitHub username.")
    else:
        with st.spinner("Processing CV with Vision Agent and fetching GitHub data..."):
            try:
                # Prepare payload and files for FastAPI form multi-part request
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }
                data = {
                    "github_username": github_username.strip(),
                    "custom_prompt": custom_prompt.strip(),
                    "output_format": output_format.lower()
                }

                response = requests.post(BACKEND_URL, files=files, data=data, timeout=180)

                if response.status_code == 200:
                    st.success("CV processing complete!")

                    if output_format == "latex":
                        result = response.json()
                        latex_code = result.get("latex_code", "")

                        st.subheader("Generated LaTeX Code")
                        st.code(latex_code, language="latex")
                        
                        # Download button for .tex file
                        st.download_button(
                            label="Download .tex File",
                            data=latex_code,
                            file_name="Updated_CV.tex",
                            mime="text/x-tex"
                        )
                    else:
                        # Output format is PDF binary response
                        st.subheader("Generated PDF Document")
                        st.download_button(
                            label="Download PDF CV",
                            data=response.content,
                            file_name="Empowered_CV.pdf",
                            mime="application/pdf"
                        )
                else:
                    try:
                        err_detail = response.json().get("detail", response.text)
                    except Exception:
                        err_detail = response.text
                    st.error(f"Error from server: {err_detail}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI backend. Ensure `uvicorn app:app --reload` is running on http://127.0.0.1:8000.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")