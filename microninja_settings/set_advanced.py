#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_advance.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation

from gi.repository import Gtk, Gdk
from microninja.gtk3.microninja_dialog import KanoDialog
from microninja.gtk3.buttons import OrangeButton

from microninja import logging
from microninja_settings.templates import Template, LabelledListTemplate
from system.advanced import get_parental_enabled, set_parental_enabled
from parental_config import ParentalConfig


class SetAdvanced(Template):
    def __init__(self, win, noHome=False):

        Template.__init__(
            self,
            _("Advanced options"),
            _("Enable and configure parental control"),
            _("APPLY MODIFIES"),
            win.is_plug(),
            back_btn=False
        )

        parental_box = self.create_parental_button()
        #debug_box = self.create_debug_button()

        self.box.set_spacing(20)
        self.box.pack_start(parental_box, False, False, 0)
        #self.box.pack_start(debug_box, False, False, 0)

        self.win = win
        self.noHome = noHome
        self.win.set_size_request(460, 420)

        #debug_mode = self.get_stored_debug_mode()

        self.parental_button.set_active(get_parental_enabled())
        self.parental_button.connect("clicked", self.go_to_password)
        #self.debug_button.set_active(debug_mode)
        #self.debug_button.connect("clicked", self.on_debug_toggled)

        self.win.set_main_widget(self)

        # Add the callbacks to the top bar and to the extra back button
        if not noHome:
            self.set_prev_callback(self.win.go_to_home)       
            self.win.change_prev_callback(self.win.go_to_home)
            self.win.top_bar.enable_prev()
        else:
            self.win.top_bar.disable_prev()

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)
        self.win.show_all()

    def create_parental_button(self):
        desc = (
            _("Use different configurations to:\n"
            "- Block adult contents in your browser and Youtube\n"
            "- Block internet access")
        ).split('\n')

        self.parental_button = Gtk.CheckButton()
        box = LabelledListTemplate.label_button(
            self.parental_button,
            _("Enable parental control"),
            desc[0])

        grid = Gtk.Grid()
        grid.attach(box, 0, 0, 1, 1)

        i = 1

        for text in desc[1:]:
            label = Gtk.Label(text)
            label.set_alignment(xalign=0, yalign=0.5)
            label.set_padding(xpad=25, ypad=0)
            label.get_style_context().add_class("normal_label")
            grid.attach(label, 0, i, 1, 1)
            i = i + 1

        if get_parental_enabled():
            parental_config_button = OrangeButton(_("Configure"))
            parental_config_button.connect("button-press-event",
                                           self.go_to_parental_config)
            grid.attach(parental_config_button, 0, i, 1, 1)

        return grid

    def go_to_parental_config(self, button=None, event=None):
        self.win.clear_win()
        ParentalConfig(self.win, self.noHome)

    def create_debug_button(self):
        desc = (
            "Difficoltà di configurazione?\n"
            "1) Abilita questa modalità\n"
            "2) Segnala un bug"
        ).split('\n')
        self.debug_button = Gtk.CheckButton()
        box = LabelledListTemplate.label_button(
            self.debug_button,
            "Modalità debug",
            desc[0]
        )

        grid = Gtk.Grid()
        grid.attach(box, 0, 0, 1, 1)

        i = 1

        for text in desc[1:]:
            label = Gtk.Label(text)
            label.set_alignment(xalign=0, yalign=0.5)
            label.set_padding(xpad=25, ypad=0)
            label.get_style_context().add_class("normal_label")
            grid.attach(label, 0, i, 1, 1)
            i = i + 1

        return grid

    def go_to_password(self, event=None):
        self.win.clear_win()
        SetPassword(self.win, self.noHome)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            old_debug_mode = self.get_stored_debug_mode()
            new_debug_mode = self.debug_button.get_active()
            if new_debug_mode == old_debug_mode:
                logging.Logger().debug('skipping debug mode change')
                if not self.noHome:
                    self.win.go_to_home()
                else:
                    Gtk.main_quit()
                return

            if new_debug_mode:
                # set debug on:
                logging.set_system_log_level('debug')
                logging.Logger().info('setting logging to debug')
                msg = _("Enabled")
            else:
                # set debug off:
                logging.set_system_log_level('error')
                logging.Logger().info('setting logging to error')
                msg = _("Disabled")

            kdialog = KanoDialog("Modalità debug", msg, parent_window=self.win)
            kdialog.run()

            self.kano_button.set_sensitive(False)
            if not self.noHome:
                self.win.go_to_home()
            else:
                Gtk.main_quit()

    def on_debug_toggled(self, checkbutton):
        self.kano_button.set_sensitive(True)

    def get_stored_debug_mode(self):
        ll = logging.Logger().get_log_level()
        debug_mode = ll == 'debug'
        logging.Logger().debug('stored debug-mode: {}'.format(debug_mode))
        return debug_mode


