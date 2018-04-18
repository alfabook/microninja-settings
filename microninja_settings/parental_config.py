#!/usr/bin/env python
# -*- coding: utf-8 -*-
# parental_config.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation
# track data removed


from urlparse import urlparse

from gi.repository import Gtk

from microninja_settings import common
from microninja_settings.templates import Template, EditableList
from microninja.gtk3.buttons import OrangeButton
from microninja.gtk3.microninja_dialog import KanoDialog
#from microninja_profile.tracker import track_data

from microninja_settings.config_file import get_setting, set_setting
from system.advanced import write_whitelisted_sites, write_blacklisted_sites, \
    read_listed_sites, set_parental_level, authenticate_parental_password


class ParentalConfig(Template):
    def __init__(self, win, noHome=False):
        Template.__init__(
            self,
            _("Parental control"),
            _("Choose your preferred protection level"),
            _("APPLY MODIFIES"),
            win.is_plug(),
            True
        )

        win.set_size_request(500, -1)
        self.parental_level = Gtk.VScale(
            adjustment=Gtk.Adjustment(value=0, lower=0, upper=3,
                                      step_incr=1, page_incr=0, page_size=0))
        self.parental_level.get_style_context().add_class('parental_slider')
        self.parental_level.set_draw_value(False)
        self.parental_level.set_round_digits(0)
        self.parental_level.set_inverted(True)
        #if get_setting('Parental-level') ==0:
        #    self.parental_level.set_value(1)
        #else:
        self.parental_level.set_value(get_setting('Parental-level'))
        self.parental_level.connect('value-changed', self._value_change_handler)

        self._parental_labels = [
            (
                Gtk.Label(_("Low protection")),
                Gtk.Label(_("Block the websites defined in the backlist"))
            ),
            (
                Gtk.Label(_("Medium protection")),
                Gtk.Label(_("Use secure DNS to filter traffic"))
            ),
            (
                Gtk.Label(_("High protection")),
                Gtk.Label(_("Enable all filters and restrict search engines usage"))
            ),
            (
                Gtk.Label(_("Full protection")),
                Gtk.Label(_("Block all accesses"))
            )
        ]

        self.blacklist_button = OrangeButton(_("Configure allowed/blocked websites"))
        self.blacklist_button.connect("button-press-event",
                                      self.go_to_blacklist)

        self._value_change_handler(self.parental_level)

        #self._parental_labels[0][0].set_tooltip_markup("Il sistema operativo verifica se il sito che si tenta di raggiungere è presente in una lista di siti (cosiddetta Blacklist) dai contenuti non adatti a minorenni (circa 11.000 siti). Questa lista può essere personalizzata, aggiungendo siti specifici alla Blacklist o inserendo siti che invece si desidera che siano raggiungibili (secondo un principio di Whitelist).")
        #self._parental_labels[0][1].set_tooltip_markup("Il sistema operativo verifica se il sito che si tenta di raggiungere è presente in una lista di siti (cosiddetta Blacklist) dai contenuti non adatti a minorenni (circa 11.000 siti). Questa lista può essere personalizzata, aggiungendo siti specifici alla Blacklist o inserendo siti che invece si desidera che siano raggiungibili (secondo un principio di Whitelist).")
        #self._parental_labels[1][0].set_tooltip_markup("Attraverso questo livello di protezione, raccomandato di default, Microninja verifica se il dominio che si tenta di raggiungere è classificato come inappropriato per le famiglie nell’ambito educativo.")
        #self._parental_labels[1][1].set_tooltip_markup("Attraverso questo livello di protezione, raccomandato di default, Microninja verifica se il dominio che si tenta di raggiungere è classificato come inappropriato per le famiglie nell’ambito educativo.")
        #self._parental_labels[2][0].set_tooltip_markup("Questo livello, oltre ad attivare tutti i filtri precedenti, impedisce l’accesso ai principali motori di ricerca, in modo che non sia possibile effettuare ricerche inappropriate, anche senza configurare nell’account dell’utente servizi di controllo del contenuto (per esempio, SafeSearch in Google).")
        #self._parental_labels[2][1].set_tooltip_markup("Questo livello, oltre ad attivare tutti i filtri precedenti, impedisce l’accesso ai principali motori di ricerca, in modo che non sia possibile effettuare ricerche inappropriate, anche senza configurare nell’account dell’utente servizi di controllo del contenuto (per esempio, SafeSearch in Google).")
        #self._parental_labels[3][0].set_tooltip_markup("Impostando questo livello, la navigazione web viene bloccata dal sistema operativo: non sarà possibile accedere a nessun sito.")
        #self._parental_labels[3][1].set_tooltip_markup("Impostando questo livello, la navigazione web viene bloccata dal sistema operativo: non sarà possibile accedere a nessun sito.")
        parental_level_grid = Gtk.Grid()
        parental_level_grid.attach(self.parental_level, 0, 0, 1, 7)
        parental_level_grid.attach(self._parental_labels[3][0], 1, 0, 1, 1)
        parental_level_grid.attach(self._parental_labels[3][1], 1, 1, 1, 1)
        parental_level_grid.attach(self._parental_labels[2][0], 1, 2, 1, 1)
        parental_level_grid.attach(self._parental_labels[2][1], 1, 3, 1, 1)
        parental_level_grid.attach(self._parental_labels[1][0], 1, 4, 1, 1)
        parental_level_grid.attach(self._parental_labels[1][1], 1, 5, 1, 1)
        parental_level_grid.attach(self._parental_labels[0][0], 1, 6, 1, 1)
        parental_level_grid.attach(self._parental_labels[0][1], 1, 7, 1, 1)

        self.box.set_spacing(20)
        self.box.pack_start(parental_level_grid, False, False, 0)
        self.box.pack_start(self.blacklist_button, False, False, 0)

        self.win = win
        self.noHome = noHome
        self.win.set_main_widget(self)

        if not noHome:
            self.set_prev_callback(self.go_to_advanced)
            self.win.change_prev_callback(self.win.go_to_home)
            self.win.top_bar.enable_prev()
        else:
            self.win.top_bar.disable_prev()

        self.kano_button.connect('button-release-event', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)
        self.win.show_all()

    def go_to_advanced(self, widget):
        from microninja_settings.set_advanced import SetAdvanced

        self.win.clear_win()
        SetAdvanced(self.win, self.noHome)

    def apply_changes(self, button, event):
        pw_dialog = ParentalPasswordDialog(self.win)
        if not pw_dialog.verify():
            return

        level = self.parental_level.get_value()
        set_parental_level(level)
        set_setting('Parental-level', level)

        # track which parental control level people use
        #track_data("parental-control-level-changed", {
        #    "level": level
        #})

        if level == 3.0:
            # If on the highest parental control, prompt user to relaunch
            # the browser
            kdialog = KanoDialog(
                title_text=_('Settings'),
                description_text=(_("If there is a browser opened, please restart it "
                                  "for this setting to take effect")),
                parent_window=self.win
            )
            kdialog.run()

        else:
            # Only reboot for the lower parental controls
            common.need_reboot = True

        if not self.noHome:
            self.win.go_to_home()
        else:
            Gtk.main_quit()

    def go_to_blacklist(self, button, event):
        self.win.clear_win()
        AllowedSites(self.win)

    def _value_change_handler(self, gtk_range):
        for level, (title, desc) in enumerate(self._parental_labels):
            style_title = title.get_style_context()
            style_desc = desc.get_style_context()
            if gtk_range.get_value() == level:
                style_title.add_class('parental_activated')
                style_desc.add_class('parental_desc_activated')
                self.blacklist_button.set_sensitive(not level == 3.0)
            else:
                style_title.remove_class('parental_activated')
                style_title.add_class('normal_label')
                style_desc.remove_class('parental_desc_activated')
                style_desc.add_class('normal_label')


