import pdfplumber
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python print_pdf_text.py <caminho_para_pdf>")
        sys.exit(1)
    file_path = sys.argv[1]

    with pdfplumber.open(file_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text() or "[Nenhum texto extraído]"
        print("Texto da primeira página:\n")
        print(text)
