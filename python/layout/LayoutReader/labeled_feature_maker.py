import logging
import os
import sys
import unittest
import pandas
import numpy
import random
from sklearn.preprocessing import MinMaxScaler
from pdf2image import convert_from_path, convert_from_bytes
import scipy.spatial as spatial

from layouteagle import config


sys.path.append(".")

from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.pathant.Converter import converter

FEATURES_FROM_PDF2HTMLEX = "features_from_pdf2htmlex"

@converter("htm", "feature")
class LabeledFeatureMaker(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (labeled_html_path, meta) in enumerate(labeled_paths):
            if "training" in self.flags and not any([tex in labeled_html_path for tex in ["tex1", 'tex2', 'tex3']]):
                continue

            if FEATURES_FROM_PDF2HTMLEX in self.flags:
                try:
                    feature_df = self.use_pdf2htmlEX_features(meta['html_path'] + ".feat")
                except FileNotFoundError as e:
                    self.logger.error("output of pdf2htmlEX was not found")
                    raise e
                except Exception as e:
                    self.logger.error(f"could not compute features, proceeding ... error was {e}")
                    raise e
            else:
                try:
                    feature_df, soup = self.compute_html_soup_features(labeled_html_path)
                except Exception as e:
                    self.logger.error("Could not compute features for this document, empty document?")
                    continue

            for random_i, final_feature_df in enumerate(self.feature_fuzz(feature_df)):




                final_feature_df = self.compute_complex_coordination_data(final_feature_df)

                final_feature_df["doc_id"] = str(doc_id) + ".random" + str(random_i)
                meta["doc_id"] = str(doc_id) + ".random" + str(random_i)
                meta['html_path'] = labeled_html_path
                min_max_scaler = MinMaxScaler()
                x = final_feature_df[config.cols_to_use].values
                x_scaled = min_max_scaler.fit_transform(x)
                df_temp = pandas.DataFrame(x_scaled, columns=config.cols_to_use, index=final_feature_df.index)
                final_feature_df[config.cols_to_use] = df_tem

                images = convert_from_path(meta["pdf_path"])
                for page_number, pil in enumerate(page_number, pil):
                    image_path = f'{meta["path"]}.{page_number}.jpg'
                    df['image_path'] = np.where(final_feature_df.page_number == page_number,
                                                final_feature_df.page_number.map({page_number:image_path}),
                                                final_feature_df.page_number
                     )
                    pil.save(image_path)

                yield final_feature_df, meta

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

    def page_web(self, page_df):

        self.point_density_frequence_per_page(page_df)

        if FEATURES_FROM_PDF2HTMLEX in self.flags:
            page_df['x1'] = page_df.x
            page_df['y1'] = page_df.y
            page_df['x2'] = page_df.x + page_df.ascent
            page_df['y2'] = page_df.y + page_df.descent
            page_df['center_x'] = [(x1 + x1) / 2 for x1, x2 in zip(page_df.x1, page_df.x2)]
            page_df['center_y'] = [(y1 + y1) / 2 for y1, y2 in zip(page_df.y1, page_df.y2)]

            points = list(zip(page_df.center_x, page_df.center_y))
            kd_tree = spatial.KDTree(points)

            try:
                all_nearest_points = \
                    [(p, [points[k] for k in kd_tree.query(p, k=config.layout_model_next_text_boxes)[1]])
                     for p in zip(page_df.center_x, page_df.center_y)]

                for k in range(config.layout_model_next_text_boxes):
                    page_df[f'nearest_{k}_center_x'], page_df[f'nearest_{k}_center_y'] = list(zip(*
                        [nearest_points[k] for p1, nearest_points in all_nearest_points]
                                                                                                  ))

            except Exception as e:
                print (points)
                self.logger.warning(f"not enough points in page to find {config.layout_model_next_text_boxes} nearest points, faking with 0.5")
                for k in range(config.layout_model_next_text_boxes):
                    page_df[f'nearest_{k}_center_x'] = [0.5] * len(page_df)
                    page_df[f'nearest_{k}_center_y'] = [0.5] * len(page_df)

            page_df['dxy1'] = self.distances(page_df, 'x1', 'y1', 'x2', 'y2')
            page_df['dxy2'] = self.distances(page_df, 'x2', 'y2', 'x1', 'y1')
            page_df['dxy3'] = self.distances(page_df, 'x1', 'y2', 'x2', 'y1')
            page_df['dxy4'] = self.distances(page_df, 'x2', 'y1', 'x1', 'y2')

            page_df['probascent'] = page_df.ascent.map(page_df.ascent.value_counts(normalize=True))
            page_df['probdescent'] = page_df.descent.map(page_df.descent.value_counts(normalize=True))

        return page_df

    def feature_fuzz(self, feature_df):
        yield feature_df

        if False and "training" in self.flags:
            def compute_fuzz(series, value):
                return value + round(random.uniform(-fuzz_percent, +fuzz_percent), 2) * max(series)

            def iter_col(series):
                if isinstance(series[0], float):
                    return series.apply(lambda x: compute_fuzz(series, x))
                else:
                    return series

            for feature_fuzz_range in config.feature_fuzz_ranges:
                for fuzz_percent in numpy.arange(*feature_fuzz_range):
                    yield feature_df.copy().apply(iter_col)


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
