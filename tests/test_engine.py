import importlib.util
from pathlib import Path


def load_engine_class():
    # Adjust filename if your main script is named differently
    app_path = Path(__file__).resolve().parent.parent / "word_recovery_desktop_app_blue.py"
    spec = importlib.util.spec_from_file_location("word_recovery_app", app_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.WordRecoveryEngine


def test_illustrative_example():
    WordRecoveryEngine = load_engine_class()
    grid = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    engine = WordRecoveryEngine(["oath", "pea", "eat", "rain"])
    results, stats = engine.search(grid, one_indexed=True)

    assert set(results.keys()) == {"oath", "eat"}
    assert results["oath"] == [(1, 1), (1, 2), (2, 2), (3, 2)]
    assert results["eat"] == [(2, 4), (2, 3), (2, 2)]
    assert stats["nodes_visited"] > 0


def test_empty_result_and_no_cell_reuse():
    WordRecoveryEngine = load_engine_class()
    grid = [
        ["a", "b"],
        ["c", "d"],
    ]
    engine = WordRecoveryEngine(["aba", "xyz"])
    results, _ = engine.search(grid, one_indexed=True)

    assert results == {}