# Medical-Bill-Extracter
Bajaj Health Datathon: AI Bill Extraction Pipeline (URL-Based)

This repository holds the complete, end-to-end solution for the Bajaj Health Datathon. This system is designed to extract structured medical bill data (line items, totals, page details) directly from PDF or Image URLs, adhering strictly to the required request/response schema.

✨ Overview: Problem Statement

The core requirement is to build a robust pipeline that consumes a document URL and extracts all critical billing data into a precise JSON structure.

📋 Required Extraction Fields

The pipeline must successfully identify and extract the following:

Line Item Details: item_name, item_rate, item_quantity, item_amount, page_number, page_type.

Total Summaries: sub_total_amount, final_total_amount, total_item_count.

📥 Input & 📤 Output Format (Datathon Mandate)

Input Format (Strict JSON)

The system accepts input only as a JSON payload containing the document URL.

{
  "document": "[https://example.com/sample.pdf](https://example.com/sample.pdf)"
}


Output Format (Required Schema)

The final output must match this exact, precise JSON schema, ensuring data quality and validation status.

{
  "is_success": true,
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail",
        "bill_items": [
          {
            "item_name": "Consultation",
            "item_rate": 1000.0,
            "item_quantity": 4.0,
            "item_amount": 4000.0
          }
        ]
      }
    ],
    "total_item_count": 12,
    "sub_total_amount": 15390.0,
    "final_total_amount": 15390.0
  }
}


🚀 Architecture: The 5-Step Extraction Pipeline

The solution employs a multi-step pipeline for robust and accurate data extraction:

Input: Document URL received via JSON.

Download & Pre-process: The file (PDF/Image) is securely downloaded.

Text Extraction (The Smart Split):

PDF (Machine-Generated): Text layer is extracted using PyMuPDF.

Image (Scanned/Photo): Text is extracted using the powerful Gemini OCR capability.

Structured Extraction (Gemini Flash): The extracted plain text is fed to Gemini 2.5 Flash with a strict response_schema to produce raw JSON line items.

Safety & Finalization:

The raw JSON is sanitized (cleaning out markdown/code fences).

Totals are computed mathematically in Python (safety layer against LLM hallucination):

sub_total_amount = sum(item_amount)

final_total_amount = sum(item_amount)

Final response packaged into the Datathon format.

⚙ Key Components Breakdown

Component

Technology / Role

Function

URL Handler

requests

Supports secure download of cloud-hosted PDFs, PNGs, JPGs, and SAS-URLs.

PDF Text Extractor

PyMuPDF

Extracts high-fidelity text from machine-generated PDF text layers.

Image OCR

Gemini OCR

Handles all image formats and badly scanned PDFs, providing highly accurate text.

Structured Parser

Gemini 2.5 Flash

Uses a custom, highly constrained prompt to ensure strict JSON output and precise line-item fidelity.

Safety Layer

Python (totals.py)

Recalculates all aggregate totals (sub_total, final_total) from the extracted line items to prevent LLM errors.

Sanitizer

Python (parser.py)

Removes potential LLM-generated artifacts like json code fences from the raw output.

📂 Project Structure

bill-extractor/
├── README.md                  # This file
├── extractor.ipynb            # Main Google Colab notebook for execution
├── src/
│     ├── extractor.py         # Core logic and API integration
│     ├── ocr.py               # Handles text extraction (PyMuPDF & Gemini OCR)
│     ├── parser.py            # JSON cleaning and validation
│     └── totals.py            # Total computation safety layer
├── sample_requests/
│     └── request.json         # Example input payload
├── sample_outputs/
│     └── output.json          # Example expected output
└── requirements.txt           # Required libraries


🛠 Setup & Execution

Installation

Install the necessary libraries in your Colab environment or local machine:

pip install google-genai pymupdf pillow requests


Execution in Google Colab

Open the extractor.ipynb file.

Insert your Gemini API Key in the designated cell.

Run all cells to define the pipeline functions.

Call the main function with a sample request URL:

# Sample Request URL (Example placeholder, replace with actual URL)
sample_request = {
  "document": "[https://hackrx.blob.core.windows.net/assets/datathonIIT/sample_3.png?sv=](https://hackrx.blob.core.windows.net/assets/datathonIIT/sample_3.png?sv=)..."
}

# Execute the extraction
final_json_result = extract_bill_from_url(sample_request)
print(final_json_result)


⚠ Limitations & Future Work

Known Limitations

Handwriting: Currently, extraction of purely handwritten fields is not supported.

Complex Layouts: Extremely dense or non-standard pharmacy tabular layouts may require minor prompt tuning for perfect accuracy.

Artifacts: Raw JSON output from the LLM may contain trailing code artifacts, which are automatically cleaned by the parser.py safety layer.

Future Improvements

Deployment: Convert the core logic into a scalable, high-performance FastAPI service.

Inference Layer: Implement discount/tax inference capabilities to enhance total computation accuracy.

Page Type Classification: Auto-detect and classify pages (e.g., Pharmacy Summary, Diagnostic Bill, Lab Report) for better context.

PDF Remediation: Implement table reconstruction logic for highly broken or poorly structured PDFs.

👤 Contact

Attribute

Details

Name
GAGAN VERMA

Email

12212207@nitkkr.ac.in
