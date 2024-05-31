import pandas as pd
import numpy as np
from utils.topics_spreadsheet import read_cols

# simple compare topics between main model and openai model
topics = pd.read_csv('outputs/doc_topic_df.csv')
topics_openai = pd.read_csv('outputs/doc_topic_df_openai.csv')

print("main model")
# print(topics.head())
# print(topics['Topic'].value_counts())
# print(topics['Document_description'].value_counts())

print("\nopenai model")
# print(topics_openai.head())
# print(topics_openai['Topic'].value_counts())
# print(topics_openai['Document_description'].value_counts())

# save both to document descriptions to file to compare
compare_dict = {'main_model': topics['Document_description'].values,
                'openai_model': topics_openai['Document_description'].values}

# Find the maximum length of the arrays
max_length = max(len(compare_dict['main_model']), len(compare_dict['openai_model']))

# Pad the shorter array with NaN values to match the length of the longer array
compare_dict['main_model'] = np.pad(compare_dict['main_model'], (0, max_length - len(compare_dict['main_model'])), constant_values=np.nan)
compare_dict['openai_model'] = np.pad(compare_dict['openai_model'], (0, max_length - len(compare_dict['openai_model'])), constant_values=np.nan)

compare_df = pd.DataFrame(compare_dict)
# compare_df.to_csv('TROUBLESHOOTING_doc_descriptions_comparison.csv', index=False)


# get article data
EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"
ARTICLE_SHEET_NAME = "articles_data"
ARTICLE_COLS = ['title', 'published_date', 'description', 'canonical_url', 'conversation_id', 'thumbnail_url'] #[article_thumbnail_alt_text, article_text, article_author]


article_data = read_cols(
    excel_file_path=EXCEL_FILE_PATH,
    sheet_name=ARTICLE_SHEET_NAME,
    column_names=ARTICLE_COLS)

print(article_data.head())
print(article_data['description'].nunique())

# is the issue with this join?

# joined_topics = pd.merge(
#     topics,
#     article_data,
#     left_on='Document_description',
#     right_on='description',
#     how='right')

# print("\nlength of joined df")
# print(joined_topics.dropna().shape[0])


# joined_topics_openai = pd.merge(
#     topics_openai, 
#     article_data, 
#     left_on='Document_description', 
#     right_on='description', 
#     how='right')

# print("\nlength of joined df open AI")
# print(joined_topics_openai.dropna().shape[0])