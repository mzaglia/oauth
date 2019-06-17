import locale

from flask import Response, json
from contextlib import contextmanager
from datetime import datetime

@contextmanager
def setlocale():
        saved = locale.setlocale(locale.LC_ALL)
        try:
                yield locale.setlocale(locale.LC_ALL, os.environ.get('LC_ALL', 'pt_BR.UTF-8'))
        finally:
                locale.setlocale(locale.LC_ALL, saved)


def return_response(data, status_code, dumps=True):
        data = json.dumps(data) if dumps else data
        return Response(data, status_code, content_type='application/json')
