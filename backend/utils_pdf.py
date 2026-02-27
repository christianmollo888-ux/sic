import re
from pypdf import PdfReader

def extract_form_200_data(file_path):
    """
    Extracts key fields from Formulario 200 PDF using pypdf.
    Returns a dictionary with the extracted data.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Debug: print(text) 
    
    data = {
        "header": {
            "version": "6", # Default if not found
            "presentation_date": None,
            "print_date": None,
            "pdf_user": None
        },
        "rubro1": {},
        "rubro2": {},
        "rubro3": {}
    }
    
    # Extract Header info
    # Pattern: NIT, AÑO, MES followed by their values on the next line
    header_pattern = r"NIT\s+AÑO\s+MES\n(\d+)\s+(\d{4})\s+(\d{1,2})"
    header_match = re.search(header_pattern, text)
    if header_match:
        data["header"]["nit"] = header_match.group(1)
        data["header"]["year"] = header_match.group(2)
        data["header"]["month"] = header_match.group(3)
        
    razon_social_pattern = r"NOMBRE\(S\) Y APELLIDO\(S\) O Razón Social del SUJETO PASIVO IDENTIFICADOR DEUDA\n(.*?)\s+\d+"
    razon_social_match = re.search(razon_social_pattern, text, re.IGNORECASE)
    if razon_social_match:
        data["header"]["business_name"] = razon_social_match.group(1).strip()

    # Extract Version
    version_pattern = r"Formulario 200 - Versión (\d+)"
    version_match = re.search(version_pattern, text)
    if version_match:
        data["header"]["version"] = version_match.group(1)

    # Extract Audit Info
    # Fecha y hora de presentación: 08/01/2026 11:42:41
    pres_pattern = r"Fecha y hora de presentación:\s*([\d/]+\s+[\d:]+)"
    pres_match = re.search(pres_pattern, text)
    if pres_match:
        data["header"]["presentation_date"] = pres_match.group(1)

    # Fecha y hora de Impresión: 08/01/2026 11:56:01
    print_pattern = r"Fecha y hora de Impresión:\s*([\d/]+\s+[\d:]+)"
    print_match = re.search(print_pattern, text)
    if print_match:
        data["header"]["print_date"] = print_match.group(1)

    # Usuario: taide.guardia@gmail.com
    user_pattern = r"Usuario:\s*([^\s\n]+)"
    user_match = re.search(user_pattern, text)
    if user_match:
        data["header"]["pdf_user"] = user_match.group(1)

    # Extract Casillas using Regex
    # Pattern: Digit(s) followed by optional spaces and a numeric value
    def get_casilla_value(c_number):
        # Pattern: field number followed by value (often separated by space or newline)
        # Handle cases like "13 0" or "11 47.652" or "114 6.194,80"
        pattern = rf"\s+{c_number}\s+([\d\.,]+)"
        match = re.search(pattern, text)
        if match:
            raw_str = match.group(1).strip()
            if ',' in raw_str:
                # If there's a comma, treat it as the decimal separator (Bolivian format)
                clean_str = raw_str.replace('.', '').replace(',', '.')
            else:
                # If there's only a dot, assuming pypdf extracted it as an English float (e.g. 4765.2)
                clean_str = raw_str
            
            try:
                return float(clean_str)
            except ValueError:
                return 0.0
        return 0.0

    # Rubro 1
    casillas_r1 = ["13", "14", "15", "505", "16", "17", "18", "39", "55", "19", "1002"]
    for c in casillas_r1:
        data["rubro1"][f"C{c}"] = get_casilla_value(c)

    # Rubro 2
    casillas_r2 = ["11", "26", "31", "27", "28", "114", "30", "1003", "1004"]
    for c in casillas_r2:
        data["rubro2"][f"C{c}"] = get_casilla_value(c)

    # Rubro 3
    casillas_r3 = ["693", "909", "635", "1001", "621", "629", "622", "640", "468", "465", "466", "996"]
    for c in casillas_r3:
        data["rubro3"][f"C{c}"] = get_casilla_value(c)

    return data
