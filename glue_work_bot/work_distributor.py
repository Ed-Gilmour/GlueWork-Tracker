from classifier_agents import CodeAgent

class WorkDistributor:
    def __init__(self, data, output):
        self.output = output
        self.data = data

    def distribute_work(self):
        print("Distribute work")
        code_agent = CodeAgent()
        for i in range(len(self.data["issues"])):
            issue = self.data["issues"][i]
            self.output.add_contributor(issue["author"])
            if i < 2:
                self.output.add_classification(code_agent.classify_data(code_agent.get_issue_prompt(issue)))