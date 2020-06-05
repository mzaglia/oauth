#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import base64
import binascii
import hashlib
import os
import subprocess
import threading
import webbrowser
from bdc_core.email.business import EmailBusiness

from bdc_oauth.config import Config

def open_brower(url, time=1):
    """
    open new brower
    Args:
        url: url to open in brower
        time: time delay to open brower
    """
    threading.Timer(time, lambda: webbrowser.open(url)).start()


def random_string(size=16):
    """
    generate random string
    Args:
        size: string size
    """
    return (binascii.hexlify(os.urandom(size))).decode('ascii')


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()


def key_id_encode(the_bytes):
    source = base64.b32encode(the_bytes).decode('utf-8')
    result = []
    for i in range(0, len(source), 4):
        start = i
        end = start+4
        result.append(source[start:end])
    return ":".join(result)


def kid_from_crypto_key(private_key_path, key_type='EC'):
    algorithm = hashlib.sha256()
    if key_type == 'EC':
        der, msg = run_command(['openssl', 'ec', '-in', private_key_path,
                                '-pubout', '-outform', 'DER'])

    elif key_type == 'RSA':
        der, msg = run_command(['openssl', 'rsa', '-in', private_key_path,
                                '-pubout', '-outform', 'DER'])

    else:
        raise Exception("Key type not supported")

    if not der:
        raise Exception(msg)

    algorithm.update(der)
    return key_id_encode(algorithm.digest()[:30])


def send_email(to: str, subject: str, template: str, **kwargs):
    try:
        email = EmailBusiness(
            '', to, subject, template,
            body_args=kwargs,
            BASE_PATH_TEMPLATES=Config.BASE_PATH_TEMPLATES,
            SMTP_PORT=Config.SMTP_PORT,
            SMTP_HOST=Config.SMTP_HOST,
            EMAIL_ADDRESS=Config.EMAIL_ADDRESS,
            EMAIL_PASSWORD=Config.EMAIL_PASSWORD,
        )
        email.send()
        return True

    except Exception:
        return False