import pandas as pd
import numpy as np
from collections import defaultdict

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
    compiled_df = comment_data \
        .merge(reaction_data, how='right', left_on='conv_message_id', right_on='message_id') \
        .merge(article_data, how='left', on='conversation_id') \
        .merge(doc_topic_df, how='left', left_on='description', right_on='Document_description')
    
    # ensure no duplicate rows
    assert compiled_df.shape[0] == compiled_df.drop_duplicates().shape[0], "Duplicate rows found"

    print("\nchecking for missing topics...\n")
    compiled_df['Topic'].fillna('missing', inplace=True)
    print(f"{compiled_df[compiled_df['Topic'] == 'missing'].shape[0]} out of {compiled_df.shape[0]} comments are missing topics")
    # print(compiled_df.head(5))

    # remove rows with missing topics
    compiled_df = compiled_df[compiled_df['Topic']!= 'missing']

    print("\nCleaning up columns...\n")
    compiled_df['total_likes'] = compiled_df['total_likes'].replace('missing', np.nan)
    compiled_df['total_likes'] = compiled_df['total_likes'].fillna(0).astype(float).round().astype(int)
    compiled_df['total_views'] = compiled_df['total_views'].replace('missing', np.nan)
    compiled_df['total_views'] = compiled_df['total_views'].fillna(0).astype(float).round().astype(int)
    compiled_df['Topic'] = compiled_df['Topic'].astype(int)

    compiled_df.drop(columns=['Document_description', 'Document_name'], inplace=True)

    compiled_df = compiled_df[[
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
    
    return compiled_df

def get_top_articles_df(compiled_df:pd.DataFrame):

    # print("\nhighest number comments per conversations:") # recall that this df is at the comment granularity
    # print(compiled_df.conversation_id.value_counts().sort_values(ascending=False).head(5))

    print("\nfiltering to top comments")

    # Sort by 'Topic' and 'total_likes', and get the top 10 articles per topic
    top_articles_df = compiled_df.sort_values(by=['Topic', 'total_likes'], ascending=[True, False])
    top_articles_df = top_articles_df.groupby('Topic').head(N_ARTICLES)

    # Filter to keep only comments (assuming comments have a 'conversation_id')
    comments_df = compiled_df[compiled_df['conversation_id'].notna()]
    # Ensure the comments belong to the top 10 articles using 'canonical_url' as the linking field
    top_comments_df = comments_df[comments_df['conversation_id'].isin(top_articles_df['conversation_id'])]

    # Sort by 'conversation_id' and 'total_likes', and get the top 4 comments per article
    top_comments_df = top_comments_df.sort_values(by=['conversation_id', 'total_likes'], ascending=[True, False])
    top_comments_df = top_comments_df.groupby('conversation_id').head(N_COMMENTS)

    # Combine top articles and top comments back into a single DataFrame
    top_comments_df_sorted = top_comments_df.sort_values(by=['Topic', 'conversation_id', 'conv_message_id', 'total_likes'], ascending=[True, True, True, False])

    assert top_comments_df_sorted.shape[0] == top_comments_df_sorted.drop_duplicates().shape[0], "Duplicate rows found"

    # print("\nwriting to file...\n")
    # top_comments_df_sorted.to_csv(TOPICS_SPREADSHEET_OUTPUT_FILE_PATH, index=False)

    # Check if 'Topic' column exists
    if 'Topic' not in top_comments_df_sorted.columns:
        raise ValueError("DataFrame does not contain 'Topic' column")

    return top_comments_df_sorted

def write_to_excel(top_comments_df_sorted:pd.DataFrame):

    # Path to save the Excel file, replace CSV extension with XLSX
    output_file_path = TOPICS_SPREADSHEET_OUTPUT_FILE_PATH.replace('csv', 'xlsx')
    # Create a writer object for writing to Excel
    with pd.ExcelWriter(output_file_path) as writer:
        # Get unique topics
        unique_topics = top_comments_df_sorted['Topic'].unique()

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
            
            # create a df for each topic
            topic_df = top_comments_df_sorted[top_comments_df_sorted['Topic'] == topic]

            ### create df of reformated comment-level colmns
            message_level_cols = ['conv_message_id', 'author_id', 'text_content', 'final_state', 'message_id', 'total_views', 'total_likes']

            new_col_names = []
            for n in range(1,N_COMMENTS+1):
                for col in message_level_cols:
                    new_col_names.append(f'HEC{n}_{col}')
            
            new_cols_content = topic_df[message_level_cols].values.flatten().tolist() # this is correct

            multiplier = topic_df['title'].nunique() # multply to get correct number of rows
            
            assert len(new_col_names) * multiplier == len(new_cols_content), "Column names and content do not match"

            # Create a defaultdict with lists as default values
            d = defaultdict(list)

            # Populate the dictionary
            for key, value in zip(new_col_names * multiplier, new_cols_content):
                d[key].append(value)

            reformatted_comment_level_dict = dict(d)
            reformatted_comment_level_df = pd.DataFrame(reformatted_comment_level_dict)
            reformatted_comment_level_df.reset_index(drop=True)

            # reformatted_comment_level_df.to_csv('intermediate.csv', index=False)

            # join back with other columns
            topic_df_article_level = topic_df.drop(columns=message_level_cols).drop_duplicates()
            topic_df_article_level = topic_df_article_level.reset_index(drop=True)

            # topic_df_article_level.to_csv('intermediate.csv', index=False)

            res_reformatted_df = pd.concat([topic_df_article_level, reformatted_comment_level_df], axis=1, ignore_index=False)

            if not res_reformatted_df.empty:
                res_reformatted_df.to_excel(writer, sheet_name=sanitized_topic[:31], index=False)  # Excel sheet names must be <= 31 chars
            else:
                print(f"No data for topic '{topic}', skipping sheet.")

        # Ensure there is at least one sheet written
        if len(writer.sheets) == 0:
            raise Exception("No sheets added. Ensure there is data for at least one topic.")

def create_topics_spreadsheet():
    compiled_df = compile_data()
    top_comments_df_sorted = get_top_articles_df(compiled_df)
    write_to_excel(top_comments_df_sorted)


if __name__ == "__main__":
    # constants
    N_ARTICLES=10
    N_COMMENTS=4

    # input files
    EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"
    ARTICLE_SHEET_NAME = "articles_data"
    COMMENT_SHEET_NAME = "comments_for_published_articles"
    REACTION_SHEET_NAME = "reaction_count_for_pub_articles"
    DOC_TOPIC_DF = 'outputs/doc_topic_df.csv'

    # column cleanup
    COMMENT_COLS = ['conversation_id', 'conv_message_id', 'author_id', 'written_date', 'text_content', 'final_state']
    REACTION_COLS = [ 'message_id', 'total_views', 'total_likes']
        # note: COMMENT_SHEET_NAME[conv_message_id] matches REACTION_SHEET_NAME[message_id]
    ARTICLE_COLS = ['title', 'published_date', 'description', 'canonical_url', 'conversation_id', 'thumbnail_url'] #[article_thumbnail_alt_text, article_text, article_author]

    # final save location
    TOPICS_SPREADSHEET_OUTPUT_FILE_PATH = 'outputs/top_comments_df_sorted.csv'

    create_topics_spreadsheet()
# issue appears to be that topic modeling put many articles into the -1 topic, which is not included in the topic summary, and this results in many nulls when joined