import os
import io
import zipfile
import fitz
import pytesseract
from pathlib import Path
from PIL import Image
from config import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

SUBJECT_KEYWORDS = {
    "CN": ["network", "tcp", "ip", "routing", "osi", "protocol", "ethernet", "subnet", "dns", "http", "cn", "computer network"],
    "ML": ["machine learning", "neural", "regression", "classification", "clustering", "svm", "decision tree", "ml", "gradient", "epoch"],
    "Python": ["python", "def ", "class ", "pandas", "numpy", "flask", "django", "list comprehension", "lambda"],
    "Database": ["sql", "dbms", "normalization", "er diagram", "transaction", "acid", "join", "query", "relational", "database"],
    "DOS": ["operating system", "process", "thread", "scheduling", "deadlock", "memory management", "dos", "semaphore", "paging"],
    "C": ["pointer", "malloc", "struct", "printf", "scanf", "array", "linked list", "c programming", "#include"],
}

FILE_TYPE_KEYWORDS = {
    "PYQ": ["question paper", "q.p", "qp", "mid sem", "end sem", "university exam", "examination", "2019", "2020", "2021", "2022", "2023", "2024"],
    "Notes": ["notes", "lecture", "unit", "chapter", "handwritten", "module"],
    "Reference": ["reference", "textbook", "solution", "assignment"],
}


def extract_zip(zip_path: str, extract_to: str) -> list:
    extracted_files = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_to)
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            full_path = os.path.join(root, file)
            extracted_files.append(full_path)
    return extracted_files


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def ocr_pdf_with_tesseract(pdf_path: str, max_pages: int = 2) -> str:
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_to_scan = min(total_pages, max_pages)
    
    all_text = []
    
    for i in range(pages_to_scan):
        page = doc[i]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        
        image = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(image)
        all_text.append(text)
    
    doc.close()
    return "\n\n".join(all_text)


def ocr_image_with_tesseract(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def detect_subject(filename: str, text_sample: str) -> str:
    combined = (filename + " " + text_sample).lower()
    scores = {}
    for subject, keywords in SUBJECT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in combined)
        scores[subject] = score
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "Unknown"
    return best


def detect_file_type(filename: str, text_sample: str) -> str:
    combined = (filename + " " + text_sample).lower()
    scores = {}
    for ftype, keywords in FILE_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in combined)
        scores[ftype] = score
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "Unknown"
    return best


def process_file(file_path: str) -> dict:
    import io
    
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    filename = file_path.name

    result = {
        "filename": filename,
        "path": str(file_path),
        "extension": extension,
        "raw_text": "",
        "subject": "Unknown",
        "file_type": "Unknown",
        "ocr_used": False,
        "error": None
    }

    if extension == ".pdf":
        text = extract_text_from_pdf(str(file_path))
        if len(text) < 100:
            text = ocr_pdf_with_tesseract(str(file_path), max_pages=2)
            result["ocr_used"] = True
        result["raw_text"] = text

    elif extension in [".jpg", ".jpeg", ".png"]:
        text = ocr_image_with_tesseract(str(file_path))
        result["raw_text"] = text
        result["ocr_used"] = True

    elif extension == ".txt":
        with open(str(file_path), "r", encoding="utf-8", errors="ignore") as f:
            result["raw_text"] = f.read()

    else:
        result["error"] = f"Unsupported file type: {extension}"
        return result

    text_sample = result["raw_text"][:500]
    result["subject"] = detect_subject(filename, text_sample)
    result["file_type"] = detect_file_type(filename, text_sample)

    return result


def process_upload(zip_path: str, extract_dir: str) -> dict:
    all_files = extract_zip(zip_path, extract_dir)
    
    subject_buckets = {}

    for file_path in all_files:
        ext = Path(file_path).suffix.lower()
        if ext not in [".pdf", ".jpg", ".jpeg", ".png", ".txt"]:
            continue
        
        processed = process_file(file_path)
        
        subject = processed["subject"]
        if subject not in subject_buckets:
            subject_buckets[subject] = {
                "PYQ": [],
                "Notes": [],
                "Reference": [],
                "Unknown": []
            }
        
        file_type = processed["file_type"]
        if file_type not in subject_buckets[subject]:
            file_type = "Unknown"
        
        subject_buckets[subject][file_type].append(processed)

    return subject_buckets