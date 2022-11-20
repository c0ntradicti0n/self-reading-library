import itertools
from collections import defaultdict
from functools import reduce
from typing import Callable

from more_itertools import first_true

from helpers.list_tools import nest
from helpers.nested_dict_tools import flatten


def tagStrip(t):
    if len(t) < 2:
        return [t, ""]
    try:
        return [t[0:1], t[2:]]
    except Exception as e:
        raise ValueError(f"No t.slice of {t}`")


def annotation2spans(annotation):
    value = [[w, *tagStrip(t), i] for i, [w, t] in enumerate(annotation)]

    return [
        (g["group"], sp["value"])
        for g in nest(["[2]", lambda item: item[1] in ["B", "U"]], value)
        for sp in g["value"]
    ]


def annotation2span_sets(annotation):
    spans = annotation2spans(annotation)

    result = defaultdict(list)

    for span in spans:
        appended = False

        for k, v in result.items():
            if any(
                abs(t[3] - span[1][0][3]) == 1 or abs(t[3] - span[1][-1][3]) == 1
                for sp in v
                for t in sp[1]
            ):
                result[k].append(span)
                appended = True

        if not appended:
            result[len(result)] = [span]

    return result


def span_sets2kind_sets(span_sets):
    return nest("[0]", [el for els in list(span_sets.values()) for el in els])


import unittest


