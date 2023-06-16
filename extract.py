from flask import Flask, request, render_template, jsonify
from PIL import Image
import tabula
import pandas as pd
import pdf2image
import csv
import os
import pdf2image.exceptions
import pytesseract

app = Flask(__name__)

# Set the path to Tesseract executable if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

@app.route('/')
def index():
    return render_template('index.html')




@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    input_file = file.filename
    output_folder = 'output'

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process text extraction for all file types
    try:
        text_output = extract_text(input_file)

        # Save text to CSV file
        text_csv_file = os.path.join(output_folder, 'text_output.csv')
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

    return 'Output generated from the Python script'





if __name__ == '__main__':
    app.run()