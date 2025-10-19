import PyPDF2

class DocumentChunker:
    chunk_token_size: int
    overlap: int
    
    def __init__(self, chunk_token_size=100, overlap=20):
        self.chunk_token_size = chunk_token_size
        self.overlap = overlap

    def __main__(self):
        sample_text = "This is a sample text to demonstrate the chunking functionality. " * 100
        chunks = self.chunk_text(sample_text)
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1}:\n{chunk}\n")


    def chunk_documents(self, document_paths: list[str]) -> list[str]:
        chunks = []
        for doc in document_paths:
            if doc.lower().endswith('.pdf'):
                text = self._getTextFromPDF(doc)
            else:
                with open(doc, 'r', encoding='utf-8') as file:
                    text = file.read()
            chunks.append(self.chunk_text(text))
        return chunks
    
    def chunk_text(self, text: str) -> list[str]:
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_token_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_token_size - self.overlap

        return chunks
    
    def _getTextFromPDF(self, pdf_path):
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
if __name__ == "__main__":
    doc_chunker = DocumentChunker()
    doc_chunker.__main__()