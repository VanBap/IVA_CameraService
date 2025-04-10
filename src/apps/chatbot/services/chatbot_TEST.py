import os

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
import pickle
from langchain_community.vectorstores import FAISS

# === Vannhk ===
from . import chatbot_crawl_data as crawl_data
from . splitter import SapoSupportChunker
import time

from langchain_milvus import Milvus


VECTOR_DB_DEMO_PATH = os.getenv("VECTOR_DB_PATH_MILVUS")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
collection_name = "sapo_documents"

# === CHECK IF VECTOR DB EXISTED ===

if os.path.exists(VECTOR_DB_DEMO_PATH):
    print("[INFO] ================ chatbot_TEST =======================")
    print("[INFO] Đã tồn tại vector store - Đang load lại từ Milvus...")
    vector_store = Milvus(
        collection_name=collection_name,
        embedding_function=embeddings,
        connection_args={
            "uri": VECTOR_DB_DEMO_PATH
        }
    )

else:
    print("[INFO] ================ chatbot_TEST =======================")
    print("[INFO] Lần đầu tiên chạy - Đang tải và embedding dữ liệu...")
    start = time.time()

    # url = "https://support.sapo.vn/ket-noi-kenh-facebook-tren-app-sapo"
    # loader = crawl_data.WebWithImageLoader(web_paths=(url,))
    # documents = loader.load()

    base_url = "https://support.sapo.vn/sapo-retail"
    get_article_links = crawl_data.get_article_links(base_url)
    documents = crawl_data.load_articles(get_article_links)

    print(f"[INFO] Đã tải {len(documents)} tài liệu từ URL")

    chunker = SapoSupportChunker(chunk_size=2000, chunk_overlap=200)
    all_splits = chunker.split_documents(documents)

    print(f"[INFO] Đã tách thành {len(all_splits)} đoạn")

    # In thông tin về một số đoạn đầu tiên để kiểm tra
    for i in range(len(all_splits)):
        doc = all_splits[i]
        print(f"\n--- Đoạn {i + 1} ---")
        print(f"Metadata: {doc.metadata}")
        print(doc.page_content)
        has_images = "image link:" in doc.page_content
        print(f"Có hình ảnh: {has_images}")
        if has_images:
            image_links = [line.strip() for line in doc.page_content.split("\n") if "image link:" in line]
            print(f"image_links: {image_links}")
            print(f"Số lượng hình ảnh: {len(image_links)}")




    # ============ TEST MILVUS as VECTOR STORE ==============

    vector_store = Milvus.from_documents(
        documents = all_splits,
        embedding = embeddings,
        connection_args={
            "uri": VECTOR_DB_DEMO_PATH
        },
        collection_name = collection_name,
        # drop_old=True
    )

    # # === Lưu Vector DB để sử dụng sau ===
    # with open(VECTOR_DB_DEMO_PATH, "wb") as f:
    #     pickle.dump(vector_store, f)

    end = time.time()
    print(f"[CRAWL + SPLIT + EMBEDDING DATA] {end-start} seconds")
    print("[INFO] Lưu trữ Vector DB thành công!")



# === Choose LLM model ===
# Model 1: gpt-4o
llm = ChatOpenAI(model_name="gpt-4o-mini",
                 api_key=OPEN_API_KEY,
                 base_url="https://models.inference.ai.azure.com",
                 temperature=0.0)

# # Model 2: OpenVlab/1B
# llm = ChatOpenAI(model_name="OpenGVLab/InternVL2_5-1B",
#                  api_key="EMPTY",
#                  base_url="http://10.124.64.125:9903/v1/",
#                  temperature=0.0)

print(f"[MODEL NAME]: {llm.model_name}")

# === Define state for application ===
class State(TypedDict):
    question: str
    context: List[Document]
    answer:str


# === Define application steps (NODE) ===
def retrieve(state: State):
    start = time.time()

    retrieved_docs = vector_store.similarity_search(state["question"], k=7) #default k=4

    # # Phân tích các đoạn văn bản này
    # has_images = any("<image_link>" in doc.page_content for doc in retrieved_docs)
    #
    # # Thông báo debug nếu có hình ảnh
    # if has_images:
    #     print("[DEBUG] Kết quả retrieved có chứa image links")

    end = time.time()
    print(f"[retrieve] TIME: {end - start}")
    return {"context": retrieved_docs}

from . vannhk_template import template1, template2

prompt = PromptTemplate.from_template(template1)

def generate(state: State):

    start = time.time()
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])

    messages = prompt.invoke(
        {
        "question": state["question"],
        "context":docs_content
        }
    )
    # print(f"[MESSEAGES]: {messages}")

    response = llm.invoke(messages)

    end = time.time()
    print(f"[generate] TIME: {end - start}")
    return {"answer": response.content}

# Compile application and test (CONTROL FLOW)
graph_builder = StateGraph(State).add_sequence([retrieve, generate]) # Dam bao "ket noi": "retrieve" chay truoc, "generate" chay sau.
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

def chatbot_run(text):

    start = time.time()
    response = graph.invoke(text)
    response = dict(response)
    end = time.time()

    # print(f"CONTEXT: {response['context']}")
    # print(f"ANSWER {response['answer']}")
    # # print(response)
    #
    # print(f"[chatbot_run] TIME: {end - start}")

    return response








