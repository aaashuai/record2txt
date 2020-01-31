import base64
import logging
import time

import requests

from models import ReqParams, ResData
from settings import TRANSFER_URL, CALLBACK_URL


def req_transfer(file_path):
    logging.info(f"ready to request {file_path}")
    with open(file_path, "rb") as f:
        base64_data = base64.b64encode(f.read())
    req = ReqParams(callback_url=CALLBACK_URL, speech=base64_data)
    while 1:
        count = 1
        try:
            res = requests.post(TRANSFER_URL, req.req_params())
            res_data = ResData.parse_raw(res.content)
        except Exception as e:
            logging.error(f"try tiems: {count}, {e}")
            count += 1
            if count > 10:
                raise Exception("尝试次数过多")
            time.sleep(2.0)
            continue
        assert res_data.ret == 0, "request error"
        logging.info(f"success: {res_data.data.task_id}")
        file_path.unlink()
        return res_data.data.task_id


if __name__ == "__main__":
    from pathlib import Path

    path = Path(__file__).parent / "tmp" / "new-1.wav"
    print(req_transfer(path))
