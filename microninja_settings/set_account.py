#!/usr/bin/env python
# -*- coding: utf-8 -*-
# account.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Controls the UI of the account setting

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation 

from gi.repository import Gtk, Gdk, GObject
import threading
import os

from microninja_settings.components.heading import Heading
import microninja.gtk3.microninja_dialog as kano_dialog
from microninja.gtk3.buttons import KanoButton
from microninja.gtk3.labelled_entries import LabelledEntries

from microninja.utils import ensure_dir
import microninja_settings.common as common
from microninja_settings.templates import Template

from microninja_settings.system.account import add_user, delete_user,delete_users, \
    verify_current_password, change_password, UserError


class SetAccount(Gtk.Box):
    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = win
        self.win.set_main_widget(self)
        self.win.set_size_request(350, 150)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.added_or_removed_account = False

        main_heading = Heading(
            "Impostazioni utenti di sistema",
            "Imposta il tuo utente"
        )
        

        self.pass_button = KanoButton("CAMBIA PASSWORD")
        self.pass_button.pack_and_align()
        self.pass_button.set_size_request(350, 44)
        self.pass_button.connect("button-release-event", self.go_to_password_screen)
        self.pass_button.connect("key-release-event", self.go_to_password_screen)

        self.add_button = KanoButton("AGGIUNGI UTENTE")
        self.add_button.set_size_request(350, 44)
        self.add_button.connect("button-release-event", self.add_account)
        self.add_button.connect("key-release-event", self.add_account)

        self.remove_button = KanoButton("RIMUOVI UTENTE DAL SISTEMA", color="red")
        self.remove_button.set_size_request(350, 44)
        self.remove_button.connect("button-release-event", self.remove_account_dialog)
        self.remove_button.connect("key-release-event", self.remove_account_dialog)


        self.reset_button = KanoButton(_("RESET TO FACTORY SETTINGS"), color="red")
        self.reset_button.set_size_request(350, 44)
        self.reset_button.connect("button-release-event", self.reset_dialog)
        self.reset_button.connect("key-release-event", self.reset_dialog)

        self.bottomPaddingBox = Gtk.Box()
        self.bottomPaddingBox.set_size_request(-1, 5)
        button_container = Gtk.VBox()
        #button_container.pack_start(self.add_button, False, False, 10)
        #button_container.pack_start(self.remove_button, False, False, 10)
        button_container.pack_start(self.reset_button, False, False, 10)
        button_container.pack_start(self.bottomPaddingBox, False, False, 10)

        button_align = Gtk.Alignment(xscale=0, xalign=0.5)
        button_align.set_padding(0, 0, 25, 25)
        button_align.add(button_container)
        accounts_heading = Heading(
            _("Factory settings"),
            _("Reset system to factory settings")
        )

        # Check if we already scheduled an account add or remove
        # We import kano-init locally to avoid circular dependency
        # the packages.
	#try:
        #    from kano_init.utils import is_any_task_scheduled
        #    if is_any_task_scheduled():
        #        self.disable_buttons()
        #except ImportError:
        #    self.disable_buttons()

        #self.pack_start(main_heading.container, False, False, 0)
        #self.pack_start(self.pass_button.align, False, False, 0)
        self.pack_start(accounts_heading.container, False, False, 0)
        self.pack_start(button_align, False, False, 0)

        self.win.show_all()

    def go_to_password_screen(self, widget, event):

        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            self.win.clear_win()
            SetPassword(self.win)

    # Gets executed when ADD button is clicked
    def add_account(self, widget=None, event=None):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            from microninja_greeter.newUserGui import NewUserGui
            dialog = NewUserGui(self.win,"privato")
            response = dialog.run()



    def refreshUserList():
        pass

    # Gets executed when REMOVE button is clicked
    def remove_account_dialog(self, widget=None, event=None):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            # Bring in message dialog box
            kdialog = kano_dialog.KanoDialog(
                "Sei sicuro di voler rimuovere l'utente corrente da questo sistema?",
                "Perderai tutti i locali ma potrai riconnetterti "
                "con le stesse credenziali quando desideri.",
                [
                    {
                        'label': "ANNULLA",
                        'color': 'red',
                        'return_value': False
                    },
                    {
                        'label': "OK",
                        'color': 'green',
                        'return_value': True
                    }
                ],
                parent_window=self.win
            )
            do_delete_user = kdialog.run()
            if do_delete_user:
                try:
                    delete_user()
                except UserError as e:
                    kdialog = kano_dialog.KanoDialog(
                        "Errore eliminando l'utente",
                        str(e),
                        parent_window=self.win
                    )
                    return

    def reset_dialog(self, widget=None, event=None):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            # Bring in message dialog box
            kdialog = kano_dialog.KanoDialog(
                    _("Are you sure do you want to restore the system?"),
                    _("Warning: this operation will erase all data and documents.\nSeveral minutes may be required."),
                    [
                        {
                            'label': _("CANCEL"),
                            'color': 'red',
                            'return_value': False
                        },
                        {
                            'label': "OK",
                            'color': 'green',
                            'return_value': True
                        }
                    ],
                    parent_window=self.win
            )
            do_delete_users = kdialog.run()
            if do_delete_users:
                try:
                    delete_users()
                except UserError as e:
                    kdialog = kano_dialog.KanoDialog(
                            "Errore eliminando l'utente",
                            str(e),
                            parent_window=self.win
                    )
                    return


    # Disables both buttons and makes the temp 'flag' folder
    def disable_buttons(self):

        self.add_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.added_or_removed_account = True


