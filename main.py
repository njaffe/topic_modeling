import os
import sys

from utils.topic_model import topic_model_names_summaries
from utils.topics_spreadsheet import create_topics_spreadsheet

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config import API_KEY, DATA_PATH, CHROMA_PATH


def main():
    process_inputs_in_directory()
    topic_model_names_summaries()
    create_topics_spreadsheet()

if __name__ == "__main__":
    EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"
    SHEET_NAME = "articles_data"
    NAME_COLUMN_NAME = "title"
    SUMMARY_COLUMN_NAME = "description"
    NTOPICS = 21
    TOPIC_SUMMARY_OUTPUT_FILE_PATH = "outputs/topic_summaries.csv"
    DOC_TOPIC_OUTPUT_FILE_PATH = "outputs/doc_topic_df.csv"
    ENGAGEMENTS_OUTPUT_FILE_PATH = 'outputs/engagements.csv'

    EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"
    SHEET_NAME = "articles_data"
    NAME_COLUMN_NAME = "title"
    SUMMARY_COLUMN_NAME = "description"
    NTOPICS = 21
    TOPIC_SUMMARY_OUTPUT_FILE_PATH = "outputs/topic_summaries.csv"
    DOC_TOPIC_OUTPUT_FILE_PATH = "outputs/doc_topic_df.csv"

    ARTICLE_SHEET_NAME = "articles_data"
    COMMENT_SHEET_NAME = "comments_for_published_articles"

    ARTICLE_COLS = ['title', 'published_date', 'description', 'canonical_url', 'conversation_id', 'thumbnail_url'] #[article_thumbnail_alt_text, article_text, article_author]
    COMMENT_COLS = ['conversation_id', 'author_id', 'written_date', 'text_content']
    OUTPUT_FILE_PATH = 'outputs/engagements.csv'
    DOC_TOPIC_DF = 'outputs/doc_topic_df.csv'

    main()