class TestStringMethods(unittest.TestCase):
    testNestAnnotation = [
        ["the", "B-CONTRAST"],
        ["lazy", "B-SUBJECT"],
        ["yellow", "I-SUBJECT"],
        ["socks", "L-SUBJECT"],
        ["glued", "I-CONTRAST"],
        ["on", "I-CONTRAST"],
        ["the", "I-CONTRAST"],
        ["wall", "L-CONTRAST"],
        [".", "O"],
        ["the", "B-SUBJECT"],
        ["lazy", "I-SUBJECT"],
        ["yellow", "I-SUBJECT"],
        ["socks", "L-SUBJECT"],
        ["glued", "B-CONTRAST"],
        ["on", "I-CONTRAST"],
        ["the", "I-CONTRAST"],
        ["wall", "L-CONTRAST"],
        [".", "O"],
    ]

    def test_nest(self):
        value = [
            [w, *tagStrip(t), i] for i, [w, t] in enumerate(self.testNestAnnotation)
        ]
        result = nest(["[2]", lambda item: item[1] in ["B", "U"]], value)
        self.assertEqual(
            [
                {
                    "group": "CONTRAST",
                    "value": [
                        {
                            "group": 1,
                            "value": [
                                ["the", "B", "CONTRAST", 0],
                                ["glued", "I", "CONTRAST", 4],
                                ["on", "I", "CONTRAST", 5],
                                ["the", "I", "CONTRAST", 6],
                                ["wall", "L", "CONTRAST", 7],
                            ],
                        },
                        {
                            "group": 2,
                            "value": [
                                ["glued", "B", "CONTRAST", 13],
                                ["on", "I", "CONTRAST", 14],
                                ["the", "I", "CONTRAST", 15],
                                ["wall", "L", "CONTRAST", 16],
                            ],
                        },
                    ],
                },
                {
                    "group": "SUBJECT",
                    "value": [
                        {
                            "group": 1,
                            "value": [
                                ["lazy", "B", "SUBJECT", 1],
                                ["yellow", "I", "SUBJECT", 2],
                                ["socks", "L", "SUBJECT", 3],
                            ],
                        },
                        {
                            "group": 2,
                            "value": [
                                ["the", "B", "SUBJECT", 9],
                                ["lazy", "I", "SUBJECT", 10],
                                ["yellow", "I", "SUBJECT", 11],
                                ["socks", "L", "SUBJECT", 12],
                            ],
                        },
                    ],
                },
            ],
            result,
        )

    def test_annotation2span(self):
        res = annotation2spans(self.testNestAnnotation)
        self.assertEqual(
            res,
            [
                (
                    "CONTRAST",
                    [
                        ["the", "B", "CONTRAST", 0],
                        ["glued", "I", "CONTRAST", 4],
                        ["on", "I", "CONTRAST", 5],
                        ["the", "I", "CONTRAST", 6],
                        ["wall", "L", "CONTRAST", 7],
                    ],
                ),
                (
                    "CONTRAST",
                    [
                        ["glued", "B", "CONTRAST", 13],
                        ["on", "I", "CONTRAST", 14],
                        ["the", "I", "CONTRAST", 15],
                        ["wall", "L", "CONTRAST", 16],
                    ],
                ),
                (
                    "SUBJECT",
                    [
                        ["lazy", "B", "SUBJECT", 1],
                        ["yellow", "I", "SUBJECT", 2],
                        ["socks", "L", "SUBJECT", 3],
                    ],
                ),
                (
                    "SUBJECT",
                    [
                        ["the", "B", "SUBJECT", 9],
                        ["lazy", "I", "SUBJECT", 10],
                        ["yellow", "I", "SUBJECT", 11],
                        ["socks", "L", "SUBJECT", 12],
                    ],
                ),
            ],
        )

    def test_annotation2span_sets(self):
        res = annotation2span_sets(self.testNestAnnotation)
        self.assertEqual(
            {
                0: [
                    (
                        "CONTRAST",
                        [
                            ["the", "B", "CONTRAST", 0],
                            ["glued", "I", "CONTRAST", 4],
                            ["on", "I", "CONTRAST", 5],
                            ["the", "I", "CONTRAST", 6],
                            ["wall", "L", "CONTRAST", 7],
                        ],
                    ),
                    (
                        "SUBJECT",
                        [
                            ["lazy", "B", "SUBJECT", 1],
                            ["yellow", "I", "SUBJECT", 2],
                            ["socks", "L", "SUBJECT", 3],
                        ],
                    ),
                ],
                1: [
                    (
                        "CONTRAST",
                        [
                            ["glued", "B", "CONTRAST", 13],
                            ["on", "I", "CONTRAST", 14],
                            ["the", "I", "CONTRAST", 15],
                            ["wall", "L", "CONTRAST", 16],
                        ],
                    ),
                    (
                        "SUBJECT",
                        [
                            ["the", "B", "SUBJECT", 9],
                            ["lazy", "I", "SUBJECT", 10],
                            ["yellow", "I", "SUBJECT", 11],
                            ["socks", "L", "SUBJECT", 12],
                        ],
                    ),
                ],
            },
            res,
        )

    def test_grouping_spans(self):
        start = {
            "2": [
                [
                    "CONTRAST",
                    [
                        ["the", "B", "CONTRAST", 0],
                        ["glued", "I", "CONTRAST", 4],
                        ["on", "I", "CONTRAST", 5],
                        ["the", "I", "CONTRAST", 6],
                        ["wall", "L", "CONTRAST", 7],
                    ],
                ],
                [
                    "SUBJECT",
                    [
                        ["lazy", "B", "SUBJECT", 1],
                        ["yellow", "I", "SUBJECT", 2],
                        ["socks", "L", "SUBJECT", 3],
                    ],
                ],
            ],
            "1": [
                [
                    "CONTRAST",
                    [
                        ["glued", "B", "CONTRAST", 13],
                        ["on", "I", "CONTRAST", 14],
                        ["the", "I", "CONTRAST", 15],
                        ["wall", "L", "CONTRAST", 16],
                    ],
                ],
                [
                    "SUBJECT",
                    [
                        ["the", "B", "SUBJECT", 9],
                        ["lazy", "I", "SUBJECT", 10],
                        ["yellow", "I", "SUBJECT", 11],
                        ["socks", "L", "SUBJECT", 12],
                    ],
                ],
            ],
        }

        self.assertEqual(
            [
                {
                    "group": "CONTRAST",
                    "value": [
                        [
                            "CONTRAST",
                            [
                                ["the", "B", "CONTRAST", 0],
                                ["glued", "I", "CONTRAST", 4],
                                ["on", "I", "CONTRAST", 5],
                                ["the", "I", "CONTRAST", 6],
                                ["wall", "L", "CONTRAST", 7],
                            ],
                        ],
                        [
                            "CONTRAST",
                            [
                                ["glued", "B", "CONTRAST", 13],
                                ["on", "I", "CONTRAST", 14],
                                ["the", "I", "CONTRAST", 15],
                                ["wall", "L", "CONTRAST", 16],
                            ],
                        ],
                    ],
                },
                {
                    "group": "SUBJECT",
                    "value": [
                        [
                            "SUBJECT",
                            [
                                ["lazy", "B", "SUBJECT", 1],
                                ["yellow", "I", "SUBJECT", 2],
                                ["socks", "L", "SUBJECT", 3],
                            ],
                        ],
                        [
                            "SUBJECT",
                            [
                                ["the", "B", "SUBJECT", 9],
                                ["lazy", "I", "SUBJECT", 10],
                                ["yellow", "I", "SUBJECT", 11],
                                ["socks", "L", "SUBJECT", 12],
                            ],
                        ],
                    ],
                },
            ],
            span_sets2kind_sets(start),
        )


if __name__ == "__main__":
    unittest.main()
