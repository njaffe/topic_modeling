import argparse
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


api_key = os.environ["OPENAI_API_KEY"]
CHROMA_PATH = "chroma"

def query_database():
    print("Querying database")

    # CLI arg parsing
    parser = argparse.ArgumentParser(description="Query the database.")
    parser.add_argument("query_text", type=str, help="Query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Load the database
    embedding_function = OpenAIEmbeddings(openai_api_key=api_key)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Load results
    results = db.similarity_search_with_relevance_scores(query_text, k=3)

    # Check results
    if len(results) == 0 or results[0][1] < 0.7:
        print("No results found.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    print(context_text)

if __name__ == "__main__":
    query_database()