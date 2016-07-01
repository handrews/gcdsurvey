#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

import re
import sys
import codecs
import json
import collections
import functools

import gviz_api

from support import (
    Line, REGIONS, COUNTRIES, COUNTRIES_BY_CODE, LANGUAGES, LANGUAGES_BY_CODE,
    GENDERS, WHY_LABELS, WHY_VALUES)
from charts import make_label, CountDataSet, MultiCountDataSet

HEADER_SPEC = [
    ('personal', 'boolean'),
    ('writing', 'boolean'),
    ('academics', 'boolean'),
    ('research', 'boolean'),
    ('indexing', 'boolean'),
    ('collecting', 'boolean'),
    ('other_reason', 'string'),
    ('recent', 'boolean'),
    ('older', 'boolean'),
    ('preferred', 'boolean'),
    ('posts_to_lists', 'boolean'),
    ('posts_to_fb', 'boolean'),
    ('follows_lists', 'boolean'),
    ('follows_fb', 'boolean'),
    ('follows_gplus', 'boolean'),
    ('follows_twitter', 'boolean'),
    ('follows_pinterest', 'boolean'),
    ('non_social', 'boolean'),
    ('age', 'number'),
    ('gender', 'string'),
    ('region', 'string'),
    ('country', 'string'),
    ('languages', 'string'),
    ('english_only', 'boolean'),
    ('improve_search', 'boolean'),
]
HEADER_TYPES = {h[0]: h[1] for h in HEADER_SPEC}

