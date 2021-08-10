import logging
import os
import sys
import unittest
import pandas
import numpy
import random
from sklearn.preprocessing import MinMaxScaler
import scipy.spatial as spatial
from layouteagle import config
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import pdfminer
from collections import namedtuple

sys.path.append(".")

from layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from layouteagle.pathant.Converter import converter

FEATURES_FROM_PDF2HTMLEX = "features_from_pdf2htmlex"

@converter(["labeled.pdf", 'pdf'], "feature")
class BoxFeatureMaker(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (labeled_pdf_path, meta) in enumerate(labeled_paths):
            if "training" in self.flags and not any([tex in labeled_pdf_path for tex in ["tex1", 'tex2', 'tex3']]):
                continue

            pdfminer

            feature_gen = self.mine_pdf(labeled_pdf_path)
            feature_df = pandas.DataFrame(
                list(feature_gen),
            columns=BoxFeatureMaker.TextBoxData._fields)

            for random_i, final_feature_df in enumerate(self.feature_fuzz(feature_df)):
                final_feature_df = self.compute_complex_coordination_data(final_feature_df)

                final_feature_df["doc_id"] = str(doc_id) + ".random" + str(random_i)
                meta["doc_id"] = str(doc_id) + ".random" + str(random_i)
                meta['html_path'] = labeled_pdf_path
                min_max_scaler = MinMaxScaler()
                x = final_feature_df[config.cols_to_use].values
                x_scaled = min_max_scaler.fit_transform(x)
                df_temp = pandas.DataFrame(x_scaled, columns=config.cols_to_use, index=final_feature_df.index)
                final_feature_df[config.cols_to_use] = df_temp

                yield final_feature_df, meta

    TextBoxData = namedtuple("TextBoxData", ["page_number","x","y", "x0", "x1", "y0", "y1", "height", "width", "text", "LABEL"])

    def mine_pdf(self, pdf_path):
        for page_number, page_layout in enumerate(extract_pages(pdf_path)):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text()
                    label = self.determine_layout_label_from_text(text)
                    feature = BoxFeatureMaker.TextBoxData(
                        page_number,
                        element.x0, element.y0,
                        element.x0, element.x0+element.height,
                        element.y0, element.y0+element.width,
                        element.height, element.width,
                        text,
                        label)
                    yield feature._asdict()


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

        self.point_density_frequence_per_page(sub_df)

        if FEATURES_FROM_PDF2HTMLEX in self.flags:
            sub_df['x1'] = sub_df.x
            sub_df['y1'] = sub_df.y
            sub_df['x2'] = sub_df.x + sub_df.ascent
            sub_df['y2'] = sub_df.y + sub_df.descent
            sub_df['center_x'] = [(x1 + x1) / 2 for x1, x2 in zip(sub_df.x1, sub_df.x2)]
            sub_df['center_y'] = [(y1 + y1) / 2 for y1, y2 in zip(sub_df.y1, sub_df.y2)]

            points = list(zip(sub_df.center_x, sub_df.center_y))
            kd_tree = spatial.KDTree(points)

            try:
                all_nearest_points = \
                    [(p, [points[k] for k in kd_tree.query(p, k=config.layout_model_next_text_boxes)[1]])
                     for p in zip(sub_df.center_x, sub_df.center_y)]

                for k in range(config.layout_model_next_text_boxes):
                    sub_df[f'nearest_{k}_center_x'], sub_df[f'nearest_{k}_center_y'] = list(zip(*
                        [nearest_points[k] for p1, nearest_points in all_nearest_points]
                    ))

            except Exception as e:
                print (points)
                self.logger.warning(f"not enough points in page to find {config.layout_model_next_text_boxes} nearest points, faking with 0.5")
                for k in range(config.layout_model_next_text_boxes):
                    sub_df[f'nearest_{k}_center_x'] = [0.5] * len(sub_df)
                    sub_df[f'nearest_{k}_center_y'] = [0.5] * len(sub_df)

            sub_df['dxy1'] = self.distances(sub_df, 'x1', 'y1', 'x2', 'y2')
            sub_df['dxy2'] = self.distances(sub_df, 'x2', 'y2', 'x1', 'y1')
            sub_df['dxy3'] = self.distances(sub_df, 'x1', 'y2', 'x2', 'y1')
            sub_df['dxy4'] = self.distances(sub_df, 'x2', 'y1', 'x1', 'y2')

            sub_df['probascent'] = sub_df.ascent.map(sub_df.ascent.value_counts(normalize=True))
            sub_df['probdescent'] = sub_df.descent.map(sub_df.descent.value_counts(normalize=True))

        return sub_df


    FeatureKinds = namedtuple(
        "FeatureKinds",
        ["box_schema"])

    edges = numpy.array(
        [[0, 0, config.reader_width, config.reader_height]])
    def analyse_point_density_frequence(self, page_features, debug=True, axe_len_X=100, axe_len_Y=100) -> FeatureKinds:
        boxes = numpy.column_stack((page_features.x0, page_features.y0, page_features.x1, page_features.y1))

        indices = numpy.einsum(
            "ij,j->ij",
           boxes,
           [axe_len_X/config.reader_width,
            axe_len_Y/config.reader_height,
            axe_len_X/config.reader_width,
            axe_len_Y/config.reader_height]
        ).astype(int)

        box_schema_pics = []
        for _x0, _y0, _x1, _y1 in indices:
            box_schema = numpy.ones((axe_len_X, axe_len_Y))

            for x0, y0, x1, y1 in indices:
                try:
                    box_schema[x0:x1+1, y0:y1+1] = box_schema[x0:x1+1, y0:y1+1] + 1
                except IndexError:
                    self.logger.error("Indexes wrong after index normalization ")

            box_schema[_x0:_x1+1, _y0:_y1+1] = box_schema[_x0:_x1+1, _y0:_y1+1] * -1

            box_schema = (box_schema) / numpy.amax(box_schema)

            box_schema_pics.append(box_schema)

        return box_schema_pics


    def point_density_frequence_per_page(self, features, **kwargs):
        # map computation to pageclusters
        page_groups = features.groupby(by="page_number").apply(
            lambda page_group: self.analyse_point_density_frequence(
                page_group,
                **kwargs)
        ).tolist()
        features["box_schema"] = [feature for page_group in page_groups for feature in page_group]
        return features

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
