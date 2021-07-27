import logging
import os
import pathlib
from typing import Dict

import bs4

from collections import Counter, defaultdict, namedtuple
import more_itertools
import itertools

import numpy
import pandas

from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks

import matplotlib.pyplot as plt
import seaborn as sns
import regex
from scipy.spatial import distance_matrix

from layouteagle import config
from helpers.list_tools import threewise

from layout.LayoutReader.trueformatupmarker import TrueFormatUpmarker

logging.getLogger().setLevel(logging.WARNING)


class TrueFormatUpmarkerPDF2HTMLEX(TrueFormatUpmarker):
    replacement_mapping_tag2tag = {
        "div": "z"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, replacements=self.replacement_mapping_tag2tag, **kwargs)

    def __call__(self, pdf_paths, **kwargs):
        for pdf_path in pdf_paths:
            self.pdf2htmlEX(pdf_path)
            pdf_obj = self.generate_css_tagging_document()
            yield pdf_obj

    feat_regex = regex.compile(
        r"(?<text>.*?) ?(?<word_num>\d+) (?<page_number>\d+) (?<width>-?\d+(?:\.\d+)?) (?<ascent>-?\d+(?:\.\d+)?) (?<descent>-?\d+(?:\.\d+)?) (?<x>-?\d+(?:\.\d+)?) (?<y>-?\d+(?:\.\d+)?)$")

    def read_positional_data(self, path):
        with open(path, 'r', errors='ignore') as f:
            lines = f.readlines()
            matches = [match for match in self.add_layoutlabel_from_text(lines)]
        if not matches:
            raise IndexError
        return pandas.DataFrame(matches)

    def add_layoutlabel_from_text(self, lines):
        for line in lines:
            match = regex.match(self.feat_regex, line)
            if match:
                match_dict = match.groupdict()

                try:
                    yield {
                        **{k: float(v) for k, v in match_dict.items() if k != "text"},
                        "text": match_dict['text'],
                        "layoutlabel": next(
                            (label for label in self.label_strings[0:-1] if
                             label in match_dict['text'].replace(" ", "")),
                            self.label_strings[-1])}
                except Exception as e:
                    raise e

    def generate_css_tagging_document(self, html_read_from="", html_write_to="", parameterizing=False,
                                      premade_features=None, premade_soup=None):
        """
        This manipulates an html-file from the result of pdf2htmlEX, that inserts word for word tags with css ids
        to apply markup to these words only with a css-file, without changing this document again.

        This has to restore the semantics of the layout, as the reading sequence of left right, top to bottom,
        column for column, page for page. Other layout things should disappear from the text sequence.
        """
        if isinstance(premade_features, pandas.DataFrame) and isinstance(premade_soup, bs4.BeautifulSoup):
            features = premade_features
            soup = premade_soup
        else:
            features, soup = self.generate_data_for_file(html_read_from)

        self.manipulate_document(soup=soup,
                                 features=features)

        # sanitizing
        # change '<' and '>' mail adress of pdf2htmlEX-author, because js thinks, it's a tag
        with open(html_write_to, "w",
                  encoding='utf8') as file:
            file.write(str(soup).replace("<coolwanglu@gmail.com>", "coolwanglu@gmail.com"))

        self.pdf_obj.features = features
        self.pdf_obj.text = " ".join(self.word_index.values())
        self.pdf_obj.indexed_words = self.word_index
        return self.pdf_obj

    def generate_data_for_file(self, html_read_from):
        soup = self.make_soup(html_read_from)
        # create data and features for clustering
        self.css_dict = self.get_css(soup)

        try:
            self.features = self.extract_features(soup=soup)
        except:
            raise
        self.pdf_obj.columns = self.number_columns
        self.pdf_obj.features = self.features
        return self.features, soup

    def make_soup(self, html_read_from):
        with open(html_read_from, 'r', encoding='utf8') as f:
            soup = bs4.BeautifulSoup(f.read(), features='lxml')
        return soup

    def get_page_tags(self, soup):
        return soup.select("div[data-page-no]")

    def assign_labels_from_div_content(self, feature_df: pandas.DataFrame):
        page_cluster_lr_groups = self.make_reading_sequence(feature_df)
        self.make_text_per_page(page_cluster_lr_groups)
        return feature_df

    def make_text_per_page(self, page_cluster_lr_groups):
        self.pdf_obj.pages_to_column_to_text = {
            page_number: {cluster: cluster_content["text"]
                          for cluster, cluster_content in page_content}
            for page_number, page_content in page_cluster_lr_groups.items()

        }

    def make_reading_sequence(self, feature_df):
        page_cluster_lr_groups = defaultdict(list)
        for page, page_group in feature_df.groupby(by="page_number"):
            # itertools would break up the clusters, when the clusters are unsorted
            # TODO right to left and up to down!
            # Assuming, also column labels have bpdf2htmlEX.htmleen sorted yet from left to right

            groups_of_clusters = page_group.groupby(by="layoutlabel")

            groups_of_clusters = sorted(groups_of_clusters,
                                        key=lambda cluster_and_cluster_group: cluster_and_cluster_group[1].x.mean())

            page_cluster_up_bottom_groups = \
                [(new_cluster, cluster_group.sort_values(by="y"))
                 for new_cluster, (cluster, cluster_group) in enumerate(groups_of_clusters)
                 ]

            page_cluster_lr_groups[page] = \
                sorted(page_cluster_up_bottom_groups, key=lambda c: c[1].x.mean())
        # feature_df["reading_sequence"] = list(more_itertools.flatten([cluster_content["index"].tolist()
        #                                                              for page_number, page_content in
        #                                                              page_cluster_lr_groups.items()
        #                                                              for cluster, cluster_content in page_content
        #                                                              ]))
        return page_cluster_lr_groups

    FeatureStuff = namedtuple("FeatureStuff", ["divs", "coords", "data", "density_field", "labels"])

    def extract_features(self, soup) -> FeatureStuff:
        features = pandas.DataFrame()

        # Collect divs (that they have an x... attribute, that is generated by pdf2htmlEX)
        page_tags = list(self.get_page_tags(soup))
        page_to_divs = self.collect_pages_dict(page_tags)

        i = itertools.count()
        features["index"], features["page_number"], features["divs"] = \
            list(list(x) for x in zip(*[(next(i), pn, div) for pn, divs in page_to_divs for div in divs]))
        features["len"] = features.divs.apply(lambda div: len(div.text))

        # Generate positional features
        self.set_css_attributes(features)
        self.point_density_frequence_per_page(features, debug=True)
        return features

    div_selector = 'div[class*=x]'

    def collect_pages_dict(self, pages):
        page_to_divs = [(page_number, page.select(self.div_selector)) for page_number, page in enumerate(pages)]
        return page_to_divs

    def get_pdf2htmlEX_header(tag):
        return tag.attrs['class'][3]

    def debug_pic(self, clusterer, coords, debug_pic_name, outliers):
        color_palette = sns.color_palette('deep', 20)
        cluster_colors = [color_palette[x] if x >= 0
                          else (0.5, 0.5, 0.5)
                          for x in clusterer.labels_]
        cluster_member_colors = [sns.desaturate(x, p) for x, p in
                                 zip(cluster_colors, clusterer.probabilities_)]
        plt.scatter(*list(coords), c=cluster_member_colors, linewidth=0)

        plt.savefig(debug_pic_name + ".png", bbox_inches='tight')

    def get_declaration_value(self, declaration, key):
        try:
            return [decla.value[0].value for decla in declaration if decla.name == key][0]
        except:
            logging.error(f"{key} not in {str(declaration)}")
            return 0

    point_before = (0, 0)

    assinging_features_to_css_class_startswith = {
        'height': "h",
        'font-size': "fs",
        'line-height': "ff",
        'left': "x",
        'bottom': "y"
    }

    def css_class_of_tag(self, tag):
        for lookup_attribute, attr_start, in self.assinging_features_to_css_class_startswith.items():
            yield next(filter(lambda x: x.startswith(attr_start), tag.attrs['class']), None), lookup_attribute

    def set_css_attributes(self, features):
        features["tag_attributes"] = features.divs.apply(self.css_class_of_tag).apply(list)
        concrete_features = pandas.DataFrame(features.tag_attributes.tolist(),
                                             columns=list(self.assinging_features_to_css_class_startswith.keys()))

        for feature_name in concrete_features.columns:
            try:
                features[feature_name] = concrete_features[feature_name].apply(
                    lambda class_and_attribute: self.css_dict_lookup(class_and_attribute))
            except KeyError:
                raise

        features.rename(columns={"bottom": "y", "left": "x"}, inplace=True)

    def css_dict_lookup(self, css_class_and_attribute):
        if css_class_and_attribute[0] == None:
            return -1
        return self.get_declaration_value(self.css_dict[css_class_and_attribute[0]], css_class_and_attribute[1])

    def point_density_frequence_per_page(self, features, **kwargs):
        # map computation to pageclusters
        page_groups = features.groupby(by="page_number").apply(
            lambda page_group: self.analyse_point_density_frequence(
                page_group,
                **kwargs)
        ).tolist()
        other_feature_kinds_stacked = self.FeatureKinds(*list(zip(*page_groups)))

        self.number_columns = self.most_common_value(other_feature_kinds_stacked.number_of_columns)

        coarse_grained_field = sum(f for i, f in enumerate(other_feature_kinds_stacked.coarse_grained_field))

        features["coarse_grained_pdf"] = numpy.hstack(other_feature_kinds_stacked.coarse_grained_pdfs)
        features["fine_grained_pdf"] = numpy.hstack(other_feature_kinds_stacked.fine_grained_pdfs)

        features["distance_vector"] = [distance_vector for distance_matrix in other_feature_kinds_stacked.distances for
                                       distance_vector in distance_matrix]
        features["angle"] = [angle_vector for angle_matrix in other_feature_kinds_stacked.angles for angle_vector in
                             angle_matrix]
        features["x_profile"] = [x_profile_vector
                                 for x_profile_vector, angle_matrix in zip(other_feature_kinds_stacked.x_profile,
                                                                           other_feature_kinds_stacked.angles) for _ in
                                 angle_matrix]

        features["y_profile"] = [y_profile_vector
                                 for y_profile_vector, angle_matrix in zip(other_feature_kinds_stacked.y_profile,
                                                                           other_feature_kinds_stacked.angles) for _ in
                                 angle_matrix]
        return coarse_grained_field

    edges = numpy.array(
        [[0, 0], [0, config.reader_height], [config.reader_width, 0], [config.reader_width, config.reader_height]])

    def normalized(self, a):
        return a / [a_line.max() - a_line.min() for a_line in a.T]

    FeatureKinds = namedtuple(
        "FeatureKinds",
        ["coarse_grained_pdfs", "fine_grained_pdfs", "coarse_grained_field", "number_of_columns",
         "distances", "angles", 'x_profile', 'y_profile'])

    def analyse_point_density_frequence(self, page_features, debug=True, axe_len_X=100, axe_len_Y=100) -> FeatureKinds:
        points2d = numpy.column_stack((page_features.x, page_features.y))

        edges_and_points = numpy.vstack((points2d, self.edges))
        edges_and_points = self.normalized(edges_and_points)
        edges_and_points = edges_and_points[:-4]
        indices = (edges_and_points * [axe_len_X - 1, axe_len_Y - 1]).astype(int)

        dotted = numpy.zeros((100, 100))

        try:
            dotted[indices[:, 0], indices[:, 1]] = 1
        except IndexError:
            logging.error("indexes wrong after index nomralisation ")

        coarse_grained_field = gaussian_filter(dotted, sigma=3)
        coarse_grained_pdfs = coarse_grained_field[indices[:, 0], indices[:, 1]]

        fine_grained_field = gaussian_filter(dotted, sigma=2)
        fine_grained_pdfs = fine_grained_field[indices[:, 0], indices[:, 1]]

        distances = distance_matrix(points2d, points2d)
        angles = angles = numpy.array(
            [[numpy.arctan2(p2[1] - p1[1], p2[0] - p1[0]) for p1 in points2d] for p2 in points2d])

        number_of_columns = self.number_of_columns(density2D=fine_grained_field.T)

        x_profile = numpy.sum(dotted, axis=0)
        y_profile = numpy.sum(dotted, axis=1)

        return self.FeatureKinds(coarse_grained_pdfs, fine_grained_pdfs, coarse_grained_field, number_of_columns,
                                 distances, angles, x_profile, y_profile)

    def most_common_value(self, values, constraint=None):
        if constraint:
            test_values = [v for v in values if constraint(v)]
        else:
            test_values = values
        counts = Counter(test_values)
        return max(counts, key=counts.get)

    def create_eval_range(self, number, sigma=0.5, resolution=0.2):
        start = number * (1 - sigma)
        end = number * (1 + sigma)
        step = (end - start) * resolution
        return numpy.arange(start, end, step)

    def collect_all_divs(self, soup):
        return soup.select('div[class*=x]')

    def number_of_columns(self, density2D):
        peaks_at_height_steps = []
        for height in range(
                int(config.page_array_model * 0.1),
                int(config.page_array_model * 0.9),
                int(config.page_array_model * 0.01)):
            peaks, _ = find_peaks(density2D[height], distance=15, prominence=0.000001)
            peaks_at_height_steps.append(peaks)
        lens = [len(peaks) for peaks in peaks_at_height_steps if len(peaks) != 0]
        number_of_clumns = self.most_common_value(lens)
        if number_of_clumns == 0:
            number_of_clumns = 1
        return number_of_clumns

    def header_footer_mask(self, field, pdfs, points, number_of_culumns, divs):
        mask = numpy.full_like(pdfs, False).astype(bool)

        indexed_points = list(enumerate(points))
        indices = numpy.array(range(len(points)))
        # raw column sorting

        left_border = min(points[:, 0][points[:, 0] > 0.05])
        x_sorted_points = [(
            int(((indexed_point[1][0] - left_border + 0.9) / (1 - 2 * left_border) * number_of_culumns)),
            indexed_point)
            for indexed_point in indexed_points]

        if not (len({t[0] for t in x_sorted_points}) == number_of_culumns):
            logging.info("other number of columns detexted, than sorted to")
        # raw top down sorting
        xy_sorted_points = sorted(x_sorted_points, key=lambda x: x[0] * 1000 - x[1][1][1])

        y_sorted_indexed_points = [(len(points) + 1, 0)] + \
                                  [(column_index_point_tuple[1][0], column_index_point_tuple[1][1][1])
                                   for column_index_point_tuple
                                   in xy_sorted_points] + \
                                  [(len(points) + 2, 1)]

        indexed_distances = [(i2, list((numpy.abs(b - a), numpy.abs(c - b))))
                             for (i1, a), (i2, b), (i3, c)
                             in threewise(y_sorted_indexed_points)]
        dY = list(id[1] for id in indexed_distances)
        dI = numpy.array(list(id[0] for id in indexed_distances))

        # If there are text boxes on the same height, the distance will be very small due to rounding,
        # replace them with the value for the textbox in the same line
        threshold = 0.3
        to_sanitize = list(enumerate(dY))
        self.sanitize_line_distances(dY, threshold, to_sanitize, direction=1)
        self.sanitize_line_distances(dY, threshold, to_sanitize, direction=-1)

        norm_distance = numpy.median(list(more_itertools.flatten(dY)))
        distance_std = norm_distance * 0.1

        logging.debug(f"median {norm_distance} std {distance_std}")

        valid_points_at = numpy.logical_and(dY > norm_distance - distance_std, dY < norm_distance + distance_std).any(
            axis=1)
        good = indices[dI[valid_points_at]]
        mask[good] = True
        column_indices = numpy.full_like(divs, 0)
        column_indices[indices[dI]] = numpy.array([column_index for column_index, point in xy_sorted_points])

        return mask, column_indices

    def sanitize_line_distances(self, dY, threshold, to_sanitize, direction):
        dd_overwrite = 0
        if direction == 1:
            tindex = 1
        elif direction == -1:
            tindex = 0
        for i, dyy in to_sanitize[::direction]:
            if dyy[tindex] < threshold:
                dY[i][tindex] = dd_overwrite
            else:
                dd_overwrite = dyy[tindex]

    def pdf2htmlEX(self, pdf_path, html):
        assert (pdf_path.endswith(".pdf"))
        logging.info(f"converting pdf {pdf_path} to html ")
        os.system(f"{config.pdf2htmlEX} "
                  f"--space-as-offset 1 "
                  f"--decompose-ligature 1 "
                  f"--optimize-text 1 "
                  f"--fit-width {config.reader_width}  "
                  f"\"{pdf_path}\" \"{html}\"")


