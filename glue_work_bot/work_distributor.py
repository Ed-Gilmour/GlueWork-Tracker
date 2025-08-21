from classifier_agents import CodeAgent, GlueWorkType
from work_aggregator import WorkAggregator

class WorkDistributor:
    def __init__(self, data):
        self.aggregator = WorkAggregator()
        self.data = data

    def distribute_work(self):
        code_agent = CodeAgent(self.aggregator)
        for i in range(len(self.data["issues"])):
            issue = self.data["issues"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = code_agent.classify_data(code_agent.get_issue_prompt(issue))
            print(f"Issue {i}: {classification.get_label()}", flush=True)
            self.aggregator.add_work(issue["author"], classification)
        for i in range(len(self.data["pull_requests"])):
            pull_request = self.data["pull_requests"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = code_agent.classify_data(code_agent.get_pull_request_prompt(pull_request))
            print(f"Pull Request {i}: {classification.get_label()}", flush=True)
            self.aggregator.add_work(pull_request["author"], classification)
        for i in range(len(self.data["commits"])):
            commit = self.data["commits"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = code_agent.classify_data(code_agent.get_commit_prompt(commit))
            print(f"Commit {i}: {classification.get_label()}", flush=True)
            self.aggregator.add_work(commit["author"], classification)
        for i in range(len(self.data["reviews"])):
            review = self.data["reviews"][i]
            self.aggregator.add_work(review["author"], GlueWorkType.CODE_REVIEW)
        self.aggregator.output_work()