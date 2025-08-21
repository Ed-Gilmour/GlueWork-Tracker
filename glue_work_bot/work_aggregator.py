from output_handler import OutputHandler
from classifier_agents import GlueWorkType
from datetime import datetime, timezone
import argparse

class WorkAggregator():
    def __init__(self):
        self.authors = {}

    def add_work(self, author, glue_work_type):
        if author in self.authors:
            self.authors[author][glue_work_type] = self.authors[author].get(glue_work_type, 0) + 1
        else:
            self.authors[author] = { glue_work_type: 1 }

    def get_contributor_list(self): # Add contribution areas?
        current_utc_datetime = datetime.now(timezone.utc)
        contributors_str = f"[{current_utc_datetime}]\n# Glue Work Contributor List #"
        for author in self.authors.keys():
            contributors_str += f"\n- {author}"
        return contributors_str

    def get_glue_work_contribution_count(self, glue_work_type):
        total_count = 0
        for author in self.authors.keys():
            for type, count in self.authors[author].items():
                if type == glue_work_type:
                    total_count += count
        return total_count

    def get_top_contributors(self, glue_work_type, count=10):
        contributors = {}
        for author in self.authors.keys():
            for type, count in self.authors[author].items():
                if type == glue_work_type:
                    contributors[author] = count
        if len(contributors) < count:
            count = len(contributors)
        cutoff = sorted(contributors.keys(), reverse=True)[-count]
        for author, count in contributors.items():
            if count < cutoff:
                del contributors[author]
        return contributors

    def get_glue_work_report(self):
        current_utc_datetime = datetime.now(timezone.utc)
        report_str = f"[{current_utc_datetime}]\n# Glue Work Report #"
        for glue_work_type in GlueWorkType:
            total_count = self.get_glue_work_contribution_count(glue_work_type)
            report_str += f"\n## {glue_work_type.get_label()} ##"
            for author, count in self.get_top_contributors(glue_work_type).items():
                percent = (count / total_count) * 100
                report_str += f"\n- {author}: {percent:.2f}%"
        return report_str

    def output_work(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--output-dir', required=True)
        args = parser.parse_args()
        output_dir = args.output_dir
        output_handler = OutputHandler(output_dir, self.get_contributor_list(), self.get_glue_work_report())
        output_handler.save_output()