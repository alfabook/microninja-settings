#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_style.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This page has the screensaver and wallpaper options on different tabs

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation

import os
import shutil

from microninja.utils import run_cmd

from gi.repository import Gtk, Gdk
from microninja_settings.set_wallpaper import SetWallpaper
from microninja_settings.set_screensaver import SetScreensaver
from microninja_settings.system.wallpaper import change_wallpaper


class SetStyle(Gtk.Notebook):

    def __init__(self, win):

        Gtk.Notebook.__init__(self)
        self.connect("switch-page", self._switch_page)
        background = Gtk.EventBox()
        background.get_style_context().add_class('set_style_window')
        background.add(self)

        self.win = win
        self.win.set_main_widget(background)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)
        self.win.set_size_request(350, 350)

        # Modify set_wallpaper so it doesn't add itself to the window
        wallpaper_widget = SetWallpaper(self.win)
        screensaver_widget = SetScreensaver(self.win)
        reset_widget = SetResetDesktop(self.win)

        wallpaper_label = Gtk.Label(_('WALLPAPER'))
        screensaver_label = Gtk.Label(_('SCREENSAVER'))
        general_label = Gtk.Label(_('GENERAL'))
        self.evtBox = []
        self.evtBox.append(wallpaper_label)
        self.evtBox.append(screensaver_label)
        self.evtBox.append(general_label)
        # Add the screensaver and wallpaper tabs
        self.append_page(wallpaper_widget, wallpaper_label)
        self.append_page(screensaver_widget, screensaver_label)
        self.append_page(reset_widget, general_label)

        self.win.show_all()

    def removeLabelCass(self):
        for box in self.evtBox:
            context = box.get_style_context()
            context.remove_class("notebook-label")

    def _switch_page(self, notebook, page, page_num, data=None):
        self.removeLabelCass()
        label = notebook.get_tab_label(notebook.get_nth_page(page_num))
        context = label.get_style_context()
        context.add_class("notebook-label")

from microninja.gtk3.buttons import KanoButton
from microninja.gtk3.microninja_dialog import KanoDialog


class SetResetDesktop(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('set_background_window')
        self.win = win

        reset_button = KanoButton(text=_('RESET YOUR DESKTOP'), color='orange')
        reset_button.connect('button-release-event', self.reset_button_cb)
        reset_button.connect('key-release-event', self.reset_button_cb)
        reset_button.pack_and_align()
        reset_button.align.set(0.5, 0.5, 0, 0)

        self.pack_start(reset_button.align, True, True, 0)

    def reset_button_cb(self, widget, event):

        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            kdialog = KanoDialog(
                title_text=_('This will reset your wallpaper and your toolbar.'),
                description_text=_('Do you want to continue?'),
                button_dict=[
                    {
                        'label': _('YES'),
                        'color': 'green',
                        'return_value': 'yes'
                    },
                    {
                        'label': _('NO'),
                        'color': 'red',
                        'return_value': 'no'
                    }
                ],
                parent_window=self.win
            )

            response = kdialog.run()

            if response == 'yes':
                self.reset_desktop()
                self.win.go_to_home()

    def restore_lxpanel_configuration(self):
        userid = os.getuid()
        groupid = os.getgid()
        original_lxpanel_path = '/etc/skel/.config/lxpanel/'
        user_lxpanel_path = os.path.join('/home/' + os.getenv('SUDO_USER'), '.config/lxpanel')

        # remove the current local copy
        shutil.rmtree(user_lxpanel_path, ignore_errors=True)

        # re-create the copy from the skeleton
        shutil.copytree(original_lxpanel_path, user_lxpanel_path, symlinks=False, ignore=None)
        for root, dirs, files in os.walk(user_lxpanel_path):
            for name in files:
                os.chown(os.path.join(root, name), userid, groupid)

        run_cmd('lxpanelctl restart')

    def restore_wallpaper(self):
        '''Restore the wallpaper to the system default.
        '''

        kdesk_path = "/usr/share/microninja-desktop/kdesk/.kdeskrc"
        identifier = 'Background.File-medium: '

        # We split the default paths into the containing directory of the
        # wallpapers and the name of the file without the size.
        # This is so we can pass these parameters into the change_wallpaper
        # function, so it can decide the appropriate size to set the wallpaper.
        with open(kdesk_path) as f:
            for line in f:
                line = line.strip()

                if line.startswith(identifier):
                    line = line.replace(identifier, '').replace('-1024.png', '')
                    path = '/'.join(line.split('/')[:-1])
                    name = line.split('/')[-1]
                    change_wallpaper(path, name)

                    # finish once we change the wallpaper
                    return

    def reset_desktop(self):
        # Add functionality here
        self.restore_lxpanel_configuration()
        self.restore_wallpaper()
