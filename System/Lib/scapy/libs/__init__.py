# This file is part of Scapy
# See http://www.secdev.org/projects/scapy for more information
# This program is published under a GPLv2 license

"""
Library bindings
"""
import os
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)