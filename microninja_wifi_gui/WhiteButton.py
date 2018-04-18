#!/usr/bin/env python

# WhiteButton.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Create a white version of the orange link found in toolset

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja

import os
from microninja.gtk3.buttons import GenericButton
from microninja_wifi_gui.paths import css_dir
from microninja.gtk3.apply_styles import apply_styling_to_widget


class WhiteButton(GenericButton):
    button_css = os.path.join(css_dir, 'small_white_button.css')

    def __init__(self, text=""):

        # Create button
        GenericButton.__init__(self, text)
        apply_styling_to_widget(self, self.button_css)
        apply_styling_to_widget(self.label, self.button_css)
        self.get_style_context().add_class("small_white_button")
