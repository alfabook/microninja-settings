#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_keyboard.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation

import threading
from gi.repository import Gtk, GObject

import microninja_settings.system.keyboard_layouts as keyboard_layouts
import microninja_settings.system.keyboard_config as keyboard_config
import microninja_settings.common as common
from microninja_settings.templates import Template
from microninja_settings.config_file import get_setting, set_setting
from microninja.gtk3.buttons import OrangeButton
from microninja.gtk3.microninja_combobox import KanoComboBox
from microninja.utils import detect_kano_keyboard
from microninja.logging import logger


def choose_keyboard_screen(win):
    # Check for kano-keyboard
    kano_keyboard = detect_kano_keyboard()
    if kano_keyboard:
        SetKanoKeyboard(win)

    else:
        SetKeyboard(win)

def keyboard_screen_install(win):
    SetKeyboard(win, first_boot=True)


class SetKanoKeyboard(Template):
    def __init__(self, win):
        Template.__init__(
            self,
            _("Keyboard"),
            _("Microninja keyboard found"),
            _("APPLY MODIFIES")
        )

        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.enable_prev()
        self.win.set_size_request(530, 350)

        # height is 106px
        img = Gtk.Image()
        img.set_from_file(common.media + "/Graphics/keyboard.png")

        # Link to advance options
        self.to_advance_button = OrangeButton("Layout options")
        self.to_advance_button.connect("button_press_event", self.to_advance)

        self.kano_button.connect("button-release-event", self.win.go_to_home)
        self.win.change_prev_callback(self.win.go_to_home)

        self.box.pack_start(img, False, False, 0)
        self.box.pack_start(self.to_advance_button, False, False, 0)

        # Refresh window
        self.win.show_all()

    def to_advance(self, widget, event):

        self.win.clear_win()
        SetKeyboard(self.win)


