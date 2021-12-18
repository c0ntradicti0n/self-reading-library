import bs4
import pandas
import tinycss
from helpers.list_tools import flatten


import json
from collections import namedtuple

import itertools
import more_itertools
import numpy
from regex import regex

from core import config
from layout.latex.LatexReplacer.replacer import SoupReplacer
from layout.latex.LayoutReader.pdf import Pdf


class TrueFormatUpmarker(SoupReplacer):
    def __init__(self, *args,
                 min_bottom=None,
                 max_bottom=None,
                 debug=True,
                 parameterize=False,
                 debug_folder='./.core/debug/',
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.pdf_obj = Pdf()
        self.debug_folder =  debug_folder

        self.cuts = []
        self.text_divs = []
        self.debug = debug
        self.parameterize = parameterize
        din_rel = numpy.sqrt(2)

        if not min_bottom:
            self.min_bottom = 0
        else:
            self.min_bottom = min_bottom
        if not max_bottom:
            self.max_bottom = config.reader_width * din_rel  # * (1- config.page_margin_top)
        else:
            self.max_bottom = max_bottom

        self.WRAP_TAG = config.INDEX_WRAP_TAG_NAME

        self.CUT = "CUT"
        delimiters = r" ", r"\n"
        self.splitter = '|'.join(map(regex.escape, delimiters))

    def convert_and_index(self, html_read_from="", html_write_to="") -> Pdf:
        self.logger.warning(f"working on {html_read_from}")

        self.generate_css_tagging_document(html_read_from, html_write_to)
        self.pdf_obj.indexed_words = self.word_index
        self.pdf_obj.text = " ".join(self.word_index.values())
        return self.pdf_obj


    def get_indexed_words(self):
        return self.word_index

    def save_doc_json(self, json_path):
        doc_dict = {
            "text": " ".join(list(self.word_index.values())),
            "indexed_words": self.word_index,
            "cuts": self.cuts}
        with open(json_path, "w", encoding="utf8") as f:
            f.write(json.dumps(doc_dict))

    def add_text_coverage_markup(self, soup):
        z_style = "\nz {background: rgba(0, 0, 0, 1) !important;   font-weight: bold;} "
        soup.head.append(soup.new_tag('style', type='text/css'))
        soup.head.style.append(z_style)

    def manipulate_document(self,
                            features: pandas.DataFrame,
                            soup: bs4.BeautifulSoup,
                            **kwargs
                            ):

        # reset container for words
        self.make_word_index(soup=soup,
                             features=features,
                             **kwargs,
                             )
        if self.debug:
            self.add_text_coverage_markup(soup)

    def get_css(self, soup):
        css_parts = [tag for tag in soup.select('style[type="text/css"]') if isinstance(tag, bs4.Tag)]
        style_rules = flatten([tinycss.make_parser().parse_stylesheet(css.string, encoding="utf8").rules for css in css_parts])
        style_dict = {}
        for rule in style_rules:
            try:
                style_dict.update(self.css_rule2entry(rule) )
            except IndexError as e:
                self.logger.error(f"Could not get css styles out of soup from rule {rule}" + str(e))
                continue
        if None in style_dict:
            del style_dict[None]
        return style_dict

    def css_rule2entry(self, rule):
        if isinstance(rule, tinycss.css21.RuleSet):
            decla = rule.declarations
            ident = [sel for sel in rule.selector if sel.type in ['IDENT', 'HASH']][0].value
            if not isinstance(ident, str):
                self.logger.info("multi value css found, ignoring")
                return {}
            return {ident: decla}
        return {}

    keep_delims = r""",;.:'()[]{}&!?`/"""

    def tokenize_differential_signs(poss_token):
        try:
            words = poss_token.split(" ")
        except:
            raise
        applying_delims = [d for d in TrueFormatUpmarker.keep_delims if d in poss_token]
        for d in applying_delims:
            intermediate_list = []
            for line in words:
                splitted = line.split(d)
                # flattenning double list is done because two things splitted on tokens need
                # to be splittted into three: token, delimiter, token
                intermediate_list.extend(more_itertools.flatten([[e, d] if i < len(splitted) - 1 else [e]
                                                  for i, e in enumerate(line.split(d)) if e]))
            words = intermediate_list
        words = [word.strip() for word in words if word.strip()]
        return words

    IndexedWordTag = namedtuple("IndexedWordTag", ["index", "word", "tag"])
    def make_new_tag(self, soup, word, debug_percent, **kwargs) -> IndexedWordTag:
        self.id = self.count_i.__next__()
        color_code = f"color:hsl({int(debug_percent * 360)}, 100%, 50%);"
        if self.debug:
            kwargs.update(
                {
                    "style":
                        color_code
                }
            )
        tag = soup.new_tag(self.WRAP_TAG,
                           id=f"{self.WRAP_TAG}{self.id}",
                           **kwargs)

        tag.append(word)
        return self.IndexedWordTag(self.id, word, tag)

    label_strings = \
        ["c1", "c2", "c3", "NONE"]
    def check_for_label_in_string(self, text):
        contained_labels = [s for s in self.label_strings if s in text.lower().replace(" ", "")]
        if contained_labels:
            if len(contained_labels) > 1:
                self.logger.warning("More labels in div text found than wanted")
            return contained_labels[0]
        else:
            return self.label_strings[-1]

    shifts = 2
    def overwrite_by_labeled_document(self, features):
        features["text"] = features.divs.apply(lambda div: div.text)
        features["spans_no"] = features.divs.apply(lambda div:  div.__str__().count(r'/span') -  div.__str__().count('"_'))
        features["pcl"] = features["text"].apply(lambda text: self.check_for_label_in_string(text))
        for shift in range(self.shifts, 0, -1):
            features["shift_up"], features["shift_pn_up"], features["shift_down"], features["shift_pn_down"]= (
                features["pcl"].shift(-shift), features["page_number"].shift(-shift),
                features["pcl"].shift(1), features["page_number"].shift(1)
            )

            # fill in, where is NONE between other labels, to keep these included parts
            where = ((features["shift_up"] == features["shift_down"]) &
            (features["shift_pn_up"] == features["shift_pn_down"]) &
            (features["pcl"].str.contains("NONE")) &
            (features["pcl"] != features["shift_down"]) &
            (features["shift_down"].str.contains("column")))

            features["pcl"][where] = features["shift_down"]

        features["LABEL"] = features["pcl"]
        del features["pcl"]


    def index_labels(self, string):
        return self.label_lookup.token_to_id[string] / len(self.label_lookup.token_to_id)

    def make_word_index(self,
                    soup,  # for generating new tags
                    features
                    ):
        """
            splitter is a function that gives back a list of 2-tuples, that mean the starting index,
            where to replace and list of tokens
        """
        self.word_index = {}
        self.count_i = itertools.count()  # counter for next indices for new html-tags
        #features.sort_values(by="reading_sequence", inplace=True)
        features["debug_color"] = abs(features.LABEL.apply(lambda string: self.index_labels(string)))
        for index, feature_line in features.iterrows():
            div = feature_line.divs

            change_list = list(self.tags_to_change(feature_line.debug_color, soup, div))
            indexing_css_update = {}
            for indexed_div_content in change_list[::-1]:
                indexed_div_content.parent.contents.pop(indexed_div_content.div_content_index)

                for indexed_word_tag in indexed_div_content.indexed_word_tags[::-1]:
                    indexed_div_content.parent.contents.insert(
                        indexed_div_content.div_content_index,
                        indexed_word_tag.tag)
                    indexing_css_update[indexed_word_tag.index] = indexed_word_tag.word

            self.word_index.update(dict(indexing_css_update))

        return dict(sorted(self.word_index.items(), key=lambda x: int(x[0])))

    IndexedDivContent = namedtuple("IndexedDivContent", ["div_content_index", "parent", "indexed_word_tags"])

    def tags_to_change(self, debug_percent, soup, text_div) -> IndexedDivContent :
        for div_tag_index, content in enumerate(text_div.contents):
            if isinstance(content, bs4.Tag) and content.contents != [' ']:
                yield from self.tags_to_change( debug_percent, soup, content)
            elif isinstance(content, bs4.NavigableString):
                words = TrueFormatUpmarker.tokenize_differential_signs(content)
                new_tags = [
                    self.make_new_tag(
                        soup,
                        word,
                        debug_percent=debug_percent)
                    for word in words
                ]
                yield TrueFormatUpmarker.IndexedDivContent(div_tag_index, text_div, new_tags)

    def collect_all_divs(self, soup):
        raise NotImplementedError




