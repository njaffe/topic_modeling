import pandas as pd
import numpy as np
from bertopic import BERTopic


def read_single_column(
    excel_file_path, 
    sheet_name, 
    column_name,
    verbose=False):

    print(f"\nreading {column_name}...\n")
    # Read the specified sheet and column
    df = pd.read_excel(
        excel_file_path, 
        sheet_name=sheet_name, 
        usecols=[column_name])
    
    # Convert all entries to strings and handle NaN values
    df[column_name] = df[column_name].fillna('missing').astype(str)
    
    # Remove special characters
    df[column_name] = df[column_name].str.replace(r'[^\x00-\x7F#&;]+', '', regex=True)
    
    # Print the first few entries to verify
    if verbose:
        print(f"First few entries of {column_name}:")
        print(df[column_name].head(5))
    
    return df[column_name].tolist()

def topic_model(
    name_summary_dict,
    n_topics=21,
    verbose=False,
    topic_summary_output_file_path='outputs/topic_summaries.csv',
    doc_topic_output_file_path='outputs/doc_topic_df.csv'):

    """
    inputs:
    name_summary_dict: dictionary with keys as doc names and values as summaries
    n_topics: number of topics to generate
    output_file_path: path to save topic summaries
    """

    print("\nPerforming topic modeling...\n")
    doc_summaries = list(name_summary_dict.values())

    # initialize model
    topic_model = BERTopic(nr_topics=n_topics)

    # fit model
    topics, probabilities = topic_model.fit_transform(doc_summaries)

    # adjust model to have correct number topics
    topic_model.reduce_topics(doc_summaries, nr_topics=n_topics)

    # get topics
    topics = topic_model.topics_  # returns list of topics for each doc 

    # create doc topic df
    doc_topic_df = pd.DataFrame({'Topic': topics, 'Document_description': doc_summaries})

    # join with names
    doc_names = list(name_summary_dict.keys())
    assert len(doc_names) == len(doc_topic_df), \
        "Error: Length of name_summary_dict does not match length of doc_topic_df"
    doc_topic_df['Document_name'] = doc_names

    # look at the number of docs per topic
    print("\nNumbers per topic:")
    print(doc_topic_df['Topic'].value_counts().sort_index())
    doc_topic_df = doc_topic_df[doc_topic_df['Topic'] != -1]  # remove docs that don't belong to any topic

    if verbose:
        print("\ndoc_topic_df:\n")
        print(doc_topic_df.head(5))

    # create topic summary df
    topic_summary_df = topic_model.get_topic_info()  # This gives a summary of all topics

    topic_summary_df = topic_summary_df[topic_summary_df['Count'] > 0]  # remove topics with no docs
    topic_summary_df = topic_summary_df[topic_summary_df['Topic'] != -1]  # remove docs that don't belong to any topic
    if verbose:
        print("\ntopic_summary_df:")
        print(topic_summary_df.head(5))
    
    # save to file
    doc_topic_df.to_csv(doc_topic_output_file_path, index=False)
    print(f"\nSaved doc-topic df to {doc_topic_output_file_path}\n")
    topic_summary_df.to_csv(topic_summary_output_file_path, index=False)
    print(f"\nSaved topic summaries to {topic_summary_output_file_path}")

def topic_model_names_summaries():
    doc_names = read_single_column(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=SHEET_NAME,
        column_name=NAME_COLUMN_NAME)

    doc_summaries = read_single_column(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=SHEET_NAME,
        column_name=SUMMARY_COLUMN_NAME)
    
    topic_model(
        name_summary_dict=dict(zip(doc_names, doc_summaries)),
        n_topics=N_TOPICS,
        topic_summary_output_file_path=TOPIC_SUMMARY_OUTPUT_FILE_PATH,
        doc_topic_output_file_path=DOC_TOPIC_OUTPUT_FILE_PATH)

if __name__ == "__main__":
    EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"
    SHEET_NAME = "articles_data"
    NAME_COLUMN_NAME = "title"
    SUMMARY_COLUMN_NAME = "description"
    N_TOPICS = 21
    TOPIC_SUMMARY_OUTPUT_FILE_PATH = "outputs/topic_summaries.csv"
    DOC_TOPIC_OUTPUT_FILE_PATH = "outputs/doc_topic_df.csv"

    ARTICLE_SHEET_NAME = "articles_data"
    COMMENT_SHEET_NAME = "comments_for_published_articles"

    ARTICLE_COLS = ['title', 'published_date', 'description', 'canonical_url', 'conversation_id', 'thumbnail_url'] #[article_thumbnail_alt_text, article_text, article_author]
    COMMENT_COLS = ['conversation_id', 'author_id', 'written_date', 'text_content']
    OUTPUT_FILE_PATH = 'outputs/engagements.csv'
    DOC_TOPIC_DF = 'outputs/doc_topic_df.csv'

    topic_model_names_summaries()
