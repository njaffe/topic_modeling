import pandas as pd
import numpy as np


def read_cols(
    excel_file_path:str, 
    sheet_name:str, 
    column_names:list
):
    print(f"\nreading {column_names}...\n")
    df = pd.read_excel(
        excel_file_path,
        sheet_name=sheet_name,
        usecols=column_names)
        
    # Remove special characters
    for column_name in column_names:
        df[column_name] = df[column_name].fillna('missing').astype(str)
        df[column_name] = df[column_name].str.replace(r'[^\x00-\x7F#&;]+', '', regex=True)

    # Print the first few entries to verify
    print("\nDf head:")
    print(df.head(5))
    return df

def compile_data():
    article_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=ARTICLE_SHEET_NAME,
        column_names=ARTICLE_COLS)
    
    comment_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=COMMENT_SHEET_NAME,
        column_names=COMMENT_COLS)

    comment_df = pd.merge(article_data, comment_data, on='conversation_id', how='right')
    # comment_df = comment_df.dropna(subset=['title', 'text_content'])
    comment_df = comment_df[[
        'title',
        'published_date',
        'description',
        'canonical_url',
        'thumbnail_url',
        'conversation_id',
        'author_id',
        'written_date',
        'text_content']]

    doc_topic_df = pd.read_csv(DOC_TOPIC_DF)

    final_df = pd.merge(comment_df, doc_topic_df, left_on='description', right_on='Document_description', how='left')
    final_df['Topic'].fillna('missing', inplace=True)
    print(final_df.head(5))

    final_df.to_csv(ENGAGEMENTS_OUTPUT_FILE_PATH, index=False)
    # next step: read out to individual sheets for each topic


if __name__ == "__main__":
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
    ENGAGEMENTS_OUTPUT_FILE_PATH = 'outputs/engagements.csv'
    DOC_TOPIC_DF = 'outputs/doc_topic_df.csv'
    compile_data()
