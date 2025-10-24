from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from pathlib import Path
import os
import faiss
import json

class DataPaths:
    def __init__(self, name):
        script_dir = Path(__file__).parent
        self.training_path = script_dir / f"training_data/{name}/{name}_training_dataset.csv"
        self.data_path = script_dir / f"cached_data/{name}/{name}_data.json"
        self.index_path = script_dir / f"cached_data/{name}/{name}_index.faiss"
        self.test_csv_path = script_dir / f"training_data/{name}/{name}_test_dataset.csv"
        self.test_data_path = script_dir / f"cached_data/{name}/{name}_test_data.json"
        self.training_test_data_path = script_dir / f"cached_data/{name}/{name}_training_test_data.json"
        self.test_index_path = script_dir / f"cached_data/{name}/{name}_test_index.faiss"
        self.cached_path = script_dir / f"cached_data/{name}"
        self.training_path = script_dir / f"training_data/{name}"


class VectorIndexer:
    def __init__(self, name):
        self.model = SentenceTransformer("all-mpnet-base-v2")
        self.index = None
        self.data = {}
        self.name = name
        self.paths = DataPaths(name)
        self.csv_data = None

    def encode_texts(self):
        embeddings = self.model.encode(list(self.data.keys()), convert_to_tensor=False)
        return np.array(embeddings).astype("float32")

    def build_index(self, embeddings_np):
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_np)

    def save_index(self, index_path):
        os.makedirs(self.paths.cached_path, exist_ok=True)
        faiss.write_index(self.index, str(index_path))

    def load_index(self, index_path):
        self.index = faiss.read_index(str(index_path))

    def search(self, query_text, k=1):
        query_embedding = self.model.encode([query_text]).astype("float32")
        distances, indices = self.index.search(query_embedding, k)
        return [(list(self.data.keys())[i], distances[0][idx]) for idx, i in enumerate(indices[0])]

    def save_csv_data(self, csv_path, key_name, value_name, data_path, split=0, label="", is_test=False):
        df = pd.read_csv(csv_path)
        if split != 0:
            train_df, test_df = train_test_split(
                df,
                test_size=split,
                stratify=df[label],
                random_state=42
            )
            if is_test:
                self.data = dict(zip(test_df[key_name], test_df[value_name]))
                self.csv_data = pd.DataFrame(test_df)
            else:
                self.data = dict(zip(train_df[key_name], train_df[value_name]))
                self.csv_data = pd.DataFrame(train_df)
        else:
            self.data = dict(zip(df[key_name], df[value_name]))
        os.makedirs(self.paths.cached_path, exist_ok=True)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load_index_data(self, data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def load_csv_data(self, data_path):
        df = pd.read_csv(data_path)
        self.csv_data = pd.DataFrame(df)

    def store_data(self):
        self.save_csv_data(self.paths.training_path, "comments", self.name, self.paths.data_path)
        self.build_index(self.encode_texts())
        self.save_index(self.paths.index_path)

    def load_data(self):
        self.load_index_data(self.paths.data_path)
        self.load_index(self.paths.index_path)

    def store_test_data(self):
        self.save_csv_data(self.paths.training_path, "comments", self.name, self.paths.test_data_path, 0.2, self.name, True)

    def save_test_csv_data(self, new_column):
        self.csv_data["Predicted"] = new_column
        os.makedirs(self.paths.training_path, exist_ok=True)
        self.csv_data.to_csv(self.paths.test_csv_path, index=False)

    def store_training_test_data(self):
        self.save_csv_data(self.paths.training_path, "comments", self.name, self.paths.training_test_data_path, 0.2, self.name, False)
        self.build_index(self.encode_texts())
        self.save_index(self.paths.test_index_path)

    def load_test_data(self):
        self.load_index_data(self.paths.test_data_path)
        self.load_csv_data(self.paths.test_csv_path)

    def load_training_test_data(self):
        self.load_index_data(self.paths.training_test_data_path)
        self.load_index(self.paths.test_index_path)

    def load_classification_data(self):
        self.load_index_data(self.paths.data_path)
        self.load_index(self.paths.index_path)