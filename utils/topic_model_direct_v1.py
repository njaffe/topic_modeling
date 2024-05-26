import pandas as pd
import numpy as np
from bertopic import BERTopic

def read_comment_text_to_df(excel_file_path, sheet_name, column_name):
    # Read the specified sheet and column
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, usecols=[column_name])
    
    # Convert all entries to strings and handle NaN values
    df[column_name] = df[column_name].fillna('missing').astype(str)
    
    # Remove special characters
    df[column_name] = df[column_name].str.replace(r'[^\x00-\x7F#&;]+', '', regex=True)
    
    # Print the first few entries to verify
    # print("First few entries:")
    # print(df[column_name].head(5))
    
    return df[column_name].tolist()

def perform_topic_modeling(documents, n_topics=20):
    print("Performing topic modeling")
    # Initialize BERTopic
    topic_model = BERTopic()
    
    # Fit the model on the documents
    original_topics, original_probabilities = topic_model.fit_transform(documents)

    # specify the number of topics
    updated_topics, updated_probs = topic_model.update_topics(documents, original_topics, n_topics)
    
    # Print topics and their probabilities
    for topic, prob in zip(updated_topics, updated_probs):
        print(f"Topic: {topic}, Probability: {prob}")
    
    # Get the most representative document for each topic
    representative_docs = topic_model.get_representative_docs()

    # Print the most representative document for each topic
    for topic, (doc_id, prob) in representative_docs.items():
        print(f"Topic {topic}: Document {doc_id} with probability {prob}")

def main(excel_file_path, sheet_name, column_name):
    documents = read_comment_text_to_df(
        excel_file_path=excel_file_path,
        sheet_name=sheet_name,
        column_name=column_name)
    
    # Perform topic modeling on the retrieved documents
    perform_topic_modeling(documents)

if __name__ == "__main__":
    excel_file_path = 'data/fox_news_comments.xlsx'
    sheet_name = "comments_for_published_articles"
    column_name = "text_content"

    main(excel_file_path,sheet_name,column_name)
