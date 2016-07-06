#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

import re
import sys


REGIONS = {
    'au': 'pacific anglophone',
    'nz': 'pacific anglophone',
    'us': 'united states',
    'ca': 'canada',
    'uk': 'united kingdom',
    'kr': 'pacific anglophone',
    'ph': 'pacific anglophone',
    'pr': 'latin america',
    'mx': 'latin america',
    'br': 'latin america',
    'co': 'latin america',
    'ar': 'latin america',
    'pe': 'latin america',
    'be': 'europe',
    'fr': 'europe',
    'es': 'europe',
    'de': 'europe',
    'dk': 'europe',
    'no': 'europe',
    'se': 'europe',
    'is': 'europe',
    'nl': 'europe',
    'pt': 'europe',
    'it': 'europe',
    'gr': 'europe',
    'ro': 'europe',
    'bg': 'europe',
    'pl': 'europe',
    'cz': 'europe',
    'lt': 'europe',
    'fi': 'europe',
    'at': 'europe',
    'ly': 'north africa',
    'zz': 'unspecified',
    'zze': 'europe',
    '': 'unspecified',
}

COUNTRIES_BY_CODE = {
    "gw": "Guinea-Bissau",
    "gu": "Guam",
    "gt": "Guatemala",
    "gs": "S. Georgia and S. Sandwich Isls.",
    "gr": "Greece",
    "gq": "Equatorial Guinea",
    "gp": "Guadeloupe",
    "gy": "Guyana",
    "gf": "French Guiana",
    "ge": "Georgia",
    "gd": "Grenada",
    "gb": "United Kingdom",
    "ga": "Gabon",
    "gn": "Guinea",
    "gm": "Gambia",
    "gl": "Greenland",
    "cshh": "Czechoslovakia (former)",
    "gh": "Ghana",
    "lb": "Lebanon",
    "lc": "Saint Lucia",
    "la": "Laos",
    "tv": "Tuvalu",
    "tw": "Taiwan",
    "tt": "Trinidad and Tobago",
    "tr": "Turkey",
    "lk": "Sri Lanka",
    "tp": "East Timor",
    "li": "Liechtenstein",
    "lv": "Latvia",
    "to": "Tonga",
    "lt": "Lithuania",
    "lu": "Luxembourg",
    "lr": "Liberia",
    "ls": "Lesotho",
    "th": "Thailand",
    "tf": "French Southern Territories",
    "tg": "Togo",
    "td": "Chad",
    "tc": "Turks and Caicos Islands",
    "ly": "Libya",
    "do": "Dominican Republic",
    "dm": "Dominica",
    "dj": "Djibouti",
    "dk": "Denmark",
    "um": "US Minor Outlying Islands",
    "de": "Germany",
    "ye": "Yemen",
    "dz": "Algeria",
    "uy": "Uruguay",
    "yu": "Yugoslavia",
    "yt": "Mayotte",
    "vu": "Vanuatu",
    "kn": "Saint Kitts and Nevis",
    "cy": "Cyprus",
    "qa": "Qatar",
    "suhh": "USSR (former)",
    "tm": "Turkmenistan",
    "eh": "Western Sahara",
    "wf": "Wallis and Futuna Islands",
    "ee": "Estonia",
    "eg": "Egypt",
    "za": "South Africa",
    "ec": "Ecuador",
    "sj": "Svalbard and Jan Mayen Islands",
    "us": "United States",
    "et": "Ethiopia",
    "zw": "Zimbabwe",
    "es": "Spain",
    "er": "Eritrea",
    "ru": "Russian Federation",
    "rw": "Rwanda",
    "re": "Reunion",
    "gi": "Gibraltar",
    "it": "Italy",
    "ro": "Romania",
    "tk": "Tokelau",
    "bd": "Bangladesh",
    "be": "Belgium",
    "bf": "Burkina Faso",
    "bg": "Bulgaria",
    "vg": "Virgin Islands (British)",
    "ba": "Bosnia and Herzegovina",
    "bb": "Barbados",
    "bm": "Bermuda",
    "bn": "Brunei Darussalam",
    "bo": "Bolivia",
    "bh": "Bahrain",
    "bi": "Burundi",
    "bj": "Benin",
    "bt": "Bhutan",
    "jm": "Jamaica",
    "bv": "Bouvet Island",
    "bw": "Botswana",
    "ws": "Samoa",
    "sa": "Saudi Arabia",
    "br": "Brazil",
    "bs": "Bahamas",
    "tz": "Tanzania",
    "by": "Belarus",
    "bz": "Belize",
    "om": "Oman",
    "zm": "Zambia",
    "ua": "Ukraine",
    "jo": "Jordan",
    "mz": "Mozambique",
    "ck": "Cook Islands",
    "ci": "Cote D'Ivoire (Ivory Coast)",
    "ch": "Switzerland",
    "co": "Colombia",
    "cn": "China",
    "cm": "Cameroon",
    "cl": "Chile",
    "cc": "Cocos (Keeling) Islands",
    "ca": "Canada",
    "cg": "Congo",
    "cf": "Central African Republic",
    "cz": "Czech Republic",
    "xx": "-- FIX ME --",
    "cx": "Christmas Island",
    "cr": "Costa Rica",
    "cv": "Cape Verde",
    "cu": "Cuba",
    "ve": "Venezuela",
    "pr": "Puerto Rico",
    "tn": "Tunisia",
    "pw": "Palau",
    "pt": "Portugal",
    "py": "Paraguay",
    "iq": "Iraq",
    "pa": "Panama",
    "pf": "French Polynesia",
    "pg": "Papua New Guinea",
    "pe": "Peru",
    "pk": "Pakistan",
    "ph": "Philippines",
    "pn": "Pitcairn",
    "pl": "Poland",
    "pm": "St. Pierre and Miquelon",
    "hr": "Croatia (Hrvatska)",
    "ht": "Haiti",
    "hu": "Hungary",
    "hk": "Hong Kong",
    "hn": "Honduras",
    "ddde": "German Democratic Republic [former]",
    "hm": "Heard and McDonald Islands",
    "jp": "Japan",
    "md": "Moldova",
    "mg": "Madagascar",
    "ma": "Morocco",
    "mc": "Monaco",
    "uz": "Uzbekistan",
    "mm": "Myanmar",
    "ml": "Mali",
    "mo": "Macau",
    "mn": "Mongolia",
    "mh": "Marshall Islands",
    "mk": "Macedonia",
    "mu": "Mauritius",
    "mt": "Malta",
    "mw": "Malawi",
    "mv": "Maldives",
    "mq": "Martinique",
    "mp": "Northern Mariana Islands",
    "ms": "Montserrat",
    "mr": "Mauritania",
    "ug": "Uganda",
    "my": "Malaysia",
    "mx": "Mexico",
    "il": "Israel",
    "va": "Vatican City State (Holy See)",
    "vc": "Saint Vincent and the Grenadines",
    "ae": "United Arab Emirates",
    "ad": "Andorra",
    "ag": "Antigua and Barbuda",
    "af": "Afghanistan",
    "ai": "Anguilla",
    "vi": "Virgin Islands (U.S.)",
    "is": "Iceland",
    "ir": "Iran",
    "am": "Armenia",
    "al": "Albania",
    "ao": "Angola",
    "an": "Netherlands Antilles",
    "aq": "Antarctica",
    "as": "American Samoa",
    "ar": "Argentina",
    "au": "Australia",
    "at": "Austria",
    "aw": "Aruba",
    "in": "India",
    "az": "Azerbaijan",
    "ie": "Ireland",
    "id": "Indonesia",
    "ni": "Nicaragua",
    "nl": "Netherlands",
    "no": "Norway",
    "na": "Namibia",
    "nc": "New Caledonia",
    "ne": "Niger",
    "nf": "Norfolk Island",
    "ng": "Nigeria",
    "nz": "New Zealand (Aotearoa)",
    "sh": "St. Helena",
    "zr": "Zaire",
    "vn": "Viet Nam",
    "np": "Nepal",
    "so": "Somalia",
    "nr": "Nauru",
    "nt": "Neutral Zone",
    "nu": "Niue",
    "fr": "France",
    "io": "British Indian Ocean Territory",
    "fx": "France, Metropolitan",
    "sb": "Solomon Islands",
    "fi": "Finland",
    "fj": "Fiji",
    "fk": "Falkland Islands (Malvinas)",
    "fm": "Micronesia",
    "fo": "Faroe Islands",
    "tj": "Tajikistan",
    "sz": "Swaziland",
    "sy": "Syria",
    "kg": "Kyrgyzstan",
    "ke": "Kenya",
    "sr": "Suriname",
    "ki": "Kiribati",
    "kh": "Cambodia",
    "sv": "El Salvador",
    "km": "Comoros",
    "st": "Sao Tome and Principe",
    "sk": "Slovak Republic",
    "kr": "Korea (South)",
    "si": "Slovenia",
    "kp": "Korea (North)",
    "kw": "Kuwait",
    "sn": "Senegal",
    "sm": "San Marino",
    "sl": "Sierra Leone",
    "sc": "Seychelles",
    "kz": "Kazakhstan",
    "ky": "Cayman Islands",
    "sg": "Singapore",
    "se": "Sweden",
    "sd": "Sudan",
    "zz": "Unspecified",
    "zze": "Europe - Unspecified",
}

