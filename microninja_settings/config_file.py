#!/usr/bin/env python
# -*- coding: utf-8 -*-
# config_file.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions controlling reading and writing to config file
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja

import os
import re
import shutil
from microninja.utils import ensure_dir, get_user_unsudoed, read_json, write_json, chown_path
from microninja.logging import logger
from microninja_settings.common import settings_dir
from microninja.utils import is_model_2_b, is_model_3_b

USER = None
USER_ID = None

username = get_user_unsudoed()
if username != 'root':
    if os.path.exists(settings_dir) and os.path.isfile(settings_dir):
        os.rename(settings_dir, settings_dir + '.bak')
    ensure_dir(settings_dir)
    chown_path(settings_dir)
    settings_file = os.path.join(settings_dir, 'settings')

defaults = {
    'pi1': {
        'Keyboard-continent-index': 4,
        'Keyboard-country-index': 19,
        'Keyboard-variant-index': 0,
        #'Keyboard-continent-human': _('Europa'),
        #'Keyboard-country-human': _('Italia'),
        #'Keyboard-variant-human': _('Generica'),
        'Audio': 'Analog',
        'Wifi': '',
        'Wifi-connection-attempted': False,
        'Overclocking': 'Alto',
        'Mouse': 'Normale',
        'Font': 1,
        'Wallpaper': 'microninja-background',
        'Parental-level': 1,
        'Locale': 'en_GB'
    },
    'pi2': {
        'Keyboard-continent-index': 4,
        'Keyboard-country-index': 19,
        'Keyboard-variant-index': 0,
        #'Keyboard-continent-human': _('Europa'),
        #'Keyboard-country-human': _('Italia'),
        #'Keyboard-variant-human': _('Generica'),
        'Audio': 'HDMI',
        'Wifi': '',
        'Wifi-connection-attempted': False,
        'Overclocking': 'Predefinito',
        'Mouse': 'Normale',
        'Font': 1,
        'Wallpaper': 'microninja-background',
        'Parental-level': 1,
        'Locale': 'en_GB'
    }
}


def file_replace(fname, pat, s_after):
    logger.debug('config_file / file_replace {} "{}" "{}"'.format(fname, pat, s_after))
    if not os.path.exists(fname):
        logger.debug('config_file / file_replace file doesn\'t exists')
        return -1

    # if escape:
        # pat = re.escape(pat)
        # logger.debug('config_file / file_replace replacing pattern, new pattern: "{}"'.format(pat))

    # See if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            logger.debug('config_file / file_replace pattern does not occur in file')
            return -1  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()

        # preserving permissions from the old file
        shutil.copystat(fname, out_fname)

        # overwriting the old file with the new one
        os.rename(out_fname, fname)

    logger.debug('config_file / file_replace file replaced')


def get_pi_key():
    pi2 = is_model_2_b()
    pi3 = is_model_3_b()

    key = "pi1"
    if pi2:
        key = "pi2"
    
    if pi3:
        key = "pi2"

    return key


def get_setting(variable):

    try:
        value = read_json(settings_file)[variable]
    except Exception:
        key = get_pi_key()
        if variable not in defaults[key]:
            logger.info('Defaults not found for variable: {}'.format(variable))
        value = defaults[key][variable]
    return value


def set_setting(variable, value):

    if username == 'root':
        return

    logger.debug('config_file / set_setting: {} {}'.format(variable, value))

    data = read_json(settings_file)
    if not data:
        data = dict()

    data[variable] = value
    write_json(settings_file, data)
    chown_path(settings_file)
