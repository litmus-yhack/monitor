#!/usr/bin/env python3

import os
import subprocess

SID_FILE = "sid.txt"

if os.path.exists(SID_FILE):
    print("file exists!")
else:
    with open(SID_FILE, "a+") as f:
        cmd = '/usr/bin/uuidgen'
        sid = subprocess.check_output([cmd]).decode("utf-8")
        for i in range(1):
            f.write(sid)
