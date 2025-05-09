# chunker.py

import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def chunk_text_by_item(docs: list[tuple[str, str, list[str]]], chunk_size=1024, chunk_overlap=100) -> list[Document]:
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
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "year": year,
                        "part": section["part"],
                        "item": section["item"],
                        "item_title": section["title"],
                        "chunk_id": i,
                        "contains_table": False
                    }
                )
                all_documents.append(doc)

        # 테이블 청크
        for i, table_html in enumerate(tables):
            doc = Document(
                page_content=table_html,
                metadata={
                    "year": year,
                    "part": "Unknown",
                    "item": "Table",
                    "item_title": "HTML Table",
                    "chunk_id": i,
                    "contains_table": True
                }
            )
            all_documents.append(doc)

    return all_documents

# def chunk_text_by_item(docs: list[tuple[str, str]], chunk_size=1024, chunk_overlap=100) -> list[Document]:
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         separators=["\n\n", "\n", ". ", " "]
#     )

#     item_pattern = re.compile(r"^ITEM\s+(\d+[A-Z]?)\.?\s+(.*)", re.IGNORECASE | re.MULTILINE)

#     all_documents = []  # ✅ 반드시 있어야 함!

#     for year, text in docs:
#         matches = list(item_pattern.finditer(text))
#         print(f"[DEBUG] Found {len(matches)} item sections in year {year}")

#         item_sections = []
#         for i, match in enumerate(matches):
#             start = match.start()
#             end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
#             section_text = text[start:end].strip()
#             item = f"Item {match.group(1)}"
#             title = match.group(2).strip()
#             part = "Unknown Part"

#             item_sections.append({
#                 "part": part,
#                 "item": item,
#                 "title": title,
#                 "text": section_text
#             })

#         for section in item_sections:
#             chunks = splitter.split_text(section["text"])
#             for i, chunk in enumerate(chunks):
#                 doc = Document(
#                     page_content=chunk,
#                     metadata={
#                         "year": year,
#                         "part": section["part"],
#                         "item": section["item"],
#                         "item_title": section["title"],
#                         "chunk_id": i
#                     }
#                 )
#                 all_documents.append(doc)

#     return all_documents