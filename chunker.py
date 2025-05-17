
# chunker.py
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# def chunk_text_by_item(docs: list[tuple[str, str, list[str]]], chunk_size=1024, chunk_overlap=100) -> list[Document]:
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         separators=["\n\n", "\n", ". ", " "]
#     )

def chunk_text_by_item(
                        docs: list[tuple[str, str, list[str]]],
                        ticker: str,
                        company_name: str,
                        conformed_period: str,
                        filing_year: int,
                        chunk_size=1024,
                        chunk_overlap=100
                    ) -> list[Document]:
    
    splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ". ", " "]
            )


    item_pattern = re.compile(r"^ITEM\s+(\d+[A-Z]?)\.?\s+(.*)", re.IGNORECASE | re.MULTILINE)
    all_documents = []

    for year, text, tables in docs:
        matches = list(item_pattern.finditer(text))
        print(f"[DEBUG] Found {len(matches)} item sections in year {year}")

        item_sections = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()
            item = f"Item {match.group(1)}"
            title = match.group(2).strip()
            part = "Unknown Part"

            item_sections.append({
                "part": part,
                "item": item,
                "title": title,
                "text": section_text
            })

        # 텍스트 청크
        for section in item_sections:
            chunks = splitter.split_text(section["text"])
            for i, chunk in enumerate(chunks):
                contains_table = "[Structured Table Data]" in chunk
                doc = Document(
                            page_content=chunk,
                            metadata={
                                "ticker": ticker,
                                "company_name": company_name,
                                "fiscal_year": year,
                                "filing_year": filing_year,
                                "conformed_period_of_report": conformed_period,
                                "year": year,
                                "part": section["part"],
                                "item": section["item"],
                                "item_title": section["title"],
                                "chunk_id": i,
                                "contains_table": contains_table
                            }
                        )
                all_documents.append(doc)
                    
    return all_documents
