from neo4j import GraphDatabase

class GraphApp:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # Tạo Graph và thêm dữ liệu
    def create_graph(self):
        with self.driver.session() as session:
            session.write_transaction(self._create_data)

    @staticmethod
    def _create_data(tx):
        # Xóa dữ liệu cũ (nếu có)
        tx.run("MATCH (n) DETACH DELETE n")

        # Thêm đỉnh
        tx.run("CREATE (:Vertex {id: '1', name: 'v1'})")
        tx.run("CREATE (:Vertex {id: '2', name: 'v2'})")
        tx.run("CREATE (:Vertex {id: '3', name: 'v3'})")

        # Thêm cạnh
        tx.run("MATCH (a:Vertex {id: '1'}), (b:Vertex {id: '2'}) CREATE (a)-[:CONNECTED]->(b)")
        tx.run("MATCH (a:Vertex {id: '2'}), (b:Vertex {id: '3'}) CREATE (a)-[:CONNECTED]->(b)")
        tx.run("MATCH (a:Vertex {id: '3'}), (b:Vertex {id: '1'}) CREATE (a)-[:CONNECTED]->(b)")

    # Thuật toán Fleury để tìm chu trình Euler
    def euler_cycle(self, start_vertex):
        with self.driver.session() as session:
            return session.write_transaction(self._find_euler_cycle, start_vertex)

    @staticmethod
    def _find_euler_cycle(tx, start_vertex):
        # Truy vấn để tìm chu trình Euler
        query = """
        MATCH path=(start:Vertex {id: $start_vertex})-[:CONNECTED*]->(start)
        WHERE all(r IN relationships(path) WHERE size(
          [e IN relationships(path) WHERE id(e) = id(r)]) = 1)
        RETURN [n IN nodes(path) | n.id] AS cycle
        """
        result = tx.run(query, start_vertex=start_vertex)
        record = result.single()
        return record["cycle"] if record else None

    # Thuật toán Backtracking để tìm chu trình Hamilton
    def hamilton_cycle(self, start_vertex):
        with self.driver.session() as session:
            return session.write_transaction(self._find_hamilton_cycle, start_vertex)

    @staticmethod
    def _find_hamilton_cycle(tx, start_vertex):
        # Truy vấn để tìm chu trình Hamilton
        query = """
        MATCH path=(start:Vertex {id: $start_vertex})-[:CONNECTED*]->(start)
        WHERE size(apoc.coll.toSet([n IN nodes(path) | n.id])) = size((:Vertex))
        RETURN [n IN nodes(path) | n.id] AS cycle
        """
        result = tx.run(query, start_vertex=start_vertex)
        record = result.single()
        return record["cycle"] if record else None

# Chạy chương trình
if __name__ == "__main__":
    app = GraphApp("bolt://localhost:7687", "neo4j", "yourpassword")

    # Tạo graph và thêm dữ liệu
    app.create_graph()

    # Tìm chu trình Euler
    euler = app.euler_cycle("1")
    print("Euler Cycle:", euler if euler else "No Euler cycle found")

    # Tìm chu trình Hamilton
    hamilton = app.hamilton_cycle("1")
    print("Hamilton Cycle:", hamilton if hamilton else "No Hamilton cycle found")

    app.close()