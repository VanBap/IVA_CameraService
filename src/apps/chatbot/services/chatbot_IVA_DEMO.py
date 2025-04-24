import os
import re

from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

# === Vannhk ===
import time

from . IVA_HDSD_chunk import process_html_with_chunking
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

VECTOR_DB_DEMO_PATH = os.getenv("VECTOR_DB_DEMO_IVA_FULL_PATH")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
collection_name = "VBD_full_documents"

# === EMBEDDING (accuracy #6>#3>#2>#1>#4) ===
# embeddings = HuggingFaceEmbeddings(model_name='keepitreal/vietnamese-sbert') #1
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v2") #2
# embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5") #3
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2") #4
# embeddings = HuggingFaceEmbeddings(model_name="VoVanPhuc/sup-SimCSE-VietNamese-phobert-base") #5

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/LaBSE') #6

# === CHECK IF VECTOR DB EXISTED ===
# Kiểm tra xem collection đã tồn tại trong Milvus chưa
from pymilvus import utility, connections

connections.disconnect(alias='default')
# Kết nối đến Milvus
connections.connect(
    alias="default",
    uri=VECTOR_DB_DEMO_PATH
)

collection_exists = utility.has_collection(collection_name)

# # Sau đoạn code kiểm tra collection_exists
# if collection_exists:
#     print("[INFO] Collection đã tồn tại. Đang xóa và tạo lại...")
#     utility.drop_collection(collection_name)
#     collection_exists = False

if not collection_exists:
    print("[INFO] ================ chatbot_TEST =======================")
    print("[INFO] Lần đầu tiên chạy - Đang tải và embedding dữ liệu...")
    start = time.time()

    # ============== LOAD DATA FROM FILE .HTML =============================
    file_path = "/home/vbd-vanhk-l1-ubuntu/Desktop/Job/camera-service/src/apps/chatbot/data/IVA_HDSD_full/IVA_HDSD_full-with-image-refs.html"
    all_splits = process_html_with_chunking(file_path)

    print(f"[INFO] Đã tách thành {len(all_splits)} đoạn")

    # In thông tin về một số đoạn đầu tiên để kiểm tra
    for i in range(len(all_splits)):
        doc = all_splits[i]
        print(f"\n--- Đoạn {i + 1} ---")
        print(f"Metadata: {doc.metadata}")
        print(doc.page_content)
        has_images = "image_link:" in doc.page_content
        print(f"Có hình ảnh: {has_images}")
        if has_images:
            image_links = [line.strip() for line in doc.page_content.split("\n") if "image_link:" in line]
            print(f"image_links: {image_links}")
            print(f"Số lượng hình ảnh: {len(image_links)}")

    # ============ TEST MILVUS as VECTOR STORE ==============

    # Khi tạo mới vector store
    # Phiên bản đơn giản hơn không sử dụng hybrid search
    vector_store = Milvus.from_documents(
        documents=all_splits,
        embedding=embeddings,
        connection_args={"uri": VECTOR_DB_DEMO_PATH},
        collection_name=collection_name,
        text_field="page_content",
        vector_field="embedding",
        consistency_level="Strong",
    )

    end = time.time()
    print(f"[SPLIT + EMBEDDING DATA] {end-start} seconds")
    print("[INFO] Lưu trữ Vector DB thành công!")

else:
    print("[INFO] ================ chatbot_TEST =======================")
    print("[INFO] Đang load vector store đã tồn tại...")

    # Khi load vector store đã tồn tại
    vector_store = Milvus(
        collection_name=collection_name,
        embedding_function=embeddings,
        connection_args={"uri": VECTOR_DB_DEMO_PATH},
        text_field="page_content",
        vector_field="embedding",
        enable_dynamic_field=True,

    )




from . vannhk_template import template1
prompt = PromptTemplate.from_template(template1)

# === Choose LLM model ===
llm = ChatOpenAI(model_name="gpt-4o-mini",
                 api_key=OPEN_API_KEY,
                 base_url="https://models.inference.ai.azure.com",
                 temperature=0.0)


# === Define state for application ===
class State(TypedDict):
    question: str
    context: List[Document]
    answer:str


