import pytesseract
from PIL import Image
import tabula
import pandas as pd
import pdf2image
import csv
import os
import pdf2image.exceptions

# Method to extract simple text from an image or PDF
def extract_text(filename):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(filename)
        text = pytesseract.image_to_string(image)
    elif filename.lower().endswith('.pdf'):
        try:
            images = pdf2image.convert_from_path(filename)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image)
        except pdf2image.exceptions.PDFPageCountError as e:
            print(f"Error extracting text from PDF: {e}")
            text = ""
    else:
        raise ValueError("Unsupported file format. Only PNG, JPEG, and PDF are supported.")
    
    return text

# Method to extract table data from an image or PDF
def extract_table(filename):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        tables = tabula.read_pdf(filename, pages='all', multiple_tables=True)
    elif filename.lower().endswith('.pdf'):
        try:
            tables = tabula.read_pdf(filename, pages='all', multiple_tables=True)
        except Exception as e:
            print(f"Error extracting table from PDF: {e}")
            tables = []
    else:
        raise ValueError("Unsupported file format. Only PNG, JPEG, and PDF are supported.")
    
    return tables

# Method to save table contents to CSV file
def save_table_to_csv(table_contents, csv_file):
    table_contents.to_csv(csv_file, index=False)
    print(f"Table contents saved to CSV file: {csv_file}")

# Function to process input files and generate CSV files
def process_files(input_file, text_csv_file, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process text extraction for all file types
    try:
        text_output = extract_text(input_file)

        # Save text to CSV file
        text_csv_file = os.path.join(output_folder, text_csv_file)
        with open(text_csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Text'])
            writer.writerow([text_output])

        print(f"Text extracted and saved to CSV file: {text_csv_file}")
    except Exception as e:
        print(f"Error processing text extraction: {e}")

    # Process table extraction for PDF files
    if input_file.lower().endswith('.pdf'):
        # Extract table data
        try:
            table_output = extract_table(input_file)

            # Process each table found
            for i, table in enumerate(table_output, start=1):
                # Create the CSV file path for the table
                table_csv_file = os.path.join(output_folder, f"table{i}.csv")

                # Extract table contents
                table_contents = pd.DataFrame(table)

                # Save table contents to CSV file
                save_table_to_csv(table_contents, table_csv_file)
        except Exception as e:
            print(f"Error processing table extraction: {e}")

# Example usage
input_file = r'D:\puthon cloudyML\Sample Files\sample2.jpg'
text_csv_file = r'text_output.csv'
output_folder = r'D:\puthon cloudyML\Sample Files\output'

# Process input file and generate CSV files
process_files(input_file, text_csv_file, output_folder)