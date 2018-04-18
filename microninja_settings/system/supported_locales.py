# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Set configuration for i18n locale
#
# Note: Several conflicting conventions are used by the system tools for the
# naming of locales. Here, everything will be converted to use UTF-8 and take
# the standard format
#
#     <language>_<REGION>.UTF-8
#
# -*- coding: utf-8 -*-
# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# added France and Spain


class Locales(dict):
    #do not translate
    LANGUAGES = {
        'en': 'English',
	'it': 'Italiano',
        'de': 'Deutsch',
        'fr': 'Français',
        'es': 'Español',
        'pt': 'Português'
    }

    #do not translate
    REGIONS = {
        'US': 'United States',
        'GB': 'United Kingdom',
        'IT': 'Italia',
        'DE': 'Deutschland',
        'FR': 'France',
        'ES': 'España',
        'PT': 'Portugal',
        'BR': 'Brasil'
    }

    def list_language_codes(self):
        return self.keys()

    def list_languages(self):
        return [self.LANGUAGES[lang] for lang in self.iterkeys()]

    def list_region_codes(self, lang=None, lang_code=None):
        if lang:
            lang_code = self.lang_to_lang_code(lang)

        return self[lang_code]

    def list_regions(self, lang=None, lang_code=None):
        return [
            self.REGIONS[region_code] for region_code
            in self.list_region_codes(lang=lang, lang_code=lang_code)
        ]

    @staticmethod
    def lang_to_lang_code(lang):
        for lang_code, _lang in Locales.LANGUAGES.iteritems():
            if lang == _lang:
                return lang_code

    @staticmethod
    def lang_code_to_lang(lang_code):
        return Locales.LANGUAGES[lang_code]

    @staticmethod
    def region_to_region_code(region):
        for region_code, _region in Locales.REGIONS.iteritems():
            if region == _region:
                return region_code

    @staticmethod
    def region_code_to_region(region_code):
        return Locales.REGIONS[region_code]

    @staticmethod
    def get_codes_from_locale_code(locale_code):
        return locale_code.split('_')

    @staticmethod
    def get_locale_code_from_codes(lang_code, region_code):
        return "{}_{}".format(lang_code, region_code)

    @staticmethod
    def get_locale_code_from_langs(lang, region):
        region_code = Locales.region_to_region_code(region)
        lang_code = Locales.lang_to_lang_code(lang)

        return Locales.get_locale_code_from_codes(lang_code, region_code)


SUPPORTED_LOCALES = Locales({
    'en': ['US', 'GB'],
    'it': ['IT'],
    'de': ['DE'],
    'fr': ['FR'],
    'es': ['ES'],
    'pt': ['PT', 'BR']
})
