"""Thin requests wrapper from Flask to the FastAPI backend."""
import requests
from flask import session

import config


def _headers():
    token = session.get("token")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _url(path: str) -> str:
    return f"{config.BACKEND_URL}{path}"


def get(path: str, **kwargs):
    return requests.get(_url(path), headers=_headers(), timeout=60, **kwargs)


def post(path: str, json=None, data=None, files=None, **kwargs):
    return requests.post(_url(path), json=json, data=data, files=files, headers=_headers(), timeout=60, **kwargs)


def delete(path: str, **kwargs):
    return requests.delete(_url(path), headers=_headers(), timeout=60, **kwargs)
