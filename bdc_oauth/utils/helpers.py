import locale
import threading, webbrowser
import os, binascii

def open_brower(url, time=1):
    """
    open new brower
    @params {string} url to open in brower
    @params {string} time delay to open brower
    """
    threading.Timer(time, lambda: webbrowser.open(url)).start()


def random_string(size=16):
    """
    generate random string
    @params {int} string size
    """
    return (binascii.hexlify(os.urandom(size))).decode('ascii')