# Note: Everything is lower-cased first, and terminal periods are trimmed.
COUNTRIES = {
    ('australia',): 'au',
    ('new zealand',): 'nz',

    ('usa', 'us', 'u.s.a', 'u.s', 'u.s of a', 'united states',
     'united states of america', 'america', 'usa! usa! usa!',
     'united states of anerica', 'united  states'): 'us',
    ('canada',): 'ca',

    ('uk', 'u.k', 'united kingdom', 'great britain', 'england', 'english',
     'scotland', 'northern ireland', 'wales',
     'england (united kingdom)'): 'uk',
    ('germany',): 'de',
    ('spain', 'soain', 'españa'): 'es',
    ('france',): 'fr',
    ('belgium',): 'be',
    ('czech republic', 'czech'): 'cz',
    ('the netherlands', 'netherlands'): 'nl',
    ('portugal',): 'pt',
    ('denmark',): 'dk',
    ('romania',): 'ro',
    ('norway',): 'no',
    ('italy',): 'it',
    ('greece',): 'gr',
    ('bulgaria',): 'bg',
    ('iceland',): 'is',
    ('lithuania',): 'lt',
    ('poland',): 'pl',
    ('sweden',): 'se',
    ('finland',): 'fi',
    ('austria',): 'at',

    ('puerto rico',): 'pr',
    ('argentina',): 'ar',
    ('brazil',): 'br',
    ('colombia',): 'co',
    ('mexico',): 'mx',
    ('peru',): 'pe',

    ('korea',): 'kr',
    ('phl',): 'ph',

    ('libya',): 'ly',

    # Using zz for unknown / ambiguous
    ('', 'earth'): 'zz',
}