import unittest


class TestPaperReader(unittest.TestCase):

    def test_dump_features(self):
        files = list(pathlib.Path('testdata').glob('*.html'))
        dfs = []
        for doc_id, path in enumerate(files):
            score = self.extract(path)
            logging.info(f"collected {path} with {score}")
            self.tfu_pdf.features["doc_id"] = doc_id
            dfs.append(self.tfu_pdf.features)
        df = pandas.concat(dfs)
        df.divs = df.divs.astype(str)
        df.to_pickle("data.pckl")

    def extract(self, path):
        path = str(path)
        kwargs = {}
        kwargs['html_read_from'] = path
        kwargs['html_write_to'] = path + ".computed.htm"
        columns = int(regex.search(r"\d", path).group(0))
        pdf_obj = TestPaperReader.tfu_pdf.convert_and_index(**kwargs)
        score_pdf = pdf_obj.verify(columns=columns, serious=True, test_document=True)
        return score_pdf

    def test_layout_files(self):
        files = list(pathlib.Path('test/data').glob('*.html'))
        for path in files:
            path = str(path)
            kwargs = {}
            kwargs['html_read_from'] = path
            kwargs['html_write_to'] = path + ".computed.htm"
            columns = int(regex.search(r"\d", path).group(0))

            pdf_obj = TrueFormatUpmarkerPDF2HTMLEX(**kwargs)

            score = pdf_obj.verify(serious=True, test_document=True)
            logging.info(f"PDF extraction score: {score}")

            assert pdf_obj.columns == columns
            assert os.path.exists(kwargs['html_write_to'])

    def test_columns_and_file_existence(self):
        docs = [
            {
                'html_read_from': 'Laia Font-Ribera - Short-Term Changes in Respiratory Biomarkers after Swimmingin a Chlorinated Pool.pdf.html',
                'html_write_to': 'Laia Font-Ribera - Short-Term Changes in Respiratory Biomarkers after Swimmingin a Chlorinated Pool.pdf.pdf2htmlEX.test.html',
                'cols': 3
            },
            {
                'html_read_from': 'Sonja Vermeulen - Climate Change and Food Systems.pdf.html',
                'html_write_to': 'Sonja Vermeulen - Climate Change and Food Systems.pdf.html.pdf2htmlEX.test.html',
                'cols': 2
            },
            {
                'html_read_from': 'Wei Quian - Translating Embeddings for Knowledge Graph Completion with Relation Attention Mechanism.pdf.html',
                'html_write_to': 'Wei Quian - Translating Embeddings for Knowledge Graph Completion with Relation Attention Mechanism.test.html',
                'cols': 2
            },
            {'html_read_from': 'Ludwig Wittgenstein - Tractatus-Logico-Philosophicus.pdf.html',
             'html_write_to': 'Ludwig Wittgenstein - Tractatus-Logico-Philosophicus.pdf.html.pdf2htmlEX.test.html',
             'cols': 1
             },

            {
                'html_read_from': 'Filipe Mesquita - KnowledgeNet: A Benchmark Dataset for Knowledge Base Population.pdf.html',
                'html_write_to': 'Filipe Mesquita - KnowledgeNet: A Benchmark Dataset for Knowledge Base Population.pdf.pdf2htmlEX.test.html',
                'cols': 2
            },
            {
                'html_read_from': 'Laia Font-Ribera - Short-Term Changes in Respiratory Biomarkers after Swimmingin a Chlorinated Pool.pdf.html',
                'html_write_to': 'Laia Font-Ribera - Short-Term Changes in Respiratory Biomarkers after Swimmingin a Chlorinated Pool.pdf.pdf2htmlEX.test.html',
                'cols': 3
            },
            {
                'html_read_from': 'F. Ning - Toward automatic phenotyping of developing embryos from videos.pdf.html',
                'html_write_to': 'F. Ning - Toward automatic phenotyping of developing embryos from videos.pdf.pdf2htmlEX.test.html',
                'cols': 2
            },
            {
                'html_read_from': 'HumKno.pdf.html',
                'html_write_to': 'HumKno.pdf.pdf2htmlEX.test.html',
                'cols': 1
            }
        ]

        for kwargs in docs:
            logging.error(kwargs)
            columns = kwargs['cols']
            del kwargs['cols']
            kwargs['html_read_from'] = config.appcorpuscook_docs_document_dir + kwargs['html_read_from']
            kwargs['html_write_to'] = config.appcorpuscook_docs_document_dir + kwargs['html_write_to']
            self.tfu_pdf.convert_and_index(**kwargs)
            print(self.tfu_pdf.number_columns, columns)
            assert self.tfu_pdf.number_columns == columns
            assert self.tfu_pdf.indexed_words
            assert os.path.exists(kwargs['html_write_to'])


if __name__ == '__main__':

    tfu_pdf = TrueFormatUpmarkerPDF2HTMLEX(debug=True, parameterize=False)

    files = list(pathlib.Path('testdata').glob('*.html'))
    dfs = []
    for doc_id, path in enumerate(files):
        path = str(path)
        kwargs = {}
        kwargs['html_read_from'] = path
        kwargs['html_write_to'] = path + ".computed.htm"
        try:
            columns = int(regex.search(r"\d", path).group(0))
        except:
            continue
        pdf_obj = tfu_pdf.convert_and_index(**kwargs)
        score = pdf_obj.verify(columns=columns, serious=True, test_document=True)
        logging.info(f"collected {path} with {score}")
        tfu_pdf.features["doc_id"] = doc_id
        dfs.append(tfu_pdf.features)
    df = pandas.concat(dfs)
    df.divs = df.divs.astype(str)
    df.to_pickle("data.pckl")

    # unittest.main()