class SetKeyboard(Template):
    selected_layout = None
    selected_continent_index = 4
    selected_country = None
    selected_country_index = 18
    selected_variant = None
    selected_variant_index = 0
    #selected_continent_hr = _("Europa")
    #selected_country_hr = "It"
    #selected_variant_hr = _("Generica")
    variants_combo = None
    continents = keyboard_layouts.continents
    continents_list_countries = keyboard_layouts.continents_list_countries
    codes_list = keyboard_layouts.codes_list
    kano_keyboard = True

    def __init__(self, win, first_boot=False):
        Template.__init__(
            self,
            _("Keyboard"),
            _("Where do you live? So I can set your keyboard."),
            _("APPLY MODIFIES"),
            close_btn=first_boot
        )

        self.win = win
        self.win.set_main_widget(self)
        self.read_config()
        self.first_boot = first_boot
        self.win.set_size_request(530, 350)

        # kano_keyboard = detect_kano_keyboard()
        if not first_boot:
            self.win.top_bar.enable_prev()

        # if kano_keyboard:
        #    self.win.change_prev_callback(self.go_to_kano_screen)
        #else:
        self.win.change_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.apply_changes)
        if first_boot:
            self.kano_button_close.connect("button-release-event", Gtk.main_quit)

        # Make sure continue button is enabled
        self.kano_button.set_sensitive(False)

        # Create Continents Combo box
        self.continents_combo = KanoComboBox(max_display_items=7)
        for c in self.continents:
            self.continents_combo.append(c)
        self.continents_combo.connect("changed", self.on_continent_changed)

        # Create Countries Combo box
        self.countries_combo = KanoComboBox(max_display_items=7)
        self.countries_combo.connect("changed", self.on_country_changed)
        self.countries_combo.props.valign = Gtk.Align.CENTER

        # Create Advance mode checkbox
        advance_button = Gtk.CheckButton(_("Advanced options"))
        advance_button.set_can_focus(False)
        advance_button.props.valign = Gtk.Align.CENTER
        advance_button.connect("clicked", self.on_advance_mode)
        advance_button.set_active(False)

        # Create Variants Combo box
        self.variants_combo = KanoComboBox(max_display_items=7)
        self.variants_combo.connect("changed", self.on_variants_changed)
        self.variants_combo.props.valign = Gtk.Align.CENTER

        # Set up default values in dropdown lists
        self.set_defaults("continent")
        self.fill_countries_combo(self.continents_combo.get_selected_item_index())
        self.set_defaults("country")
        self.on_country_changed(self.countries_combo)
        self.set_defaults("variant")

        # Ceate various dropdown boxes so we can resize the dropdown lists appropriately
        # We create two boxes side by side, and then stack the country dropdow lists in one, and one by itself in the other

        #   dropdown_box_countries     dropdown_box_keys
        # |                        |                        |
        # |-------continents-------|   Advance option       |
        # |                        |                        |
        # |                        |                        |
        # |-------countries -------|--------variants--------|
        # |                        |                        |

        dropdown_box_countries = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        dropdown_box_countries.set_size_request(230, 30)
        dropdown_box_countries.props.valign = Gtk.Align.CENTER
        dropdown_box_keys = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        dropdown_box_keys.set_size_request(230, 30)
        dropdown_box_countries.pack_start(self.continents_combo, False, False, 0)
        dropdown_box_countries.pack_start(self.countries_combo, False, False, 0)
        box_spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_spacer.set_size_request(-1, 2)
        dropdown_box_keys.pack_start(box_spacer, False, False, 0)
        dropdown_box_keys.pack_start(advance_button, False, False, 0)
        dropdown_box_keys.pack_start(self.variants_combo, False, False, 0)
        dropdown_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        dropdown_container.pack_start(dropdown_box_countries, False, False, 0)
        dropdown_container.pack_start(dropdown_box_keys, False, False, 0)

        self.box.pack_start(dropdown_container, False, False, 0)

        # show all elements except the advanced mode
        GObject.timeout_add(0, self.refresh_window)

    def go_to_kano_screen(self, widget=None, event=None):
        self.win.clear_win()
        SetKanoKeyboard(self.win)

    def refresh_window(self):
        self.win.show_all()
        self.variants_combo.hide()

    def apply_changes(self, button, event):

        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:

            def lengthy_process():
                if keyboard_config.is_changed(self.selected_country_index, self.selected_variant_index):
                    # Apply the keyboard changes
                    keyboard_config.set_keyboard(self.selected_country, self.selected_variant)

                # The callback runs a GUI task, so wrap it!
                GObject.idle_add(self.work_finished_cb)

            # Apply changes
            thread = threading.Thread(target=lengthy_process)
            thread.start()

            # Save the changes in the config
            self.update_config()

            # kano_keyboard = detect_kano_keyboard()

            # Go back a screen
            # if kano_keyboard:
            #    self.go_to_kano_screen()
            # else:
            if not self.first_boot:
                self.win.go_to_home()
                self.win.show_all()
            else:
                Gtk.main_quit()            

    def read_config(self):
        self.selected_continent_index = get_setting("Keyboard-continent-index")
        self.selected_country_index = get_setting("Keyboard-country-index")
        self.selected_variant_index = get_setting("Keyboard-variant-index")
        #self.selected_continent_hr = get_setting("Keyboard-continent-human")
        #self.selected_country_hr = get_setting("Keyboard-country-human")
        #self.selected_variant_hr = get_setting("Keyboard-variant-human")

    def update_config(self):
        logger.info('set_keyboard.update_config {} {} {}'.format(
            self.selected_continent_index,
            self.selected_country_index,
            self.selected_variant_index
        ))

        # Add new configurations to config file.
        set_setting("Keyboard-continent-index", self.selected_continent_index)
        set_setting("Keyboard-country-index", self.selected_country_index)
        set_setting("Keyboard-variant-index", self.selected_variant_index)
        #set_setting("Keyboard-continent-human", self.selected_continent_hr)
        #set_setting("Keyboard-country-human", self.selected_country_hr)
        #set_setting("Keyboard-variant-human", self.selected_variant_hr)

    # setting = "variant", "continent" or "country"
    def set_defaults(self, setting):

        # Set the default info on the dropdown lists
        # "Keyboard-continent":continents_combo, "Keyboard-country", "Keyboard-variant"]:

        active_item = get_setting("Keyboard-" + setting + "-index")

        if setting == "continent":
            self.continents_combo.set_selected_item_index(int(active_item))
        elif setting == "country":
            self.countries_combo.set_selected_item_index(int(self.sorted_index_list.index(active_item)))
        elif setting == "variant":
            self.variants_combo.set_selected_item_index(int(active_item))
        else:
            logger.error("Bad argument in set_defaults - should be 'continent', 'country' or 'variant'")
            return

    def set_variants_to_generic(self):
        self.variants_combo.set_selected_item_index(0)   

    def on_continent_changed(self, combo):

        # making sure the continent has been set
        continent_text = combo.get_selected_item_text()
        continent_index = combo.get_selected_item_index()
        if not continent_text or continent_index == -1:
            return

        self.selected_continent_hr = continent_text
        self.selected_continent_index = continent_index

        self.kano_button.set_sensitive(False)
        self.fill_countries_combo(self.selected_continent_index)

        # Use the first country as the default value for country combo
        self.countries_combo.set_selected_item_index(0)
        self.on_country_changed(self.countries_combo)

    def on_country_changed(self, combo):

        # making sure the country has been set
        country_text = combo.get_selected_item_text()
        country_index = self.sorted_index_list[combo.get_selected_item_index()]
        if not country_text or country_index == -1:
            return

        # Remove entries from variants combo box
        self.variants_combo.remove_all()
        self.selected_country_hr = country_text
        self.selected_country_index = country_index

        # Refresh variants combo box
        self.selected_country = self.codes_list[self.selected_continent_index][country_index]
        variants = keyboard_config.find_keyboard_variants(self.selected_country)
        self.variants_combo.append(_("Generic"))
        if variants is not None:
            for v in variants:
                self.variants_combo.append(v[0])
        
        self.set_variants_to_generic()
        self.on_variants_changed(self.variants_combo)

    def on_variants_changed(self, combo):

        # making sure the variant has been set
        variant_text = combo.get_selected_item_text()
        variant_index = combo.get_selected_item_index()
        if not variant_text or variant_index == -1:
            return

        self.kano_button.set_sensitive(True)

        self.selected_variant_index = 0
        self.selected_variant = self.selected_variant_hr = variant_text
        #if variant_text == _("Generica"):
        #    self.selected_variant = self.selected_variant_hr = variant_text
        #    self.selected_variant_index = 0
        #    return
        # Select the variant code
        variants = keyboard_config.find_keyboard_variants(self.selected_country)
        if variants is not None:
            for v in variants:
                if v[0] == variant_text:
                    self.selected_variant = v[1]
                    self.selected_variant_index = variant_index
                    self.selected_variant_hr = variant_text

    def on_advance_mode(self, button):
        if int(button.get_active()):
            self.variants_combo.show()
        else:
            self.variants_combo.hide()

    def work_finished_cb(self):
        # Finished updating keyboard
        pass

    def fill_countries_combo(self, continent_index):
        # continent = continent.lower()

        try:
            self.selected_layout = self.continents_list_countries[continent_index]
        except KeyError:
            print _("Countries not found")
            return

        self.selected_continent_hr = self.continents[continent_index]

        # Remove entries from countries and variants combo box
        self.countries_combo.remove_all()
        self.variants_combo.remove_all()

        # Get a sorted list of the countries from the dict layout
        #DO NOT SORT: this breaks indexes!!!

        self.sorted_index_list = sorted(range(len(self.selected_layout)), key=lambda k: self.selected_layout[k])
        sorted_countries = sorted(self.selected_layout)
        
        #sorted_countries = self.selected_layout

        # Refresh countries combo box
        for country in sorted_countries:
            self.countries_combo.append(country)
