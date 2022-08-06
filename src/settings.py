#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os


VERSION = "1.0.1"


PLATFORMS = {
    "linux2": "linux",
    "linux": "linux",
    "win32": "windows",
    "darwin": "mac",
}


TOOL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools")
