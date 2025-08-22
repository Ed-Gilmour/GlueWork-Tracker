from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from config_handler import ConfigHandler
import os
import requests
import json
import argparse

class DataScraper:
    retrieved_days = 1

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--config-file', required=True)
        args = parser.parse_args()
        config_file = args.config_file
        config_handler = ConfigHandler(config_file)
        config_handler.load_config()
        self.config_scraper = ConfigScraper(config_handler)
        self.github_scraper = GitHubScraper(config_handler.get_excluded_users())

    def scrape_github_data(self):
        self.github_scraper.scrape_github_data(self.retrieved_days)

class GitHubScraper:
    def __init__(self, excluded_users):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo = "flutter/flutter"
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        self.headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.excluded_users = excluded_users

    def github_paginate(self, url, params=None):
        results = []
        session = requests.Session()

        page = 1
        while True:
            query = params.copy() if params else {}
            query["per_page"] = 100
            query["page"] = page

            response = session.get(url, params=query, headers=self.headers)
            if response.status_code != 200:
                print(f"Break: {url} (status {response.status_code})", flush=True)
                break

            data = response.json()
            if not data:
                break

            page += 1
            results.extend(data)

        return results

    def get_requests_updated_since(self, item_type, per_page=100, branch=None):
        cutoff = datetime.now(timezone.utc) - timedelta(days=DataScraper.retrieved_days)
        since_iso = cutoff.isoformat().replace("+00:00", "Z")

        params = {
            "per_page": per_page,
            "since": since_iso,
            "state": "all",
            "direction": "desc",
            "sort": "updated",
            "sha": branch
        }

        url = self.base_url + "/" + item_type

        return self.github_paginate(url=url, params=params)

    def get_all_branches(self):
        url = f"{self.base_url}/branches"
        return self.github_paginate(url)

    def get_all_commits(self, days):
        branches = self.get_all_branches()
        commits = []
        used_shas = set()
        for branch in branches:
            branch_commits = self.get_requests_updated_since(item_type="commits", branch=branch["name"])
            for commit in branch_commits:
                if commit["sha"] in used_shas:
                    continue
                else:
                    used_shas.add(commit["sha"])
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
        session = requests.Session()
        for url in urls:
            response = session.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Skipping {url} (status {response.status_code})", flush=True)
                continue
            data = response.json()
            pull_requests.append(data)
        return pull_requests

    def get_all_pull_request_reviews(self, urls):
        reviews = []
        session = requests.Session()
        for url in urls:
            response = session.get(url + "/reviews", headers=self.headers)
            if response.status_code != 200:
                print(f"Skipping {url} (status {response.status_code})", flush=True)
                continue
            data = response.json()
            for review in data:
                reviews.append(review)
        return reviews

    def write_glue_work_data(self, data):
        os.makedirs("temp", exist_ok=True)
        with open("temp/glue_work_data.json", "w") as f:
            json.dump(data, f)

    def scrape_github_data(self, days):
        issues = self.get_requests_updated_since(item_type="issues")
        pull_requests_urls = self.get_all_pull_request_urls(issues=issues)
        pull_requests = self.get_all_pull_requests(urls=pull_requests_urls)
        pull_request_reviews = self.get_all_pull_request_reviews(urls=pull_requests_urls)
        commits = self.get_all_commits(days=days)
        data = {
            "issues": [
                {
                    "title": issue["title"],
                    "body": issue.get("body", ""),
                    "author": issue["user"]["login"]
                } for issue in issues
                if self.is_user_valid(issue["user"])
            ],
            "pull_requests": [
                {
                    "title": pr["title"],
                    "body": pr.get("body", ""),
                    "author": pr["user"]["login"]
                } for pr in pull_requests
                if self.is_user_valid(pr["user"])
            ],
            "commits": [
                {
                    "message": commit["commit"]["message"],
                    "author": commit["author"]["login"]
                } for commit in commits
                if self.is_user_valid(commit["author"])
            ],
            "reviews": [
                {
                    "author": review["user"]["login"]
                } for review in pull_request_reviews
                if self.is_user_valid(review["user"])
            ]
        }
        self.write_glue_work_data(data=data)

    def is_user_valid(self, user):
        return user["login"] not in self.excluded_users and user["type"] != "Bot"

class ConfigScraper:
    def __init__(self, config_handler):
        self.config_handler = config_handler

if __name__ == "__main__":
    data_scraper = DataScraper()
    data_scraper.scrape_github_data()