# 🤖 Agentic CV Enrichment System

An autonomous, stateful agentic system built with **LangGraph**, **LangChain**, and **Model Context Protocol (MCP)** principles. The application automatically fetches an engineer's GitHub projects (public and private), analyzes repository metadata, and enriches a raw CV with concrete, technical proof points formatted as publication-ready **LaTeX** (or compiled PDF).

---

## 🏗️ System Architecture
+------------------------+
             |    Raw PDF / Input     |
             +-----------+------------+
                         |
                         v
             +------------------------+
             |  1. Fetch GitHub Node  | <---> GitHub REST API (MCP Tool)
             +-----------+------------+
                         |
                         v
             +------------------------+
             |   2. Enrich CV Node    | <--- Prompt Engineering & LLM
             +-----------+------------+
                         |
                         v
             +------------------------+
             |  3. Validate CV Node   | (Reflection & Anti-Hallucination)
             +-----------+------------+
                         |
               Passed? --+-- Failed? (Loop back up to 3x)
                  |            |
                 Yes           No
                  |            v
                  |    [ Re-run Enrich Node with Critique ]
                  v
             +------------------------+
             | Output LaTeX / PDF     |
             +------------------------+

---

## ✨ Key Features

- **Stateful Directed Graph**: Orchestrated via **LangGraph** to manage multi-node execution state.
- **Agentic Reflection & Validation**: Self-correcting validation node audits generated claims against retrieved raw data to eliminate AI hallucinations.
- **MCP-Compliant Tool Integration**: Decoupled tool layer for fetching GitHub repositories (`public` and authenticated `private`).
- **Flexible Model Factory**: Easily toggle between Academic Cloud APIs (GWDG SAIA), standard OpenAI endpoints, or local Ollama instances (`qwen2.5-coder`, `llama3`).
- **LaTeX & PDF Output**: Generates valid, error-free LaTeX source files (`.tex`) and auto-compiles to `.pdf` if a local TeX distribution is detected.

---

## 📂 Project Structure

```text
cv_agentic/
├── src/
│   ├── agent/
│   │   ├── factory.py      # LLM provider factory (Academic Cloud / OpenAI / Ollama)
│   │   ├── state.py        # Agent State Schema (TypedDict)
│   │   ├── nodes.py        # Graph nodes (Fetch, Enrich, Validate)
│   │   └── graph.py        # LangGraph construction and conditional edges
│   ├── tools/
│   │   └── github_mcp.py   # MCP-compliant GitHub repository scraper tool
│   └── utils/
│       └── helpers.py      # Helper utilities
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules protecting local credentials
├── main.py                 # Application entry point
├── requirements.txt        # Locked python dependencies
└── README.md               # Project documentation

**Installation**
Clone the repository and set up a virtual environment:
git clone [https://github.com/Sedighe-Raeisi/cv_agentic.git](https://github.com/Sedighe-Raeisi/cv_agentic.git)
cd cv_agentic

python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

**Environment Configuration**
Create a .env file in the root directory:
# Provider Options: academiccloud | openai | ollama
PROVIDER=academiccloud

# Academic Cloud (GWDG SAIA) Configuration
ACADEMIC_API_KEY=your_academic_cloud_key
ACADEMIC_BASE_URL=[https://chat-ai.academiccloud.de/v1](https://chat-ai.academiccloud.de/v1)
ACADEMIC_MODEL=meta-llama-3.1-8b-instruct

# Optional: GitHub Personal Access Token (Required for Private Repos)
GITHUB_TOKEN=your_github_personal_access_token

**Usage**
Place your target PDF CV in the root directory (e.g., CV_SedigheRaeisi2026.pdf).

**Run the pipeline:**

PowerShell
python main.py
The system will process your CV, fetch GitHub metadata, pass the validation graph, and generate:

Updated_Empowered_CV.tex: Raw LaTeX code ready for Overleaf or local compilation.

Updated_Empowered_CV.pdf: Compiled PDF document (if pdflatex is installed).

**📄 License**
This project is open-source and available under the MIT License.