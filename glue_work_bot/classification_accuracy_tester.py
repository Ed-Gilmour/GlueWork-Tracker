from sentence_bert_vectorizer import VectorIndexer
from classifier_agents import ClassifierAgent
import ollama

class BinaryAccuracyTester:
    def __init__(self, training_indexer, test_indexer):
        self.training_indexer = training_indexer
        self.test_indexer = test_indexer
        self.predicted = [""] * len(test_indexer.csv_data)

    def llm_classify(self, prompt):
        response = ClassifierAgent.strip_think_tags(text=ollama.generate(model="deepseek-r1:7b", prompt=prompt)["response"])
        if "y" in response.lower():
            return "Y"
        else:
            return "N"

    def get_mentoring_prompt(self, text):
        return f"""
Classify the following comment as either mentoring or not mentoring.
It's mentoring if it is an instruction, suggestion, or mechanism to fix errors.

Instruction example:
@caidezhi next time please run `mvn verify` on the project before creating a PR. You would have noticed that checkstyle would have complaint. I'll fix it on our master.

Suggestion example:
I would still duplicate a WordCount copy into the Spark runner like I did in https://github.com/apache/incubator-beam/pull/539 because it's widely used in the runner's unit tests.
Maybe this could be removed after the runner is mature enough to rely only on the RunnableOnService tests.
And like I also said in https://github.com/apache/incubator-beam/pull/539, transitive dependency is your enemy here, I can't come up with something better than adding Spark provided/runtime dependencies.
This could be resolved by removing the provided scope on spark dependencies from the Spark runner, but I don't think that's a good idea. Looping in @jbonofre WDYT ? this could make the Spark runner Jar become very heavy.. and what about different Spark distributions on clusters ?

Mechanism to fix errors example:
That is fine. @milamberspace would you mind just doing a force push again to kick off jenkins. I have seen other jenkins runs passing so I think jenkins is just not happy when it has a lot of load.

Not mentoring examples:
- LGTM, Merging into master and release-1.13
- This PR currently has merge conflicts, but #1515 is next in line, so you may want to wait till it is merged before you fix these conflicts.  
- This is not ready. Missing apache header on the new file and there is no test. No idea what this is fixing. 

Comment to classify:
{text}

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
            data += f"Example:\n{text}\nClassification for mentoring and support: {classification}\n"
        return data

    def test_accuracy(self):
        i = 0
        for text, actual in self.test_indexer.data.items():
            predicted = self.llm_classify(self.get_mentoring_prompt(text))
            self.predicted[i] = predicted
            print(i, predicted)
            i += 1

if __name__ == "__main__":
    test_indexer = VectorIndexer()
    training_indexer = VectorIndexer()
    training_indexer.load_mentoring_training_test_data()
    test_indexer.load_mentoring_test_data()
    accuracy_tester = BinaryAccuracyTester(training_indexer, test_indexer)
    accuracy_tester.test_accuracy()
    test_indexer.save_mentoring_test_csv_data(accuracy_tester.predicted)