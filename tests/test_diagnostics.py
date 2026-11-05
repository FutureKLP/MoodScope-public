from backend import diagnostics


def test_error_log_has_reference_and_frames_without_payloads(tmp_path):
    try:raise RuntimeError('Private song sentence and fixture-key must not appear')
    except RuntimeError as exc:message=diagnostics.user_error(tmp_path,'test-operation',exc,'Analyse fehlgeschlagen.')
    log=(tmp_path/'logs/moodscope.log').read_text(encoding='utf-8')
    assert 'RuntimeError' in log and 'test_error_log_has_reference' in log
    assert 'Private song' not in log and 'fixture-key' not in log
    reference=message.split('Fehler-ID: ')[1].split('.')[0]
    assert reference in log
