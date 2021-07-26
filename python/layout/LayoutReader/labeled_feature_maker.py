import logging
import os
import sys
import unittest

import spatial as spatial

from python.layouteagle import config

sys.path.append(".")

from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.pathant.Converter import converter


@converter("htm", "feature")
class LabeledFeatureMaker(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (labeled_html_path, meta) in enumerate(labeled_paths):
            print(doc_id, labeled_html_path)
            try:
                feature_df = self.read_positional_data(
                    meta['filename'] + ".feat")  # self.generate_data_for_file(labeled_html_path)

            except FileNotFoundError as e:
                logging.error("output of pdf2htmlEX was not found")
                continue
            except Exception as e:
                self.logger.error(f"could not compute features, proceeding ... error was {e}")
                raise e
                continue

            feature_df = self.compute_complex_coordination_data(feature_df)

            feature_df["doc_id"] = doc_id
            if False and self.debug:
                debug_html_path = labeled_html_path + ".debug.html"
                self.tfu = TrueFormatUpmarkerPDF2HTMLEX(debug=True)
                self.tfu.label_lookup = Lookup(self.tfu.label_strings)
                self.tfu.generate_css_tagging_document(html_read_from=labeled_html_path, html_write_to=debug_html_path)
                os.system(f"google-chrome {debug_html_path}")

            yield feature_df, meta

    def compute_complex_coordination_data(self, feature_df):
        feature_df = feature_df.groupby(['page_number']).apply(self.page_web)
        return feature_df

    def distances(self, sub_df, ax, ay, bx, by):
        return [min([((xa - xb) ** 2 + (ya - yb) ** 2)
                     for xa, ya in list(zip(sub_df[ax], sub_df[ay]))
                     if ya != yb and xa != xb])
                for xb, yb in list(zip(sub_df[bx], sub_df[by]))]

    def sinuses(self, sub_df, ax, ay, bx, by):
        return [min([round((((xa - xb) / (ya - yb))), 2)
                     for xa, ya in list(zip(sub_df[ax], sub_df[ay]))
                     if ya != yb and xa != xb])
                for xb, yb in list(zip(sub_df[bx], sub_df[by]))]

    def page_web(self, sub_df):
        sub_df['x1'] = sub_df.x
        sub_df['y1'] = sub_df.y
        sub_df['x2'] = sub_df.x + sub_df.ascent
        sub_df['y2'] = sub_df.y + sub_df.descent
        sub_df['center_x'] = [(x1 + x1) / 2 for x1, x2 in zip(sub_df.x1, sub_df.x2)]
        sub_df['center_y'] = [(y1 + y1) / 2 for y1, y2 in zip(sub_df.y1, sub_df.y2)]

        points = list(zip(sub_df.center_x, sub_df.center_y))
        kdTree = spatial.KDTree(points)
        for k in range(config.layout_model_next_text_boxes):
            sub_df[f'nearest_{k}_center_x'], sub_df[f'nearest_{k}_center_y'] = \
                list(zip([points[kdTree.query(p, k=k)][1] for p in zip(sub_df.center_x, sub_df.center_y)]))

        sub_df['dxy1'] = self.distances(sub_df, 'x1', 'y1', 'x2', 'y2')
        sub_df['dxy2'] = self.distances(sub_df, 'x2', 'y2', 'x1', 'y1')
        sub_df['dxy3'] = self.distances(sub_df, 'x1', 'y2', 'x2', 'y1')
        sub_df['dxy4'] = self.distances(sub_df, 'x2', 'y1', 'x1', 'y2')
        sub_df['sin1'] = self.sinuses(sub_df, 'x1', 'y1', 'x2', 'y2')
        sub_df['sin2'] = self.sinuses(sub_df, 'x2', 'y2', 'x1', 'y1')
        sub_df['sin3'] = self.sinuses(sub_df, 'x1', 'y2', 'x2', 'y1')
        sub_df['sin4'] = self.sinuses(sub_df, 'x2', 'y1', 'x1', 'y2')
        # frequence of values in this table, the more often a value is there,
        # the more probable to be floeating text
        sub_df['probsin1'] = sub_df.sin1.map(sub_df.sin1.value_counts(normalize=True))

        sub_df['probsin2'] = sub_df.sin2.map(sub_df.sin2.value_counts(normalize=True))

        sub_df['probsin3'] = sub_df.sin3.map(sub_df.sin3.value_counts(normalize=True))

        sub_df['probsin4'] = sub_df.sin4.map(sub_df.sin4.value_counts(normalize=True))
        # some max and min of text size to recognize a title page with abstract
        sub_df['probascent'] = sub_df.ascent.map(sub_df.ascent.value_counts(normalize=True))
        sub_df['probdescent'] = sub_df.descent.map(sub_df.descent.value_counts(normalize=True))

        return sub_df


class TestComputedFeatureTable(unittest.TestCase):
    def init(self):
        from python.layout.LayoutReader.labeled_feature_maker import LabeledFeatureMaker

        latex_maker = LabeledFeatureMaker
        res = list(latex_maker.__call__(
            [(
             "/home/finn/PycharmProjects/LayoutEagle/python/.layouteagle/tex_data/8d885eb85effba6b693ab5c3a82715ee/main.tex1.labeled.pdf",
             {
                 "filename": ".layouteagle/tex_data/8d885eb85effba6b693ab5c3a82715ee/main.tex1.labeled.pdf"
             })]))
        self.df = res[0][0]

    def test_spider_web_lines(self):
        self.init()

        cols = self.df.columns
        assert ("sin1" in cols)
        assert ("probsin1" in cols)
        assert ("probascent" in cols)
        assert ("dxy1" in cols)
        assert ("qwertz" not in cols)
        print(cols)


if __name__ == '__main__':
    unittest.main()
