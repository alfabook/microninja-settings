#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Structures to hold the screens
#
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation
# notifications removed
# overclock removed

from collections import OrderedDict

from microninja.utils import get_user_unsudoed

import microninja_settings.common as common
from microninja_settings.config_file import get_setting
from microninja_settings.components.menu_button import Menu_button

import microninja_settings.system.keyboard_layouts as keyboard_layouts
from microninja_settings.set_keyboard import choose_keyboard_screen, keyboard_screen_install
from microninja_settings.set_mouse import SetMouse
#from microninja_settings.set_notifications import SetNotifications
from microninja_settings.set_font import SetFont
from microninja_settings.set_audio import SetAudio
from microninja_settings.set_display import SetDisplay
from microninja_settings.set_wifi import SetWifi, SetProxy
from microninja_settings.no_internet_screen import NoInternet
from microninja_settings.set_overclock import SetOverclock
from microninja_settings.set_account import SetAccount
from microninja_settings.set_about import SetAbout
from microninja_settings.set_advanced import SetAdvanced, SetPassword
from microninja_settings.set_style import SetStyle
from microninja_settings.set_wallpaper import FirstBootSetWallpaper
from microninja_settings.locale import LocaleConfig


class Screen(object):
    """
    NB: screen_no is here for legacy reasons - remove as soon as support is
        withdrawn.
    """

    def __init__(self, name, label, screen_widget,
                 screen_no=None, on_home_screen=True,
                 setting_param=None, icon=''):
        self.name = name
        self._label = label
        self.screen_widget = screen_widget
        self.screen_no = screen_no
        self.on_home_screen = on_home_screen
        self.menu_button = None
        self._setting_param = setting_param
	self._icon = icon
	if(self._icon == ''):
		self._icon = label

    def create_menu_button(self, cb):
        self.menu_button = button = Menu_button(self._label, '', icon=self._icon)
        button.button.state = self.screen_no
        button.button.connect('clicked', cb, self.name)

    def refresh_menu_button(self):
        description = ''

        if self.name == 'appearance':
             description = _('Wallpapers and screensavers')
             self.menu_button.description.set_text(description)
             return

        if self._setting_param:
            if self.name == 'font':
                value = get_setting(self._setting_param)
                if value == 0:
                   description = _('Small')
                if value == 1:
                   description = _('Medium')
                if value == 2:
                   description = _('Big')
            elif self.name == 'keyboard':
                continent = get_setting('Keyboard-continent-index')
                country = get_setting('Keyboard-country-index')
                description = keyboard_layouts.continents_list_countries[continent][country]
            else:    
                description = get_setting(self._setting_param)
        else:
            if self.name == 'wifi':
                if common.has_internet:
                    description = _('Connected')
                else:
                    description = _('Not connected')

            elif self.name == 'account':
                description = get_user_unsudoed()
            
            elif self.name == 'display':
                return

        self.menu_button.description.set_text(description)


class ScreenCollection(OrderedDict):

    def __init__(self, screens):
        super(ScreenCollection, self).__init__()

        for screen in screens:
            self[screen.name] = screen

    def get_screen_from_number(self, number):
        for screen in self.itervalues():
            if screen.screen_no == number:
                return screen

    def get_screens_on_home(self):
        displayed_screens = []

        for screen in self.itervalues():
            if screen.on_home_screen:
                displayed_screens.append(screen)

        return displayed_screens


SCREENS = ScreenCollection([
    Screen('keyboard', _('Keyboard'), choose_keyboard_screen, screen_no=0,
           setting_param='Keyboard-country-index', icon='Keyboard'),
    #Screen('mouse', 'Mouse', SetMouse, screen_no=1, setting_param='Mouse', icon='Mouse')
    Screen('locale', _('Language'), LocaleConfig, screen_no=1, setting_param='Locale', icon='Language'),
    Screen('audio', _('Audio'), SetAudio, screen_no=2, setting_param='Audio', icon='Audio'),
    Screen('display', _('Screen'), SetDisplay, screen_no=3, icon='Display'),
    Screen('wifi', _('WiFi'), SetWifi, screen_no=4, icon='WiFi'),
    #Screen('overclocking', 'Overclocking', SetOverclock, screen_no=5,
    #       setting_param='Overclocking', icon='Overclocking'),
    Screen('account', _('Reset'), SetAccount, screen_no=5, icon='Account'),
    Screen('appearance', _('Style'), SetStyle, screen_no=6,
           setting_param='Wallpaper', icon='Style'),
    Screen('font', _('Fonts'), SetFont, screen_no=7, setting_param='Font', icon='Font'),
    Screen('advanced', _('Parental Control'), SetAdvanced, screen_no=8, icon='Advanced'),
    Screen('about', _('About'), SetAbout, screen_no=9, icon='About'),
    #Screen('notifications', 'Notifications', SetNotifications, screen_no=11),
    Screen('no-internet', 'No-internet', NoInternet, screen_no=10,
           on_home_screen=False),
    Screen('proxy', 'proxy', SetProxy, screen_no=11, on_home_screen=False),
    Screen('first-boot-set-wallpaper', 'first-boot-set-wallpaper',
           FirstBootSetWallpaper, screen_no=12, on_home_screen=False),
    Screen('set-parental-password', 'set-parental-password', SetPassword,
           screen_no=13, on_home_screen=False),
    #special keyboard window for first boot
    Screen('keyboard-install', _('Keyboard'), keyboard_screen_install, screen_no=14,
           setting_param='Keyboard-country-human', icon='Keyboard', on_home_screen=False),
    # TODO: Add 'Locale' screen to home screen when translations are available.
    # TODO: Add icon for the 'Locale' screen.
])
