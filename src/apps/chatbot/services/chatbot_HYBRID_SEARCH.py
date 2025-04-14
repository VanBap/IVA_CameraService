# import os
#
# from langchain_core.documents import Document
# from langchain_milvus import Milvus, BM25BuiltInFunction
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langgraph.graph import START, StateGraph
# from typing_extensions import List, TypedDict
#
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import PromptTemplate
# from langchain_community.embeddings import HuggingFaceEmbeddings
# import pickle
# from langchain_community.vectorstores import FAISS
#
# # === Vannhk ===
# from . import chatbot_crawl_data as crawl_data
# from . splitter import SapoSupportChunker
# import time
#
# from langchain_milvus.retrievers import MilvusCollectionHybridSearchRetriever
# from langchain_milvus.utils.sparse import BM25SparseEmbedding
# from langchain_openai import ChatOpenAI
# # from pymilvus import (
# #     Collection,
# #     CollectionSchema,
# #     DataType,
# #     FieldSchema,
# #     WeightedRanker,
# #     connections,
# # )
#
# VECTOR_DB_DEMO_PATH = os.getenv("VECTOR_DB_PATH_MILVUS_HYBRID_SEARCH")
# OPEN_API_KEY = os.getenv("OPEN_API_KEY")
# embeddings = []
# dense_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# collection_name = "sapo_documents_hybrid_search"
#
# # === CHECK IF VECTOR DB EXISTED ===
#
# # Kiểm tra xem collection đã tồn tại trong Milvus chưa
# from pymilvus import utility, connections
#
# # Kiểm tra và đóng kết nối cũ nếu tồn tại
# try:
#     if connections.has_connection("default"):
#         connections.disconnect("default")
# except Exception as e:
#     print(f"[INFO] Lỗi khi ngắt kết nối: {str(e)}")
#
# # Kết nối đến Milvus
# connections.connect(
#     alias="default",
#     uri=VECTOR_DB_DEMO_PATH
# )
#
# collection_exists = utility.has_collection(collection_name)
#
#
# if not collection_exists:
#     print("[INFO] ================ chatbot_TEST =======================")
#     print("[INFO] Lần đầu tiên chạy - Đang tải và embedding dữ liệu...")
#     start = time.time()
#
#     # url = "https://support.sapo.vn/ket-noi-kenh-facebook-tren-app-sapo"
#     # loader = crawl_data.WebWithImageLoader(web_paths=(url,))
#     # documents = loader.load()
#
#     base_url = "https://support.sapo.vn/sapo-retail"
#     get_article_links = crawl_data.get_article_links(base_url)
#     documents = crawl_data.load_articles(get_article_links)
#
#     print(f"[INFO] Đã tải {len(documents)} tài liệu từ URL")
#
#     chunker = SapoSupportChunker(chunk_size=2000, chunk_overlap=200)
#     all_splits = chunker.split_documents(documents)
#
#     corpus = [doc.page_content for doc in all_splits]
#     sparse_embedding = BM25SparseEmbedding(corpus = corpus)
#
#     print(f"[INFO] Đã tách thành {len(all_splits)} đoạn")
#
#     # In thông tin về một số đoạn đầu tiên để kiểm tra
#     for i in range(len(all_splits)):
#         doc = all_splits[i]
#         print(f"\n--- Đoạn {i + 1} ---")
#         print(f"Metadata: {doc.metadata}")
#         print(doc.page_content)
#         has_images = "image link:" in doc.page_content
#         print(f"Có hình ảnh: {has_images}")
#         if has_images:
#             image_links = [line.strip() for line in doc.page_content.split("\n") if "image link:" in line]
#             print(f"image_links: {image_links}")
#             print(f"Số lượng hình ảnh: {len(image_links)}")
#
#
#
#     # ============ TEST MILVUS as VECTOR STORE ==============
#
#     # Khi tạo mới vector store
#     # Phiên bản đơn giản hơn không sử dụng hybrid search
#     vector_store = Milvus.from_documents(
#         documents=all_splits,
#         embedding=[dense_embeddings, sparse_embedding],
#         connection_args={"uri": VECTOR_DB_DEMO_PATH},
#         collection_name=collection_name,
#         vector_field="embedding",
#
#         consistency_level="Strong",
#         drop_old=True
#     )
#     embeddings.extend([dense_embeddings, sparse_embedding])
#     end = time.time()
#     print(f"[CRAWL + SPLIT + EMBEDDING DATA] {end-start} seconds")
#     print("[INFO] Lưu trữ Vector DB thành công!")
#
# else:
#     print("[INFO] ================ chatbot_TEST =======================")
#     print("[INFO] Đang load vector store đã tồn tại...")
#
#     # Khi load vector store đã tồn tại
#     vector_store = Milvus(
#         collection_name=collection_name,
#         embedding_function=embeddings,
#         connection_args={"uri": VECTOR_DB_DEMO_PATH},
#         text_field="page_content",
#         vector_field="embedding",
#         enable_dynamic_field=True,
#         drop_old=True,
#
#     )
#
# # except Exception as e:
# #     if "invalid index type: AUTOINDEX" in str(e):
# #         print("[INFO] Lỗi AUTOINDEX, đang thử lại với SPARSE_INVERTED_INDEX...")
# #         # Thực hiện lại với index type cụ thể
# #         # ...
# #     else:
# #         print(f"[ERROR] Lỗi khi khởi tạo Milvus: {str(e)}")
# #         raise
#
#
#
# # === Choose LLM model ===
# # Model 1: gpt-4o
# llm = ChatOpenAI(model_name="gpt-4o-mini",
#                  api_key=OPEN_API_KEY,
#                  base_url="https://models.inference.ai.azure.com",
#                  temperature=0.0)
#
#
#
# print(f"[MODEL NAME]: {llm.model_name}")
#
# # === Define state for application ===
# class State(TypedDict):
#     question: str
#     context: List[Document]
#     answer:str
#
#
# # === Define application steps (NODE) ===
# def retrieve(state: State):
#     start = time.time()
#
#     retrieved_docs = vector_store.similarity_search(state["question"], k=1, ranker_type="weighted", ranker_params={"weights": [0.6, 0.4]}) #default k=4
#
#     end = time.time()
#     print(f"[retrieve] TIME: {end - start}")
#     return {"context": retrieved_docs}
#
# from . vannhk_template import template1, template2
# prompt = PromptTemplate.from_template(template1)
#
# def generate(state: State):
#
#     start = time.time()
#     docs_content = "\n\n".join(doc.page_content for doc in state["context"])
#
#     messages = prompt.invoke(
#         {
#         "question": state["question"],
#         "context":docs_content
#         }
#     )
#     # print(f"[MESSEAGES]: {messages}")
#
#     response = llm.invoke(messages)
#
#     end = time.time()
#     print(f"[generate] TIME: {end - start}")
#     return {"answer": response.content}
#
# # Compile application and test (CONTROL FLOW)
# graph_builder = StateGraph(State).add_sequence([retrieve, generate]) # Dam bao "ket noi": "retrieve" chay truoc, "generate" chay sau.
# graph_builder.add_edge(START, "retrieve")
# graph = graph_builder.compile()
#
# def chatbot_run(text):
#
#     start = time.time()
#     response = graph.invoke(text)
#     response = dict(response)
#     end = time.time()
#
#     print(f"CONTEXT: {response['context']}")
#     print(f"ANSWER {response['answer']}")
#     # # print(response)
#     #
#     print(f"[chatbot_run] TIME: {end - start}")
#     return response
#
#
#
#
#
#
#
#
