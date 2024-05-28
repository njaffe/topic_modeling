import pandas as pd
import numpy as np
from bertopic import BERTopic


def read_comment_text_to_df(excel_file_path, sheet_name, column_name):
    print("\nreading data...\n")
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

def perform_topic_modeling(docs, n_topics=21, output_file_path='outputs/topic_summaries.csv'):
    print("\nPerforming topic modeling...\n")

    # initialize model
    topic_model = BERTopic(nr_topics=n_topics)

    # fit model
    topics, probabilities = topic_model.fit_transform(docs)

    # adjust model to have correct number topics
    topic_model.reduce_topics(docs, nr_topics=n_topics)

    # get topics
    topics = topic_model.topics_  # returns list of topics for each doc 

    # topic summary df
    topic_summary_df = topic_model.get_topic_info()  # This gives a summary of all topics
    
    # Get the most representative document for each topic
    topic_rep = topic_model.get_representative_docs()

    print(f"\n topics type: {type(topics)}, topics shape: {len(topics)}, \n")
    print(f"\n topic_rep type: {type(topic_rep)}, topic_rep shape: {len(topic_rep)}, \n")
    
    print("\ntopics and representative docs:\n")
    for topic, rep_doc in topic_rep.items(): 
        print(f"Topic {topic}: Document {rep_doc}\n")
    
    # print("topic_summary_df:")
    # print(topic_summary_df.head(5))

    # remove the first row which is the [the, of, to, in, and, for, on, was, is, after] column
    topic_summary_df = topic_summary_df.iloc[1:,:]

    print("topic_summary_df:")
    print(topic_summary_df.head(5))

    # save topic summaries to csv
    topic_summary_df.to_csv(output_file_path, index=False)
    print(f"Saved topic summaries to {output_file_path}")
    return topics, topic_rep, topic_summary_df

def main():
    documents = read_comment_text_to_df(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=SHEET_NAME,
        column_name=COLUMN_NAME)
    
    perform_topic_modeling(
       docs=documents,
        n_topics=NTOPICS,
        output_file_path=OUTPUT_FILE_PATH)

if __name__ == "__main__":
    EXCEL_FILE_PATH = 'data/fox_news_comments.xlsx'
    SHEET_NAME = "articles_data"
    COLUMN_NAME = "description"
    NTOPICS = 21
    OUTPUT_FILE_PATH = 'outputs/topic_summaries.csv'
    # SHEET_NAME = "comments_for_published_articles"
    # COLUMN_NAME = "text_content"

    main()
