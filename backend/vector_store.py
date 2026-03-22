from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from backend.embeddings import embed_query
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

from qdrant_client import QdrantClient

client = QdrantClient(":memory:")

# ---------- Check If Collection Exists ----------
def collection_exists(collection_name):
    try:
        info = client.get_collection(collection_name)
        return info.points_count > 0
    except:
        return False


# ---------- Create Collection (ONLY IF NOT EXISTS) ----------
def create_collection(collection_name):
    try:
        client.get_collection(collection_name)
    except:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


# ---------- Store in Batches ----------
def store_chunks(chunks, collection_name, batch_size=10):

    total = len(chunks)

    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        points = []

        for chunk in batch:
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=chunk["embedding"],
                    payload={
                        "content": chunk["content"],
                        "file_path": chunk["file_path"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                    },
                )
            )

        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )

        print(f"Uploaded batch {i//batch_size + 1} / {total//batch_size + 1}")


# ---------- Search ----------
def search(question, collection_name, k=25):

    query_vector = embed_query(question)

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=40,  # get more
    )

    hits = [{
        "score":hit.score,
        **hit.payload
    }
    for hit in results.points]

    # If question references a file
    if "." in question:
        filename = [word for word in question.split() if ".js" in word or ".ts" in word]
        if filename:
            filename = filename[0]

            file_hits = [h for h in hits if filename in h["file_path"]]

            if file_hits:
                return file_hits[:k]

    return hits[:k]
