import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pyFortiManagerAPI  # noqa: E402

SESSION_ID = "test-session-id"


class FakeResponse:
    def __init__(self, body):
        self._body = body

    def json(self):
        return self._body


class FakeSession:
    """Stands in for requests.Session; records every JSON-RPC payload posted."""

    def __init__(self, responder):
        self.responder = responder
        self.calls = []
        self.proxies = {}
        self.trust_env = True

    def post(self, url=None, json=None, verify=None, **kwargs):
        self.calls.append({"url": url, "json": json, "verify": verify, **kwargs})
        return FakeResponse(self.responder(json))

    @property
    def api_calls(self):
        """Payloads excluding the login request."""
        return [c["json"] for c in self.calls
                if c["json"]["params"][0].get("url") != "sys/login/user"]

    @property
    def last(self):
        return self.api_calls[-1]


def default_responder(payload):
    url = payload["params"][0].get("url")
    if url == "sys/login/user":
        return {"result": [{"status": {"code": 0, "message": "OK"}, "url": url}], "session": SESSION_ID}
    return {"result": [{"status": {"code": 0, "message": "OK"}, "url": url, "data": {}}]}


@pytest.fixture
def fake_session(monkeypatch):
    sessions = []

    def factory():
        s = FakeSession(default_responder)
        sessions.append(s)
        return s

    monkeypatch.setattr(pyFortiManagerAPI.requests, "session", factory)
    return sessions


@pytest.fixture
def fmg(fake_session):
    return pyFortiManagerAPI.FortiManager(host="fmg.example", username="u", password="p", adom="lab")


@pytest.fixture
def session(fmg, fake_session):
    """Logged-in FortiManager's fake session."""
    fmg.login()
    return fake_session[0]
