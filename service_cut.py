import logging
import wave
from pathlib import Path

import numpy as np
from pydub import AudioSegment

from settings import BASE_PATH

CUT_TIME = 70


def write_file(content: bytes, file_type: str):
    logging.info("ready to write mp3")
    file_path = BASE_PATH / "origin" / f"b.{file_type}"
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def trans_file_to_wav(filepath: str, file_type: str):
    logging.info("ready to transfer file to wav")
    wav_path = BASE_PATH / "origin" / "new.wav"
    voice = AudioSegment.from_file(filepath, format=file_type)
    voice.export(str(wav_path), format="wav")
    Path(filepath).unlink()
    return wav_path


def cut_file(filepath: Path, to_dir: Path):
    logging.info("ready to cut file")
    file_list = []
    with wave.open(str(filepath), "rb") as f:
        params = f.getparams()
        nchannel, sampwidth, framerate, nframes = params[:4]
        cut_frame_num = framerate * CUT_TIME
        str_data = f.readframes(nframes)
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, 2
    wave_data = wave_data.T
    temp_data = wave_data.T
    step_num = cut_frame_num
    step_total = 0
    cur = 0
    while step_total < nframes:
        new_filename = f"{filepath.name.split('.')[0]}-{cur+1}.wav"
        new_path = to_dir / new_filename
        file_list.append(new_path)
        tmp = temp_data[step_num * cur : step_num * (cur + 1)]
        if not tmp.any():
            break
        cur += 1
        step_total = cur * step_num
        tmp.shape = 1, -1
        tmp = tmp.astype(np.short)
        with wave.open(str(new_path), "wb") as f:
            f.setnchannels(nchannel)
            f.setsampwidth(sampwidth)
            f.setframerate(framerate)
            f.writeframes(tmp.tostring())
    filepath.unlink()
    return file_list


if __name__ == "__main__":
    BASE_PATH = Path(__file__).parent
    path = BASE_PATH / "origin" / "a.m4a"
    to_path = BASE_PATH / "origin" / "new.wav"
    wav_path = trans_file_to_wav(str(path), "m4a")
    f_l = cut_file(wav_path, BASE_PATH / "tmp")
    print(f_l)
