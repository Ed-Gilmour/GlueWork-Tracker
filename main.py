from github_scraper import GitHubScraper
from sentence_bert_vectorizer import VectorIndexer
import os

def main():
    indexer = VectorIndexer()

    if os.path.exists("test_index.faiss"):
        indexer.load_index("test_database")
    else:
        scraper = GitHubScraper()
        texts = []
        issues = scraper.get_issues()

        for issue in issues:
            texts.append(scraper.get_issue_str(issue))

        embeddings = indexer.encode_texts(texts)
        indexer.build_index(embeddings)
        indexer.save_index("test_database")

    results = indexer.search("Is there an issue on linux-17 losing external connection from a phone?", k=5)
    for match, score in results:
        print(f"Match: {match} (Distance: {score:.4f})")

main()