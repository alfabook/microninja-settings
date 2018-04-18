#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_font.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation

from gi.repository import Gdk
import os
from microninja.utils import get_user_unsudoed
from microninja_settings.templates import RadioButtonTemplate
from .config_file import get_setting, set_setting
from microninja_settings.system.font import change_font_size

selected_button = 0
initial_button = 0

username = get_user_unsudoed()
config_file = os.path.join('/home', username, '.config/lxsession/LXDE/desktop.conf')


MODES = [_('Small'), _('Normal'), _('Large')]


class SetFont(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0

    def __init__(self, win):
        RadioButtonTemplate.__init__(
            self,
            _("Font"),
            _("Choose a comfortable font size"),
            _("APPLY MODIFIES"),
            [
                [_("Small"), _("SUGGESTED FOR SMALL SCREENS")],
                [_("Normal"), _("DEFAULT")],
                [_("Large"), _("SUGGESTED FOR BIG SCREENS")]
            ]
        )

        self.win = win
        self.win.set_main_widget(self)
        self.win.set_size_request(420, 350)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.reset_and_go_home)

        # Show the current setting by electing the appropriate radio button
        try:
            self.initial_button = get_setting('Font')
        except ValueError:
            self.initial_button = 1
        if not str(self.initial_button).isdigit():
            self.initial_button = 1

        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.kano_button.connect('clicked', self.change_font)
        self.win.show_all()

    def reset_and_go_home(self, widget=None, event=None):
        change_font_size(self.initial_button)
        self.win.go_to_home()

    def change_font(self, button):
        try:
            config = self.selected_button
        except IndexError:
            config = 1

        if not config == get_setting('Font'):
            set_setting('Font', config)
        self.win.go_to_home()

    def on_button_toggled(self, button, selected):
        if button.get_active():
            self.selected_button = selected
            # Apply changes so font can be tested
            change_font_size(selected)
