#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

import codecs
import json
import functools

import gviz_api

from support import (Line, REGIONS, COUNTRIES_BY_CODE)
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

    # Throw away the header line, as we build headers more suitable
    # for charts instead.
    Line(*lines.pop(0).replace('\r', '').split('\t'))

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

        fields.process_why(row)
        fields.process_era(row)
        fields.process_preferred(row)
        fields.process_social(row)
        fields.process_languages(row)
        fields.process_country(row)
        fields.process_age(row)
        fields.process_gender(row)

        rows.append(row)

    make_social_label = functools.partial(make_label, label_map={
        True: 'Non Social', False: 'Social'})

    make_preference_label = functools.partial(make_label, label_map={
        True: 'Prefers the GCD',
        None: 'Uses the GCD and other sites',
        False: 'Prefers other sites',
    })
    make_gender_label = functools.partial(make_label, label_map={
        'f': 'Female',
        'm': 'Male',
    })

    # This turns into our JavaScript data structure eventually.
    output = {}

    gender_counts = CountDataSet(rows, 'gender')
    gender_table = gender_counts.get_data_table(label_with=make_gender_label)
    output['Visitors by Gender'] = {
        'target': 'gender',
        'data': gender_table,
        'type': 'pie',
    }

    region_counts = CountDataSet(rows, 'region')
    region_table = region_counts.get_data_table()
    output['Visitors by Region or Frequent Country'] = {
        'target': 'regions',
        'data': region_table,
        'type': 'pie',
    }

    for title, target, region in (('Europe by Country',
                                   'european_countries',
                                   'europe'),
                                  ('Latin America by Country',
                                   'latin_countries',
                                   'latin america'),
                                  ('Pacific Anglophone by Country',
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
    # the final iteration value of the loop variable.  Because closures.
    age_filters = [('All', lambda r: True)]
    age_filters.append(('< 40', lambda r: r['age'] < 40))
    age_filters.append(('40+', lambda r: r['age'] >= 40))
    pref_by_age_counts = MultiCountDataSet(rows, 'preferred')
    pref_by_age_table = pref_by_age_counts.get_data_table(
        'Age', age_filters, label_with=make_preference_label)
    output['Database Preference by Age'] = {'target': 'preference_by_age',
                                            'data': pref_by_age_table,
                                            'type': 'stack'}

    print("GCDSurveyData = %s;" % json.dumps(output, indent=4))

    # Also make an entirely separate table of everything.
    dt = gviz_api.DataTable(HEADER_SPEC)
    processed_rows = []
    for r in rows:
        current_row = []
        for h in HEADER_SPEC:
            current_row.append(r[h[0]])
        processed_rows.append(current_row)

    dt.LoadData(processed_rows)
    print("GCDRawData = %s;" % json.dumps(json.loads(dt.ToJSon()), indent=4))
