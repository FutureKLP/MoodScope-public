"""Synthetic provider-boundary regressions; no external service is contacted."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import threading

import httpx
import pytest

from backend import cloud, provider_http, providers


@pytest.fixture
def server():
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            calls.append((self.command, self.path, dict(self.headers), body))
            structured = (self.command == 'POST' and
                          isinstance(json.loads(body)['messages'][0]['content'], list))
            value = ({'data': [{'id': 'fixture'}]} if self.command == 'GET' else
                     {'choices': [{'finish_reason': 'stop', 'message': {
                         'content': '{"answer":1}' if structured else
                         'A cautious reading of the authored fixture.'}}]})
            raw = json.dumps(value).encode()
            self.send_response(302 if self.path.startswith('/redirect') else 200)
            self.send_header('Location', f'http://127.0.0.1:{self.server.server_port}/unwanted')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        do_GET = respond
        do_POST = respond

    instance = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield instance.server_port, calls
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()


def test_dns_checked_addresses_are_the_only_wire_targets(server, monkeypatch):
    port, calls = server
    real = socket.getaddrinfo
    lookups = []

    def resolve(host, *args, **kwargs):
        if host == 'fixture.invalid':
            lookups.append(host)
            return real('127.0.0.1' if len(lookups) == 1 else '127.0.0.2', *args, **kwargs)
        assert host == '127.0.0.1'
        return real(host, *args, **kwargs)

    monkeypatch.setattr(socket, 'getaddrinfo', resolve)
    with provider_http.stream('GET', f'http://fixture.invalid:{port}/v1/models', timeout=2) as response:
        assert response.status_code == 200
        response.read()
    assert len(lookups) == 1
    assert calls[0][2]['Host'] == f'fixture.invalid:{port}'


def test_revalidation_blocks_change_after_endpoint_preflight(server, monkeypatch):
    port, calls = server
    lookups = []

    def resolve(host, *args, **kwargs):
        lookups.append(host)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                 ('127.0.0.1' if len(lookups) == 1 else '8.8.8.8', port))]

    monkeypatch.setattr(socket, 'getaddrinfo', resolve)
    with pytest.raises(ValueError):
        providers.discover_models(f'http://fixture.invalid:{port}/v1', 'fixture-key')
    assert len(lookups) == 2 and not calls


@pytest.mark.parametrize('scheme,addresses', [
    ('http', ['127.0.0.1', '8.8.8.8']), ('http', ['::1', '2001:4860:4860::8888']),
    ('https', ['169.254.169.254']), ('https', ['::ffff:169.254.169.254']),
    ('https', ['fe80::1']), ('https', ['0.0.0.0']), ('https', ['::']),
    ('https', ['224.0.0.1']), ('http', ['100.64.0.1']),
    ('http', ['192.0.2.1']), ('https', []),
])
def test_unsafe_or_mixed_dns_sets_fail_before_transport(monkeypatch, scheme, addresses):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [
        (socket.AF_INET6 if ':' in ip else socket.AF_INET, 1, 6, '', (ip, 80)) for ip in addresses])
    with pytest.raises(ValueError):
        provider_http._resolve(httpx.URL(f'{scheme}://fixture.invalid/v1'))


@pytest.mark.parametrize('value', [
    'http://127.0.0.1/v1', 'http://[::1]/v1', 'http://[::ffff:127.0.0.1]/v1',
    'http://192.168.1.2/v1', 'http://10.0.0.2/v1', 'https://172.16.0.2/v1',
    'http://[fd00::1]/v1', 'https://8.8.8.8/v1',
])
def test_explicit_local_lan_and_https_targets_remain_valid(value):
    assert provider_http.endpoint(value) == value


@pytest.mark.parametrize('value', [
    'https://fixture.invalid:bad/v1', 'https://fixture.invalid:99999/v1',
    'https://fixture.invalid:/v1', 'https://fixture.invalid\\@127.0.0.1',
    'http://[fe80::1%25eth0]/v1', 'https://fixture.invalid/\nmodels',
    'https://@fixture.invalid/v1',
])
def test_ambiguous_provider_urls_rejected(value):
    with pytest.raises(ValueError):
        provider_http.endpoint(value)


def test_localhost_cannot_resolve_outside_loopback(monkeypatch):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(2, 1, 6, '', ('192.168.1.2', 80))])
    with pytest.raises(ValueError):
        provider_http.endpoint('http://localhost/v1')


def test_provider_calls_ignore_environment_proxies_and_do_not_follow_redirects(server, monkeypatch):
    port, calls = server
    # If inherited, this proxy would receive an absolute URL rather than /v1/models.
    proxy = f'http://127.0.0.1:{port}'
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        monkeypatch.setenv(name, proxy)
    monkeypatch.setenv('NO_PROXY', '')
    monkeypatch.setenv('no_proxy', '')
    base = f'http://127.0.0.1:{port}/v1'
    assert providers.discover_models(base, 'fixture-key')['models'] == ['fixture']
    profile = {'base_url': base, 'protocol': 'openai', 'model': 'fixture', 'name': 'Fixture'}
    assert providers.generate_snapshot(profile, 'fixture-key', 'Authored fixture')['text']
    with pytest.raises(ValueError, match='HTTP 302'):
        providers.discover_models(f'http://127.0.0.1:{port}/redirect', 'fixture-key')
    assert [call[1] for call in calls] == ['/v1/models', '/v1/chat/completions', '/redirect/models']
    assert all(call[2]['Authorization'] == 'Bearer fixture-key' for call in calls)


def test_https_pinning_preserves_host_sni_timeout_and_verified_transport(monkeypatch):
    captured = []
    constructors = []

    class Direct:
        def __init__(self, **kwargs):
            constructors.append(kwargs)

        def handle_request(self, request):
            captured.append(request)
            return httpx.Response(200, content=b'{}')

        def close(self):
            pass

    monkeypatch.setattr(httpx, 'HTTPTransport', Direct)
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(2, 1, 6, '', ('127.0.0.1', 443))])
    with httpx.Client(transport=provider_http.ProviderTransport(), trust_env=False) as client:
        client.get('https://fixture.invalid/v1/models', timeout=3)
    request = captured[0]
    assert request.url.host == '127.0.0.1'
    assert request.headers['Host'] == 'fixture.invalid'
    assert request.extensions['sni_hostname'] == 'fixture.invalid'
    assert request.extensions['timeout']['connect'] == 3
    assert constructors == [{'trust_env': False, 'retries': 0}]


@pytest.mark.parametrize('protocol', ['openai', 'gemini'])
def test_audio_adapters_use_direct_provider_transport(monkeypatch, protocol):
    calls = []

    def stream(method, url, **kwargs):
        from contextlib import nullcontext
        calls.append((method, url, kwargs))
        if protocol == 'openai':
            result = {'choices': [{'finish_reason': 'stop', 'message': {'content': '{"answer":1}'}}]}
        else:
            result = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': '{"answer":1}'}]}}]}
        return nullcontext(httpx.Response(200, json=result))

    monkeypatch.setattr(provider_http, 'stream', stream)
    profile = {'id': 'fixture', 'name': 'Fixture', 'protocol': protocol,
               'base_url': 'http://127.0.0.1:11434/v1', 'model': 'fixture',
               'audio_usage_confirmed': True, 'free_project_confirmed': True}
    with cloud.bound_target(profile, 'fixture-key'):
        assert cloud.request_json('Authored fixture', {'type': 'object'}) == {'answer': 1}
    assert len(calls) == 1 and calls[0][0] == 'POST'
    assert calls[0][2]['follow_redirects'] is False


@pytest.mark.parametrize('with_audio', [False, True])
def test_compatible_structured_requests_reach_only_own_server(server, monkeypatch, with_audio):
    import numpy as np
    port, calls = server
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'):
        monkeypatch.setenv(name, 'http://127.0.0.1:1')
    profile = {'base_url': f'http://127.0.0.1:{port}/v1', 'model': 'fixture'}
    audio = cloud.encode_audio(np.zeros(1600), 16000) if with_audio else None
    assert cloud.compatible_json(profile, 'fixture-key', 'Authored fixture', {}, audio) == {'answer': 1}
    assert len(calls) == 1 and calls[0][1] == '/v1/chat/completions'
    assert calls[0][2]['Authorization'] == 'Bearer fixture-key'


def test_ipv6_loopback_wire_connection():
    class Server(ThreadingHTTPServer):
        address_family = socket.AF_INET6

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            raw = b'{"data":[{"id":"ipv6-fixture"}]}'
            self.send_response(200)
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    try:
        server = Server(('::1', 0), Handler)
    except OSError:
        pytest.skip('IPv6 loopback is unavailable on this host')
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert providers.discover_models(f'http://[::1]:{server.server_port}/v1')['models'] == ['ipv6-fixture']
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()


def test_cloud_dns_failure_keeps_safe_adapter_error(monkeypatch):
    def failed(*args, **kwargs):
        raise ValueError('PRIVATE FIXTURE')

    monkeypatch.setattr(provider_http, 'post', failed)
    profile = {'protocol': 'openai', 'base_url': 'http://127.0.0.1:11434/v1',
               'model': 'fixture', 'audio_usage_confirmed': True}
    with cloud.bound_target(profile, 'fixture-key'), pytest.raises(cloud.CloudError) as error:
        cloud.request_json('Authored fixture', {})
    assert 'PRIVATE' not in str(error.value)
