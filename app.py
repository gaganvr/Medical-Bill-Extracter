# ============================================================
# 🔥 INSTALL DEPENDENCIES
# ============================================================
!pip install google-genai pymupdf pillow requests --quiet

# ============================================================
# 🔥 IMPORTS
# ============================================================
import fitz  # PyMuPDF
import requests
import json
from google.genai import Client
import base64

# ============================================================
# 🔥 GEMINI CLIENT
# ============================================================
API_KEY = "AIzaSyC7-S7s0jhUKGE3xSqMTYoH1I807Cdb2HE"   # <- PUT YOUR KEY
client = Client(api_key=API_KEY)

# ============================================================
# 🔥 DOWNLOAD FILE FROM URL
# ============================================================
def download_from_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("❌ Cannot download file. Check URL or SAS expiry.")
    
    ext = url.split("?")[0].split(".")[-1].lower()
    
    filename = "downloaded_file." + ext
    with open(filename, "wb") as f:
        f.write(r.content)

    return filename

# ============================================================
# 🔥 EXTRACT TEXT (PDF or IMAGE)
# ============================================================
def extract_text_from_file(filepath):
    # --- PDF ---
    if filepath.endswith(".pdf"):
        print("📄 PDF detected — extracting pages...")
        doc = fitz.open(filepath)
        pages = [p.get_text() for p in doc]
        return pages

    # --- IMAGE ---
    print("🖼 Image detected — sending to Gemini Vision...")
    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Extract ALL visible text from this medical bill image.
    Return ONLY text. No markdown. No comments.
    """

    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=[
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image": b64}
        ]
    )

    return [response.text]

# ============================================================
# 🔥 BILL ITEM EXTRACTION (LLM)
# ============================================================
def extract_bill_items(page_texts):

    prompt = f"""
    You are an expert medical bill extraction AI.

    Extract ALL line items strictly in this JSON structure:

    {{
      "pagewise_line_items": [
        {{
          "page_no": "1",
          "page_type": "Bill Detail | Final Bill | Pharmacy",
          "bill_items": [
            {{
              "item_name": "string",
              "item_rate": 0,
              "item_quantity": 0,
              "item_amount": 0
            }}
          ]
        }}
      ]
    }}

    RULES:
    - No markdown.
    - No comments.
    - No extra fields.
    - item_amount = item_rate * item_quantity
    - Use EXACT item names from bill text
    - If a value is missing, put 0 (never hallucinate)

    BILL TEXT:
    {page_texts}
    """

    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=prompt
    )

    raw = response.text.strip()
    raw = raw.replace("json", "").replace("", "")

    return json.loads(raw)

# ============================================================
# 🔥 COMPUTE TOTALS
# ============================================================
def compute_totals(data):
    total_items = 0
    total_amount = 0

    for page in data["pagewise_line_items"]:
        for item in page["bill_items"]:
            total_items += 1
            total_amount += float(item.get("item_amount", 0))

    data["total_item_count"] = total_items
    data["sub_total_amount"] = total_amount
    data["final_total_amount"] = total_amount

    return data
  
def format_final_output(data):
  return {
      "is_success": True,
      "data": data
  }

# ============================================================
# 🔥 MAIN FUNCTION — TAKES URL LIKE DATATHON SPEC
# ============================================================
def extract_bill_from_url(request_json):
    url = request_json["document"]

    print("📥 Downloading from URL...")
    filepath = download_from_url(url)

    print("🔍 Extracting text...")
    pages = extract_text_from_file(filepath)

    print("🤖 Sending to Gemini LLM...")
    structure = extract_bill_items(pages)

    print("🧮 Computing totals...")
    return compute_totals(structure)

# ============================================================
# 🚀 TEST (Using Datathon sample)
# ============================================================
sample_request = {
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/Sample%20Document%203.pdf?sv=2025-07-05&spr=https&st=2025-11-28T10%3A08%3A55Z&se=2025-11-30T10%3A08%3A00Z&sr=b&sp=r&sig=S7bEYe%2FswaS7BZPZBiEnc6gXfb9YUH22H%2BBn%2FG2Vycc%3D"
}

output = extract_bill_from_url(sample_request)

print("\n==================== FINAL JSON ====================")
# print(json.dumps(output, indent=2))
output = extract_bill_from_url(sample_request)
final_output = format_final_output(output)

print(json.dumps(final_output, indent=2))