import os
from PyPDF2 import PdfReader

tenders_file_path = os.path.join(os.path.dirname(__file__), "tenders")
tenders = [t for t in os.listdir(tenders_file_path) if t.endswith(".pdf")]
tenders_info = {}
for tender in tenders:
    print(f"Reading the tender {tender} ...")
    reader = PdfReader(os.path.join(tenders_file_path, tender))

    tenders_info[tender] = {}
    tenders_info[tender]["name"] = tender
    tenders_info[tender]["content"] = [page.extract_text() for page in reader.pages]

tender_info = "".join(tenders_info[tenders[0]].get("content", {}))
print(tender_info)
