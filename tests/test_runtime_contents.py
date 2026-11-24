from scripts.build_backend_runtime import exclude_test_assets
from scripts import build_backend_runtime as builder
import hashlib
import json
from pathlib import Path
import pytest


def test_runtime_pruning_preserves_runtime_helpers_and_application_resources(tmp_path):
    removed=['_internal/torch/bin/test_jit','_internal/torch/bin/FileStoreTest',
             '_internal/torch/bin/test_interpreter_async.pt','_internal/torch/bin/script_module_v4.ptl',
             '_internal/library/tests/reference.wav']
    retained=['_internal/torch/bin/torch_shm_manager','_internal/torch/bin/protoc',
              '_internal/backend/test_policy.json','licenses/library/LICENSE']
    for name in removed+retained:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'authored fixture')
    exclude_test_assets(tmp_path)
    assert all(not (tmp_path/name).exists() for name in removed)
    assert all((tmp_path/name).read_bytes()==b'authored fixture' for name in retained)


def test_inventory_collects_british_spelling_and_notices(monkeypatch, tmp_path):
    class Distribution:
        metadata = {'Name': 'example'}
        version = '1.0'
        files = [Path('licenses/LICENCE'), Path('NOTICE'), Path('module.py')]

        def locate_file(self, entry):
            return tmp_path / entry

    class Metadata(dict):
        def get_all(self, key, default):
            return default

    Distribution.metadata = Metadata(Distribution.metadata)
    for entry in Distribution.files:
        path = tmp_path / entry
        path.parent.mkdir(exist_ok=True)
        path.write_text('authored test text')
    monkeypatch.setattr(builder.metadata, 'distributions', lambda: [Distribution()])
    assert builder.inventory()[0][1]['license_files'] == [str(Path('licenses/LICENCE')), 'NOTICE']


def test_supplemental_texts_require_matching_version_and_hash(monkeypatch, tmp_path):
    source = tmp_path / 'docs/distribution-licenses'
    source.mkdir(parents=True)
    body = b'authored license test fixture'
    (source / 'LICENSE').write_bytes(body)
    item = {'package': 'example', 'version': '1.0', 'file': 'LICENSE',
            'sha256': hashlib.sha256(body).hexdigest()}
    (source / 'provenance.json').write_text(json.dumps([item]))
    monkeypatch.setattr(builder, 'ROOT', tmp_path)
    legal = tmp_path / 'legal'
    legal.mkdir()
    builder.supplemental_licenses([(None, {'name': 'example', 'version': '2.0'}, [])], legal)
    assert not (legal / 'example').exists()
    packages = [(None, {'name': 'example', 'version': '1.0'}, [])]
    builder.supplemental_licenses(packages, legal)
    assert (legal / 'example/upstream-LICENSE').read_bytes() == body
    (source / 'LICENSE').write_text('tampered')
    with pytest.raises(ValueError, match='checksum mismatch'):
        builder.supplemental_licenses(packages, legal)


def test_native_license_requires_the_reviewed_platform_binary(monkeypatch, tmp_path):
    source = tmp_path / 'docs/distribution-licenses'
    source.mkdir(parents=True)
    text = b'authored license fixture'
    (source / 'LICENSE').write_bytes(text)
    runtime = tmp_path / 'runtime'
    legal = runtime / 'licenses'
    legal.mkdir(parents=True)
    binary = runtime / 'program'
    binary.write_bytes(b'authored binary fixture')
    item = {'package': 'example', 'version': '1', 'file': 'LICENSE',
            'sha256': hashlib.sha256(text).hexdigest(), 'runtime_files': {
                builder.sys.platform: {'path': 'program', 'sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}}}
    catalog = source / 'provenance.json'
    catalog.write_text(json.dumps([item]))
    monkeypatch.setattr(builder, 'ROOT', tmp_path)
    packages = [(None, {'name': 'example', 'version': '1'}, [])]
    builder.supplemental_licenses(packages, legal)
    assert (legal / 'example/upstream-LICENSE').read_bytes() == text
    binary.write_bytes(b'different program')
    with pytest.raises(ValueError, match='binary checksum mismatch'):
        builder.supplemental_licenses(packages, legal)
    item['runtime_files'] = {'unsupported-platform': {}}
    catalog.write_text(json.dumps([item]))
    builder.supplemental_licenses(packages, legal)
    assert json.loads((legal / 'upstream-provenance.json').read_text()) == []
