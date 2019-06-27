import locale
import threading, webbrowser
import os, binascii

from flask import Response, json

def return_response(data, status_code, dumps=True):
    data = json.dumps(data) if dumps else data
    return Response(data, status_code, content_type='application/json')


def ope_brower(url, time=1):
    threading.Timer(time, lambda: webbrowser.open(url) ).start()

def valid_scope_auth(list_scope):
    for scope in list_scope:
        if scope not in ['read']:
            return True
    return True

def random_string(size=16):
    return (binascii.hexlify(os.urandom(size))).decode('ascii')