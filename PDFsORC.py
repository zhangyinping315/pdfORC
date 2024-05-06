import os
from pdf2image import convert_from_path
from PIL import Image
import fitz
import pytesseract

# Set up Tesseract command path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set up Poppler path for pdf2image
poppler_path = r'C:\Program Files\poppler-24.02.0\Library\bin'

# Input and output folder paths
input_folder = 'input'
output_folder = 'output'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Process each PDF file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.pdf'):
        input_pdf_path = os.path.join(input_folder, filename)
        output_pdf_path = os.path.join(output_folder, filename)

        # Convert PDF to list of images
        images = convert_from_path(input_pdf_path, dpi=300, poppler_path=poppler_path)

        # Create a new PDF to store all OCR'd images
        doc = fitz.open()

        # Process each page/image
        for img in images:
            img_pil = img.convert("RGB")  # Convert to RGB for pytesseract processing
            img_path = "temp_page.pdf"
            img_pil.save(img_path, "PDF")  # Save each image as a PDF

            imgpdf = fitz.open(img_path)  # Open the image PDF for overlay
            page = doc.new_page(width=img.width, height=img.height)  # Create a new page based on the image dimensions

            # Use pytesseract to extract text and bounding box information
            ocr_data = pytesseract.image_to_data(img_pil, lang='eng+fra', output_type=pytesseract.Output.DICT)

            # Insert text before placing the image
            for i, text in enumerate(ocr_data['text']):
                if text.strip():  # Ensure we don't add empty strings
                    x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                    fontsize = 1.2*h  # Set font size based on bounding box height
                    # Insert text at calculated position
                    page.insert_text((x, y + fontsize), text, fontsize=fontsize, color=(0, 0, 0))

            # Overlay the image over the entire page, covering the text
            page.show_pdf_page(page.rect, imgpdf, pno=0)

        # Save the new searchable PDF
        doc.save(output_pdf_path)
        doc.close()

        print(f"Searchable PDF saved as: {output_pdf_path}")

print("All PDFs processed successfully.")