from classifier_agents import CodeAgent, MentoringAgent, CommunityAgent, GlueWorkType
from work_aggregator import WorkAggregator

class WorkDistributor:
    def __init__(self, data):
        self.aggregator = WorkAggregator()
        self.data = data

    def distribute_work(self):
        github_data = self.data["github"]
        stackexchange_data = self.data["stackexchange"]
        code_agent = CodeAgent(self.aggregator)
        for i in range(len(github_data["issues"])):
            issue = github_data["issues"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = code_agent.classify_code_text(issue["body"])
            self.aggregator.add_work(issue["author"], classification)
        for i in range(len(github_data["pull_requests"])):
            pull_request = github_data["pull_requests"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = code_agent.classify_code_text(pull_request["body"])
            self.aggregator.add_work(pull_request["author"], classification)
        for i in range(len(github_data["commits"])):
            commit = github_data["commits"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = code_agent.classify_code_text(commit["message"])
            self.aggregator.add_work(commit["author"], classification)

        mentoring_agent = MentoringAgent(self.aggregator)
        for i in range(len(github_data["comments"])):
            comment = github_data["comments"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = mentoring_agent.classify_mentoring_text(comment["body"])
            self.aggregator.add_work(comment["author"], classification)

        community_agent = CommunityAgent(self.aggregator)
        for i in range(len(stackexchange_data["replies"])):
            post = stackexchange_data["replies"][i]
            classification = GlueWorkType.UNKNOWN
            if i < 3:
                classification = community_agent.classify_community_text(post["body"])
            self.aggregator.add_work(post["author"], classification)

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