import os
from langchain_core.documents import Document
from bs4 import BeautifulSoup
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import tiktoken

class HTMLWithImageLoader:
    """Loader class để đọc file HTML kèm hình ảnh."""

    def __init__(self, file_path: str):
        """Khởi tạo loader với đường dẫn file HTML.

        Args:
            file_path: Đường dẫn đến file HTML cần xử lý
        """
        self.file_path = file_path

    def _process_html_with_images(self) -> str:
        """Đọc và xử lý nội dung HTML, chuyển đổi hình ảnh thành định dạng đặc biệt."""

        # Đọc file HTML
        with open(self.file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Parse HTML với BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Xử lý các thẻ hình ảnh
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                # Tạo text mới với định dạng image_link
                img_text = soup.new_string(f'\n image_link: "{img_url}"\n')
                img.replace_with(img_text)

        # Lấy phần nội dung chính từ body
        content_div = soup.find("div", class_="page")
        if not content_div:
            content_div = soup.body  # Nếu không có div.page thì lấy toàn bộ body

        # Trích xuất văn bản với các liên kết hình ảnh nội tuyến
        if content_div:
            text = content_div.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        return text

    def load(self) -> List[Document]:
        """Tải và chuyển đổi HTML thành Document(s).

        Returns:
            Danh sách Document với nội dung và metadata
        """
        text_content = self._process_html_with_images()
        metadata = {"source": self.file_path}

        # Tạo đối tượng Document
        document = Document(page_content=text_content, metadata=metadata)
        return [document]