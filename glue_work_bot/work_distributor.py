from classifier_agents import CodeAgent

class WorkDistributor:
    def __init__(self, data, output):
        self.output = output
        self.data = data

    def distribute_work(self):
        code_agent = CodeAgent()
        for i in range(len(self.data["issues"])):
            issue = self.data["issues"][i]
            self.output.add_contributor(issue["author"])
            if i < 3:
                self.output.add_classification(code_agent.classify_data(code_agent.get_issue_prompt(issue)))
        for i in range(len(self.data["pull_requests"])):
            pull_request = self.data["pull_requests"][i]
            self.output.add_contributor(pull_request["author"])
            if i < 3:
                self.output.add_classification(code_agent.classify_data(code_agent.get_pull_request_prompt(pull_request)))
        for i in range(len(self.data["commits"])):
            commit = self.data["commits"][i]
            self.output.add_contributor(commit["author"])
            if i < 3:
                self.output.add_classification(code_agent.classify_data(code_agent.get_commit_prompt(commit)))