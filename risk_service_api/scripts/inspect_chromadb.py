import chromadb
from pathlib import Path
import json

service_root = Path(__file__).resolve().parents[1]
db_path = str(service_root / "data" / "chroma_db")
client = chromadb.PersistentClient(path=db_path)

print(f"\n======== 🗂️  ChromaDB Inspector ========\n")

while True:
    print("\nSelect a collection to search:")
    print("1. post_op_propositions (RAG Data)")
    print("2. symptoms (Symptom Mapping)")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-2): ")
    
    if choice == '0':
        break
        
    collection_name = "post_op_propositions" if choice == '1' else "symptoms" if choice == '2' else None
    
    if not collection_name:
        print("Invalid choice.")
        continue
        
    try:
        col = client.get_collection(collection_name)
        count = col.count()
        print(f"\nCollection: '{collection_name}' (Total items: {count})")
        
        query = input(f"Search text for {collection_name} (leave empty to just show first 10 items): ")
        
        if query:
            results = col.query(
                query_texts=[query],
                n_results=5,
                include=["documents", "metadatas", "distances"]
            )
            print(f"\n--- Top 5 Results for '{query}' ---")
            for i in range(len(results['ids'][0])):
                dist = results['distances'][0][i]
                print(f"[{i+1}] Distance: {dist:.4f} (Sim: {1-dist:.4f})")
                print(f"Content: {results['documents'][0][i][:200]}...")
                print(f"Metadata: {json.dumps(results['metadatas'][0][i], ensure_ascii=False)}")
                print("-" * 50)
        else:
            print("\n--- First 10 Items ---")
            peek = col.peek(10)
            for i in range(len(peek['ids'])):
                print(f"[{i+1}] ID: {peek['ids'][i]}")
                print(f"Content: {peek['documents'][i][:100]}...")
                print(f"Metadata: {json.dumps(peek['metadatas'][i], ensure_ascii=False)}")
                print("-" * 50)
                
    except ValueError:
        print(f"Collection '{collection_name}' does not exist or is empty.")
