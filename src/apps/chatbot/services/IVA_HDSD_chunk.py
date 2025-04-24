import os
from langchain_core.documents import Document
from bs4 import BeautifulSoup
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import tiktoken

from . IVA_HDSD_crawl_data import HTMLWithImageLoader

class IVA_HDSD_SupportChunker:
    """Chunker cho tài liệu IVA HDSD, phân đoạn theo tiêu đề."""

    def __init__(self, chunk_size=6000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Pattern cho các header và section
        self.header_patterns = [
            # Tiêu đề dạng "3.7.1. Xem danh sách event đếm theo quy tắc"
            r'^(\d+\.\d+\.\d+\.)\s+(.+)$',
            # # Tiêu đề dạng "3.7. Event đếm theo quy tắc"
            # r'^(\d+\.\d+\.)\s+(.+)$',

            # # Tiêu đề dạng "3. Hướng dẫn sử dụng"
            # r'^(\d+\.)\s+(.+)$',
        ]

        # Tokenizer de dem Tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """Đếm số lượng tokens trong một đoạn text"""
        return len(self.tokenizer.encode(text))

    def extract_images_from_text(self, text):
        """Trích xuất tất cả các link hình ảnh từ văn bản"""
        images = []
        lines = text.split('\n')
        for line in lines:
            if 'image_link:' in line:
                images.append(line.strip())
        return images

    def split_by_headers(self, text):
        """Tách text thành các đoạn dựa vào các header"""
        # Tách văn bản bằng regex
        sections = []
        current_section = ""

        lines = text.split("\n")

        for line in lines:
            # Kiểm tra xem dòng hiện tại có phải là header không
            is_header = any(re.search(pattern, line) for pattern in self.header_patterns)

            if is_header and current_section:
                # Lưu section hiện tại và bắt đầu section mới
                sections.append(current_section)
                current_section = line + "\n"
            else:
                # Thêm dòng vào section hiện tại
                current_section += line + "\n"

        # Thêm section cuối cùng
        if current_section:
            sections.append(current_section)

        return sections

    def ensure_images_in_chunks(self, chunks):
        """Đảm bảo mỗi chunk chứa đúng link hình ảnh liên quan đến nội dung đó"""
        processed_chunks = []
        header_to_images = {}  # Dict: mapping header -> img_urls

        # Lần đầu, tạo mapping giữa header và images
        for chunk in chunks:
            lines = chunk.split("\n")
            current_header = None

            for line in lines:
                # Xác định header
                is_header = any(re.search(pattern, line) for pattern in self.header_patterns)
                if is_header:
                    current_header = line.strip()

                # Thu thập link hình ảnh cho header hiện tại
                if current_header and "image_link:" in line:
                    if current_header not in header_to_images:
                        header_to_images[current_header] = []
                    header_to_images[current_header].append(line.strip())

        # Lần thứ hai, thêm link hình ảnh vào mỗi chunk
        for chunk in chunks:
            chunk_header = None
            chunk_lines = chunk.split("\n")

            for line in chunk_lines:
                is_header = any(re.search(pattern, line) for pattern in self.header_patterns)
                if is_header:
                    chunk_header = line.strip()
                    break

            # Kiểm tra xem chunk đã có link hình ảnh chưa
            has_images = any("image_link:" in line for line in chunk_lines)

            # Nếu chunk có header nhưng không có hình ảnh, thêm vào
            if chunk_header and not has_images and chunk_header in header_to_images:
                chunk += "\n" + "\n".join(header_to_images[chunk_header])

            processed_chunks.append(chunk)

        return processed_chunks

    def split_text(self, text):
        """Tách text thành các đoạn, đảm bảo giữ nguyên cấu trúc và link hình ảnh"""
        # Bước 1: Tách theo headers
        header_sections = self.split_by_headers(text)

        # Bước 2: Tách tiếp các section dài hơn chunksize
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )

        all_chunks = []
        for section in header_sections:
            # Kiểm tra độ dài của section
            if self.count_tokens(section) > self.chunk_size:
                # Thu thập hình ảnh trước khi tách
                images = self.extract_images_from_text(section)

                # Tách section thành các đoạn nhỏ hơn
                sub_chunks = splitter.split_text(section)

                # Đảm bảo link hình ảnh được giữ nguyên trong các chunk con
                for i, chunk in enumerate(sub_chunks):
                    # Nếu đây là chunk cuối và chưa có hình ảnh, thêm vào
                    if i == len(sub_chunks) - 1 and not any("image_link:" in line for line in chunk.split("\n")):
                        for img in images:
                            if img not in chunk:
                                chunk += f"\n{img}"

                    all_chunks.append(chunk)
            else:
                all_chunks.append(section)

        # Bước 3: Đảm bảo mỗi chunk chứa đúng link hình ảnh
        processed_chunks = self.ensure_images_in_chunks(all_chunks)

        return processed_chunks

    def create_documents(self, documents: List[Document]) -> List[Document]:
        """Tạo danh sách Document từ danh sách Document đầu vào"""
        result_docs = []

        for doc in documents:
            # Xử lý từng document
            chunks = self.split_text(doc.page_content)

            for i, chunk in enumerate(chunks):
                # Tạo metadata mới cho mỗi chunk
                chunk_metadata = doc.metadata.copy() if doc.metadata else {}
                chunk_metadata["chunk_id"] = i
                chunk_metadata["total_chunks"] = len(chunks)
                chunk_metadata["has_images"] = "image_link:" in chunk
                chunk_metadata["image_count"] = chunk.count("image_link:")

                result_docs.append(Document(page_content=chunk, metadata=chunk_metadata))

        return result_docs


def load_html_file(file_path: str) -> List[Document]:
    """Hàm tiện ích để tải file HTML.

    Args:
        file_path: Đường dẫn đến file HTML

    Returns:
        Danh sách Document từ file HTML
    """
    loader = HTMLWithImageLoader(file_path)
    docs = loader.load()
    return docs


def process_html_with_chunking(file_path: str, chunk_size=6000, chunk_overlap=200) -> List[Document]:
    """Hàm kết hợp để tải file HTML và chia nhỏ thành các đoạn.

    Args:
        file_path: Đường dẫn đến file HTML
        chunk_size: Kích thước tối đa của mỗi đoạn văn bản
        chunk_overlap: Độ chồng lấp giữa các đoạn

    Returns:
        Danh sách Document đã được chia nhỏ
    """
    # Tải file HTML
    docs = load_html_file(file_path)

    # Khởi tạo chunker và xử lý documents
    chunker = IVA_HDSD_SupportChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    processed_docs = chunker.create_documents(docs)

    return processed_docs