import csv
from data_scraper import GitHubScraper
from pathlib import Path

class TrainingDataCollector:
    def __init__(self):
        self.data_scraper = GitHubScraper(retrieved_days=7)

    def collect_issue_data(self, path):
        issues = self.data_scraper.get_requests_updated_since(item_type="issues")
        pull_requests_urls = self.data_scraper.get_all_pull_request_urls(issues=issues)
        comments = []
        for url in pull_requests_urls:
            comments.extend(self.data_scraper.get_issue_comments(url.split("/")[-1]))

        rows = [
            {
                "body": comment["body"],
            } for comment in comments
            if self.data_scraper.is_user_valid(comment["user"])
        ]

        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["body"])
            writer.writeheader()
            writer.writerows(rows)

if __name__ == "__main__":
    collector = TrainingDataCollector()
    SCRIPT_DIR = Path(__file__).parent
    collector.collect_issue_data(SCRIPT_DIR / "training_data/mentoring/mentoring_dataset.csv")