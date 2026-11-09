import subprocess
import pytest
from scripts import check_publication,check_push


def test_public_update_uses_a_separate_parent_chain(tmp_path,monkeypatch):
    def git(*args,input=None):
        return subprocess.check_output([check_publication.GIT,*args],cwd=tmp_path,input=input).decode().strip()
    git('init');git('config','user.name','Publication test');git('config','user.email','test@users.noreply.github.com')
    (tmp_path/'README.md').write_text('App baseline')
    git('add','README.md');git('commit','-m','App baseline');base=git('rev-parse','HEAD')
    git('checkout','-b','codex/working')
    (tmp_path/'README.md').write_text('App change for review')
    git('add','README.md');git('commit','-m','Private source checkpoint');private=git('rev-parse','HEAD')
    git('branch','codex/public-release',private)
    git('remote','add','origin','https://example.test/public.git')
    git('config','moodscope.publicRemote','origin');git('config','moodscope.privateBranch','codex/working')
    monkeypatch.setattr(check_publication,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='separate'):
        check_push.check('origin','https://example.test/public.git',[('refs/heads/codex/working',private,'refs/heads/main',base)])
    with pytest.raises(ValueError,match='private checkpoint'):
        check_push.check('origin','https://example.test/public.git',[('refs/heads/codex/public-release',private,'refs/heads/main',base)])
    release=git('commit-tree',git('rev-parse','HEAD^{tree}'),'-p',base,'-m','Publish verified app change')
    git('update-ref','refs/heads/codex/public-release',release)
    reports=check_push.check('origin','https://example.test/public.git',[('refs/heads/codex/public-release',release,'refs/heads/main',base)])
    assert reports[0]['passed']
    assert subprocess.run([check_publication.GIT,'merge-base','--is-ancestor',private,release],cwd=tmp_path).returncode==1
