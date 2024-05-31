# match users to most engaged comments/articles/topics
import pandas as pd
from utils.reader import read_cols

# def reformat_comments(comment_df):
#     return comment_df

# def compile_user_reaction_data():
    
#     user_data = read_cols(
#             excel_file_path=USER_FILE_PATH,
#             sheet_name=USER_SHEET_NAME,
#             column_names=USER_COLS)

#     comment_data_raw = pd.ExcelFile(COMMENT_FILE_PATH)

#     # Read all sheets, assuming they all have the same columns
#     df_list = []
#     for sheet_name in comment_data_raw.sheet_names:
#         df = pd.read_excel(comment_data_raw, sheet_name=sheet_name)
#         df_list.append(df)

#     # Concatenate all DataFrames from the list into one DataFrame
#     comment_data = pd.concat(df_list, ignore_index=True)

#     comment_data.to_csv('intermediate_user.csv', index=False)
    
    
    # merged = user_data.merge(
    #     comment_data,
    #     how='left',
    #     left_on='registred_user_id',
    #     right_on='user_id')

def get_most_engaged():

    # get conversation with most engaged comments
    comment_data = read_cols(
            excel_file_path=RAW_FILE_PATH,
            sheet_name='comments_history',
            column_names=['user_id', 'conversation_id', 'message_id'])
    
    top_convos = comment_data.groupby(['user_id','conversation_id']).size().sort_values(ascending=False).reset_index()
    print("\nview top convos")
    print(top_convos)

    conversation_counts = comment_data.groupby(['user_id', 'conversation_id']).size()

    # Convert the series to a DataFrame and name the column
    conversation_counts = conversation_counts.reset_index(name='count')

    # Sort the values by 'user_id' and 'count' in descending order to prepare for ranking
    conversation_counts.sort_values(by=['user_id', 'count'], ascending=[True, False], inplace=True)

    # Rank the conversation IDs by their frequency within each user
    conversation_counts['rank'] = conversation_counts.groupby('user_id')['count'].rank(method='dense', ascending=False)

    # Display the resulting DataFrame
    # print("\nview conversation counts" )
    # print(conversation_counts)

     # get topic of that article
    topic_data_raw = pd.ExcelFile(COMMENT_FILE_PATH)

    # Read all sheets, assuming they all have the same columns
    df_list = []
    for sheet_name in topic_data_raw.sheet_names:
        df = pd.read_excel(topic_data_raw, sheet_name=sheet_name)
        df_list.append(df)

    # Concatenate all DataFrames from the list into one DataFrame
    topic_data = pd.concat(df_list, ignore_index=True)

    convo_topic_dict = dict(zip(topic_data['conversation_id'], topic_data['Topic']))

    # Creating the dictionary that maps conversation_ids to topics
    convo_topic_dict = dict(zip(topic_data['conversation_id'], topic_data['Topic']))

    # Create a new column in the conversation_counts DataFrame for topics by mapping the conversation IDs
    conversation_counts['topic'] = conversation_counts['conversation_id'].map(convo_topic_dict)

    # Filter out rows where topic is NaN (i.e., the conversation_id was not found in the topic dictionary)
    filtered_conversations = conversation_counts.dropna(subset=['topic'])

    # Now select the highest-ranked conversation for each user where a topic exists
    top_topic_per_user = filtered_conversations.groupby('user_id').first().reset_index()

    # If you want to ensure the output includes all users, even those without a matching topic, merge back to the original user list:
    all_users = conversation_counts['user_id'].drop_duplicates().to_frame()
    top_topic_per_user = pd.merge(all_users, top_topic_per_user, on='user_id', how='left')

    # Print or return the resulting DataFrame
    print("\nview top topic per user")
    print(top_topic_per_user)

    print("\ncheck nulls")
    print(top_topic_per_user.isna().sum()/len(top_topic_per_user))

    # this means that ~68% of users have engaged with conversations that do not have topics assigned.

if __name__ == "__main__":

    VERBOSE = True
    RAW_FILE_PATH = "data/fox_news_comments.xlsx"
    USER_SHEET_NAME = 'random_user_id_list_data'
    USER_COLS = ['country', 'city', 'region', 'is_registered', 'registration_date', 'registred_user_id']
    COMMENT_FILE_PATH = "outputs/top_comments_df_sorted.xlsx"

    # compile_user_reaction_data()

    get_most_engaged()