import pandas as pd
import numpy as np
from bertopic import BERTopic
import os
from dotenv import load_dotenv
import openai
import sys
from hdbscan import HDBSCAN
from collections import defaultdict
from utils.reader import read_cols


def compile_data(verbose=False):
    """
    Reads and compiles data from Excel sheets, filters out blocked comments, and merges comment, reaction,
    and article data into a single DataFrame, which is then saved to a CSV file.

    Parameters:
    - verbose (bool): If True, prints additional information about the process.

    Returns:
    - list: A list of unique descriptions extracted from the compiled DataFrame.
    """

    print("\nreading data...\n")
    comment_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=COMMENT_SHEET_NAME,
        column_names=COMMENT_COLS)

    print("-------------------")
    print(f"comment_data['conversation_id'].nunique(): {comment_data['conversation_id'].nunique()}")
    print("-------------------")
    print(f"removing {comment_data[comment_data['final_state'] == 'blocked'].shape[0]} blocked comments...")
    comment_data = comment_data[comment_data['final_state'] != 'blocked'] # remove blocked comments ~28K

    reaction_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=REACTION_SHEET_NAME,
        column_names=REACTION_COLS)

    article_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=ARTICLE_SHEET_NAME,
        column_names=ARTICLE_COLS)

    print("\nmerging data...\n")
    compiled_df = comment_data \
        .merge(reaction_data, how='left', left_on='conv_message_id', right_on='message_id') \
        .merge(article_data, how='left', on='conversation_id').dropna()
    
    # compiled_df.to_csv('intermediate_check_compiled.csv', index=False)
    
    return compiled_df['description'].unique().tolist()

def run_topic_model(
    doc_summaries,
    n_topics=21,
    verbose=False,
    topic_summary_output_file_path='outputs/topic_summaries.csv',
    doc_topic_output_file_path='outputs/doc_topic_df.csv'):

    """
    Performs topic modeling using the BERTopic algorithm on a list of document summaries. Generates a specified number of topics, creates and saves two CSV files containing document topics and topic summaries.

    Parameters:
    - doc_summaries (list): List of document summaries to model.
    - n_topics (int): Number of topics to generate.
    - verbose (bool): If True, prints additional details about the process.
    - topic_summary_output_file_path (str): Path to save the topic summaries CSV file.
    - doc_topic_output_file_path (str): Path to save the document topics CSV file.

    Outputs:
    - Two CSV files: One containing a summary of topics and another detailing the topics assigned to each document.
    """

    print("\nPerforming topic modeling...\n")

    # initialize model
    topic_model = BERTopic(nr_topics=n_topics)

    # fit model
    topics, probabilities = topic_model.fit_transform(doc_summaries)

    # create doc topic df
    doc_topic_df = pd.DataFrame({'Topic': topics, 'Document_description': doc_summaries})

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

class OpenAIEmbedder:
    """
    A class to handle the embedding of documents using OpenAI's models.

    Attributes:
    - api_key (str): OpenAI API key for authenticating requests.
    - model (str): The specific OpenAI model to use for embedding.

    Methods:
    - fit_transform(documents): Embeds a list of documents and returns their embeddings.
    """

    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def fit_transform(self, documents):
        """
        Transforms documents into embeddings using an OpenAI model.

        Parameters:
        - documents (list): List of documents to embed.

        Returns:
        - list: List of embeddings for the input documents.
        """
        embeddings = []
        for doc in documents:
            response = openai.Embedding.create(
                input=doc,
                model=self.model,
                api_key=self.api_key
            )
            embeddings.append(response['data']['embeddings'])
        return embeddings

