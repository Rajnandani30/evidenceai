from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path):

    pdf_path = Path(file_path)

    reader = PdfReader(pdf_path)

    pages = []

    # Basic document metadata
    metadata = reader.metadata or {}

    title = metadata.get("/Title") or pdf_path.stem
    author = metadata.get("/Author") or "Unknown"

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        pages.append(
            {
                "file_name": pdf_path.name,
                "title": title,
                "author": author,
                "page_number": page_number,
                "source": pdf_path.name,
                "text": text.strip(),
            }
        )

    return pages


if __name__ == "__main__":

    pdf_path = "data/pdf_documents/sample.pdf"

    pages = load_pdf(pdf_path)

    print("PDF:", pages[0]["file_name"])
    print("Title:", pages[0]["title"])
    print("Author:", pages[0]["author"])
    print("Number of pages:", len(pages))

    for page in pages[:2]:

        print("\nPage:", page["page_number"])
        print("Source:", page["source"])
        print(page["text"][:500])