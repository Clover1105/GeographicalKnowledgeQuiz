import os
from langchain_neo4j import Neo4jGraph


def get_neo4j_conn():
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "12345678"),
        database=os.getenv("NEO4J_DATABASE", "neo4j")
    )


if __name__ == '__main__':
    conn = get_neo4j_conn()
    print(f"连接成功：{conn}")