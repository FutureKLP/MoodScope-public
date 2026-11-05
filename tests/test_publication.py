from scripts.check_publication import content_problems, path_problem


def test_private_music_and_cache_are_rejected():
    assert path_problem('for test only music files/subfolder/song.mp3')
    assert path_problem('data/results.json')
    assert path_problem('other/song.flac')
    assert path_problem('.env.production')
    assert path_problem('src-tauri/target/release/app.exe')


def test_source_and_project_icons_are_allowed():
    assert path_problem('src/main.tsx') is None
    assert path_problem('src-tauri/icons/icon.png') is None
    assert path_problem('README.md') is None


def test_secret_patterns_do_not_print_values():
    token=('gh'+'p_'+'A'*30).encode()
    assert 'GitHub token' in content_problems(token)
    assert 'model hub token' in content_problems(('h'+'f_'+'B'*30).encode())
    assert 'personal Windows path' in content_problems(('C:'+'\\Users\\'+'example\\file.txt').encode())
    assert 'email address' in content_problems(('person'+'@'+'example.test').encode())


def test_emoji_is_rejected_without_literal_emoji_in_test_source():
    assert 'emoji or decorative pictograph' in content_problems(chr(0x1F600).encode())
    assert content_problems(b'Local music analysis with no secrets') == []
