from utils.convert_to_md import convert_to_md
from utils.create_database import create_database
from utils.query_database import query_database

def main():
    print("Hello from main.py")
    convert_to_md() # works on its own
    create_database() # works on its own
    # next steps: query, add argparse
    query_database()

if __name__ == "__main__":
    main()