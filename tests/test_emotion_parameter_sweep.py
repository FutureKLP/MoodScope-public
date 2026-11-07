import json
from types import SimpleNamespace
import pytest
from scripts.audio_evaluation import digest
from scripts.music2emo_curve import verify_installation
from scripts.emotion_parameter_sweep import run


def test_repeated_contexts_are_rejected_before_loading_any_model():
    with pytest.raises(ValueError,match='Distinct'):
        run(SimpleNamespace(contexts=[10,10]))


def test_shared_inference_verification_rejects_modified_sources(tmp_path):
    source=tmp_path/'source';source.mkdir()
    weights=tmp_path/'fixture.bin';weights.write_bytes(b'authored weights')
    code=source/'fixture.py';code.write_text('value = 1\n')
    (tmp_path/'provenance.json').write_text(json.dumps({'files':[{'file':'fixture.bin','sha256':digest(weights)}]}))
    (tmp_path/'installation.json').write_text(json.dumps({'source_sha256':{'fixture.py':digest(code)}}))
    verify_installation(tmp_path)
    code.write_text('value = 2\n')
    with pytest.raises(ValueError,match='Source checksum'):
        verify_installation(tmp_path)
