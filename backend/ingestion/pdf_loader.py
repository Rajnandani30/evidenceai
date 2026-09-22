from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path):
    pdf_path = Path(file_path)

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "file_name": pdf_path.name,
                "page_number": page_number,
                "text": text.strip(),
            }
        )

    return pages


if __name__ == "__main__":
    pdf_path = "data/pdf_documents/sample.pdf"

    pages = load_pdf(pdf_path)

    print("PDF:", pages[0]["file_name"])
    print("Number of pages:", len(pages))

    for page in pages[:2]:
        print("\nPage:", page["page_number"])
        print(page["text"][:500])