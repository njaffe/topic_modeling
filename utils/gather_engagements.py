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

def compile_data(n_comments_to_keep=4):

    print("\nreading data...\n")
    comment_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=COMMENT_SHEET_NAME,
        column_names=COMMENT_COLS)
    comment_data = comment_data[comment_data['final_state'] != 'blocked'] # remove blocked comments
    
    reaction_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=REACTION_SHEET_NAME,
        column_names=REACTION_COLS)
    
    article_data = read_cols(
        excel_file_path=EXCEL_FILE_PATH,
        sheet_name=ARTICLE_SHEET_NAME,
        column_names=ARTICLE_COLS)
    
    doc_topic_df = pd.read_csv(DOC_TOPIC_DF)

    print("\nchecking for duplicates...\n")
    article_data = article_data.drop_duplicates(subset=['canonical_url', 'title'])
    comment_data = comment_data.drop_duplicates(subset=['conv_message_id'])

    print("\nmerging data...\n")
    res_df = comment_data \
        .merge(reaction_data, how='right', left_on='conv_message_id', right_on='message_id') \
        .merge(article_data, how='left', on='conversation_id') \
        .merge(doc_topic_df, how='left', left_on='description', right_on='Document_description')
    
    # ensure no duplicate rows
    assert res_df.shape[0] == res_df.drop_duplicates().shape[0], "Duplicate rows found"

    print("\nchecking for missing topics...\n")
    res_df['Topic'].fillna('missing', inplace=True)
    print(f"{res_df[res_df['Topic'] == 'missing'].shape[0]} out of {res_df.shape[0]} comments are missing topics")
    # print(res_df.head(5))

    # remove rows with missing topics
    res_df = res_df[res_df['Topic']!= 'missing']

    print("\nCleaning up columns...\n")
    res_df['total_likes'] = res_df['total_likes'].replace('missing', np.nan)
    res_df['total_likes'] = res_df['total_likes'].fillna(0).astype(float).round().astype(int)
    res_df['total_views'] = res_df['total_views'].replace('missing', np.nan)
    res_df['total_views'] = res_df['total_views'].fillna(0).astype(float).round().astype(int)
    res_df['Topic'] = res_df['Topic'].astype(int)

    res_df.drop(columns=['Document_description', 'Document_name'], inplace=True)

    res_df = res_df[[
        'title',
    	'description',
        'published_date',
        'canonical_url',
    	'thumbnail_url',
    	'Topic',
        'written_date',
    	'conversation_id',
    	'conv_message_id',
    	'author_id',
    	'text_content',
    	'final_state',
    	'message_id',
    	'total_views',
    	'total_likes']]

    print("\nhighest number comments per conversations:") # recall that this df is at the comment granularity
    print(res_df.conversation_id.value_counts().sort_values(ascending=False).head(5))
    print("\nfiltering to top comments")

    # Sort by 'Topic' and 'total_likes', and get the top 10 articles per topic
    top_articles_df = res_df.sort_values(by=['Topic', 'total_likes'], ascending=[True, False])
    top_articles_df = top_articles_df.groupby('Topic').head(10) # this is correct

    # Filter to keep only comments (assuming comments have a 'conversation_id')
    comments_df = res_df[res_df['conversation_id'].notna()]
    # Ensure the comments belong to the top 10 articles using 'canonical_url' as the linking field
    top_comments_df = comments_df[comments_df['conversation_id'].isin(top_articles_df['conversation_id'])]

    # Sort by 'conversation_id' and 'total_likes', and get the top 4 comments per article
    top_comments_df = top_comments_df.sort_values(by=['conversation_id', 'total_likes'], ascending=[True, False])
    top_comments_df = top_comments_df.groupby('conversation_id').head(4) # this is correct

    assert top_comments_df.shape[0] == top_comments_df.drop_duplicates().shape[0], "Duplicate rows found"

    # Combine top articles and top comments back into a single DataFrame
    # THIS IS PROBLEM AREA
    res_df = top_comments_df.sort_values(by=['Topic', 'conversation_id', 'conv_message_id', 'total_likes'], ascending=[True, True, True, False])

    assert res_df.shape[0] == res_df.drop_duplicates().shape[0], "Duplicate rows found"
    # print("-----------------------------------")
    # print(res_df.head())
    # print("-----------------------------------")

    # assert res_df.shape[0] == (NTOPICS-1) * n_comments_to_keep, \
    #     f"Expected {NTOPICS * n_comments_to_keep} rows, got {res_df.shape[0]}"

    print("\nwriting to file...\n")
    res_df.to_csv(ENGAGEMENTS_OUTPUT_FILE_PATH, index=False)

    # Check if 'Topic' column exists
    if 'Topic' not in res_df.columns:
        raise ValueError("DataFrame does not contain 'Topic' column")

    # Path to save the Excel file, replace CSV extension with XLSX
    output_file_path = ENGAGEMENTS_OUTPUT_FILE_PATH.replace('csv', 'xlsx')

    # Create a writer object for writing to Excel
    with pd.ExcelWriter(output_file_path) as writer:
        # Get unique topics
        unique_topics = res_df['Topic'].unique()

        # Write each topic to a separate sheet
        for topic in unique_topics:
            print(f"Writing data for topic '{topic}'..."    )
            if pd.isna(topic):  # Check for empty or NaN topic names
                print("Invalid topic name, skipping.")
                continue
            
            sanitized_topic = str(topic).strip()
            if not sanitized_topic:  # Further checks for empty strings after stripping
                print("Empty topic name after stripping, skipping.")
                continue
            
            topic_df = res_df[res_df['Topic'] == topic]
            if not topic_df.empty:
                topic_df.to_excel(writer, sheet_name=sanitized_topic[:31], index=False)  # Excel sheet names must be <= 31 chars
            else:
                print(f"No data for topic '{topic}', skipping sheet.")

        # Ensure there is at least one sheet written
        if len(writer.sheets) == 0:
            raise Exception("No sheets added. Ensure there is data for at least one topic.")


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