if __name__ == '__main__':
    data = codecs.open('gcd-survey.tsv', encoding='utf-8')
    lines = data.readlines()
    header = Line(*lines.pop(0).replace('\r', '').split('\t'))
    # print(format_output_header(header))

    # output_header = format_output_header(header)
    # output_data = gviz_api.DataTable(output_header)

    rows = []
    for line in lines:
        row = {h[0]: ('' if h[1] == 'string' else None) for h in HEADER_SPEC}
        line = line.replace('\r', '')
        fields = Line(*line.split('\t'))

        # The absurdist nature of all of the answers in this particular
        # response is amusing, but not useful in the data.  Although
        # points for referencing the carny's cant (ciazarny).
        if 'zarny' in fields.language:
            continue

        # ######### WHY
        original_why = fields.why
        why = fields.why.replace('comics, creators, publishers, etc.',
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

        # ########## ERA
        if fields.era.startswith('I am primarily interested in recent'):
            row['recent'] = True
            row['older'] = False
        elif fields.era.startswith('I am primarily interested in older'):
            row['recent'] = False
            row['older'] = True
        else:
            row['recent'] = True
            row['older'] = True

        # ######### PREFERRED
        # True means GCD preferred, False means GCD used only if other sites
        # fail, None means use GCD and other sites about equally.
        # All of the "other" values can be mapped to these reasonablye
        # well, so we just do that.
        if fields.preferred.startswith('Yes, I use the GCD more'):
            row['preferred'] = True
        elif fields.preferred.startswith('No, I use the GCD and one or more') \
                or fields.preferred.lower().startswith('first'):
            row['preferred'] = None
        elif fields.preferred.startswith('No, I only use the GCD if') or \
                fields.preferred == 'Atlas Tales':
            row['preferred'] = False
        elif 'GCD' in fields.preferred:
            # Need to do this last or else would catch standard "No" options
            # But all of the nonstandard options with GCD in them are
            # essentially positive responses.
            row['preferred'] = True
        assert row['preferred'] is None or isinstance(row['preferred'], bool)

        # ######### SOCIAL
        # Same general approach as with 'why', but we don't have to worry
        # about embedded commas in the values this time.
        try:
            social = fields.social.split(', ')
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
            # We've processed the whole thing and didn't use all fields,
            # which is fine.
            pass

        # ######### LANGUAGE
        # Remove complicated stuff that people put in.
        # And yes, there's an extra 'a' in a hilarious location in one of
        # the 'occasionally' instances.  And yes, it's hilarious because
        # mentally I'm apparently 12.
        fields.language = re.sub(
            (r"sometimes|rarely|occasioa?nally|almost|but| in |attempt|some|"
             r"exclusively| or[ /]| and|and |doesn't|matter|; i own|other|"
             r"languages?|i can read, art is a universal "),
            ' ', fields.language)

        # All language names are one word, so normalize all punctuation
        # and spacing to a comma-separated list.  A few "two word" entries
        # are just synonyms, so they'll get added to the set twice which
        # is harmless.  Because set.
        fields.language = re.sub(r'[ /,.&;)(]+', ', ', fields.language)
        language_set = set()
        for lang in map(lambda x: x.strip(' .'), fields.language.split(', ')):
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

        # ######### COUNTRY
        # The keys in COUNTRIES are tuples of names, so we have to
        # look for the data in the tuple rather than just checking equality.
        for country_names in COUNTRIES:
            if fields.country in country_names:
                row['country'] = COUNTRIES[country_names]
                break
        # This else goes with the for- it executes if we did *NOT*
        # find a matching country, and therefore never did a 'break'
        else:
            sys.stderr.write('Unknown country: "%s"\n' % fields.country)
            row['country'] = 'zz'

        # ######### AGE
        # Pick the number in the middle of the decade ragnes just so that
        # we can use numbers here for things like selecting larger ranges.
        if fields.age == '':
            row['age'] = None
        elif '<' in fields.age:
            row['age'] = 15
        else:
            try:
                row['age'] = int(fields.age[0:2]) + 5
            except ValueError:
                raise ValueError("Could not parse age: '%r'" % fields.age)

        assert row['age'] is None or isinstance(row['age'], int)

        # ######### GENDER
        if fields.gender in GENDERS['m']:
            row['gender'] = 'm'
        elif fields.gender in GENDERS['f']:
            row['gender'] = 'f'
        else:
            # None of the other values are actionable- they all seem to be
            # either mistakes (age or, um... genre? in the field) or people
            # just being amusing ("earthling" is the closest thing to an
            # actual alternative gender that anyone supplied).
            # So just treat them all as "decline to state."
            row['gender'] = 'declined to state'

        # output_line = format_output_line(fields)
        # encoded = codecs.encode(output_line, 'utf-8')
        # print(encoded)
        # output_data.AppendData([output_line])

        rows.append(row)

    # count_data = CountDataSet(rows, 'preferred')
    # data_table = count_data.get_data_table(label_with=make_preference_label,
    #     filters=collections.OrderedDict([
    #         ('Non Social', lambda r: r['non_social']),
    #         ('Social', lambda r: not r['non_social']),
    #     ]))
    # print("GCDSurveyData = %s" % data_table)
          # json.dumps(json.loads(data_table.ToJSon()), indent=4))

    # make_social_label = functools.partial(make_label, label_map={
    #     True: 'Non Social', False: 'Social'})
    make_preference_label = functools.partial(make_label, label_map={
        True: 'Prefers the GCD',
        None: 'Uses the GCD and other sites',
        False: 'Prefers other sites',
    })

    # soc_counts = CountDataSet(rows, 'non_social')
    # soc_table = soc_counts.get_data_table(label_with=make_social_label,
    #     filters=collections.OrderedDict([
    #         (make_preference_label(True), lambda r: r['preferred']),
    #         (make_preference_label(None), lambda r: r ['preferred'] is None),
    #         (make_preference_label(False), lambda r: r ['preferred'] is False),
    #     ]))


    # pref_counts = CountDataSet(rows, 'preferred')
    # pref_table = pref_counts.get_data_table(label_with=make_preference_label,
    #     filters=collections.OrderedDict([
    #         ('Non Social', lambda r: r['non_social']),
    #         ('Social', lambda r: not r['non_social']),
    #     ]))
    output = {}
    
    region_counts = CountDataSet(rows, 'region',
                                 lambda r: REGIONS[r['country']])
    region_table = region_counts.get_data_table()
    output['Region'] = {
        'target': 'regions',
        'data': region_table,
    }

    for title, target, region in (('Europe by Country',
                                   'european_countries',
                                   'europe'),
                                  ('Latin America by Countries',
                                   'latin_countries',
                                   'latin america'),
                                  ('Pacific Anglophone Countries',
                                   'pacific_countries',
                                   'pacific anglophone')):
        country_counts = CountDataSet(rows, 'country')
        country_table = country_counts.get_data_table(
            filter_by=lambda r: REGIONS[r['country']] == region,
            label_with=functools.partial(make_label,
                                         label_map=COUNTRIES_BY_CODE))
        output[title] = {'target': target,
                         'data': country_table,
                         'type': 'pie'}
    # Note: You cannot create lambdas in a loop, as they will all capture
    # the final iteration value of the loop variable.
    age_filters = [('All', lambda r: True)]
    age_filters.append(('15', lambda r: r['age'] == 15))
    age_filters.append(('25', lambda r: r['age'] == 25))
    age_filters.append(('35', lambda r: r['age'] == 35))
    age_filters.append(('45', lambda r: r['age'] == 45))
    age_filters.append(('55', lambda r: r['age'] == 55))
    age_filters.append(('65', lambda r: r['age'] == 65))
    age_filters.append(('75', lambda r: r['age'] == 75))
    foo = MultiCountDataSet(rows, 'preferred')
    t = foo.get_data_table('Age', age_filters, label_with=make_preference_label)
    sys.stderr.write('%r\n' % t)
    output['Database Preference by Age'] = {'target': 'preference_by_age',
                                            'data': t,
                                            'type': 'stack'}
                               
    print("GCDSurveyData = %s;" % json.dumps(output, indent=4))

    import gviz_api
    dt = gviz_api.DataTable(HEADER_SPEC)
    processed_rows = []
    for r in rows:
        current_row = []
        for h in HEADER_SPEC:
            d = r[h[0]]
            current_row.append(d)
        processed_rows.append(current_row)

    dt.LoadData(processed_rows)
    j = dt.ToJSon()
    print("GCDRawData = %s;" % json.dumps(json.loads(j), indent=4))

# ########################################################################
