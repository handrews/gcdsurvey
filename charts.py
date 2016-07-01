#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

import sys
import json
import collections
import functools

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
    # sys.stderr.write("'%r' -> '%s'\n" % (value, label))
    return label


class GoogleDataSet(object):
    def __init__(self, dataset):
        self._raw_dataset = list(dataset)

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
    # [[bucket type] [bucket 1] [bucket 2] [bucket 3]]
    # [[filter 1]    [f1b1    ] [f1b2    ] [f1b3    ]]
    # [[filter 2]    [f2b2    ] [f2b2    ] [f2b3    ]]

    # [[Reason]      [personal] [research] [interact]]
    # [[]
    # [[non social]
    # [[followers]
    # [[active]

    # MultiCountDataSet(dataset, 'Reason', 'Socialness',
    #                   lambda r: r[
    def __init__(self, dataset,
                 count_column, column_callable=None):
        super(MultiCountDataSet, self).__init__(dataset)
        self._count_column = count_column
        self._column_callable = column_callable
        self._data_spec = None

    # XXX: DUPLICATE from CountDataSet, inheritance or what?
    def _get_counts(self, filter_by):
        counts = collections.Counter()
        # filtered_dataset = [r for r in self._raw_dataset if filter_by(r)]

        # sys.stderr.write('\n%s\n\n' % '\n\n'.join(
        #                  [repr(r)
        #                   for r in self._raw_dataset
        #                   if filter_by(r)]))
        # sys.stderr.write('\n*************************\n%s\n\n' %
        #                  '\n\nXXXXXXXX\n\n'.join(map(repr, filtered_dataset)))

        # if self._column_callable:
        #     counts.update([self._column_callable(r) for r in filtered_dataset])
        # else:
        #     counts.update([r[self._count_column] for r in filtered_dataset])

        # raise Exception("Done!")

        for r in self._raw_dataset:
            if filter_by(r):
                if self._column_callable:
                    v = self._column_callable(r)
                    sys.stderr.write('\nCalculated: %r\n' % v)
                else:
                    v = r[self._count_column]
                    # sys.stderr.write('\n%s: %r\n' % (self._count_column, v))
                counts.update((v,))
                # sys.stderr.write('New count: %r\n\n' % counts[v])
            else:
                # sys.stderr.write('.')
                pass

        # counts.update([
        #     # flake8 loses its mind on wraped ternary ifs, so turn it off.
        #     self._column_callable(r) if self._column_callable    # noqa
        #                              else r[self._count_column]  # noqa
        #     for r in self._raw_dataset
        #     if filter_by(r)
        # ])
        return counts

    def get_data_table(self,
                       filter_type_name='',
                       filters=(('All', lambda r: True),),
                       sort_by=None,
                       label_with=make_label):

        # We just assume that these all fit together b/c this is not
        # actuall a general purpose library for the public.
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

        header = [(filter_type_name, 'string')]
        header.extend([(label_with(k), 'number') for k in all_keys])
        table = []
        spec = [('age', 'string')]
        spec.extend([('count', 'number') for x in xrange(len(all_keys))])
        for f, count in zip(filters, counts):
            row = [f[0]]
            row.extend([count[k] for k in all_keys])
            table.append(row)
        return self._make_table(header, table)
        # return self._make_table([('age', 'string'), ('count both', 'number'), ('count no', 'number'), ('count yes', 'number')], table)
        # raise Exception('\n[%r]\n[%s]' % (header, '\n '.join([repr(r) for r in table])))


class CountDataSet(GoogleDataSet):
    def __init__(self, dataset, count_column, column_callable=None):
        super(CountDataSet, self).__init__(dataset)
        self._count_column = count_column
        self._column_callable = column_callable
        self._data_spec = [
            (make_label(self._count_column), 'string'),
            ('Count', 'number'),
        ]

        # Even if we don't need all_counts, we do need to know the full
        # set of distinct elements so that we can set counts to zero
        # when they are filtered out entirely by a filter.
        # The keys in the counter are the values that we are counting.
        # self._all_counts = self._get_counts()
        # self._all_values = self._all_counts.keys()

    def _get_counts(self, filter_by):
        counts = collections.Counter()
        counts.update([
            # flake8 loses its mind on wraped ternary ifs, so turn it off.
            self._column_callable(r) if self._column_callable    # noqa
                                     else r[self._count_column]  # noqa
            for r in self._raw_dataset
            if filter_by(r)
        ])
        return counts

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
