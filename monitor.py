#!/usr/bin/env python3

import os
import sys
import subprocess

TIMEOUT = 5

capture_cmd_fmt = "tcpdump -l -s 64 -e -p -Ini {} type mgt subtype probe-req"

if __name__ == "__main__":

  IFACE = "en0"

  # must be running as root
  if os.geteuid() != 0:
    print("Requires privileges to capture on {}. Elevating to root...".format(IFACE))
    os.execvp("sudo", ["sudo"] + sys.argv) # replace process
  
  while True:
    try:
      print(capture_cmd_fmt.format(IFACE))
      completed = subprocess.run(capture_cmd_fmt.format(IFACE).split(), timeout=TIMEOUT, stdout=subprocess.PIPE, encoding="utf-8")
      # here goes error handling - tcpdump should just run until killed
    except subprocess.TimeoutExpired as e:
      print(e.stdout)
      print("{} lines received".format(len(e.stdout.split("\n"))))

    input()

