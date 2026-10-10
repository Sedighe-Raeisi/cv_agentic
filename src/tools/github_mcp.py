import os

import requests
from langchain_core.tools import tool


@tool
def fetch_github_repositories(username: str) -> list[dict]:
    """Fetches public GitHub repositories for a given username."""
    token = os.getenv("GITHUB_TOKEN")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Target the specific user's public repos endpoint instead of /user/repos
    url = f"https://api.github.com/users/{username}/repos"
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params={"per_page": 100, "sort": "updated"},
            timeout=10  # 10-second explicit timeout prevents hanging
        )
        
        if response.status_code != 200:
            print(f"GitHub API Error [{response.status_code}]: {response.text}")
            return []

        repos = response.json()
        if not isinstance(repos, list):
            return []

        # Return a lightweight list of repo details for the agent
        return [
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count"),
                "html_url": repo.get("html_url")
            }
            for repo in repos
        ]

    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not connect to GitHub API ({e}). Proceeding without live GitHub data.")
        return []