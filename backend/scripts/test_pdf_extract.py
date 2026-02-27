from backend.utils_pdf import extract_form_200_data
import json

def test_extraction():
    pdf_path = r"c:\sicjac\formularios\F-200 12-2025.pdf"
    try:
        data = extract_form_200_data(pdf_path)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    test_extraction()
