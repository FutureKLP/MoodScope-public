"""Direct provider connections, with DNS validation bound to the wire target."""
from contextlib import contextmanager
import ipaddress
import socket
from urllib.parse import urlsplit

import httpx


_LAN = tuple(ipaddress.ip_network(value) for value in
             ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', 'fc00::/7'))


def _address(value: str):
    address = ipaddress.ip_address(value)
    if isinstance(address, ipaddress.IPv6Address) and address.scope_id:
        raise ValueError('Scoped provider addresses are not supported')
    return getattr(address, 'ipv4_mapped', None) or address


def _local(address) -> bool:
    return address.is_loopback or any(address in network for network in _LAN)


def endpoint(value: str, *, resolve_http: bool = True) -> str:
    value = value.strip().rstrip('/')
    if '\\' in value or any(ord(c) < 33 or ord(c) == 127 for c in value):
        raise ValueError('Ungültige Serveradresse.')
    parsed = urlsplit(value)
    if (parsed.scheme not in {'http', 'https'} or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment or '%' in parsed.hostname):
        raise ValueError('Basis-URL ohne Zugangsdaten, Query oder Fragment eingeben.')
    try:
        url = httpx.URL(value)
        parsed.port
    except (httpx.InvalidURL, ValueError):
        raise ValueError('Ungültige Serveradresse oder Port.') from None
    if not url.port and parsed.netloc.endswith(':'):
        raise ValueError('Ungültiger Serverport.')
    try:
        address = _address(url.host)
    except ValueError:
        address = None
    if address is not None:
        _check_addresses(url, [address])
    elif url.scheme == 'http' and resolve_http:
        _resolve(url)
    return str(url).rstrip('/')


def _check_addresses(url: httpx.URL, addresses: list) -> None:
    if not addresses or len(addresses) > 16:
        raise ValueError('Serveradresse nicht unterstützt.')
    for address in addresses:
        if not (_local(address) or (url.scheme == 'https' and address.is_global
                                   and not address.is_multicast and not address.is_reserved
                                   and not getattr(address, 'is_site_local', False))):
            raise ValueError('Internetserver benötigen HTTPS; nur lokale/LAN-Adressen dürfen HTTP nutzen.')
        if url.host == 'localhost' and not address.is_loopback:
            raise ValueError('Localhost muss auf Loopback zeigen.')


def _resolve(url: httpx.URL) -> list:
    try:
        addresses = [_address(url.host)]
    except ValueError:
        try:
            rows = socket.getaddrinfo(url.host, url.port or (443 if url.scheme == 'https' else 80),
                                      type=socket.SOCK_STREAM)
            addresses = list(dict.fromkeys(_address(row[4][0]) for row in rows))
        except (OSError, ValueError):
            raise ValueError('Servername nicht auflösbar. Netzwerkverbindung oder lokale IP-Adresse prüfen.') from None
    _check_addresses(url, addresses)
    return addresses


class ProviderTransport(httpx.BaseTransport):
    def __init__(self) -> None:
        # No environment proxy or environment-selected CA bundle; normal TLS verification stays on.
        self._direct = httpx.HTTPTransport(trust_env=False, retries=0)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        endpoint(str(request.url), resolve_http=False)
        addresses = _resolve(request.url)
        # Prefer IPv4 for dual-stack home servers; no request replay or recipient fallback.
        address = min(addresses, key=lambda item: item.version)
        headers = request.headers.copy()
        headers['Host'] = request.url.netloc.decode('ascii')
        pinned = httpx.Request(request.method, request.url.copy_with(host=str(address)),
                               headers=headers, stream=request.stream,
                               extensions={**request.extensions, 'sni_hostname': request.url.host})
        # HTTPCore's documented sni_hostname extension preserves certificate identity.
        return self._direct.handle_request(pinned)

    def close(self) -> None:
        self._direct.close()


@contextmanager
def stream(method: str, url: str, **kwargs):
    with httpx.Client(transport=ProviderTransport(), trust_env=False, follow_redirects=False) as client:
        with client.stream(method, url, **kwargs) as response:
            yield response


def post(url: str, **kwargs) -> httpx.Response:
    # Audio response contract is separate from the bounded metadata/text contract.
    with stream('POST', url, **kwargs) as response:
        if response.status_code != 200:
            return httpx.Response(response.status_code)
        response.read()
        return httpx.Response(response.status_code, content=response.content)
