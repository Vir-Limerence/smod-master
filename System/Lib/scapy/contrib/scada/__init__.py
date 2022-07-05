# This file is part of Scapy
# See http://www.secdev.org/projects/scapy for more information
# Copyright (C) Thomas Tannhaeuser <hecke@naberius.de>
# This program is published under a GPLv2 license
#
# scapy.contrib.status = skip


# Package of contrib SCADA modules.


"""contains packages related to SCADA protocol layers."""

from scapy.contrib.scada.iec104 import *  # noqa F403,F401
import os
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)