# locale.py
# -*- coding: utf-8 -*-
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja

import os
from gi.repository import Gtk
from microninja.gtk3.microninja_combobox import KanoComboBox
from microninja.utils import get_home_by_username, get_user_unsudoed

import microninja_settings.common as common
from microninja_settings.templates import Template
from microninja_settings.system.locale import set_locale, get_locale, \
    strip_encoding_from_locale
from microninja_settings.system.supported_locales import Locales, SUPPORTED_LOCALES
from microninja_settings.config_file import get_setting, set_setting


class LocaleConfig(Template):

    def __init__(self, win):
        Template.__init__(
            self,
            _('Language setting'),
            _('Choose system language (A reboot is needed)'),
            _('APPLY CHANGES')
        )

        dropdown_container = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=20
        )
        self.box.pack_start(dropdown_container, False, False, 0)

        self._language_combo = self._create_language_combo()
        dropdown_container.pack_start(self._language_combo, False, False, 0)

        self._region_combo = self._create_region_combo()
        dropdown_container.pack_start(self._region_combo, False, False, 0)

        self._load_saved_settings()

        self.win = win
        self.win.set_main_widget(self)
        self.win.set_size_request(420, 350)

        self.win.change_prev_callback(self.win.go_to_home)
        self.win.top_bar.enable_prev()

        self.kano_button.connect('clicked', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)
        self.win.show_all()

    def _create_language_combo(self):
        language_combo = KanoComboBox(max_display_items=7)
        language_combo.connect('changed', self._on_language_changed)

        language_combo.set_items(SUPPORTED_LOCALES.list_languages())

        return language_combo

    def _on_language_changed(self, combo):
        self._region_combo.remove_all()

        lang = self._language_combo.get_selected_item_text()
        self._region_combo.set_items(SUPPORTED_LOCALES.list_regions(lang=lang))

        self._region_combo.set_selected_item_index(0)

        self.kano_button.set_sensitive(True)

    def _create_region_combo(self):
        region_combo = KanoComboBox(max_display_items=7)
        region_combo.connect('changed', self._on_region_changed)

        return region_combo

    def _on_region_changed(self, combo):
        self.kano_button.set_sensitive(True)

    def _load_saved_settings(self):
        locale_setting = strip_encoding_from_locale(get_locale())
        locale_setting = get_setting('Locale')
        lang_code, region_code = Locales.get_codes_from_locale_code(
            locale_setting)

        lang = Locales.lang_code_to_lang(lang_code)
        region = Locales.region_code_to_region(region_code)

        selected_index = self._language_combo.get_items().index(lang)
        self._language_combo.set_selected_item_index(selected_index)

        self._on_language_changed(self._language_combo)

        selected_index = self._region_combo.get_items().index(region)
        self._region_combo.set_selected_item_index(selected_index)

    def apply_changes(self, button):
        language = self._language_combo.get_selected_item_text()
        region = self._region_combo.get_selected_item_text()

        locale_code = Locales.get_locale_code_from_langs(language, region)
        set_locale(locale_code)
        set_setting('Locale', locale_code)

        #installing lxpanel config translation
        lang = locale_code[:2]
        cmd = "cp /usr/share/locale/microninja/lxpanel/" + lang + "/panel " + os.path.join(get_home_by_username(get_user_unsudoed()),
                                '.config/lxpanel/LXDE/panels/panel')
        os.system(cmd)

        '''
        #setting throught system commands
        #cmd = "sudo locale-gen " + locale_code
        #os.system(cmd)

        #cmd = "sudo locale-gen " + locale_code + ".UTF8"
        #os.system(cmd)

        cmd = "sudo update-locale LC_ALL=\"" + locale_code + ".UTF-8\""
        print cmd
        os.system(cmd)
        cmd = "sudo update-locale LANG=" + locale_code + ".UTF-8 LANGUAGE=" + locale_code
        print cmd
        os.system(cmd)
        '''
        
        common.need_reboot = True

        self.win.go_to_home()
