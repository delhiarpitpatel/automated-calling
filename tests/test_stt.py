import os


def test_stt_file_exists():
    assert os.path.exists("src/models/stt.py"), "src/models/stt.py must exist"
