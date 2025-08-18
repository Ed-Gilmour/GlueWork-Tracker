from classifier_agents import CodeAgent

class WorkDistributor:
    def __init__(self, data, output):
        self.output = output
        self.data = data

    def distribute_work(self):
        code_agent = CodeAgent()
        for issue in self.data["issues"]:
            self.output.add_contributor(issue["author"])
            self.output.add_classification(code_agent.classify_data(code_agent.get_issue_prompt(issue)))