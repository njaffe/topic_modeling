# README: Topic Modeling and User Engagement Analysis
This document provides instructions on how to execute the scripts to perform topic modeling, generate a topics spreadsheet, and analyze user engagement based on topics. These scripts are part of a data analysis pipeline that processes user comments, identifies key topics, and matches users to their most engaged topics.

## Prerequisites
Before you run the scripts, ensure that you have the following:

- Python 3.8 or higher installed.
- Pandas library installed. You can install it via pip: `pip install pandas`
- Access to the necessary Excel files that contain the data.

## File Descriptions
- topic_model.py: This script performs topic modeling from the comments data.
- topics_spreadsheet.py: This script generates an Excel spreadsheet that organizes comments and articles by the identified topics.
- users.py: This script matches users to their most engaged comments/articles/topics based on the data processed in the previous scripts.

## Data Files
Ensure that the following data files are in your working directory or specify the path to where they are located:

- `data/fox_news_comments.xlsx`: Contains the raw comments, reactions, and other related data.
- `outputs/doc_topic_df_filtered.csv`: Output from topic_model.py used in topics_spreadsheet.py.
- `outputs/top_comments_df_sorted.xlsx`: Output from topics_spreadsheet.py used in users.py.

## Running the Scripts
Follow these steps to run the scripts in the correct order to ensure the data flows through the analysis pipeline correctly:

### 1. Topic Modeling
First, run the topic_model.py script to analyze the comments and identify various topics. This script processes the comments data and saves the topic information in outputs/doc_topic_df_filtered.csv.

Command to run: `python topic_model.py`

### 2. Generating Topics Spreadsheet
After the topics have been modeled, run the topics_spreadsheet.py script. This script uses the output from the topic modeling to create a detailed spreadsheet that organizes comments and articles by topic. The spreadsheet is saved in outputs/top_comments_df_sorted.xlsx.

Command to run: `python topics_spreadsheet.py`

### 3. Analyzing User Engagement
Finally, run the users.py script. This script uses the spreadsheet generated in the previous step to match users to their most engaged comments/articles/topics, providing insights into user behavior and engagement.

Command to run: `python users.py`
