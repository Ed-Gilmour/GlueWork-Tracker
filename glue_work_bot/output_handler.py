import os

class OutputHandler():
    def __init__(self, output_dir, contributor_list, glue_work_report):
        self.output_dir = output_dir
        self.contributor_list = contributor_list
        self.glue_work_report = glue_work_report

    def save_output(self):
        contributor_list_path = os.path.join(self.output_dir, "contributor_list_.md")
        glue_work_report_path = os.path.join(self.output_dir, "glue_work_report.md")

        os.makedirs(os.path.dirname(contributor_list_path), exist_ok=True)
        os.makedirs(os.path.dirname(glue_work_report_path), exist_ok=True)

        with open(contributor_list_path, "w") as f:
            f.write(self.contributor_list)
        with open(glue_work_report_path, "w") as f:
            f.write(self.glue_work_report)