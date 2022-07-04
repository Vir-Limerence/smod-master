## This file is part of Scapy
## See http://www.secdev.org/projects/scapy for more informations
## Copyright (C) Philippe Biondi <phil@secdev.org>
## This program is published under a GPLv2 license

"""
Scapy: create, send, sniff, dissect and manipulate network packets.

Usable either from an interactive console or as a Python library.
http://www.secdev.org/projects/scapy
"""
import os
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
if __name__ == "__main__":
    from scapy.main import interact
    interact()
