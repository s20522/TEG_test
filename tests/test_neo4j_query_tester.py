import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "import" / "neo4j_query_tester.py"
SPEC = importlib.util.spec_from_file_location("neo4j_query_tester", MODULE_PATH)
neo4j_query_tester = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(neo4j_query_tester)

Neo4jQueryTester = neo4j_query_tester.Neo4jQueryTester


class FakeRecord:
    def __init__(self, payload):
        self._payload = payload

    def data(self):
        return self._payload


class FakeSession:
    def __init__(self, query_map):
        self.query_map = query_map

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def run(self, query, parameters=None):
        parameters = parameters or {}
        if query == "RETURN 1 AS ok":
            class Result:
                @staticmethod
                def consume():
                    return True
            return Result()

        rows = self.query_map.get(query, [])
        return [FakeRecord(row) for row in rows]


class FakeDriver:
    def __init__(self, query_map):
        self.query_map = query_map
        self.closed = False

    def session(self, database=None):
        return FakeSession(self.query_map)

    def close(self):
        self.closed = True


def test_run_query_returns_rows():
    query = "MATCH (m:Movie) RETURN count(m) AS total_movies"
    tester = Neo4jQueryTester("bolt://localhost:7687", "neo4j", "password123")
    tester.driver = FakeDriver({query: [{"total_movies": 12}]})

    result = tester.run_query(
        name="count_movies",
        description="Count movies",
        query=query,
        parameters={},
    )

    assert result["status"] == "ok"
    assert result["row_count"] == 1
    assert result["rows"][0]["total_movies"] == 12


def test_run_smoke_tests_builds_summary():
    query = "MATCH (m:Movie) RETURN count(m) AS total_movies"
    tester = Neo4jQueryTester("bolt://localhost:7687", "neo4j", "password123")
    tester.driver = FakeDriver({query: [{"total_movies": 7}]})

    report = tester.run_smoke_tests(
        queries=[
            {
                "name": "count_movies",
                "description": "Count movies",
                "query": query,
                "parameters": {},
            }
        ]
    )

    assert report["tests_total"] == 1
    assert report["tests_passed"] == 1
    assert report["tests_failed"] == 0


def test_save_report_creates_json_file(tmp_path):
    report = {"tests_total": 1, "tests_passed": 1, "tests_failed": 0, "results": []}
    output_path = tmp_path / "reports" / "neo4j_query_report.json"

    saved_path = Neo4jQueryTester.save_report(report, str(output_path))

    assert Path(saved_path).exists()
    with open(saved_path, "r", encoding="utf-8") as file_handle:
        loaded = json.load(file_handle)
    assert loaded["tests_passed"] == 1
