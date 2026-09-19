import os

import requests
from langchain_core.tools import tool


@tool
def fetch_github_repositories(username: str) -> list[dict]:
    """MCP-compliant tool to fetch public and authenticated private repositories."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    url = "https://api.github.com/user/repos" if token else f"https://api.github.com/users/{username}/repos"
    
    response = requests.get(url, headers=headers, params={"per_page": 100, "sort": "updated"})
    if response.status_code != 200:
        return [{"error": f"Failed to fetch repos: {response.status_code}"}]
    
    repos = response.json()
    parsed_repos = []
    for repo in repos:
        parsed_repos.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
            "stars": repo.get("stargazers_count"),
            "is_private": repo.get("private", False),
            "url": repo.get("html_url")
        })
    return parsed_repos