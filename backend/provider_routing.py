"""Explicit per-task targets; persist IDs, never credentials or model outputs."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib,json,uuid
from pathlib import Path
from . import providers,cloud

TASKS=('audio','lyrics','transcription','instruments','interpretation')
AUDIO_TASKS={'audio','transcription','instruments'}
_bound_routes=ContextVar('moodscope_routes',default=None)
_session=uuid.uuid4().hex


def capture(data,local=False):
    # Same lock order as profile activation; callers serialize admission/mutation.
    with providers._lock,cloud._lock:
        return {'routes':dict.fromkeys(TASKS,'local') if local else assignments(data),'profiles':providers.profiles(data),
                'keys':dict(providers._keys),'prepared':cloud.snapshot()}


@contextmanager
def scope(data,snapshot):
    if snapshot is None:yield;return
    token=_bound_routes.set((str(Path(data).resolve()),snapshot['routes']))
    try:
        with providers.bound_profiles(data,snapshot['profiles'],snapshot['keys']),cloud.bound_target(*snapshot['prepared']):yield
    finally:_bound_routes.reset(token)

def assignments(data):
    bound=_bound_routes.get()
    if bound and bound[0]==str(Path(data).resolve()):return dict(bound[1])
    path=Path(data)/'provider_routes.json'
    if not path.exists():return dict.fromkeys(TASKS,'prepared')
    try:
        value=json.loads(path.read_text(encoding='utf8'))
        if set(value)!=set(TASKS) or any(not isinstance(v,str) for v in value.values()):raise ValueError()
        return value
    except (OSError,ValueError,TypeError):raise ValueError('Aufgabenzuordnung ist ungültig. In Modelle & API erneut speichern.') from None

def validate_target(data,task,target):
    if target in {'local','prepared'}:return
    p=providers.profile(data,target)
    if task in AUDIO_TASKS and not (p['protocol']=='gemini' or (p['protocol']=='openai' and p.get('audio_input'))):
        raise ValueError('Für Audioaufgaben ein tatsächlich audiotaugliches Profil wählen.')

def status(data):
    routes=assignments(data);descriptions={}
    for task,target in routes.items():
        if target=='local':descriptions[task]={'source':'local','name':'Lokales Modell','model':''}
        elif target=='prepared':descriptions[task]={'source':'prepared',**{k:v for k,v in cloud.settings().items() if k not in {'configured','key_storage'}}}
        else:
            try:descriptions[task]={'source':'profile',**{k:v for k,v in providers.profile(data,target).items() if k!='id'}}
            except ValueError:descriptions[task]={'source':'missing','name':'Profil nicht mehr vorhanden','model':''}
    # Unassigned profiles also matter for explicit interpretation overrides.
    basis=json.dumps({'routes':routes,'targets':descriptions,'profiles':providers.profiles(data)},sort_keys=True)
    cache_version=hashlib.sha256(basis.encode()).hexdigest()
    return {'routes':routes,'targets':descriptions,'cache_version':cache_version,
            'version':hashlib.sha256((_session+cache_version).encode()).hexdigest()}

def save(data,routes):
    if set(routes)!=set(TASKS):raise ValueError('Alle fünf Aufgaben ausdrücklich zuordnen.')
    for task,target in routes.items():validate_target(data,task,target)
    path=Path(data)/'provider_routes.json';temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(routes,sort_keys=True),encoding='utf8');temp.replace(path)
    return status(data)

def target(data,task,mode):return 'local' if mode=='local' else assignments(data)[task]

def preflight(data,task,mode):
    chosen=target(data,task,mode);validate_target(data,task,chosen)
    if chosen=='prepared':cloud.credential()
    elif chosen!='local':
        with providers._lock:
            p=providers.profile(data,chosen);key=providers.session_key(data,chosen)
        if task in AUDIO_TASKS:
            if p['protocol']=='gemini' and not p.get('free_project_confirmed'):raise ValueError('Gratisprojekt für das gewählte Gemini-Audioprofil bestätigen.')
            if p['protocol']=='openai' and not p.get('audio_usage_confirmed'):raise ValueError('Nutzungsbedingungen des gewählten Audioprofils bestätigen.')
        from urllib.parse import urlsplit
        if not key and (p['protocol'] in {'gemini','anthropic'} or urlsplit(p['base_url']).hostname in {'api.openai.com','api.mistral.ai','api.deepseek.com'}):raise ValueError('Sitzungs-Key für ein zugeordnetes Profil fehlt.')
    return chosen

@contextmanager
def bind(data,task,mode):
    chosen=preflight(data,task,mode)
    if chosen=='local':yield chosen;return
    if chosen=='prepared':
        with cloud.bound_target(*cloud.snapshot()):yield chosen
        return
    with providers._lock:
        p=providers.profile(data,chosen);key=providers.session_key(data,chosen)
    with cloud.bound_target(p,key):yield chosen

def execute(data,task,mode,local,remote,*args):
    if target(data,task,mode)=='local':return local(*args)
    with bind(data,task,mode):return remote(*args)

def model(data,task,mode,local_model):
    chosen=target(data,task,mode)
    return local_model if chosen=='local' else cloud.settings()['model'] if chosen=='prepared' else providers.profile(data,chosen)['model']

def check_consent(data,version):
    if status(data)['version']!=version:
        raise ValueError('Aufgabenzuordnung geändert. Ziele prüfen und der Übertragung erneut zustimmen.')
