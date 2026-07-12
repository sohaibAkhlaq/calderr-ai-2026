import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import sys

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

print("Loading embeddings...", flush=True)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("Loading chroma...", flush=True)
from langchain_chroma import Chroma
print("Initializing Chroma...", flush=True)
docs = [Document(page_content="test")]
vectorstore = Chroma.from_documents(docs, embeddings, collection_name="test_col", persist_directory="chroma_test")
print("Done!", flush=True)