LANGUAGES_BY_CODE = {
    "gu": "Gujarati",
    "gd": "Scots Gaelic",
    "ga": "Irish",
    "gn": "Guarani",
    "gl": "Galician",
    "la": "Latin",
    "ln": "Lingala",
    "lo": "Laothian",
    "tt": "Tatar",
    "tr": "Turkish",
    "ts": "Tsonga",
    "lv": "Latvian, Lettish",
    "to": "Tonga",
    "lt": "Lithuanian",
    "tk": "Turkmen",
    "th": "Thai",
    "ti": "Tigrinya",
    "tg": "Tajik",
    "te": "Telugu",
    "fil": "Filipino; Pilipino",
    "ta": "Tamil",
    "yo": "Yoruba",
    "de": "German",
    "da": "Danish",
    "dz": "Bhutani",
    "st": "Sesotho",
    "qu": "Quechua",
    "el": "Greek",
    "eo": "Esperanto",
    "en": "English",
    "zh": "Chinese",
    "bo": "Tibetan",
    "uk": "Ukrainian",
    "eu": "Basque",
    "et": "Estonian",
    "es": "Spanish",
    "ru": "Russian",
    "rw": "Kinyarwanda",
    "sms": "Sami (Skolt)",
    "smn": "Sami (Inari)",
    "smj": "Sami (Lule)",
    "smi": "Sami languages",
    "rm": "Rhaeto-Romance",
    "rn": "Kirundi",
    "ro": "Romanian",
    "sma": "Sami (Southern)",
    "be": "Byelorussian",
    "bg": "Bulgarian",
    "ba": "Bashkir",
    "wo": "Wolof",
    "bn": "Bengali; Bangla",
    "jw": "Javanese",
    "bh": "Bihari",
    "bi": "Bislama",
    "ji": "Yiddish",
    "br": "Breton",
    "bs": "Bosnian",
    "ja": "Japanese",
    "om": "Oromo (Afan)",
    "oc": "Occitan",
    "und": "(undetermined)",
    "tw": "Twi",
    "or": "Oriya",
    "xh": "Xhosa",
    "co": "Corsican",
    "ca": "Catalan",
    "cy": "Welsh",
    "cs": "Czech",
    "ps": "Pashto, Pushto",
    "pt": "Portuguese",
    "tl": "Tagalog",
    "pa": "Punjabi",
    "vi": "Vietnamese",
    "zxx": "(no linguistic content)",
    "pl": "Polish",
    "hy": "Armenian",
    "hr": "Croatian",
    "hu": "Hungarian",
    "hi": "Hindi",
    "ha": "Hausa",
    "mg": "Malagasy",
    "uz": "Uzbek",
    "ml": "Malayalam",
    "mo": "Moldavian",
    "mn": "Mongolian",
    "mi": "Maori",
    "ik": "Inupiak",
    "mk": "Macedonian",
    "ur": "Urdu",
    "mt": "Maltese",
    "ms": "Malay",
    "mr": "Marathi",
    "my": "Burmese",
    "aa": "Afar",
    "ab": "Abkhazian",
    "ss": "Siswati",
    "af": "Afrikaans",
    "tn": "Setswana",
    "sw": "Swahili",
    "is": "Icelandic",
    "am": "Amharic",
    "it": "Italian",
    "iw": "Hebrew",
    "sv": "Swedish",
    "ia": "Interlingua",
    "as": "Assamese",
    "ar": "Arabic",
    "su": "Sundanese",
    "in": "Indonesian",
    "ay": "Aymara",
    "az": "Azerbaijani",
    "ie": "Interlingue",
    "sk": "Slovak",
    "nl": "Dutch",
    "no": "Norwegian",
    "na": "Nauru",
    "ne": "Nepali",
    "vo": "Volapuk",
    "zu": "Zulu",
    "fr": "French",
    "sm": "Samoan",
    "fy": "Frisian",
    "fa": "Persian",
    "fi": "Finnish",
    "fj": "Fiji",
    "sa": "Sanskrit",
    "fo": "Faeroese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "sr": "Serbian",
    "sq": "Albanian",
    "ko": "Korean",
    "kn": "Kannada",
    "km": "Cambodian",
    "kl": "Greenlandic",
    "ks": "Kashmiri",
    "si": "Singhalese",
    "sh": "Serbo-Croatian",
    "so": "Somali",
    "sn": "Shona",
    "ku": "Kurdish",
    "sl": "Slovenian",
    "ky": "Kirghiz",
    "sg": "Sangro",
    "se": "Sami (Northern)",
    "sd": "Sindhi",
    "zz": "Unspecified",
}

