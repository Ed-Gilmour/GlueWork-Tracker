from dotenv import load_dotenv
from sentence_bert_vectorizer import VectorIndexer
from google import genai
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
        if "y" in response.lower():
            return "Y"
        else:
            return "N"

    def get_mentoring_prompt(self, text):
        return f"""
Classify the following comment as either mentoring or not mentoring.
It's mentoring if it is an instruction, suggestion, or mechanism to fix errors.

Comment to classify:
{text}

{self.get_rag_data(text)}

Answer with only Y for mentoring, or N for not mentoring. Nothing else and no explanation.
"""

    def get_rag_data(self, query, k=3):
        responses = self.training_indexer.search(query, k)
        data = ""
        for text, distance in responses:
            classification = self.training_indexer.data[text]
            if classification == "Y":
                classification = "Yes"
            else:
                classification = "No"
            data += f"\nExample:\n{text}\nClassification for mentoring and support: {classification}\n"
        return data

    def test_accuracy(self):
        i = 0
        for text, actual in self.test_indexer.data.items():
            predicted = self.llm_classify(self.get_mentoring_prompt(text))
            self.predicted[i] = predicted
            print(i, predicted)
            i += 1

if __name__ == "__main__":
    test_indexer = VectorIndexer("mentoring")
    training_indexer = VectorIndexer("mentoring")
    training_indexer.load_training_test_data()
    test_indexer.load_test_data()
    accuracy_tester = BinaryAccuracyTester(training_indexer, test_indexer)
    accuracy_tester.test_accuracy()
    test_indexer.save_test_csv_data(accuracy_tester.predicted)