
import os
from pdfminer.high_level import extract_text


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def convert_to_markdown(text):
    lines = text.split("\\\\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.isupper() and len(stripped) < 50:
            lines[i] = f"## {stripped}"
    return "\\\\n".join(lines)

def process_pdfs_in_directory(pdf_directory, markdown_directory):
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            # [The rest of the code to process each PDF]
            markdown_filename = filename.replace(".pdf", "_markdown.md")
            markdown_path = os.path.join(markdown_directory, markdown_filename)
            
            # Check if the markdown file already exists
            if os.path.exists(markdown_path):
                print(f"Markdown for {filename} already exists. Skipping...")
                continue
            
            pdf_path = os.path.join(pdf_directory, filename)
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(pdf_path)
            
            # Convert extracted text to markdown
            markdown_text = convert_to_markdown(extracted_text)
            
            # Save the markdown text
            with open(markdown_path, "w") as md_file:
                md_file.write(markdown_text)
            print(f"Processed {filename} and saved Markdown to {markdown_filename}")


if __name__ == "__main__":
    pdf_directory='data/pdfs'
    markdown_directory='data/markdowns'

    process_pdfs_in_directory(pdf_directory, markdown_directory)