def run_topic_model_openai(
    doc_summaries,
    n_topics=10,
    min_topic_size=5,
    zeroshot_min_similarity=0.5, # not used
    min_samples_core_point=5,
    verbose=False,
    openai_embedder=None,
    model="text-embedding-3-large",
    topic_summary_output_file_path='outputs/topic_summaries.csv',
    doc_topic_output_file_path='outputs/doc_topic_df.csv'):

    """
    Performs topic modeling using OpenAI embeddings and HDBSCAN clustering. Saves the resulting document-topic mappings and topic summaries to CSV files.

    Parameters:
    - doc_summaries (list): Document summaries to model.
    - n_topics (int): Total number of topics to generate.
    - min_topic_size (int): Minimum cluster size for HDBSCAN.
    - zeroshot_min_similarity (float): Not used currently.
    - min_samples_core_point (int): Minimum samples for a point to be considered a core point.
    - verbose (bool): If True, prints detailed output about the process.
    - openai_embedder (OpenAIEmbedder): OpenAI embedder instance for generating embeddings.
    - model (str): OpenAI model to use for embeddings.
    - topic_summary_output_file_path (str): Path to save the topic summaries CSV file.
    - doc_topic_output_file_path (str): Path to save the document topics CSV file.

    Outputs:
    - Two CSV files: One for document-topic mappings, and another for topic summaries.
    """

    print("\nPerforming topic modeling...\n")
    
    # initialize custom hdbscan model
    custom_hdbscan_model = HDBSCAN(min_cluster_size=min_topic_size, min_samples=min_samples_core_point, metric='euclidean', prediction_data=True)
    
    # Create BERTopic instance with custom OpenAI embedder
    topic_model = BERTopic(hdbscan_model=custom_hdbscan_model, nr_topics=n_topics+1, low_memory=True, embedding_model=openai_embedder)

    # alt method
    # topic_model = BERTopic(
    #     top_n_words=10,
    #     zeroshot_min_similarity=zeroshot_min_similarity,
    #     min_topic_size=min_topic_size,
    #     embedding_model=openai_embedder,
    #     nr_topics=n_topics+1)

    # fit model
    topics, probabilities = topic_model.fit_transform(doc_summaries)

    print("\nlength of topics:")
    print(len(topics))

    # create doc topic df
    doc_topic_df = pd.DataFrame({'Topic': topics, 'Document_description': doc_summaries})


    # look at the number of docs per topic
    print("\nNumbers per topic:")
    print(doc_topic_df['Topic'].value_counts().sort_index())

    topic_number_dict = doc_topic_df['Topic'].value_counts().to_dict() 

    if verbose:
        print("\ndoc_topic_df:\n")
        print(doc_topic_df.head(5))

    # create topic summary df
    topic_summary_df = topic_model.get_topic_info()  # This gives a summary of all topics

    topic_summary_df = topic_summary_df[topic_summary_df['Count'] > 0]  # remove topics with no docs
    # topic_summary_df = topic_summary_df[topic_summary_df['Topic'] != -1]  # remove docs that don't belong to any topic
    if verbose:
        print("\ntopic_summary_df:")
        print(topic_summary_df.head(5))
    
    # save to file
    doc_topic_df.to_csv(doc_topic_output_file_path, index=False)
    print(f"\nSaved doc-topic df to {doc_topic_output_file_path}\n")
    topic_summary_df.to_csv(topic_summary_output_file_path, index=False)
    print(f"\nSaved topic summaries to {topic_summary_output_file_path}")

def topic_model_names_summaries(
    open_ai=False,
    api_key=None,
    model="text-embedding-3-large"):
    """
    Orchestrates the topic modeling process using either OpenAI or BERTopic based on a flag. Retrieves data, performs topic modeling, and saves the outputs.

    Parameters:
    - open_ai (bool): Flag to determine if OpenAI's embedding model should be used.
    - api_key (str): API key for OpenAI.
    - model (str): The OpenAI model to use if open_ai is True.

    Outputs:
    - CSV files containing document-topic mappings and topic summaries.
    """

    doc_summaries = compile_data()

    print(f"Open ai: {open_ai}")

    if open_ai:
        openai_embedder = OpenAIEmbedder(api_key, model=model)
        run_topic_model_openai(
            doc_summaries=doc_summaries,
            n_topics=N_TOPICS,
            openai_embedder=openai_embedder,
            topic_summary_output_file_path=TOPIC_SUMMARY_OUTPUT_FILE_PATH,
            doc_topic_output_file_path=DOC_TOPIC_OUTPUT_FILE_PATH)
    else:
        run_topic_model(
            doc_summaries=doc_summaries,
            n_topics=N_TOPICS,
            topic_summary_output_file_path=TOPIC_SUMMARY_OUTPUT_FILE_PATH,
            doc_topic_output_file_path=DOC_TOPIC_OUTPUT_FILE_PATH)

if __name__ == "__main__":
    OPEN_AI = True
    EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"
    N_TOPICS = 6
    TOPIC_SUMMARY_OUTPUT_FILE_PATH = "outputs/topic_summaries_filtered.csv"
    DOC_TOPIC_OUTPUT_FILE_PATH = "outputs/doc_topic_df_filtered.csv"

    ARTICLE_SHEET_NAME = "articles_data"
    COMMENT_SHEET_NAME = "comments_for_published_articles"
    REACTION_SHEET_NAME = "reaction_count_for_pub_articles"
 
    COMMENT_COLS = ['conversation_id', 'conv_message_id', 'author_id', 'written_date', 'text_content', 'final_state']
    ARTICLE_COLS = ['title', 'published_date', 'description', 'canonical_url', 'conversation_id', 'thumbnail_url'] #[article_thumbnail_alt_text, article_text, article_author]
    REACTION_COLS = [ 'message_id', 'total_views', 'total_likes']
    
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path) # Load environment variables
    API_KEY =  os.environ.get("OPENAI_API_KEY")

    topic_model_names_summaries(
        open_ai=OPEN_AI,
        api_key=API_KEY, 
        model="text-embedding-3-large")
