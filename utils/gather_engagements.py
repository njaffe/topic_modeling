import pandas as pd
import numpy as np


def read_cols(
    excel_file_path:str, 
    sheet_name:str, 
    column_names:list
):
    print(f"\nreading from {sheet_name}...\n")
    df = pd.read_excel(
        excel_file_path,
        sheet_name=sheet_name,
        usecols=column_names)
        
    # Remove special characters
    for column_name in column_names:
        df[column_name] = df[column_name].fillna('missing').astype(str)
    #     df[column_name] = df[column_name].str.replace(r'[^\x00-\x7F#&;]+', '', regex=True)

    # Print the first few entries to verify
    print(f"\n{sheet_name} columns:")
    print(df.columns)
    return df

def compile_data():
    comment_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=COMMENT_SHEET_NAME,
        column_names=COMMENT_COLS)
    
    reaction_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=REACTION_SHEET_NAME,
        column_names=REACTION_COLS)
    
    article_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=ARTICLE_SHEET_NAME,
        column_names=ARTICLE_COLS)
    
    doc_topic_df = pd.read_csv(DOC_TOPIC_DF)

    res_df = comment_data \
        .merge(reaction_data, how='right', left_on='conv_message_id', right_on='message_id') \
        .merge(article_data, how='left', on='conversation_id') \
        .merge(doc_topic_df, how='left', left_on='description', right_on='Document_description')

    # res_df = res_df[[
    #     'title',
    #     'published_date',
    #     'description',
    #     'canonical_url',
    #     'thumbnail_url',
    #     'conversation_id',
    #     'author_id',
    #     'written_date',
    #     'text_content']]

    res_df['Topic'].fillna('missing', inplace=True)
    print(f"{res_df[res_df['Topic'] == 'missing'].shape[0]} out of {res_df.shape[0]} comments are missing topics")
    print(res_df.head(5))

    res_df = res_df[res_df['Topic']!= 'missing']

    res_df.to_csv(ENGAGEMENTS_OUTPUT_FILE_PATH, index=False)
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
    REACTION_SHEET_NAME = "reaction_count_for_pub_articles"

    COMMENT_COLS = ['conversation_id', 'conv_message_id', 'author_id', 'written_date', 'text_content', 'final_state']
    REACTION_COLS = [ 'message_id', 'total_views', 'total_likes']
    # COMMENT_SHEET_NAME[conv_message_id] matches REACTION_SHEET_NAME[message_id]
    ARTICLE_COLS = ['title', 'published_date', 'description', 'canonical_url', 'conversation_id', 'thumbnail_url'] #[article_thumbnail_alt_text, article_text, article_author]


    ENGAGEMENTS_OUTPUT_FILE_PATH = 'outputs/engagements.csv'
    DOC_TOPIC_DF = 'outputs/doc_topic_df.csv'
    compile_data()
# issue appears to be that topic modeling put many articles into the -1 topic, which is not included in the topic summary, and this results in many nulls when joined