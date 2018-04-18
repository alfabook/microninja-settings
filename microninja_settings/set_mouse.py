#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_mouse.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation

from gi.repository import Gdk
from microninja_settings.templates import RadioButtonTemplate
from .config_file import get_setting, set_setting
from microninja_settings.system.mouse import change_mouse_speed


MODES = ['Lento', 'Normale', 'Veloce']


class SetMouse(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0

    def __init__(self, win):
        RadioButtonTemplate.__init__(
            self,
            "Mouse",
            "Imposta velocità",
            "APPLICA MODIFICHE",
            [
                ["Lento", "RICHIEDE MINORE PRECISIONE DI MOVIMENTO"],
                ["Normale", "DEFAULT"],
                ["Veloce", "CONSIGLIATO PER SCHERMI LARGHI"]
            ]
        )
        self.win = win
        self.win.set_main_widget(self)
        self.win.set_size_request(450, 350)

        # Show the current setting by electing the appropriate radio button
        try:
            self.initial_button = MODES.index(get_setting('Mouse'))
        except ValueError:
            self.initial_button = 0

        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.reset_and_go_home)

        self.kano_button.connect('clicked', self.set_mouse)
        self.win.show_all()

    def reset_and_go_home(self, widget=None, event=None):
        change_mouse_speed(self.initial_button)
        self.win.go_to_home()

    def set_mouse(self, button):
        try:
            config = MODES[self.selected_button]
        except IndexError:
            config = 'Normale'

        if not config == get_setting('Mouse'):
            set_setting('Mouse', config)
        self.win.go_to_home()

    def on_button_toggled(self, button, selected):
        if button.get_active():
            self.selected_button = selected
            # Apply changes so speed can be tested
            change_mouse_speed(selected)

