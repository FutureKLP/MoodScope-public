from scripts.check_publication import content_problems, path_problem


def test_linux_uses_native_git_when_windows_git_is_on_path(monkeypatch):
    import types
    from scripts import check_publication as publication
    monkeypatch.setattr(publication, 'os', types.SimpleNamespace(name='posix'))
    monkeypatch.setattr(publication.shutil, 'which', lambda name: {
        'git': '/usr/bin/git', 'git.exe': '/mnt/c/tools/git.exe'}.get(name))
    assert publication.git_executable() == '/usr/bin/git'


def test_linux_does_not_fall_back_to_windows_git(monkeypatch):
    import types
    from scripts import check_publication as publication
    monkeypatch.setattr(publication, 'os', types.SimpleNamespace(name='posix'))
    monkeypatch.setattr(publication.shutil, 'which', lambda name: '/mnt/c/tools/git.exe' if name == 'git.exe' else None)
    assert publication.git_executable() is None


def test_windows_keeps_git_exe_selection(monkeypatch):
    import types
    from scripts import check_publication as publication
    monkeypatch.setattr(publication, 'os', types.SimpleNamespace(name='nt'))
    monkeypatch.setattr(publication.shutil, 'which', lambda name: 'native-git' if name == 'git.exe' else 'shell-wrapper')
    assert publication.git_executable() == 'native-git'


def test_private_music_and_cache_are_rejected():
    assert path_problem('for test only music files/subfolder/song.mp3')
    assert path_problem('data/results.json')
    assert path_problem('other/song.flac')
    assert path_problem('AGENTS.md')
    assert path_problem('.codex/settings.json')
    assert path_problem('.cursor/rules/project.mdc')
    assert path_problem('.env.production')
    assert path_problem('src-tauri/target/release/app.exe')


def test_git_excludes_private_audio_lyrics_database_sidecars_and_outputs():
    import subprocess
    from scripts.check_publication import GIT,ROOT
    names=['data/cache.sqlite3','data/cache.sqlite3-wal','data/cache.sqlite3-shm',
           'data/stems/authored/manifest.json','data/delete-fixture/journal.json',
           'models/music2emo/installation.json','authored.mp3','authored.wav','authored.flac',
           'authored.lrc','authored.srt','authored.vtt','authored.m4a','authored.aac','authored.ogg','authored.opus',
           'backend/private.sqlite3-wal','backend/private.sqlite3-shm','.tools/s5/baseline.json','data/export.wav']
    result=subprocess.run([GIT,'check-ignore','-z','--stdin'],input=('\0'.join(names)+'\0').encode(),capture_output=True,cwd=ROOT,check=True)
    assert set(result.stdout.decode().strip('\0').split('\0'))==set(names)
    assert all(path_problem(name) for name in names)


def test_source_and_project_icons_are_allowed():
    assert path_problem('src/main.tsx') is None
    assert path_problem('src-tauri/icons/icon.png') is None
    assert path_problem('README.md') is None
    assert path_problem('pytest.ini') is None
    assert path_problem('pytest-local.ini') is not None


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

def test_secret_in_commit_message_blocks_publication(tmp_path,monkeypatch):
    import subprocess
    import scripts.check_publication as publication
    def run(*args):subprocess.run([publication.GIT,*args],cwd=tmp_path,check=True,capture_output=True)
    run('init');run('config','user.name','Publication test');run('config','user.email','test@users.noreply.github.com')
    (tmp_path/'README.md').write_text('App source',encoding='utf8')
    run('add','README.md');run('commit','-m','Fixture '+('gh'+'p_'+'A'*30))
    monkeypatch.setattr(publication,'ROOT',tmp_path)
    report=publication.scan('HEAD')
    assert any(row['file']=='Git commit messages' and row['reason']=='GitHub token' for row in report['findings'])
