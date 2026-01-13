from classifier_agents import CodeAgent, MentoringAgent, GlueWorkType
from work_aggregator import WorkAggregator
import argparse

class WorkDistributor:
    def __init__(self, data):
        parser = argparse.ArgumentParser()
        parser.add_argument('--output-dir', required=True)
        parser.add_argument('--config-file', required=True)
        args = parser.parse_args()
        output_dir = args.output_dir
        config_file = args.config_file
        self.aggregator = WorkAggregator(config_file, output_dir)
        self.data = data

    def distribute_work(self):
        github_data = self.data["github"]
        code_agent = CodeAgent(self.aggregator)
        for i in range(len(github_data["issues"])):
            issue = github_data["issues"][i]
            classification = code_agent.classify_code_text(issue["body"])
            self.aggregator.add_work(issue["author"], classification)
        for i in range(len(github_data["pull_requests"])):
            pull_request = github_data["pull_requests"][i]
            classification = code_agent.classify_code_text(pull_request["body"])
            self.aggregator.add_work(pull_request["author"], classification)
        for i in range(len(github_data["commits"])):
            commit = github_data["commits"][i]
            classification = code_agent.classify_code_text(commit["message"])
            self.aggregator.add_work(commit["author"], classification)

        mentoring_agent = MentoringAgent(self.aggregator)
        for i in range(len(github_data["comments"])):
            comment = github_data["comments"][i]
            classification = mentoring_agent.classify_mentoring_text(comment["body"])
            self.aggregator.add_work(comment["author"], classification)

        for i in range(len(github_data["reviews"])):
            review = github_data["reviews"][i]
            self.aggregator.add_work(review["author"], GlueWorkType.CODE_REVIEW)
        for i in range(len(github_data["documentation"])):
            documentation = github_data["documentation"][i]
            self.aggregator.add_work(documentation["author"], GlueWorkType.DOCUMENTATION)
        for i in range(len(github_data["license"])):
            license = github_data["license"][i]
            self.aggregator.add_work(license["author"], GlueWorkType.LICENSE)
        for i in range(len(github_data["issues"])):
            issue = github_data["issues"][i]
            self.aggregator.add_work(issue["author"], GlueWorkType.REPORTING)

        self.aggregator.output_work()