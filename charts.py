#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

import json
import collections

import gviz_api


def make_label(value, label_map=None):
    """
    Given a value, creates a nicely formatted label for it.

    Requires a dictionary in which it first checks for a pre-defined
    label before attempting to produce a default label.

    Typically, the map will be set in a call to functools.partial()
    so that the resulting function takes only the value and can be
    passed along a list of values as a callback.
    """
    if label_map is None:
        label_map = {None: 'unspecified'}
    try:
        label = label_map[value]
    except KeyError:
        if type(value) in (unicode, str):
            label = value.replace('_', ' ').title()
        else:
            label = str(value)
    return label


class GoogleDataSet(object):
    def __init__(self, dataset):
        self._raw_dataset = list(dataset)

    def _get_counts(self, filter_by):
        counts = collections.Counter()
        for r in self._raw_dataset:
            if filter_by(r):
                if self._column_callable:
                    v = self._column_callable(r)
                else:
                    v = r[self._count_column]
                counts.update((v,))
        return counts

    def _make_table(self, spec, processed_rows):
        dt = gviz_api.DataTable(spec)
        dt.LoadData(processed_rows)
        return json.loads(dt.ToJSon())


def get_basic_reason(row):
    if row['indexing'] or row['collecting']:
        return 'interacting'
    if row['writing'] or row['academics']:
        return 'researching'
    # TODO: Handle weird bits
    else:
        return 'personal only'


class MultiCountDataSet(GoogleDataSet):
    # The data structure looks like this:
    #
    # [[bucket type] [bucket 1] [bucket 2] [bucket 3]]
    # [[filter 1]    [f1b1    ] [f1b2    ] [f1b3    ]]
    # [[filter 2]    [f2b2    ] [f2b2    ] [f2b3    ]]
    #
    # Here is an example of the description row & col.
    # This measures the reason, grouped four different
    # ways by social medial / mailing list participation.
    #
    # [[Reason]      [Personal] [Research] [Interactive]]
    # [[All]
    # [[Non-Social]
    # [[Followers]
    # [[Active]

    def __init__(self, dataset,
                 count_column, column_callable=None):
        super(MultiCountDataSet, self).__init__(dataset)
        self._count_column = count_column
        self._column_callable = column_callable
        self._data_spec = None

    def get_data_table(self,
                       filter_type_name='',
                       filters=(('All', lambda r: True),),
                       sort_by=None,
                       label_with=make_label):

        # We just assume that these all fit together b/c this is not
        # actually a general purpose library for the public.
        counts = [self._get_counts(f[1]) for f in filters]

        # For each set of counts, we will want a count for every key that
        # appears in any count.  If a key is missing in a set, it will be
        # assigned a count of zero because of how the Counter class works.
        # Otherwise the chart won't render.  These are the table's columns
        # starting from position 1.
        # Note also that passing None as sort_by to sorted() is equivalent
        # to not passing a sort_by argument.
        all_keys = sorted(reduce(lambda v1, v2: v1 | v2,
                                 [c.viewkeys() for c in counts]),
                          sort_by)

        # Chart column labels (which label rows in the DataTable)
        # are strings.
        header = [(filter_type_name, 'string')]

        # Chart values (the actual counts) are numbers.
        header.extend([(label_with(k), 'number') for k in all_keys])

        table = []
        for f, count in zip(filters, counts):
            row = [f[0]]
            row.extend([count[k] for k in all_keys])
            table.append(row)
        return self._make_table(header, table)


class CountDataSet(GoogleDataSet):
    def __init__(self, dataset, count_column, column_callable=None):
        super(CountDataSet, self).__init__(dataset)
        self._count_column = count_column
        self._column_callable = column_callable
        self._data_spec = [
            (make_label(self._count_column), 'string'),
            ('Count', 'number'),
        ]

    def get_data_table(self,
                       filter_by=lambda r: True,
                       sort_by=lambda a, b: cmp(b[1], a[1]),
                       label_with=make_label):
        """
        Filter, sort, and label the data, and return a graph viz
        table object from the results.

        By default, don't filter anything, sort in *descinding* order
        (note that b and and switch places in the call to cmp), and
        use the basic make_label function.

        The sort_by function is applied *after* the label_with and
        filter_by functions, and should be written accordingly.
        """
        counts = self._get_counts(filter_by)
        rows = [[label_with(k), c] for k, c in counts.iteritems()]

        # Use the pre-computed spec, nothing here (yet) requires
        # modification.
        return self._make_table(self._data_spec, sorted(rows, sort_by))
