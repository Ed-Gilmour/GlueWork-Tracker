from datetime import datetime, timezone
import os

class OutputHandler():
    def __init__(self, output_dir, config_handler):
        self.output_dir = output_dir
        self.config_handler = config_handler

    def save_output(self):
        config_loaded = self.config_handler.load_config()

        contributor_list_path = os.path.join(self.output_dir, "contributor_list_.md")
        glue_work_report_path = os.path.join(self.output_dir, "glue_work_report.md")

        os.makedirs(os.path.dirname(contributor_list_path), exist_ok=True)
        os.makedirs(os.path.dirname(glue_work_report_path), exist_ok=True)

        with open(contributor_list_path, "w") as f:
            if config_loaded:
                f.write("Test Glue Work Contributor List.")
            else:
                current_utc_datetime = datetime.now(timezone.utc)
                f.write(f"[{current_utc_datetime}] Error loading config:\n{self.config_handler.get_load_exception()}")
        with open(glue_work_report_path, "w") as f:
            if config_loaded:
                f.write("Test Glue Work Report. Here are the URLs configured.")
                for url in self.config_handler.get_urls():
                    f.write("\n" + url)
            else:
                current_utc_datetime = datetime.now(timezone.utc)
                f.write(f"[{current_utc_datetime}] Error loading config:\n{self.config_handler.get_load_exception()}")