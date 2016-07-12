#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function, absolute_import

import sys
import codecs
import json
import functools

import gviz_api

from support import (Line, REGIONS, COUNTRIES_BY_CODE)
from charts import make_label, CountDataSet, MultiCountDataSet

# Per the Google Charts specification.  We build up the data in a dict for
# each line, and then create a list matching this order at the very end
# to avoid maintaining parallel arrays.
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
    ('no_english', 'boolean'),
    ('improve_search', 'boolean'),
]
HEADER_TYPES = {h[0]: h[1] for h in HEADER_SPEC}


def parse_tsv(lines):
    # Throw away the header line, as we build headers more suitable
    # for charts instead.
    #
    # Also, for some reason, there are carriage returns in some fields, so
    # get rid of those here and in the main loop.
    Line(*next(lines).replace('\r', '').split('\t'))

    rows = []
    for line in lines:
        # Initialize with appropriate empty values per header specification.
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
        row['improve_search'] = fields.search

        rows.append(row)
    return rows


def make_social_tables():
    make_social_label = functools.partial(make_label, label_map={
        True: 'Non Social', False: 'Social'})


def make_age_filters():
    # Note: You cannot create lambdas in a loop, as they will all capture
    # the final iteration value of the loop variable.  Because closures.
    age_filters = [('All', lambda r: True)]
    age_filters.append(('< 40', lambda r: r['age'] < 40))
    age_filters.append(('40+', lambda r: r['age'] >= 40))
    return age_filters


def make_gender_tables(output):
    make_gender_label = functools.partial(make_label, label_map={
        'f': 'Female',
        'm': 'Male',
    })
    gender_counts = CountDataSet(rows, 'gender')
    gender_table = gender_counts.get_data_table(label_with=make_gender_label)
    output['Visitors by Gender'] = {
        'target': 'gender',
        'data': gender_table,
        'type': 'pie',
    }

    research_gender_table = gender_counts.get_data_table(
        label_with=make_gender_label,
        filter_by=lambda r: r['writing'])
    output['Researchers by Gender'] = {
        'target': 'research_gender',
        'data': research_gender_table,
        'type': 'pie',
    }


def make_country_tables(output):
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


def make_prefs_by_age_table(output, age_filters):
    make_preference_label = functools.partial(make_label, label_map={
        True: 'Prefers the GCD',
        None: 'Uses the GCD and other sites',
        False: 'Prefers other sites',
    })

    pref_by_age_counts = MultiCountDataSet(rows, 'preferred')
    pref_by_age_table = pref_by_age_counts.get_data_table(
        'Age', age_filters, label_with=make_preference_label)
    output['Database Preference by Age'] = {'target': 'preference_by_age',
                                            'data': pref_by_age_table,
                                            'type': 'stack'}


def make_raw_table():
    # Also make an entirely separate table of everything.
    dt = gviz_api.DataTable(HEADER_SPEC)
    processed_rows = []
    for r in rows:
        current_row = []
        for h in HEADER_SPEC:
            current_row.append(r[h[0]])
        processed_rows.append(current_row)

    dt.LoadData(processed_rows)
    return dt


if __name__ == '__main__':
    input_fd = codecs.getreader('utf-8')(sys.stdin)
    rows = parse_tsv(input_fd)

    js_data = {}

    age_filters = make_age_filters()

    make_gender_tables(js_data)
    make_country_tables(js_data)
    make_prefs_by_age_table(js_data, age_filters)

    raw_data = make_raw_table()

    print("GCDSurveyData = %s;" % json.dumps(js_data, indent=4))
    print("GCDRawData = %s;" % json.dumps(json.loads(raw_data.ToJSon()),
                                          indent=4))
