"""Check the actual pushed commits and keep private checkpoint ancestry private."""
import json
import subprocess
import sys
try:
    from . import check_publication as publication
except ImportError:
    import check_publication as publication


def config(name):
    try:return publication.git('config','--get',name).decode().strip()
    except subprocess.CalledProcessError:return ''


def check(remote,url,records):
    public=config('moodscope.publicRemote')
    public_url=''
    if public:
        try:public_url=publication.git('remote','get-url',public).decode().strip()
        except subprocess.CalledProcessError:pass
    is_public=bool(public and (remote==public or url==public_url))
    branch=config('moodscope.publicationBranch') or 'codex/public-release'
    private=config('moodscope.privateBranch')
    checked=set();reports=[]
    for local_ref,local_sha,remote_ref,remote_sha in records:
        if set(local_sha)=={'0'}:continue
        if is_public:
            if local_ref!='refs/heads/'+branch:
                raise ValueError('Public pushes require the separate verified publication branch.')
            base=remote_sha
            if set(base)=={'0'}:
                try:base=publication.git('rev-parse',f'refs/remotes/{public}/main').decode().strip()
                except subprocess.CalledProcessError:base=''
            commits=publication.git('rev-list',local_sha,*(['^'+base] if base else [])).decode().splitlines()
            for commit in commits:
                if private and subprocess.run([publication.GIT,'merge-base','--is-ancestor',commit,'refs/heads/'+private],cwd=publication.ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
                    raise ValueError('A private checkpoint is reachable from the proposed public update.')
        if local_sha not in checked:
            report=publication.scan(local_sha);reports.append(report);checked.add(local_sha)
            if not report['passed']:raise ValueError('Publication content check failed; no push allowed.')
    return reports


if __name__=='__main__':
    try:
        records=[line.split() for line in sys.stdin if line.strip()]
        if any(len(row)!=4 for row in records):raise ValueError('Unexpected push ref format')
        print(json.dumps(check(sys.argv[1],sys.argv[2],records),indent=2))
    except (ValueError,subprocess.CalledProcessError) as error:
        print(str(error),file=sys.stderr);sys.exit(1)
