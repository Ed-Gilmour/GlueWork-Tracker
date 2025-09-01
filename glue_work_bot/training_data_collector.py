import csv
from data_scraper import GitHubScraper
from pathlib import Path

class TrainingDataCollector:
    SCRIPT_DIR = Path(__file__).parent

    QUALITY_ASSURANCE_DATA_PATH = SCRIPT_DIR / "training_data/quality_assurance_dataset.csv"
    MAINTENANCE_DATA_PATH = SCRIPT_DIR / "training_data/maintenance_dataset.csv"

    def __init__(self):
        self.data_scraper = GitHubScraper(retrieved_days=7)

    def collect_issue_data(self, path):
        issues = self.data_scraper.get_requests_updated_since(item_type="issues")

        rows = []
        for issue in issues:
            rows.append({
                "number": issue["number"],
                "body": issue.get("body", ""),
            })

        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["number", "body"])
            writer.writeheader()
            writer.writerows(rows)

if __name__ == "__main__":
    collector = TrainingDataCollector()
    collector.collect_issue_data(collector.QUALITY_ASSURANCE_DATA_PATH)