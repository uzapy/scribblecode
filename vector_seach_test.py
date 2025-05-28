from azure.cosmos import CosmosClient

cosmosDB_connection_string_file = "../VDJ/cosmosdb_connection_string"
cosmosDB_name = "vdjdb"
cosmosDB_container_name = "embeddings"

# Load the connection string
with open(cosmosDB_connection_string_file, 'r', encoding='utf-8') as open_file:
    cosmosDB_connection_string = open_file.read()

# Initialize Cosmos DB client
cosmos_client = CosmosClient.from_connection_string(cosmosDB_connection_string)
cosmos_database = cosmos_client.get_database_client(cosmosDB_name)
cosmos_container = cosmos_database.get_container_client(cosmosDB_container_name)

def find_nearest_neighbors(query_vector, top_n=5):
    """
    Performs a nearest neighbor search on the 'embedding' field in Cosmos DB.

    Args:
        query_vector (list): The 128-dimensional query vector.
        top_n (int): The number of nearest neighbors to retrieve.

    Returns:
        list: A list of the top_n nearest neighbor documents with their similarity scores.
    """
    try:
        query = f"SELECT TOP {top_n} e.id, e.artist, e.title, e.original_path, e.chunk, e.embedding, VectorDistance(e.embedding, @embedding) AS score \
            FROM e \
            ORDER BY VectorDistance(e.embedding, @embedding)"

        parameters = [
            {"name": "@embedding", "value": query_vector}
        ]

        items = cosmos_container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True  # If your container is partitioned
        )

        results = []
        for item in items:
            results.append(item)

        return results

    except Exception as e:
        print(f"Error performing nearest neighbor search: {e}")
        return []

if __name__ == "__main__":
    query_embedding = [145,46,133,193,125,91,169,60,96,235,145,20,154,134,205,170,139,105,167,200,80,199,69,119,94,193,160,115,255,150,39,120,78,0,255,166,26,55,0,47,182,215,162,151,199,114,117,25,105,130,85,185,65,110,206,32,242,27,15,188,249,60,97,121,58,235,195,130,53,198,153,255,162,233,98,169,86,147,163,24,94,204,186,115,157,169,167,84,185,26,92,0,190,122,153,206,193,52,205,255,199,211,13,126,146,36,76,0,53,208,217,207,55,230,197,159,56,219,140,47,116,255,86,0,105,237,22,104]

    nearest_neighbors = find_nearest_neighbors(query_embedding)

    if nearest_neighbors:
        print(f"Top 5 Nearest Neighbors:")
        for neighbor in nearest_neighbors:
            print(f"  ID: {neighbor['id']}")
            print(f"  Artist: {neighbor.get('artist')}")
            print(f"  Title: {neighbor.get('title')}")
            print(f"  Path: {neighbor.get('original_path')}")
            print(f"  Chunk: {neighbor.get('chunk')}")
            print(f"  Similarity Score: {neighbor['score']}")
            print("-" * 20)
    else:
        print("No nearest neighbors found.")
