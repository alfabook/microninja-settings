#!/usr/bin/env python

# SpinnerScreen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Show the spinner screen and run a background process

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja

import os
import threading
from gi.repository import Gtk, GdkPixbuf

from microninja_settings.components.heading import Heading
from microninja_wifi_gui.paths import media_dir


class SpinnerScreen(Gtk.Box):

    # wiface is only here to pass onto the ConnectWifi screen
    def __init__(self, win, title, description,
                 background_cb):

        self._win = win
        self._win.top_bar.disable_prev()
        self._wiface = self._win.wiface
        self._title = title
        self._description = description
        self._background_cb = background_cb

        self._win.remove_main_widget()

        self.show_spinner_screen()
        self.run_background_process()

    def show_spinner_screen(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_size_request(self._win.width, self._win.height)

        self._win.set_main_widget(self)

        heading = Heading(
            self._title,
            self._description,
            self._win.is_plug()
        )
        self.pack_start(heading.container, False, False, 0)

        spinner = Gtk.Image()

        if self._win.is_plug():
            filename = os.path.join(media_dir, "microninja-wifi-gui/loading_bar.gif")
        else:
            filename = os.path.join(media_dir, "microninja-wifi-gui/wifi-spinner-smaller.gif")

        anim = GdkPixbuf.PixbufAnimation.new_from_file(filename)
        spinner.set_from_animation(anim)

        if self._win.is_plug():
            # Added extra padding for the plug screen.
            self.pack_start(spinner, False, False, 60)
        else:
            self.pack_start(spinner, False, False, 30)

        self._win.show_all()

    def run_background_process(self):
        t = threading.Thread(target=self._background_cb)
        t.start()
