import pandas as pd

def read_cols(
    excel_file_path:str, 
    sheet_name:str, 
    column_names:list
):
    """
    Reads specified columns from a given Excel sheet and performs initial cleaning by replacing NaN values with 'missing' and
    ensuring all data are of string type. This function is primarily used for preprocessing data read from Excel files.

    Parameters:
    - excel_file_path (str): Path to the Excel file.
    - sheet_name (str): Name of the sheet to read from.
    - column_names (list): List of column names to read from the sheet.

    Returns:
    - pd.DataFrame: A DataFrame containing the specified columns from the Excel sheet, with initial cleaning applied.
    """

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