class SetPassword(Template):
    def __init__(self, win):
        Template.__init__(
            self,
            "Modifica la tua password",
            "",
            "MODIFICA PASSWORD"
        )

        self.labelled_entries = LabelledEntries(
            [{"heading": "Password corrente", "subheading": ""},
             {"heading": "Nuova password", "subheading": ""},
             {"heading": "Ripeti password", "subheading": ""}]
        )

        self.entry1 = self.labelled_entries.get_entry(0)
        self.entry1.set_size_request(300, 44)
        self.entry1.set_visibility(False)
        self.entry1.props.placeholder_text = "Vecchia password"

        self.entry2 = self.labelled_entries.get_entry(1)
        self.entry2.set_size_request(300, 44)
        self.entry2.set_visibility(False)
        self.entry2.props.placeholder_text = "Nuova password"

        self.entry3 = self.labelled_entries.get_entry(2)
        self.entry3.set_size_request(300, 44)
        self.entry3.set_visibility(False)
        self.entry3.props.placeholder_text = "Ripeti nuova password"

        self.entry1.connect("key_release_event", self.enable_button)
        self.entry2.connect("key_release_event", self.enable_button)
        self.entry3.connect("key_release_event", self.enable_button)

        self.entry1.grab_focus()

        self.win = win
        self.win.set_main_widget(self)

        self.box.pack_start(self.labelled_entries, False, False, 0)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.go_to_accounts)

        self.kano_button.set_sensitive(False)
        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)

        self.win.show_all()

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # This is a callback called by the main loop, so it's safe to
            # manipulate GTK objects:
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self.win.get_window().set_cursor(watch_cursor)
            self.kano_button.start_spinner()
            self.kano_button.set_sensitive(False)

            def lengthy_process():
                old_password = self.entry1.get_text()
                new_password1 = self.entry2.get_text()
                new_password2 = self.entry3.get_text()

                success = False
                password_verified = verify_current_password(old_password)

                if not password_verified:
                    title = "Non posso modificare la password"
                    description = "La tua vecchia password è sbagliata!"
                elif new_password1 == new_password2:
                    from microninja_profile.profile import apiProfile
                    profile = apiProfile()
                    if profile.changePassword(new_password1) :
                        title, description, success = self.try_change_password(new_password1)
                    else :
                        title, description = ("Errore", profile.getError())
                else:
                    title = "Non posso modificare la password"
                    description = "Le password inserite non corrispondono! Prova ancora."

                def done(title, description, success):
                    if success:
                        create_success_dialog(title, description, self.win)
                        do_try_again = False
                    else:
                        do_try_again = create_error_dialog(title, description, self.win)

                    self.win.get_window().set_cursor(None)
                    self.kano_button.stop_spinner()
                    self.clear_text()

                    if not do_try_again:
                        self.go_to_accounts()

                GObject.idle_add(done, title, description, success)

            thread = threading.Thread(target=lengthy_process)
            thread.start()

    # Returns a title, description and whether the process was successful or not
    def try_change_password(self, new_password):
        success = False

        cmdvalue = change_password(new_password)

        # if password is not changed
        if cmdvalue != 0:
            title = "Non posso cambiare la password"
            description = "La password non è sufficientemente lunga e deve contenere caratteri speciali."
        else:
            title = "Password cambiata!"
            description = ""
            success = True

        return (title, description, success)

    def go_to_accounts(self, widget=None, event=None):
        self.win.clear_win()
        SetAccount(self.win)

    def clear_text(self):
        self.entry1.set_text("")
        self.entry2.set_text("")
        self.entry3.set_text("")
        self.entry1.grab_focus()

    def enable_button(self, widget, event):
        text1 = self.entry1.get_text()
        text2 = self.entry2.get_text()
        text3 = self.entry3.get_text()
        self.kano_button.set_sensitive(text1 != "" and text2 != "" and text3 != "")


def create_error_dialog(message1="Could not change password", message2="", win=None):
    kdialog = kano_dialog.KanoDialog(
        message1,
        message2,
        [
            {
                'label': "Indietro",
                'color': 'red',
                'return_value': False
            },
            {
                'label': "Riprova",
                'color': 'green',
                'return_value': True
            }
        ],
        parent_window=win
    )

    response = kdialog.run()
    return response


def create_success_dialog(message1, message2, win):
    kdialog = kano_dialog.KanoDialog(
        message1,
        message2,
        parent_window=win
    )
    response = kdialog.run()
    return response
