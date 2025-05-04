# chunker.py

import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def chunk_text_by_item(text: str, chunk_size=1024, chunk_overlap=100) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "]
    )

    # Item 헤더 패턴 (예: Item 1. Business)
    item_pattern = re.compile(
        r"(Part\s+[IVXLCDM]+)?\s*Item\s+(\d+[A-Z]?)\.?\s*(.*)",
        re.IGNORECASE
    )

    # Item 시작 위치 기록
    matches = list(item_pattern.finditer(text))
    item_sections = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()

        part = match.group(1) or "Unknown Part"
        item = match.group(2)
        title = match.group(3).strip()
        item_name = f"Item {item}"
        part = part.strip() if part else "Unknown Part"

        item_sections.append({
            "part": part,
            "item": item_name,
            "title": title,
            "text": section_text
        })

    # 청킹 + 메타데이터 부착
    documents = []
    for section in item_sections:
        chunks = splitter.split_text(section["text"])
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "part": section["part"],
                    "item": section["item"],
                    "item_title": section["title"],
                    "chunk_id": i
                }
            )
            documents.append(doc)

    return documents
