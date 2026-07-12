import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
print("Loading HuggingFaceEmbeddings...")
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("HF loaded. Loading Chroma...")
from langchain_chroma import Chroma
print("Chroma imported successfully!")
