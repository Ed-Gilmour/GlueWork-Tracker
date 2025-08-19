from datetime import datetime, timezone
import os

class OutputHandler():
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.contributors = []
        self.classifications = []

    def save_output(self):
        contributor_list_path = os.path.join(self.output_dir, "contributor_list_.md")
        glue_work_report_path = os.path.join(self.output_dir, "glue_work_report.md")

        os.makedirs(os.path.dirname(contributor_list_path), exist_ok=True)
        os.makedirs(os.path.dirname(glue_work_report_path), exist_ok=True)

        current_utc_datetime = datetime.now(timezone.utc)

        contributors_str = f"[{current_utc_datetime}]\nGlue Work Contributor List:"
        for contributor in self.contributors:
            contributors_str += f"\n- {contributor}"
        report_str = f"[{current_utc_datetime}]\nGlue Work Report:"
        for classification in self.classifications:
            report_str += f"\n{classification}"

        with open(contributor_list_path, "w") as f:
            f.write(contributors_str)
        with open(glue_work_report_path, "w") as f:
            f.write(report_str)

    def add_contributor(self, contributor):
        if contributor not in self.contributors:
            self.contributors.append(contributor)

    def add_classification(self, classification):
        self.classifications.append(classification)