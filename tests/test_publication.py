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


def test_removed_secret_still_blocks_history_publication(tmp_path, monkeypatch):
    import subprocess
    import scripts.check_publication as publication
    def run(*args):
        subprocess.run([publication.GIT,*args],cwd=tmp_path,check=True,capture_output=True)
    run('init')
    run('config','user.name','Publication test')
    run('config','user.email','test@users.noreply.github.com')
    file=tmp_path/'package.json'
    file.write_text('gh'+'p_'+'A'*30,encoding='utf-8')
    run('add','package.json');run('commit','-m','Fixture with fake credential')
    file.write_text('{}',encoding='utf-8')
    run('add','package.json');run('commit','-m','Remove fixture credential')
    monkeypatch.setattr(publication,'ROOT',tmp_path)
    result=publication.scan('HEAD')
    assert not result['passed']
    assert any(f['reason']=='GitHub token' for f in result['findings'])
