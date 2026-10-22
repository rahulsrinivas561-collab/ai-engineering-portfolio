import chromadb

# Initialize Chroma client and get or create collection safely
client = chromadb.Client()
collection = client.get_or_create_collection(name="my_learning")

# Add documents if collection is empty
if collection.count() == 0:
    collection.add(
        documents=[
            "Rahul is learning Forward Deployed AI Engineering and RAG systems.",
            "ChromaDB is an open-source vector database designed for AI applications."
        ],
        ids=["doc1", "doc2"]
    )

results = collection.query(
    query_texts=["What is Rahul learning?"],
    n_results=1
)

# Extract and print just the matching text
print("Matched Document:", results['documents'][0][0])