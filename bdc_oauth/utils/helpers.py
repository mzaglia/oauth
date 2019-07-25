import locale
import threading, webbrowser
import os, binascii

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
