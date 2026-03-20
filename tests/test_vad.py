import os


def test_vad_file_exists():
    assert os.path.exists("src/models/vad.py"), "src/models/vad.py must exist"