LANGUAGES = {
    ('english', 'englsih', 'englih', 'englisj', 'anglais', 'american'): 'en',
    ('german',): 'de',
    ('french', 'français'): 'fr',
    ('swedish',): 'sv',
    ('frisian',): 'fy',
    ('dutch',): 'nl',
    ('norwegian',): 'nb',
    ('danish',): 'da',
    ('italian',): 'it',
    ('español', 'spanish'): 'es',
    ('portuguese', 'potuguese'): 'pt',
    ('serbian',): 'sr',
    ('croatian',): 'hr',
    ('japanese',): 'ja',
    ('tagalog', 'filipino'): 'tl',
    ('icelandic', 'icelic'): 'is',
    ('romanian',): 'ro',
    ('greek',): 'el',
    ('russian',): 'ru',
    ('bulgarian',): 'bg',
    ('polish',): 'pl',
    ('arabic',): 'ar',
    ('latin',): 'la',
    # Using zz for unknown / ambiguous.
    ('',): 'zz',
    # Using zze for unknown within europe.
    ('european',): 'zze',
}

GENDERS = {
    'm': ('male', 'm', 'man', 'male last i checked', 'männlich (male ;-d)',
          'masculine', 'masculin', 'nale', 'mal', 'maschio'),
    'f': ('female', 'f', 'woman', 'feminine'),
    '': ('50', '66', 'you have to ask?', 'earthling', 'jungle',
         "what's a gender?", 'seriously?')
}


