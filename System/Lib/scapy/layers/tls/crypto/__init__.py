# This file is part of Scapy
# Copyright (C) 2007, 2008, 2009 Arnaud Ebalard
#                     2015, 2016 Maxence Tury
# This program is published under a GPLv2 license

"""
Cryptographic capabilities for TLS.
"""
import os
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)