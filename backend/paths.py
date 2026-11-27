"""Writable locations, independent of the installed resource directory."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def user_root():
    if sys.platform == 'win32':
        return Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / 'MoodScope'
    return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / 'moodscope'


def data_dir():
    return Path(os.environ.get('MOODSCOPE_DATA', user_root() / 'data' if getattr(sys, 'frozen', False) else ROOT / 'data'))


def model_dir():
    return Path(os.environ.get('MOODSCOPE_MODELS', user_root() / 'models' if getattr(sys, 'frozen', False) else ROOT / 'models'))
