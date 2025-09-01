import csv
from data_scraper import GitHubScraper
from pathlib import Path

class TrainingDataCollector:
    SCRIPT_DIR = Path(__file__).parent

    QUALITY_ASSURANCE_DATA_PATH = SCRIPT_DIR / "training_data/quality_assurance_dataset.csv"

    def __init__(self):
        self.data_scraper = GitHubScraper(retrieved_days=1)

    def collect_quality_assurance_data(self):
        issues = self.data_scraper.get_requests_updated_since(item_type="issues")

        rows = []
        for issue in issues:
            rows.append({
                "title": issue["title"],
                "body": issue.get("body", ""),
                "author": issue["user"]["login"]
            })

        with open(self.QUALITY_ASSURANCE_DATA_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "body", "author"])
            writer.writeheader()
            writer.writerows(rows)

if __name__ == "__main__":
    collector = TrainingDataCollector()
    collector.collect_quality_assurance_data()