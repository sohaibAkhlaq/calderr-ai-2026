import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
print("Starting Chroma test")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("Model loaded")
from langchain_core.documents import Document
docs = [Document(page_content="test")]
try:
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="test_col",
        persist_directory="chroma_test"
    )
    print("Chroma succeeded")
except Exception as e:
    print(f"Exception: {e}")
