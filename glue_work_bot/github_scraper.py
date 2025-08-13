from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import requests

class GitHubScraper:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo = "flutter/flutter"
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        self.headers = {"Authorization": f"Bearer {self.github_token}"}

    def github_paginate(self, url, params=None):
        results = []
        session = requests.Session()

        page = 1
        while True:
            query = params.copy() if params else {}
            query["per_page"] = 100
            query["page"] = page

            response = session.get(url, params=query, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            if not data:
                break

            results.extend(data)
            page += 1

        return results


    def get_requests_updated_since(self, type, days=365, per_page=100, branch=None):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        since_iso = cutoff.replace().isoformat().replace("+00:00", "Z")

        params = {
            "per_page": per_page,
            "since": since_iso,
            "state": "all",
            "direction": "desc",
            "sort": "updated",
            "sha": branch
        }

        url = self.base_url + "/" + type

        return self.github_paginate(url=url, params=params)

    def get_all_branches(self):
        url = f"{self.base_url}/branches"
        return self.github_paginate(url)

    def get_all_commits(self):
        branches = self.get_all_branches()
        commits = []
        used_shas = []
        for branch in branches:
            branch_commits = self.get_requests_updated_since(type="commits", days=days, branch=branch["name"])
            for commit in branch_commits:
                if commit["sha"] in used_shas:
                    continue
                else:
                    used_shas.append(commit["sha"])
                    commits.append(commit)
        return commits

    def get_all_pull_request_urls(self, issues):
        urls = []
        for issue in issues:
            if "pull_request" in issue:
                urls.append(issue["pull_request"]["url"])
        return urls

    def get_all_pull_requests(self, urls):
        pull_requests = []
        for url in urls:
            session = requests.Session()
            response = session.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            pull_requests.append(data)
        return pull_requests

if __name__ == "__main__":
    github_scraper = GitHubScraper()
    days = 2
    issues = github_scraper.get_requests_updated_since(type="issues", days=days)
    pull_requests_urls = github_scraper.get_all_pull_request_urls(issues=issues)
    pull_requests = github_scraper.get_all_pull_requests(pull_requests_urls)
    commits = github_scraper.get_all_commits()
    print(f"Fetched {len(issues)} issues updated in the past {days} days.")
    print(f"Fetched {len(pull_requests)} pull requests updated in the past {days} days.")
    print(f"Fetched {len(commits)} unique commits updated in the past {days} days.")