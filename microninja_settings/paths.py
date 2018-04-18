#!/usr/bin/env python
# -*- coding: utf-8 -*-
# paths.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# leaving only legal dir

import os

from microninja.logging import logger
from microninja.utils import get_user_unsudoed, get_home_by_username

dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# legal path - containing terms and conditions of use
legal_dir = ""
legal_local = os.path.join(dir_path, 'legal/')
legal_usr = '/usr/share/microninja-desktop/Legal/'
if os.path.exists(legal_local):
    legal_dir = legal_local
elif os.path.exists(legal_usr):
    legal_dir = legal_usr
else:
    logger.warn('Neither local nor usr legal dir found!')


