import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer, util
import wikipedia
import nltk
from nltk.tokenize import sent_tokenize
import os

# Download NLTK sentence tokenizer if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def get_wikipedia_sentences(topic="Artificial intelligence", num_sentences=100):
    print(f"Fetching Wikipedia article for: {topic}...")
    try:
        page = wikipedia.page(topic)
        content = page.content
        sentences = sent_tokenize(content)
        
        # Filter out very short or empty sentences
        sentences = [s.strip() for s in sentences if len(s.split()) > 4]
        
        if len(sentences) >= num_sentences:
            return sentences[:num_sentences]
        else:
            print(f"Only found {len(sentences)} sentences. Returning all.")
            return sentences
    except Exception as e:
        print(f"Error fetching Wikipedia data: {e}")
        return [
            "The quick brown fox jumps over the lazy dog.",
            "Artificial intelligence is a fascinating field.",
            "Machine learning is a subset of AI.",
            "Deep learning uses neural networks."
        ] * 25 # Fallback sentences

def visualize_pca(embeddings, sentences, filename="pca_visualization.png"):
    print("Performing PCA dimensionality reduction...")
    pca = PCA(n_components=2)
    pca_embeddings = pca.fit_transform(embeddings)
    
    plt.figure(figsize=(12, 8))
    plt.scatter(pca_embeddings[:, 0], pca_embeddings[:, 1], alpha=0.5, color='blue')
    
    # Annotate a few random points so it's not too cluttered
    for i in np.random.choice(len(sentences), size=10, replace=False):
        # Truncate sentence for label
        label = sentences[i][:40] + "..." if len(sentences[i]) > 40 else sentences[i]
        plt.annotate(label, (pca_embeddings[i, 0], pca_embeddings[i, 1]), fontsize=8, alpha=0.7)
        
    plt.title("2D PCA Visualization of Sentence Embeddings")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.grid(True, alpha=0.3)
    plt.savefig(filename)
    print(f"Saved PCA visualization to {filename}")

def perform_search(model_name, sentences, query, top_k=5):
    print(f"\n--- Loading Model: {model_name} ---")
    model = SentenceTransformer(model_name)
    
    print("Embedding corpus...")
    corpus_embeddings = model.encode(sentences, convert_to_tensor=True)
    
    print("Embedding query...")
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # Compute cosine similarities
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)
    hits = hits[0] # Get results for the first (and only) query
    
    print(f"\nTop {top_k} Results for Query: '{query}'")
    for i, hit in enumerate(hits):
        score = hit['score']
        sentence = sentences[hit['corpus_id']]
        print(f"{i+1}. [Score: {score:.4f}] {sentence}")
        
    return corpus_embeddings.cpu().numpy()

def main():
    parser = argparse.ArgumentParser(description="Lab 3.1: Semantic Search CLI")
    parser.add_argument("--query", type=str, default="How do machines learn?", help="Search query")
    args = parser.parse_args()
    
    sentences = get_wikipedia_sentences(num_sentences=100)
    print(f"\nTotal sentences prepared: {len(sentences)}")
    
    # Compare two models
    model1 = 'all-MiniLM-L6-v2'
    model2 = 'BAAI/bge-small-en-v1.5' # Standard small BGE model
    
    # Run for Model 1
    embeddings1 = perform_search(model1, sentences, args.query)
    # Visualize PCA using embeddings from Model 1
    visualize_pca(embeddings1, sentences, filename=f"pca_{model1.replace('/', '_')}.png")
    
    # Run for Model 2
    embeddings2 = perform_search(model2, sentences, args.query)

if __name__ == "__main__":
    main()