class SiteList(EditableList):

    def __init__(self, size_x=250, size_y=25):
        EditableList.__init__(self, size_x=size_x, size_y=size_y)

    @staticmethod
    def _sanitise_site(url):
        parse = urlparse(url)

        # enforcing some standards (e.g. http://)
        if parse.scheme == '' or parse.netloc == '':
            return None

        # removing the leading 'www.'
        netloc = parse.netloc
        if netloc.startswith('www.'):
            netloc = netloc.split('.', 1)[1]

        return netloc.lower()

    def _item_edited_handler(self, cellrenderertext, path, new_text):
        site = self._sanitise_site(new_text)
        EditableList._item_edited_handler(self, cellrenderertext, path, site)


class AllowedSites(Template):
    def __init__(self, win):
        Template.__init__(
            self,
            _("Allow and block websites"),
            _("Add other websites to allow or block"),
            _("APPLY MODIFIES"),
            win.is_plug(),
            True
        )

        self.win = win

        self.win.set_size_request(700, -1)
        blacklist, whitelist = read_listed_sites()

        self.blacklist = SiteList(size_x=250, size_y=25)
        self.whitelist = SiteList(size_x=250, size_y=25)

        if whitelist:
            for site in whitelist:
                self.whitelist.edit_list_store.append([site])

        if blacklist:
            for site in blacklist:
                self.blacklist.edit_list_store.append([site])

        grid = Gtk.Grid()
        grid.set_column_spacing(40)

        add_label = Gtk.Label(_("Add other websites to block"))
        add_label.get_style_context().add_class('normal_label')
        grid.attach(add_label, 0, 0, 1, 1)
        grid.attach(self.blacklist, 0, 1, 1, 1)

        remove_label = Gtk.Label(_("Some blocked sites that should not be?"))
        remove_label.get_style_context().add_class('normal_label')
        grid.attach(remove_label, 1, 0, 1, 1)
        grid.attach(self.whitelist, 1, 1, 1, 1)

        self.box.pack_start(grid, False, False, 0)
        self.box.pack_start(Gtk.Label(''), False, False, 0)

        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.go_to_parental_config)
        self.set_prev_callback(self.go_to_parental_config)

        self.kano_button.connect('button-release-event', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)
        self.win.show_all()

        self.win.show_all()

    def apply_changes(self, button, event):
        pw_dialog = ParentalPasswordDialog(self.win)
        if not pw_dialog.verify():
            return

        whitelist = [row[0] for row in self.whitelist.edit_list_store]
        blacklist = [row[0] for row in self.blacklist.edit_list_store]

        write_whitelisted_sites(whitelist)
        write_blacklisted_sites(blacklist)

        level = get_setting('Parental-level')
        set_parental_level(level)
        common.need_reboot = True

        # track which parental control level people use
        #track_data("parental-control-level-changed", {
        #    "level": level
        #})

        self.win.go_to_home()

    def go_to_parental_config(self, button=None, event=None):
        self.win.clear_win()
        ParentalConfig(self.win)


class ParentalPasswordDialog(KanoDialog):

    def __init__(self, win):
        entry = Gtk.Entry()
        entry.set_visibility(False)
        self.win = win
        KanoDialog.__init__(
            self,
            title_text=_('Parental control'),
            description_text=_('Insert password:'),
            widget=entry,
            has_entry=True,
            global_style=True,
            parent_window=self.win
        )

    def verify(self):
        pw = self.run()

        if authenticate_parental_password(pw):
            return True

        fail = KanoDialog(
            title_text=_('Retry?'),
            description_text=_('Wrong password. Cannot apply modifies'),
            parent_window=self.win
        )
        fail.run()

        return False
