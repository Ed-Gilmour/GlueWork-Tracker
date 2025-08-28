import pandas as pd
import ollama

class BinaryAccuracyTester:
    def __init__(self, csv_path, text_key, classification_key):
        self.csv_path = csv_path
        self.text_key = text_key
        self.classification_key = classification_key
        self.csv = pd.read_csv("training_data/mentoring_training_dataset.csv")
        self.true = self.csv["mentoring"].tolist()
        self.predicted = []

    def llm_classify(self, text):
        response = ollama.generate(model="deepseek-r1:7b", prompt=self.get_mentoring_prompt(text))
        return response

    def get_mentoring_prompt(self, text):
        return f"""
You specialize in classifying mentoring and support data.

Text to classify:
{text}

Answer with only Y for mentoring and support, or N for not mentoring and support.
Answer with only Y or N. Nothing else and no explanation.
"""

    def test_accuracy(self):
        for text in self.csv[self.text_key]:
            prediction = self.llm_classify(text)
            self.predicted.append(prediction)

        for actual, predicted, text in zip(self.true, self.predicted, self.csv[self.text_key]):
            print(f"Data: {text}\nActual: {actual}, Predicted: {predicted}\n")

if __name__ == "__main__":
    tester = BinaryAccuracyTester("training_data/mentoring_training_dataset.csv", "comments", "mentoring")
    tester.test_accuracy()