class SetPassword(Template):
    def __init__(self, win, noHome=True):

        self.parental_enabled = get_parental_enabled()
        self.noHome = noHome
        win.set_size_request(460, 420)

        # Entry container
        entry_container = Gtk.Grid(column_homogeneous=False,
                                   column_spacing=22,
                                   row_spacing=10)

        # if enabled, turning off
        if self.parental_enabled:
            Template.__init__(
                self,
                _("Disable parental control"),
                _("Insert your password"),
                _("UNBLOCK"),
                win.is_plug(),
                True
            )
            self.entry = Gtk.Entry()
            self.entry.set_size_request(300, 44)
            self.entry.props.placeholder_text = _("Insert your password")
            self.entry.set_visibility(False)
            self.entry.connect("key_release_event", self.enable_button)
            entry_container.attach(self.entry, 0, 0, 1, 1)

        # if disabled, turning on
        else:
            Template.__init__(
                self,
                _("Configure parental control"),
                _("Choose a password"),
                _("BLOCK"),
                win.is_plug()
            )

            self.entry1 = Gtk.Entry()
            self.entry1.set_size_request(300, 44)
            self.entry1.props.placeholder_text = _("Select password")
            self.entry1.set_visibility(False)

            self.entry2 = Gtk.Entry()
            self.entry2.props.placeholder_text = _("Confirm password")
            self.entry2.set_visibility(False)

            self.entry1.connect("key_release_event", self.enable_button)
            self.entry2.connect("key_release_event", self.enable_button)

            entry_container.attach(self.entry1, 0, 0, 1, 1)
            entry_container.attach(self.entry2, 0, 1, 1, 1)

        self.win = win
        self.win.set_main_widget(self)
        self.set_prev_callback(self.go_to_advanced)
        self.win.change_prev_callback(self.go_to_advanced)
        self.win.top_bar.enable_prev()

        self.kano_button.set_sensitive(False)

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)

        self.box.add(entry_container)
        self.win.show_all()

    def go_to_advanced(self, widget=None, event=None):
        self.win.clear_win()
        SetAdvanced(self.win, self.noHome)

    def go_to_parental_config(self, button=None, event=None):
        self.win.clear_win()
        ParentalConfig(self.win, self.noHome)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # Disable buttons and entry fields during validation
            # we save the current parental state now because it will flip
            # during this function
            is_locked = self.parental_enabled
            if is_locked:
                self.entry.set_sensitive(False)
                button.set_sensitive(False)
            else:
                self.entry1.set_sensitive(False)
                self.entry2.set_sensitive(False)
                button.set_sensitive(False)

            if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

                password = None

                # if disabled, turning on
                if not self.parental_enabled:
                    password = self.entry1.get_text()
                    password2 = self.entry2.get_text()
                    passed_test = (password == password2)

                # if enabled, turning off
                else:
                    password = self.entry.get_text()
                    passed_test = True

                # if test passed, update parental configuration
                if passed_test:
                    self.update_config(password)

                # else, display try again dialog
                else:
                    do_try_again = self.create_dialog(
                        _("Warning"),
                        _("Inserted passwords do not match. Try again")
                    )
                    if do_try_again:
                        if not self.parental_enabled:
                            self.entry1.set_text("")
                            self.entry2.set_text("")
                        else:
                            self.entry.set_text("")
                    else:
                        self.go_to_advanced()

            # Restore the UI controls (re-enable input focus)
            if is_locked:
                self.entry.set_sensitive(True)
                button.set_sensitive(True)
            else:
                self.entry1.set_sensitive(True)
                self.entry2.set_sensitive(True)

                # For new password input dialog (2 entry fields) the lock button
                # will be enabled only after the user enters text
                # in both password fields (self.enable_button)
                button.set_sensitive(False)

    def create_dialog(self, message1, message2):
        kdialog = KanoDialog(
            message1,
            message2,
            [
                {
                    'label': _("GO BACK"),
                    'color': 'red',
                    'return_value': False
                },
                {
                    'label': _("TRY AGAIN"),
                    'color': 'green',
                    'return_value': True
                }
            ],
            parent_window=self.win
        )

        response = kdialog.run()
        return response

    def enable_button(self, widget, event):
        # if disabled, turning on
        if not self.parental_enabled:
            text1 = self.entry1.get_text()
            text2 = self.entry2.get_text()
            self.kano_button.set_sensitive(text1 != "" and text2 != "")

        # if enabled, turning off
        else:
            text = self.entry.get_text()
            self.kano_button.set_sensitive(text != "")

    def update_config(self, password):
        if self.parental_enabled:
            success, msg = set_parental_enabled(False, password)
            self.parental_enabled = get_parental_enabled()

        else:
            success, msg = set_parental_enabled(True, password)
            self.parental_enabled = get_parental_enabled()

        if success:
            heading = _("Success")
        else:
            heading = _("Error")

        kdialog = KanoDialog(heading, msg, parent_window=self.win)
        kdialog.run()

        # If the user has just turned the parental control on, take them to
        # the config screen.
        if self.parental_enabled:
            self.go_to_parental_config()
        else:
            self.go_to_advanced()
