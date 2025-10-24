from dotenv import load_dotenv
from sentence_bert_vectorizer import VectorIndexer
from classifier_agents import MentoringAgent
from google import genai
import csv
import os

class BinaryAccuracyTester:
    def __init__(self, training_indexer, test_indexer):
        load_dotenv()
        self.training_indexer = training_indexer
        self.test_indexer = test_indexer
        self.predicted = [""] * len(test_indexer.csv_data)
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def llm_classify(self, prompt):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        ).text
        if "0" in response.lower():
            return "Y"
        else:
            return "N"

    def test_accuracy(self, csv_path):
        mentoring_agent = MentoringAgent()
        self.predicted = {}
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                predicted = self.llm_classify(mentoring_agent.get_comment_prompt(row[0]))
                self.predicted[i] = predicted
                print(i, predicted)

if __name__ == "__main__":
    test_indexer = VectorIndexer("mentoring")
    training_indexer = VectorIndexer("mentoring")
    training_indexer.load_training_test_data()
    test_indexer.load_test_data()
    accuracy_tester = BinaryAccuracyTester(training_indexer, test_indexer)
    accuracy_tester.test_accuracy("glue_work_bot/training_data/mentoring/mentoring_dataset.csv")
    test_indexer.save_test_csv_data(accuracy_tester.predicted)