import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from langchain_huggingface import HuggingFaceEmbeddings
print("Imported HuggingFaceEmbeddings")
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("Successfully loaded model")
except Exception as e:
    print(f"Exception: {e}")
