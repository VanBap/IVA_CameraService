template1 = """ 
Hướng dẫn chi tiết theo yêu cầu người hỏi. Nếu trong văn bản có đường dẫn hình ảnh ("image_link:"), hãy đưa chúng vào câu trả lời để minh họa rõ hơn.

Câu hỏi gốc: {question}
Thông tin chi tiết từ hệ thống: {context}

Trong câu trả lời của bạn:
1. Nếu có thông tin về các bước, hãy trình bày theo từng bước rõ ràng
2. Đối với mỗi bước mà có hình ảnh liên quan (có dòng "image_link:"), hãy đưa link ảnh đó vào cuối phần giải thích của bước đó
3. Định dạng câu trả lời giống như ví dụ minh họa sau:

**1.1.1 [Tên tiêu đề] ** (Thay thế "1.1.1." theo header tương đương trong context)
**a. [Tên mục con] ** (Nếu có: thay thế "a." theo tên mục con tương đương của trong trong context)
**Bước 1: [Tên bước]** (Nếu không phải "Bước" thì trả về văn bản bình thường.)
[Giải thích chi tiết]
image_link: "/path/to/image.png" (nếu có)

**Bước 2: [Tên bước]**
[Giải thích chi tiết]
image_link: "/path/to/image.png" (nếu có)

QUAN TRỌNG: Hãy sao chép chính xác các đường dẫn hình ảnh kèm theo dấu ngoặc kép như trong văn bản gốc.
Chỉ trả lời dựa trên thông tin được cung cấp, không thêm thông tin không có trong văn bản gốc.
"""