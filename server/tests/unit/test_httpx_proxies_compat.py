import inspect


def test_compat_accepts_proxies_when_client_does_not():
    from server.domain.utilities import httpx_proxies_compat as compat

    compat._APPLIED = False

    class Client:
        def __init__(self, timeout=None):
            self.timeout = timeout

    compat._patch_if_missing_proxies(Client)
    client = Client(proxies={"https://": "http://localhost:8080"}, timeout=1)
    assert client.timeout == 1
    assert "proxies" in inspect.signature(Client.__init__).parameters


def test_compat_maps_proxies_to_proxy_when_supported():
    from server.domain.utilities import httpx_proxies_compat as compat

    class Client:
        def __init__(self, proxy=None):
            self.proxy = proxy

    compat._patch_if_missing_proxies(Client)
    client = Client(proxies={"https://": "http://localhost:8080"})
    assert client.proxy == "http://localhost:8080"