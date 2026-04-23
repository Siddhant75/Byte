import os

os.environ["ANONYMIZED_TELEMETRY"] = "False"
import chromadb
from chromadb.config import Settings
import time
import uuid

# Create a robust path to the memory_db folder at the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_PATH = os.path.join(BASE_DIR, "memory_db")

# Initialize ChromaDB client with telemetry disabled
client = chromadb.PersistentClient(
    path=MEMORY_PATH, settings=Settings(anonymized_telemetry=False)
)

# Create or get the collection
collection = client.get_or_create_collection(name="pet_memories")


def save_memory(user_input: str, pet_response: str):
    """
    Saves an interaction to ChromaDB.
    """
    interaction_text = f"User: {user_input}\nPet: {pet_response}"
    interaction_id = str(uuid.uuid4())

    collection.add(
        documents=[interaction_text],
        ids=[interaction_id],
        metadatas=[{"timestamp": time.time(), "type": "chat_interaction"}],
    )
    print(f"Memory saved: {interaction_id}")


def query_memories(query_text: str, n_results: int = 3):
    """
    Retrieves relevant memories based on a query string.
    """
    results = collection.query(query_texts=[query_text], n_results=n_results)
    return results["documents"][0] if results["documents"] else []


def retrieve_context(query: str, n_results: int = 3):
    """
    Queries ChromaDB and returns a combined string of the top n_results.
    """
    memories = query_memories(query, n_results)
    if not memories:
        return ""

    return "\n---\n".join(memories)
