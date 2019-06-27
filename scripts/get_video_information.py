# -*- coding: utf-8 -*-
import subprocess
import json
import os
import datetime


def get_video_duration(media_path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    cmd = dir_path + "/video_information.sh %(input_file)s"

    run_cmd = cmd % {
        'input_file': media_path,
    }
    resp = _cli(run_cmd, read_from_stdout=True)
    try:
        _data = json.loads(resp)['format']['duration']
    except:
        _data = "0.0"
    float_duration = float(_data)
    duration = str(datetime.timedelta(seconds=round(float_duration, 0)))
    return duration


def _cli(cmd, without_output=False, read_from_stdout=False):

    if without_output:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    else:
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True, bufsize=10**8,
            universal_newlines=True
        )
        if read_from_stdout:
            return p.stdout.read()
        return p.stderr.read()
