from pypdf import PdfReader
import sys

def debug_pdf_text(file_path):
    reader = PdfReader(file_path)
    print(f"Total Pages: {len(reader.pages)}")
    for i, page in enumerate(reader.pages):
        print(f"--- Page {i+1} ---")
        text = page.extract_text()
        print(text)
        print("--- Raw segments (approximate) ---")
        # Extracting segments can be complex, but let's look for specific Rubro 2 parts
        if "RUBRO 2" in text:
            start = text.find("RUBRO 2")
            print(text[start:start+1000])

if __name__ == "__main__":
    pdf_path = r"c:\sicjac\formularios\F-200 12-2025.pdf"
    debug_pdf_text(pdf_path)
