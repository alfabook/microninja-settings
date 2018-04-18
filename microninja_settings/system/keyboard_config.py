#!/usr/bin/env python

# keyboard_config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This script is an interactive selection of the keyboard,
# based on country name and local keyboard variant.
#

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja

from microninja.utils import run_cmd
import microninja_settings.system.keyboard_layouts as keyboard_layouts
from microninja_settings.config_file import get_setting

# GLOBAL variables
keyboard_conffile = '/etc/default/keyboard'


# Given a country name return the keyboard layout code
def find_country_code(country_name, layout):
    for l in layout:
        if l.upper() == country_name.upper():
            return layout[l]
    return None


# Return list of keyboard variants for a given country
def find_keyboard_variants(country_code):
    try:
        #return sorted(keyboard_layouts.variants[country_code])
        return keyboard_layouts.variants[country_code]
    except Exception:
        # It means this country code does not have keyboard variants
        return None


# Find macintosh index within the variants combobox
def find_macintosh_index(country_name, layout):
    country_code = find_country_code(country_name, layout)
    variants = find_keyboard_variants(country_code)

    if variants:
        for i in range(len(variants)):
            if variants[i] == ("Macintosh", "mac"):
                # This is due to the adding of generic at the start of the array
                return i + 1
    else:
        return None


def is_changed(country_index, variant_index):
    country = get_setting('Keyboard-country-index')
    variant = get_setting('Keyboard-variant-index')

    return (country_index != country or variant != variant_index)


def set_keyboard(country_code, variant):
    if variant == _('Generic'):
        variant = ''

    # Notify and apply changes to the XServer
    run_cmd("setxkbmap {} {}".format(country_code, variant))


def set_saved_keyboard():
    continent_index = get_setting('Keyboard-continent-index')
    country_index = get_setting('Keyboard-country-index')
    variant_index = get_setting('Keyboard-variant-index')

    layout = keyboard_layouts.codes_list[continent_index][country_index]
    if variant_index == 0:
        variant = ''
    else:
        variants = find_keyboard_variants(layout)
        variant = variants[variant_index - 1][1]

    set_keyboard(layout, variant)
