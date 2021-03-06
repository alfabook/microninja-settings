#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_overclock.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation
#

from gi.repository import Gdk
from microninja_settings.templates import RadioButtonTemplate
import microninja_settings.common as common
from microninja_settings.boot_config import get_config_value
from microninja_settings.system.overclock import CLOCK_MODES, change_overclock_value, is_dangerous_overclock_value
from microninja.utils import is_model_2_b
from microninja.gtk3.microninja_dialog import KanoDialog


class SetOverclock(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0
    boot_config_file = "/boot/config.txt"

    def __init__(self, win):
        self.is_pi2 = is_model_2_b()

        options = []
        for m in CLOCK_MODES[self.is_pi2]['modes']:
            options.append([
                m,
                "{arm_freq}HZ ARM, "
                "{core_freq}HZ CORE, "
                "{sdram_freq}MHZ SDRAM, "
                "{over_voltage} OVERVOLT"
                .format(**CLOCK_MODES[self.is_pi2]['values'][m])
            ])

        RadioButtonTemplate.__init__(
            self,
            "Setta l'overclock al tuo processore",
            "Rendi il tuo computer più veloce, ma scalderà di più.",
            "APPLICA MODIFICHE",
            options
        )

        self.win = win
        self.win.set_main_widget(self)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()
        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.set_overclock)
        self.kano_button.connect("key-release-event", self.set_overclock)

        self.win.show_all()

    def set_overclock(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # Mode has no changed
            if self.initial_button == self.selected_button:
                self.win.go_to_home()
                return

            config = CLOCK_MODES[self.is_pi2]['modes'][self.selected_button]
            change_overclock = True

            if is_dangerous_overclock_value(config, self.is_pi2):

                kdialog = KanoDialog(
                    title_text="Attenzione",
                    description_text=(
                        "Per una piccola percentuale di utenti, questo settaggio potrebbe "
                        "rendere il computer imprevedibile. Vuoi "
                        "continuare?"
                    ),
                    button_dict=[
                        {
                            'label': "NO",
                            'color': 'red',
                            'return_value': False
                        },
                        {
                            'label': "SI",
                            'color': 'green',
                            'return_value': True
                        }
                    ],
                    parent_window=self.win
                )
                change_overclock = kdialog.run()

            if change_overclock:
                change_overclock_value(config, self.is_pi2)

                # Tell user to reboot to see changes
                common.need_reboot = True

                self.win.go_to_home()

    def current_setting(self):
        # The initial button defaults to zero (above) if the user has
        # selected a different frequency
        freq = get_config_value('arm_freq')

        for x in CLOCK_MODES[self.is_pi2]['modes']:
            if CLOCK_MODES[self.is_pi2]['values'][x]['arm_freq'] == freq:
                self.initial_button = CLOCK_MODES[self.is_pi2]['modes'].index(x)

    def on_button_toggled(self, button, selected):
        if button.get_active():
            self.selected_button = selected
