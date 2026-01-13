from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from config_handler import ConfigHandler
import os
import requests
import json
import argparse
import time

class DataScraper:
    RETRIEVED_DAYS = 30

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--config-file', required=True)
        args = parser.parse_args()
        config_file = args.config_file
        config_handler = ConfigHandler(config_file)
        config_handler.load_config()
        self.config_scraper = ConfigScraper(config_handler)
        self.github_scraper = GitHubScraper(config_handler.get_excluded_users())

    def write_data(self, data, key):
        os.makedirs("temp", exist_ok=True)
        file_path = "temp/glue_work_data.json"

        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
        else:
            existing_data = {}

        existing_data[key] = data

        with open(file_path, "w") as f:
            json.dump(existing_data, f)

    def scrape_stackexchange_data(self):
        self.write_data(self.stackexchange_scraper.scrape_stackexchange_data(), "stackexchange")

    def scrape_github_data(self):
        self.write_data(self.github_scraper.scrape_github_data(), "github")

class StackExchangeScraper:
    COMMUNITY_TAG = "Example"

    def __init__(self):
        load_dotenv()
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
        self.tag = self.COMMUNITY_TAG
        self.retrieved_days = DataScraper.RETRIEVED_DAYS

    def fetch_recent_questions(self):
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retrieved_days)
        fromdate = int(cutoff.timestamp())

        params = {
            "order": "desc",
            "sort": "creation",
            "tagged": self.tag,
            "site": self.site,
            "pagesize": 100,
            "fromdate": fromdate,
        }

        url = f"{self.base_url}/questions"
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Skipping {url} (status {response.status_code})", flush=True)
            return []

        data = response.json()
        return [q["question_id"] for q in data.get("items", [])]

    def fetch_answers_for_questions(self, question_ids):
        if not question_ids:
            return []

        all_answers = []
        chunk_size = 20

        for i in range(0, len(question_ids), chunk_size):
            chunk = question_ids[i:i+chunk_size]
            ids_str = ";".join(map(str, chunk))

            url = f"{self.base_url}/questions/{ids_str}/answers"
            params = {
                "order": "desc",
                "sort": "creation",
                "site": self.site,
                "pagesize": 100,
                "filter": "withbody"
            }

            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Skipping {url} (status {response.status_code})", flush=True)
                continue

            data = response.json()
            all_answers.extend(data.get("items", []))

        return all_answers

    def scrape_stackexchange_data(self):
        question_ids = self.fetch_recent_questions()
        answers = self.fetch_answers_for_questions(question_ids)

        data = {
            "replies": [
                {
                    "body": a.get("body", ""),
                    "author": a["owner"].get("display_name", "Unknown")
                }
                for a in answers
            ]
        }
        return data

class GitHubScraper:
    def __init__(self, excluded_users=[], retrieved_days=DataScraper.RETRIEVED_DAYS):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo = "flutter/flutter" # TODO: os.environ["GITHUB_REPOSITORY"]
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        self.headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.excluded_users = excluded_users
        self.retrieved_days = retrieved_days

    def github_request(self, session, method, url, **kwargs):
        while True:
            response = session.request(
                method,
                url,
                headers=self.headers,
                **kwargs
            )

            if response.status_code == 200:
                return response

            if response.status_code == 403:
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset = response.headers.get("X-RateLimit-Reset")

                if remaining == "0" and reset:
                    reset_time = int(reset)
                    sleep_for = max(reset_time - int(time.time()), 0) + 1
                    print(f"GitHub rate limited. Sleeping {sleep_for}s...", flush=True)
                    time.sleep(sleep_for)
                    continue

            print(f"GitHub request failed: {url} ({response.status_code})", flush=True)
            return None

    def github_paginate(self, url, params=None):
        results = []
        session = requests.Session()
        page = 1

        while True:
            query = params.copy() if params else {}
            query["per_page"] = 100
            query["page"] = page

            response = self.github_request(
                session,
                "GET",
                url,
                params=query
            )

            if response is None:
                break

            data = response.json()
            if not data:
                break

            page += 1
            results.extend(data)

        return results

    def get_requests_updated_since(self, item_type, per_page=100, branch=None):
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retrieved_days)
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

    def get_issue_comments(self, issues):
        comments = []
        session = requests.Session()

        for issue in issues:
            if issue.get("comments", 0) == 0:
                continue

            response = self.github_request(
                session,
                "GET",
                issue["comments_url"]
            )

            if response is None:
                continue

            comments.extend(response.json())

        return [
            c for c in comments
            if self.is_user_valid(c["user"])
        ]

    def get_documentation_license_authors(self, commits):
        doc_authors = []
        lic_authors = []

        lic_keywords = ("license", "copying", "unlicense", "notice")
        doc_keywords = (".md", "doc", "docs", "readme", "documentation")

        for commit in commits:
            message = commit["commit"]["message"].lower()
            author = commit.get("author")

            if not author:
                continue

            if any(k in message for k in doc_keywords):
                doc_authors.append(author)
            elif any(k in message for k in lic_keywords):
                lic_authors.append(author)

        return (doc_authors, lic_authors)

    def get_issue_comments(self, issues):
        comments = []

        for issue in issues:
            if issue.get("comments", 0) == 0:
                continue

            comments.extend(
                self.github_paginate(issue["comments_url"])
            )

        return [
            c for c in comments
            if self.is_user_valid(c["user"])
        ]

    def get_pull_request_reviews(self, issues):
        reviews = []
        session = requests.Session()

        for issue in issues:
            if "pull_request" not in issue:
                continue

            if issue.get("comments", 0) == 0:
                continue

            url = f"{self.base_url}/pulls/{issue['number']}/reviews"

            response = self.github_request(session, "GET", url)
            if response is None:
                continue

            for review in response.json():
                user = review.get("user")
                if user and self.is_user_valid(user):
                    reviews.append(user)

        return reviews

    def scrape_github_data(self):
        issues = self.get_requests_updated_since(item_type="issues")
        pull_requests = [
            issue for issue in issues
            if "pull_request" in issue
        ]
        pull_request_reviews = self.get_pull_request_reviews(issues=issues)
        commits = self.get_requests_updated_since(item_type="commits")
        comments = self.get_issue_comments(issues=issues)
        lic_doc_authors = self.get_documentation_license_authors(commits=commits)
        doc_authors = lic_doc_authors[0]
        lic_authors = lic_doc_authors[1]
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
                    "author": review["login"]
                } for review in pull_request_reviews
                if self.is_user_valid(review)
            ],
            "comments": [
                {
                    "body": comment["body"],
                    "author": comment["user"]["login"]
                } for comment in comments
                if self.is_user_valid(comment["user"])
            ],
            "documentation": [
                {
                    "author": author["login"]
                } for author in doc_authors
                if self.is_user_valid(author)
            ],
            "license": [
                {
                    "author": author["login"]
                } for author in lic_authors
                if self.is_user_valid(author)
            ]
        }
        return data

    def is_user_valid(self, user):
        return user["login"] is not None and user["login"] not in self.excluded_users and user["type"] != "Bot"

class ConfigScraper:
    def __init__(self, config_handler):
        self.config_handler = config_handler

if __name__ == "__main__":
    data_scraper = DataScraper()
    data_scraper.scrape_github_data()