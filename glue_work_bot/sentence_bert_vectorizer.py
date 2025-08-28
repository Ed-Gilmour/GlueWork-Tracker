from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from pathlib import Path
import faiss
import json

class VectorIndexer:
    SCRIPT_DIR = Path(__file__).parent

    MENTORING_TRAINING_PATH = SCRIPT_DIR / "training_data/mentoring_training_dataset.csv"
    MENTORING_DATA_PATH = SCRIPT_DIR / "cached_data/mentoring_data.json"
    MENTORING_INDEX_PATH = SCRIPT_DIR / "cached_data/mentoring_index.faiss"

    MENTORING_TEST_DATA_PATH = SCRIPT_DIR / "cached_data/mentoring_test_data.json"
    MENTORING_TRAINING_TEST_DATA_PATH = SCRIPT_DIR / "cached_data/mentoring_training_test_data.json"
    MENTORING_TEST_INDEX_PATH = SCRIPT_DIR / "cached_data/mentoring_test_index.faiss"

    def __init__(self):
        self.model = SentenceTransformer("all-mpnet-base-v2")
        self.index = None
        self.data = {}

    def encode_texts(self):
        embeddings = self.model.encode(list(self.data.keys()), convert_to_tensor=False)
        return np.array(embeddings).astype("float32")

    def build_index(self, embeddings_np):
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_np)

    def save_index(self, index_path):
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
            else:
                self.data = dict(zip(train_df[key_name], train_df[value_name]))
        else:
            self.data = dict(zip(df[key_name], df[value_name]))
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load_csv_data(self, data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def store_mentoring_data(self):
        self.save_csv_data(self.MENTORING_TRAINING_PATH, "comments", "mentoring", self.MENTORING_DATA_PATH)
        self.build_index(self.encode_texts())
        self.save_index(self.MENTORING_INDEX_PATH)

    def load_mentoring_data(self):
        self.load_csv_data(self.MENTORING_DATA_PATH)
        self.load_index(self.MENTORING_INDEX_PATH)

    def store_mentoring_test_data(self):
        self.save_csv_data(self.MENTORING_TRAINING_PATH, "comments", "mentoring", self.MENTORING_TEST_DATA_PATH, 0.2, "mentoring", True)

    def store_mentoring_training_test_data(self):
        self.save_csv_data(self.MENTORING_TRAINING_PATH, "comments", "mentoring", self.MENTORING_TRAINING_TEST_DATA_PATH, 0.2, "mentoring", False)
        self.build_index(self.encode_texts())
        self.save_index(self.MENTORING_TEST_INDEX_PATH)

    def load_mentoring_test_data(self):
        self.load_csv_data(self.MENTORING_TEST_DATA_PATH)

    def load_mentoring_training_test_data(self):
        self.load_csv_data(self.MENTORING_TRAINING_TEST_DATA_PATH)
        self.load_index(self.MENTORING_TEST_INDEX_PATH)