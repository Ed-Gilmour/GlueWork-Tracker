from dotenv import load_dotenv
from vector_indexer import VectorIndexer
from classifier_agents import GlueWorkType, MentoringAgent
from google import genai
import csv
import os

class BinaryAccuracyTester:
    def __init__(self, name):
        load_dotenv()
        self.test_indexer = VectorIndexer(name)
        self.training_indexer = VectorIndexer(name)
        # self.test_indexer.load_test_data()
        # self.training_indexer.load_training_test_data()

    def test_accuracy(self, csv_path):
        mentoring_agent = MentoringAgent()
        self.test_indexer.load_csv_data(csv_path)
        self.predicted = [""] * len(self.test_indexer.csv_data)
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                if i == 3:
                    break
                classification = mentoring_agent.classify_data(row[0])
                if classification == GlueWorkType.MENTORING:
                    predicted = "Y"
                else:
                    predicted = "N"
                self.predicted[i] = predicted
                print(i, predicted)
        self.test_indexer.save_test_csv_data(self.predicted)

if __name__ == "__main__":
    accuracy_tester = BinaryAccuracyTester("mentoring")
    accuracy_tester.test_accuracy("glue_work_bot/training_data/mentoring/mentoring_dataset.csv")