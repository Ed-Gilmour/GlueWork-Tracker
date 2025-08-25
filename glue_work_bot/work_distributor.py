from classifier_agents import CodeAgent, GlueWorkType
from work_aggregator import WorkAggregator
from deepseek_tokenizer import DeepseekTokenizer
from enum import Enum

class WorkType(Enum):
    ISSUE = 0
    PULL_REQUEST = 1
    COMMIT = 2

    def get_label(self):
        labels = {
            WorkType.ISSUE: "issues",
            WorkType.PULL_REQUEST: "pull_requests",
            WorkType.COMMIT: "commits",
        }
        return labels[self]

class WorkDistributor:
    def __init__(self, data):
        self.aggregator = WorkAggregator()
        self.code_agent = CodeAgent(self.aggregator)
        self.tokenizer = DeepseekTokenizer()
        self.data = data

    def distribute_work(self):
        self.add_classifications(WorkType.ISSUE)
        self.add_classifications(WorkType.PULL_REQUEST)
        self.add_classifications(WorkType.COMMIT)
        for i in range(len(self.data["reviews"])):
            review = self.data["reviews"][i]
            self.aggregator.add_work(review["author"], GlueWorkType.CODE_REVIEW)
        self.aggregator.output_work()

    # TODO: Remove print and end break
    def add_classifications(self, work_type):
        label = work_type.get_label()
        i = 0
        class_len = len(self.data[label])
        while i < class_len:

            authors = []
            prompt_data = []
            prompt = ""

            while self.tokenizer.get_token_count(prompt) < DeepseekTokenizer.TOKEN_LIMIT and i < class_len - 1:
                class_data = self.data[label][i]

                def get_prompt_by_type(data):
                    if work_type == WorkType.ISSUE:
                        return self.code_agent.get_issue_prompt(data)
                    elif work_type == WorkType.PULL_REQUEST:
                        return self.code_agent.get_pull_request_prompt(data)
                    elif work_type == WorkType.COMMIT:
                        return self.code_agent.get_commit_prompt(data)

                if self.tokenizer.get_token_count(get_prompt_by_type(prompt_data + [class_data])) > DeepseekTokenizer.TOKEN_LIMIT:
                    if len(prompt_data) <= 0:
                        i += 1
                    break

                prompt_data.append(class_data)
                authors.append(class_data["author"])
                prompt = get_prompt_by_type(prompt_data)
                i += 1

            classifications = self.code_agent.classify_data(prompt)

            for j in range(len(classifications)):
                print(f"{work_type.get_label()} work {j} by {authors[j]} is {classifications[j].get_label()}", flush=True)
                self.aggregator.add_work(authors[j], classifications[j])

            break