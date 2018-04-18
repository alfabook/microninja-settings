#!/usr/bin/env python

# about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the about screen backend functions

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja


from microninja.utils import run_cmd, is_model_a, is_model_b, is_model_b_plus
from microninja.utils import is_model_2_b, is_model_3_b


def get_current_version():
    version_number = "?"
    with open('/etc/microninja_version', 'r') as f:
        output = f.read().strip()
        version_number = output.split('-')[-1]
    return version_number


def get_space_available():
    out, err, rc = run_cmd('df -h / | tail -1')
    device, size, used, free, percent, mp = out.split()

    info = {
        'used': '',
        'total': ''
    }

    if not err:
        info['used'] = used
        info['total'] = size

    return info


def get_temperature():
    temperature = None
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        output = f.read().strip()
        temperature = int(output) / 1000.0
    return temperature


def get_model_name():
    if is_model_a():
        model = "A"
    elif is_model_b():
        model = "B"
    elif is_model_b_plus():
        model = "B+"
    elif is_model_2_b():
        model = "2"
    elif is_model_3_b():
        model = "3"

    return "Raspberry Pi {}".format(model)