def convert_local_path_to_url(local_path):
    """
    Chuyển đổi đường dẫn local sang URL storage

    Args:
        local_path (str): Đường dẫn local đến file ảnh

    Returns:
        str: URL tương ứng trên storage server
    """
    # Định nghĩa pattern để tìm phần đường dẫn cần thiết
    pattern = r"/home/vbd-vanhk-l1-ubuntu/Desktop/Job/camera-service/src/apps/chatbot/data/IVA_HDSD_full/IVA_HDSD_full-with-image-refs_artifacts/(.*?)\.png"

    # Tìm kiếm pattern trong đường dẫn
    match = re.search(pattern, local_path)

    if match:
        # Lấy phân đoạn cần thiết từ đường dẫn
        image_path = match.group(1)

        # Tạo URL với định dạng yêu cầu
        url = f"https://storage-iva.vizone.ai/vannk/IVA_HDSD_full/IVA_HDSD_full-with-image-refs_artifacts/{image_path}.png"

        return url
    else:
        return "Không tìm thấy pattern đường dẫn hợp lệ"


def process_chatbot_answer(answer):
    """
    Xử lý câu trả lời chatbot để chuyển đổi các đường dẫn ảnh từ local path sang URL

    Args:
        answer (str): Câu trả lời của chatbot

    Returns:
        str: Câu trả lời đã được xử lý với các đường dẫn ảnh thành URL
    """
    # Pattern để tìm đường dẫn image_link trong câu trả lời

    image_link_pattern = r'image_link:\s*"([^"]+)"'

    lines = answer.splitlines()
    processed_lines = []

    for line in lines:
        match = re.search(image_link_pattern, line)
        if match:
            local_path = match.group(1)
            url = convert_local_path_to_url(local_path)
            processed_lines.append(f"![Hình ảnh minh họa]({url})")
        else:
            processed_lines.append(line)

    return "\n".join(processed_lines)


# === Define application steps (NODES) ===
def rewrite_query(state: State):
    query = state["question"]
    start = time.time()
    # Su dung LLM de tao ra cac bien the cua cau hoi
    messages = [
        {"role": "system",
         "content": "Tạo từ khóa tìm kiếm ngắn gọn từ câu hỏi sau."},
        {"role": "user",
         "content": query}
    ]
    response = llm.invoke(messages)
    expanded_query = response.content
    print(f"===> [REWRITE QUERY] {expanded_query}")
    end = time.time()
    print(f"[REWRITE_QUERY TIME] {end - start}s")
    return {"question": expanded_query}

def retrieve(state: State):
    start = time.time()
    retrieved_docs = vector_store.similarity_search(state["question"], k=3) #default k = 4

    # Log các chunk được lấy ra để kiểm tra
    print(f"[DEBUG] Retrieved {len(retrieved_docs)} chunks")
    for i, doc in enumerate(retrieved_docs):
        print(f"[DEBUG] Chunk {i + 1} metadata: {doc.metadata}")
        print(f"[DEBUG] Chunk {i + 1} first 100 chars: {doc.page_content[:100]}...")


    end = time.time()
    print(f"[RETRIEVE TIME] {end-start}s")
    return {"context": retrieved_docs}

def generate(state: State):
    start = time.time()
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])

    messages = prompt.invoke({"question": state["question"], "context":docs_content})
    response = llm.invoke(messages)

    processed_answer = process_chatbot_answer(response.content)

    end = time.time()
    print(f"[GENERATE TIME] {end - start}s")
    return {"answer": processed_answer}

# Compile application and test (CONTROL FLOW)
graph_builder = StateGraph(State).add_sequence([rewrite_query ,retrieve, generate]) # Dam bao "ket noi": "retrieve" chay truoc, "generate" chay sau.
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

from langdetect import detect
def is_valid_query(query: str) -> bool:
    """
    Kiem tra query co phai 1 cau hop le hay khong
    """
    try:
        lang = detect(query)
        print(f"[DEBUG] LANGE: {lang}")
        if lang != "vi" and lang != "no" and lang != "es" and lang != "nl" and lang != "so":
            print("False 1 ")
            return False
        if len(query.strip().split()) <1:
            print("False 2 ")
            return False
        print("True")
        return True
    except:
        print("False 3")
        return False

def chatbot_run (text):
    start = time.time()
    response = graph.invoke(text)
    response = dict(response)

    # print(f"CONTEXT: {response['context']}")
    # print(f":ANSWER {response['answer']}")

    # print(response)
    end = time.time()
    print(f"[TOTAL RESPONSE] TIME: {end - start}")

    response = dict(response)
    return response






