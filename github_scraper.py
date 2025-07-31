from dotenv import load_dotenv
import os
import requests

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "flutter/flutter"
BASE_URL = f"https://api.github.com/repos/{REPO}"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def get_repo_info():
    response = requests.get(BASE_URL, headers=HEADERS)
    return response.json()

def get_issues(state="open", per_page=5):
    url = f"{BASE_URL}/issues"
    params = {"state": state, "per_page": per_page}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def get_pull_requests(state="open", per_page=5):
    url = f"{BASE_URL}/pulls"
    params = {"state": state, "per_page": per_page}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

if __name__ == "__main__":
    repo_info = get_repo_info()
    print("Repo:", repo_info["full_name"])
    print("Stars:", repo_info["stargazers_count"])
    print("Forks:", repo_info["forks_count"])

    issues = get_issues()
    print("\nSample Issues:")
    for issue in issues:
        print(f"- #{issue['number']} | title: {issue['title']} | name: {issue['user']['login']}")

    prs = get_pull_requests()
    print("\nSample Pull Requests:")
    for pr in prs:
        print(f"- #{pr['number']} {pr['title']}")