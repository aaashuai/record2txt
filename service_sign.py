import hashlib
from urllib.parse import urlencode

from settings import APP_KEY


def dict_sort(d: dict) -> dict:
    return dict(sorted(d.items(), key=lambda s: s[0]))


def md5_encode(string: str) -> str:
    return hashlib.md5(string.encode(encoding="UTF-8")).hexdigest()


def get_req_sign(params: dict):
    params = dict_sort(params)
    params["app_key"] = APP_KEY
    string = urlencode({k: v for k, v in params.items() if v != ""})
    return md5_encode(string).upper()


if __name__ == "__main__":
    res = get_req_sign({"c": ""})
    print(res)
