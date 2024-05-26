import os

API_KEY = os.environ["OPENAI_API_KEY"]
VECTOR_DB_PATH = "data/vector_db"
EXCEL_FILE_PATH = "data/fox_news_comments.xlsx"

DATA_PATH = "data"
JSON_DIRECTORY = "data/jsons"
CHROMA_PATH = "chroma"
PDF_DIRECTORY='data/pdfs'
MARKDOWN_DIRECTORY='data/markdowns'
CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
        Answer the question based on the following context:

        {context_text}
        ---

        Answer the question based on the above context: {query}
    """