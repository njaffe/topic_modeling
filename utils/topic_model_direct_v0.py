import faiss
import numpy as np
from bertopic import BERTopic
import pandas as pd

def load_faiss_index(index_path='data/vector_db'):
    # Load the FAISS index
    return faiss.read_index(index_path)

def search_faiss_index(index, query_vector, num_documents=10):
    # Assuming the query vector is precomputed and normalized if necessary
    distances, indices = index.search(np.array([query_vector]), num_documents)
    return indices[0]

def retrieve_documents(indices):
    # Retrieve documents from your data storage based on the indices
    # Here you would typically access your document storage
    documents = [f"Document {i}" for i in indices]  # Placeholder for document retrieval
    return documents

def read_comment_text_to_df(excel_file_path, sheet_name, column_name):
    # Read the specified sheet and column
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, usecols=[column_name])
    
    # Rename the column to 'text_content'
    df.rename(columns={column_name: 'text_content'}, inplace=True)
    print("read in comment text column:")
    # print("df head")
    # print(df.head())
    # remove special characters
    return [x for x in df['text_content']]

def perform_topic_modeling(documents):
    print("performing topic modeling")
    # Initialize BERTopic
    topic_model = BERTopic()
    
    # Fit the model on the documents
    topics, probabilities = topic_model.fit_transform(documents)
    
    # Print topics and their probabilities
    for topic, prob in zip(topics, probabilities):
        print(f"Topic: {topic}, Probability: {prob}")

def main():
    # # Load the FAISS index
    # index = load_faiss_index()
    
    # # Example query vector, replace with actual data
    # query_vector = np.random.rand(128).astype('float32')  # Adjust size to match your index
    
    # # Search the index with the query vector
    # indices = search_faiss_index(index, query_vector)
    
    # # Retrieve documents based on the indices from the FAISS search
    # # documents = retrieve_documents(indices)

    documents = read_comment_text_to_df(
        excel_file_path='data/fox_news_comments.xlsx',
        sheet_name="comments_for_published_articles",
        column_name="text_content")
    
    # Perform topic modeling on the retrieved documents
    perform_topic_modeling(documents)

if __name__ == "__main__":
    main()
