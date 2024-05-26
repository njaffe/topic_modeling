import pandas as pd
import os
import sys
from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config import EXCEL_FILE_PATH, VECTOR_DB_PATH

# Function to read all sheets of an Excel file into a single DataFrame
def read_excel_to_df(excel_file_path):
    # Read all sheets
    xls = pd.ExcelFile(excel_file_path)
    df_list = []
    for sheet_name in xls.sheet_names: # change this to only read certain columns?
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df_list.append(df)
    
    # Combine all sheets into one DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    print("df columns") #text_content
    print(combined_df.columns)
    return combined_df

# Function to get only comments from an Excel file
def read_comment_text_to_df(excel_file_path, sheet_name, column_name):
    # Read the specified sheet and column
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, usecols=[column_name])
    
    # Rename the column to 'text_content'
    df.rename(columns={column_name: 'text_content'}, inplace=True)
    print("read in comment text column:")
    print("df head")
    print(df.head())
    return df

# Function to convert DataFrame rows into a list of Documents
def df_to_documents(df):
    documents = []
    for index, row in df.iterrows():
        content = " ".join([str(item) for item in row if pd.notna(item)])
        doc = Document(page_content=content)
        documents.append(doc)
    return documents

# Main function to load Excel data into a vector database
def load_excel_to_vector_db(excel_file_path, vector_db_path):
    # Read the Excel file
    print("\nreading excel file")
    # df = read_excel_to_df(excel_file_path)

    df = read_comment_text_to_df(
        excel_file_path=excel_file_path,
        sheet_name="comments_for_published_articles",
        column_name="text_content")
    
    # Convert DataFrame to list of Documents
    print("\nconverting to documents")
    documents = df_to_documents(df)
    
    # Initialize OpenAI Embeddings (you can use other embeddings as well)
    print("\ninitializing OpenAI embeddings")
    embeddings = OpenAIEmbeddings()

    # Create a FAISS vector store from the documents
    print("\ncreating vector store")
    vector_store = FAISS.from_documents(documents, embeddings)

    # Save the vector store to disk
    print("saving to vector store")
    if os.path.exists(vector_db_path):
        shutil.rmtree(vector_db_path)
    vector_store.save_local(vector_db_path)

if __name__ == "__main__":
    from config import EXCEL_FILE_PATH, VECTOR_DB_PATH

    load_excel_to_vector_db(EXCEL_FILE_PATH, VECTOR_DB_PATH)
    print(f"Vector database created and saved to {VECTOR_DB_PATH}")
