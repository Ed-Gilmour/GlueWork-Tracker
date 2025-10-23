import csv
from data_scraper import GitHubScraper
from pathlib import Path

class TrainingDataCollector:
    RETRIEVED_DAYS = 30

    def __init__(self, name):
        self.data_scraper = GitHubScraper(self.RETRIEVED_DAYS)
        script_dir = Path(__file__).parent
        self.data_path = script_dir / f"training_data/{name}/{name}_dataset.csv"

    def collect_mentoring_data(self):
        issues = self.data_scraper.get_requests_updated_since(item_type="issues")
        pull_requests_urls = self.data_scraper.get_all_pull_request_urls(issues=issues)
        comments = self.data_scraper.get_all_comments(urls=pull_requests_urls)

        rows = []
        for comment in comments:
            rows.append({
                "body": comment["body"]
            })

        with open(self.data_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["body"])
            writer.writeheader()
            writer.writerows(rows)

if __name__ == "__main__":
    collector = TrainingDataCollector("mentoring")
    collector.collect_mentoring_data()