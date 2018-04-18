#!/usr/bin/env python

# kano_dialog.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Heading used frequently around kano-settings and kano-login

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja

from gi.repository import Gtk
import os
from microninja.gtk3.icons import set_from_name
from microninja.gtk3.apply_styles import apply_styling_to_screen
from microninja.gtk3.cursor import attach_cursor_events
from microninja_settings.common import css_dir


class Heading():
    def __init__(self, title, description, is_plug=False, back_btn=False):
        self.back_button = None
        css_path = os.path.join(css_dir, "heading.css")
        apply_styling_to_screen(css_path)
        title_hbox = None

        if is_plug:
            title_hbox = Gtk.Box()
            close_button = Gtk.Button()
            close_button.set_image(set_from_name("cross"))
            close_button.get_style_context().add_class("back_button")
            close_button.connect("clicked", Gtk.main_quit)
            close_button.set_margin_top(15)
            attach_cursor_events(close_button)
            title_hbox.pack_end(close_button, True, True, 0)

            if back_btn:
                self.back_button = Gtk.Button()
                attach_cursor_events(self.back_button)
                self.back_button.get_style_context().add_class("back_button")
                # TODO: get better back icon
                self.back_button.set_image(set_from_name("dark_left_arrow"))
                self.back_button.set_margin_top(15)
                title_hbox.pack_start(self.back_button, True, False, 0)

            else:
                empty_button = Gtk.Button(" ")
                empty_button.get_style_context().add_class("transparent")
                title_hbox.pack_start(empty_button, True, True, 0)

        self.title = Gtk.Label(title)
        self.title.get_style_context().add_class('title')
        self.title.set_justify(Gtk.Justification.CENTER)
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                 spacing=10)

        if is_plug:
            title_hbox.pack_start(self.title, True, True, 0)
            self.container.pack_start(title_hbox, False, False, 0)
        else:
            self.container.pack_start(self.title, False, False, 0)

        if description != "":
            self.description = Gtk.Label(description)
            self.description.set_justify(Gtk.Justification.CENTER)
            self.description.set_line_wrap(True)
            self.description_style = self.description.get_style_context()
            self.description_style.add_class('description')

            self.container.pack_start(self.description, False, False, 0)

    def set_text(self, title, description):
        self.title.set_text(title)
        if getattr(self, 'description'):
            self.description.set_text(description)

    def get_text(self):
        if getattr(self, 'description'):
            return [self.title.get_text(), self.description.get_text()]
        else:
            return [self.title.get_text(), ""]

    def set_margin(self, top_margin, right_margin, bottom_margin, left_margin):
        self.container.set_margin_left(left_margin)
        self.container.set_margin_right(right_margin)
        self.container.set_margin_top(top_margin)
        self.container.set_margin_bottom(bottom_margin)

    def add_plug_styling(self):
        self.title.get_style_context().add_class("plug")
        self.description.get_style_context().add_class("plug")

    def set_prev_callback(self, cb):
        if self.back_button:
            self.back_button.connect("clicked", cb)
