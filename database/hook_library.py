import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any
from uuid import uuid4

class HookLibrary:
    """
    Persistent hook library using ChromaDB for vector search.
    Allows retrieving proven viral hooks similar to current trend context.
    """
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        # Using default embedding function (all-MiniLM-L6-v2)
        self.collection = self.client.get_or_create_collection(name="viral_hooks")

    def add_hooks(self, hooks: List[Dict[str, str]]):
        """
        Adds a list of hooks to the library.
        Each hook should have 'text', 'niche', 'emotion', and 'pattern'.
        """
        documents = [h['text'] for h in hooks]
        metadatas = [{"niche": h.get('niche', 'general'), 
                      "emotion": h.get('emotion', 'unknown'),
                      "pattern": h.get('pattern', 'unknown')} for h in hooks]
        ids = [str(uuid4()) for _ in hooks]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search_hooks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for hooks similar to the query string.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
        return formatted_results

    def seed_initial_hooks(self):
        """Seeds the database with some proven viral hook patterns."""
        initial_hooks = [
            {"text": "The secret to [Topic] that nobody tells you.", "niche": "educational", "emotion": "curiosity", "pattern": "the_secret"},
            {"text": "I tried [Topic] for 30 days and here is what happened.", "niche": "lifestyle", "emotion": "curiosity", "pattern": "challenge"},
            {"text": "Stop doing [Action] if you want to achieve [Goal].", "niche": "productivity", "emotion": "urgency", "pattern": "hard_truth"},
            {"text": "This is why your [Topic] is failing (and how to fix it).", "niche": "business", "emotion": "fear", "pattern": "problem_solver"},
            {"text": "Wait for the end to see the most insane [Topic] ever.", "niche": "entertainment", "emotion": "excitement", "pattern": "wait_for_it"}
        ]
        # Only seed if empty
        if self.collection.count() == 0:
            self.add_hooks(initial_hooks)
            print(f"Seeded {len(initial_hooks)} initial hooks.")

if __name__ == "__main__":
    library = HookLibrary()
    library.seed_initial_hooks()
    results = library.search_hooks("How to use AI for business")
    for r in results:
        print(f"Found Hook: {r['text']} (Metadata: {r['metadata']})")
