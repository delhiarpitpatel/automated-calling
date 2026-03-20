import os


def test_tts_file_exists():
    assert os.path.exists("src/models/tts.py"), "src/models/tts.py must exist"