WHY_PERSONAL = 'I look up comics for personal use or curiosity'
WHY_WRITING = 'I research comics to write about them online or in print'
WHY_ACADEMICS = ('I research comics for academic purposes as a '
                 'student or teacher/professor')
WHY_INDEXING = 'I add and/or edit information in the comics.org database'
WHY_COLLECTING = 'I manage my collection at my.comics.org'

WHY_VALUES = [WHY_PERSONAL, WHY_WRITING, WHY_ACADEMICS,
              WHY_INDEXING, WHY_COLLECTING]
WHY_LABELS = {
    WHY_PERSONAL: 'personal',
    WHY_WRITING: 'writing',
    WHY_ACADEMICS: 'academics',
    WHY_INDEXING: 'indexing',
    WHY_COLLECTING: 'collecting',
}


class Line(object):
    def __init__(self, ts, why, era, preferred, social, language, country,
                 age='', gender='', contact='', extra='',
                 pro='', search='', api='', todo='', digital='', con='',
                 timeline='', bonds='', indexing='', creators='',
                 characters='', site='', current=''):
        self.ts = ts
        self.why = why
        self.era = era
        self.preferred = preferred
        self.social = social.lower()
        self.language = language.lower().strip(' .')
        self.country = country.lower().strip(' .')
        self.age = age
        self.gender = gender.lower().strip(' .')
        self.contact = contact
        self.extra = extra
        self.pro = int(pro) if pro == '1' else ''
        self.con = int(con) if con == '1' else ''
        self.search = int(search) if search == '1' else ''
        self.api = int(api) if api == '1' else ''
        self.indexing = int(indexing) if indexing == '1' else ''
        self.todo = int(todo) if todo == '1' else ''
        self.digital = int(digital) if digital == '1' else ''
        self.timeline = int(timeline) if timeline == '1' else ''
        self.bonds = int(bonds) if bonds == '1' else ''
        self.creators = int(creators) if creators == '1' else ''
        self.characters = int(characters) if characters == '1' else ''
        self.site = int(site) if site == '1' else ''
        self.current = int(current) if current == '1' else ''

    def process_why(self, row):
        why = self.why.replace('comics, creators, publishers, etc.',
                               'comics').split(', ')
        v_index = 0
        why_index = 0
        while v_index < len(WHY_VALUES) and why_index < len(why):
            if why[why_index] == WHY_VALUES[v_index]:
                row[WHY_LABELS[WHY_VALUES[v_index]]] = True
                why_index += 1
            v_index += 1

        if why_index < len(WHY_VALUES) - 1:
            row['other_reason'] = ', '.join(why[why_index:])

    def process_era(self, row):
        if self.era.startswith('I am primarily interested in recent'):
            row['recent'] = True
            row['older'] = False
        elif self.era.startswith('I am primarily interested in older'):
            row['recent'] = False
            row['older'] = True
        else:
            row['recent'] = True
            row['older'] = True

    def process_preferred(self, row):
        # True means GCD preferred, False means GCD used only if other sites
        # fail, None means use GCD and other sites about equally.
        # All of the "other" values can be mapped to these reasonably
        # well, so we just do that.
        if self.preferred.startswith('Yes, I use the GCD more'):
            row['preferred'] = True
        elif self.preferred.startswith('No, I use the GCD and one or more') \
                or self.preferred.lower().startswith('first'):
            row['preferred'] = None
        elif self.preferred.startswith('No, I only use the GCD if') or \
                self.preferred == 'Atlas Tales':
            row['preferred'] = False
        elif 'GCD' in self.preferred:
            # Need to do this last or else would catch standard "No" options
            # But all of the nonstandard options with GCD in them are
            # essentially positive responses.
            row['preferred'] = True
        assert row['preferred'] is None or isinstance(row['preferred'], bool)

    def process_social(self, row):
        # Each value, if present, is always in the same order.
        # So just walk through all of them in order and flag
        # them and move to the next value when we see a match.
        try:
            social = self.social.split(', ')
            channel = social.pop(0).lower()
            if 'but rarely if ever post' in channel:
                row['follows_lists'] = True
                channel = social.pop(0)
            if 'post to at least one of the mailing' in channel:
                row['posts_to_lists'] = True
                channel = social.pop(0)
            if 'i follow the gcd on facebook' in channel:
                row['follows_fb'] = True
                channel = social.pop(0)
            if 'post to the gcd' in channel:
                row['posts_to_fb'] = True
                channel = social.pop(0)
            if 'google' in channel:
                row['follows_gplus'] = True
                channel = social.pop(0)
            if 'twitter' in channel:
                row['follows_twitter'] = True
                channel = social.pop(0)
            if 'pinterest' in channel:
                row['follows_pinterest'] = True
                channel = social.pop(0)
            if 'do not follow' in channel:
                row['non_social'] = True
        except IndexError:
            # We've processed the whole thing and didn't use all self,
            # which is to be expected as checking all of the boxes doesn't
            # make sense.
            pass

    def process_languages(self, row):
        # Remove complicated stuff that people put in.
        # And yes, there's an extra 'a' in a hilarious location in one of
        # the 'occasionally' instances.  And yes, it's hilarious because
        # mentally I'm apparently 12.
        self.language = re.sub(
            (r"sometimes|rarely|occasioa?nally|almost|but| in |attempt|some|"
             r"exclusively| or[ /]| and|and |doesn't|matter|; i own|other|"
             r"languages?|i can read, art is a universal "),
            ' ', self.language)

        # All language names are one word, so normalize all punctuation
        # and spacing to a comma-separated list.  A few "two word" entries
        # are just synonyms, so they'll get added to the set twice which
        # is harmless.  Because set.
        self.language = re.sub(r'[ /,.&;)(]+', ', ', self.language)
        language_set = set()
        for lang in map(lambda x: x.strip(' .'), self.language.split(', ')):
            # The keys in LANGUAGES are tuples of names, so we have to look
            # for the data in the tuple rather than just checking equality.
            for lang_names in LANGUAGES:
                if lang in lang_names:
                    language_set.add(LANGUAGES[lang_names])
                    break
            # This else goes with the for- it executes if we did *NOT*
            # find a matching language, and therefore never did a 'break'
            else:
                sys.stderr.write('Unknown language: "%s"\n' % lang)
                language_set.add('zz')
        row['languages'] = ', '.join(language_set)

    def process_country(self, row):
        # The keys in COUNTRIES are tuples of names, so we have to
        # look for the data in the tuple rather than just checking equality.
        for country_names in COUNTRIES:
            if self.country in country_names:
                row['country'] = COUNTRIES[country_names]
                break
        # This else goes with the for- it executes if we did *NOT*
        # find a matching country, and therefore never did a 'break'
        else:
            sys.stderr.write('Unknown country: "%s"\n' % self.country)
            row['country'] = 'zz'

        # Set the region in the main data as we'll use it a lot.
        row['region'] = REGIONS[row['country']]

    def process_age(self, row):
        # Pick the number in the middle of the decade ragnes just so that
        # we can use numbers here for things like selecting larger ranges.
        if self.age == '':
            row['age'] = None
        elif '<' in self.age:
            row['age'] = 15
        else:
            try:
                row['age'] = int(self.age[0:2]) + 5
            except ValueError:
                raise ValueError("Could not parse age: '%r'" % self.age)

        assert row['age'] is None or isinstance(row['age'], int)

    def process_gender(self, row):
        if self.gender in GENDERS['m']:
            row['gender'] = 'm'
        elif self.gender in GENDERS['f']:
            row['gender'] = 'f'
        else:
            # None of the other values are actionable- they all seem to be
            # either mistakes (age or, um... genre? in the field) or people
            # just being amusing ("earthling" is the closest thing to an
            # actual alternative gender that anyone supplied).
            # So just treat them all as "decline to state."
            row['gender'] = 'declined to state'
