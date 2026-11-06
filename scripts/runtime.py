"""Project-local interpreter selection; the validation marker is written only after setup checks."""
import hashlib
from pathlib import Path
import sys


def preferred_python(root):
    root=Path(root)
    modern=root/'.venv-modern'
    candidate=modern/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
    if (modern/'.moodscope-validated').is_file() and candidate.is_file():return candidate
    return root/'.venv'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')


def environment_id():
    value=str(Path(sys.prefix).resolve()).casefold()+':'+sys.implementation.cache_tag
    return hashlib.sha256(value.encode()).hexdigest()[:16]
