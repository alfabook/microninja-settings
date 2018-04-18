#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation
# changing legal dir from profile to settings

import os
import sys
import subprocess
from gi.repository import Gtk
from microninja.gtk3.microninja_dialog import KanoDialog
from microninja.gtk3.buttons import OrangeButton, KanoButton
from microninja_settings.paths import legal_dir
from microninja_settings.common import media
from microninja.network import launch_browser
from microninja_settings.system.about import (
    get_current_version, get_space_available, get_temperature, get_model_name
)
from microninja.utils import get_user_unsudoed


class SetAbout(Gtk.Box):
    selected_button = 0
    initial_button = 0

    def __init__(self, win):
        reload(sys)
        sys.setdefaultencoding('utf8')
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)
        self.win.set_size_request(350, 350)

        image = Gtk.Image.new_from_file(media + "/Graphics/about-screen.png")

        version_align = self.create_align(
            "Microninja OS v.{version}".format(version=get_current_version()),
            'about_version'
        )
        space_align = self.create_align(
            _("Used disk space:") + " {used}B / {total}B".format(**get_space_available())
        )
        try:
            celsius = u"{:.1f}\N{DEGREE SIGN}C".format(get_temperature())
        except ValueError:
            celsius = "?"
        temperature_align = self.create_align(
            _("Temperature:") + " {celsius}".format(celsius=celsius)
        )
        model_align = self.create_align(
            _("Model:") + " {model}".format(model=get_model_name())
        )

        terms_and_conditions = OrangeButton(_("Terms and conditions"))
        terms_and_conditions.connect(
            "button_release_event", self.show_terms_and_conditions
        )

        #credits_button = OrangeButton("Meet the team")
        #credits_button.connect(
        #    "button_release_event", self.show_credits
        #)

        #changelog_button = OrangeButton("Changelog")
        #changelog_button.connect(
        #    "button_release_event", self.show_changelog
        #)

        self.kano_button = KanoButton(_("BACK"))
        self.kano_button.pack_and_align()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.pack_start(terms_and_conditions, False, False, 4)
        #hbox.pack_start(credits_button, False, False, 4)
        #hbox.pack_start(changelog_button, False, False, 4)
        hbutton_container = Gtk.Alignment(
            xalign=0.5, xscale=0, yalign=0, yscale=0
        )
        hbutton_container.add(hbox)

        image.set_margin_top(10)
        self.pack_start(image, False, False, 10)
        self.pack_start(version_align, False, False, 2)
        self.pack_start(space_align, False, False, 1)
        self.pack_start(temperature_align, False, False, 1)
        self.pack_start(model_align, False, False, 1)
        self.pack_start(hbutton_container, False, False, 3)
        self.pack_start(self.kano_button.align, False, False, 10)

        self.kano_button.connect("button-release-event", self.win.go_to_home)
        self.kano_button.connect("key-release-event", self.win.go_to_home)

        # Refresh window
        self.win.show_all()

    def create_align(self, text, css_class='about_label'):
        '''This styles the status information in the 'about' dialog
        '''

        label = Gtk.Label(text)
        label.get_style_context().add_class(css_class)

        align = Gtk.Alignment(xalign=0.5, xscale=0, yalign=0, yscale=0)
        align.add(label)

        return align

    def show_terms_and_conditions(self, widget, event):
        '''This is the dialog containing the terms and conditions - same as
        shown before creating an account
        '''

        legal_text = ''
        for file in os.listdir(legal_dir):
            with open(legal_dir + file, 'r') as f:
                legal_text = legal_text + f.read() + '\n\n\n'

        kdialog = KanoDialog(_("Terms and conditions"), "",
                             scrolled_text=legal_text,
                             parent_window=self.win)
        kdialog.run()

    #~ def show_credits(self, widget, event):
        #~ '''Launch the credits
        #~ '''
#~ 
        #~ os.system(
            #~ "/usr/bin/microninja-launcher \"kdesk-blur 'urxvt -bg "
            #~ "rgba:0000/0000/0000/FFFF -title 'Credits' -e "
            #~ "/usr/bin/microninja-credits'\""
        #~ )
#~ 
    #~ def show_changelog(self, widget, event):
        #~ '''Launch chromium with the link of the relevent changelog
        #~ '''
#~ 
        #~ # Assuming current_version is of the form 1.3.4
        #~ current_version = get_current_version()
#~ 
        #~ # Full link should be analogous to
        #~ # http://world.kano.me/forum/topic/kanux-beta-v1.2.3
        #~ link = "http://world.kano.me/forum/topic/kanux-beta-v{}".format(
            #~ current_version
        #~ )
#~ 
        #~ launch_browser(link)
        #~ return
