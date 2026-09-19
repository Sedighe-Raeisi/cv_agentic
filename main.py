import pypdf
from dotenv import load_dotenv

from src.agent.graph import build_cv_agent

load_dotenv()

def extract_pdf_text(pdf_path: str) -> str:
    reader = pypdf.PdfReader(pdf_path)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

if __name__ == "__main__":
    cv_path = "CV_SedigheRaeisi2026 (1).pdf" # Your uploaded file
    github_handle = "Sedighe-Raeisi"          # Replace with your actual username

    print("📄 Extracting CV text...")
    raw_cv_text = extract_pdf_text(cv_path)

    print("🚀 Initializing Agentic CV Engine...")
    app = build_cv_agent()

    initial_state = {
        "messages": [],
        "raw_cv": raw_cv_text,
        "github_username": github_handle,
        "github_data": [],
        "draft_cv": "",
        "validation_passed": False,
        "critique": "",
        "revision_count": 0
    }

    print("⚡ Executing LangGraph workflow...")
    final_state = app.invoke(initial_state)

    print("\n✅ CV Enrichment Complete!")
    print("\n--- ENHANCED CV OUTPUT ---\n")
    print(final_state["draft_cv"])

    with open("Updated_Empowered_CV.md", "w", encoding="utf-8") as f:
        f.write(final_state["draft_cv"])
    print("\nSaved output to Updated_Empowered_CV.md")