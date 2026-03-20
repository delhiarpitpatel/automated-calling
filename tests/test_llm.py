import os


def test_llm_file_exists():
    assert os.path.exists("src/models/llm.py"), "src/models/llm.py must exist"
