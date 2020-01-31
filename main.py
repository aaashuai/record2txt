import logging
import time

import uvicorn
from fastapi import FastAPI, File, UploadFile
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from models import ResultModel
from service_cut import cut_file, trans_file_to_wav, write_file
from service_transfer import req_transfer
from settings import BASE_PATH

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

TSK_ID_LIST = []
RES_DICT = {}


@app.post("/callback")
async def callback(ret: int, msg: str, data: dict):
    assert ret == 0, f"callback error: {msg}"
    task_id = data["task_id"]
    text = data["text"]
    RES_DICT[task_id] = text


@app.get("/result")
async def result():
    if not (TSK_ID_LIST and RES_DICT) or len(TSK_ID_LIST) != len(RES_DICT):
        return ResultModel(ret=1)
    msg = "".join([RES_DICT[tsk_id] for tsk_id in TSK_ID_LIST])
    return ResultModel(ret=0, message=msg)


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
def upload(*, upload_file: UploadFile = File(...)):
    file_type = upload_file.filename[-3:]
    assert file_type in ["mp3", "m4a"], "file type error"
    file_path = write_file(upload_file.file.read(), file_type=file_type)
    wav_path = trans_file_to_wav(file_path, file_type=file_type)
    file_list = cut_file(wav_path, BASE_PATH / "tmp")
    logging.info(f"files: \n{file_list}")
    for file in file_list:
        tsk_id = req_transfer(file)
        TSK_ID_LIST.append(tsk_id)
        time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s %(levelname)s %(message)s]", level=logging.DEBUG
    )
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
