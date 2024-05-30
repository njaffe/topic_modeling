import pandas as pd
import numpy as np
from bertopic import BERTopic
from bertopic.backend import OpenAIBackend
from hdbscan import HDBSCAN
import os
import sys
from dotenv import load_dotenv
import openai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class OpenAIEmbedder:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def fit_transform(self, documents):
        embeddings = []
        for doc in documents:
            response = openai.Embedding.create(
                input=doc,
                model=self.model,  # Specify the OpenAI embedding model
                api_key=self.api_key
            )
            embeddings.append(response['data']['embeddings'])
        return embeddings

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
    df[column_name] = df[column_name].str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)
    df[column_name] = df[column_name].str.replace(r'\n', '', regex=True)
    
    # Print the first few entries to verify
    if verbose:
        print(f"First few entries of {column_name}:")
        print(df[column_name].head(5))
    
    return df[column_name].tolist()

def run_topic_model(
    name_summary_dict,
    n_topics=20,
    min_topic_size=5,
    zeroshot_min_similarity=0.5, # not used
    min_samples_core_point=5,
    verbose=False,
    openai_embedder=None,
    model="text-embedding-3-large",
    topic_summary_output_file_path='outputs/topic_summaries.csv',
    doc_topic_output_file_path='outputs/doc_topic_df.csv'):

    """
    inputs:
    name_summary_dict: dictionary with keys as doc names and values as summaries
    n_topics: number of topics to generate
    output_file_path: path to save topic summaries
    """

    print("\nPerforming topic modeling...\n")
    doc_summaries = list(name_summary_dict.values()) # correct
    
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

    # adjust model to have correct number topics
    # topic_model.reduce_topics(doc_summaries, nr_topics=n_topics)

    # get topics
    # topics = topic_model.topics_  # returns list of topics for each doc 

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

    topic_number_dict = doc_topic_df['Topic'].value_counts().to_dict()    
    
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

    return topic_number_dict # for fine-tuning

def topic_model_names_summaries(openai_embedder):
    doc_names = read_single_column(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=SHEET_NAME,
        column_name=NAME_COLUMN_NAME)

    doc_summaries = read_single_column(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=SHEET_NAME,
        column_name=SUMMARY_COLUMN_NAME)
    
    # doc_summaries_embedded = get_openai_embeddings(doc_summaries)
    
    return run_topic_model(
        name_summary_dict=dict(zip(doc_names, doc_summaries)),
        n_topics=N_TOPICS,
        min_topic_size=MIN_TOPIC_SIZE,
        zeroshot_min_similarity=ZEROSHOT_MIN_SIMILARITY,
        min_samples_core_point=MIN_SAMPLES_CORE_POINT,
        topic_summary_output_file_path=TOPIC_SUMMARY_OUTPUT_FILE_PATH,
        doc_topic_output_file_path=DOC_TOPIC_OUTPUT_FILE_PATH,
        openai_embedder=openai_embedder)

if __name__ == "__main__":
    EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"
    SHEET_NAME = "articles_data"
    NAME_COLUMN_NAME = "title"
    SUMMARY_COLUMN_NAME = "description"

    N_TOPICS = 13 # chosen with parameter tuning
    MIN_TOPIC_SIZE = 14 # chosen with parameter tuning
    ZEROSHOT_MIN_SIMILARITY = 0.4
    MIN_SAMPLES_CORE_POINT = 1 # chosen with parameter tuning

    TOPIC_SUMMARY_OUTPUT_FILE_PATH = "outputs/topic_summaries.csv"
    DOC_TOPIC_OUTPUT_FILE_PATH = "outputs/doc_topic_df_openai.csv"

    ARTICLE_SHEET_NAME = "articles_data"
    COMMENT_SHEET_NAME = "comments_for_published_articles"

    ARTICLE_COLS = ['title', 'published_date', 'description', 'canonical_url', 'conversation_id', 'thumbnail_url'] #[article_thumbnail_alt_text, article_text, article_author]
    COMMENT_COLS = ['conversation_id', 'author_id', 'written_date', 'text_content']
    OUTPUT_FILE_PATH = 'outputs/engagements.csv'
    
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path) # Load environment variables
    API_KEY =  os.environ.get("OPENAI_API_KEY")
    # print(f"API_KEY:{API_KEY}")

    MODEL="text-embedding-3-large"
    print(f"\nN_TOPICS: {N_TOPICS}")
    print(f"MIN_TOPIC_SIZE: {MIN_TOPIC_SIZE}")
    # print(f"ZEROSHOT_MIN_SIMILARITY: {ZEROSHOT_MIN_SIMILARITY}")
    print(f"MIN_SAMPLES_CORE_POINT: {MIN_SAMPLES_CORE_POINT}")

    custom_openai_embedder = OpenAIEmbedder(api_key=API_KEY, model=MODEL)
    topic_model_names_summaries(openai_embedder=custom_openai_embedder)
    
    finetune=False

    if finetune:
        # parameter tuning
        parameter_dict = {}
        for i in range(1,15):
            print(f"\n\nRunning topic model for iteration {i}...\n")
            MIN_SAMPLES_CORE_POINT = i
            print(f"\nN_TOPICS: {N_TOPICS}")
            print(f"MIN_TOPIC_SIZE: {MIN_TOPIC_SIZE}")
            print(f"MIN_SAMPLES_CORE_POINT: {MIN_SAMPLES_CORE_POINT}")
            
            parameter_dict[MIN_SAMPLES_CORE_POINT] = topic_model_names_summaries(openai_embedder=custom_openai_embedder)


        print(parameter_dict.items()) 
        pd.DataFrame(parameter_dict).to_csv('parameter_tuning.csv', index=False)