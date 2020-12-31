import logging
import os

from python.layout.LayoutReader.trueformatpdf2htmlEX import TrueFormatUpmarkerPDF2HTMLEX
from python.helpers.list_tools import Lookup
from python.layouteagle.pathant.Converter import converter


@converter("htm", "feature")
class LabeledFeatureMaker(TrueFormatUpmarkerPDF2HTMLEX):
    def __init__(self, debug=True, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def __call__(self, labeled_paths, *args, **kwargs):
        for doc_id, (labeled_html_path, meta) in enumerate(labeled_paths):
            print(doc_id, labeled_html_path)
            try:
                feature_df, soup = self.generate_data_for_file(labeled_html_path)
            except FileNotFoundError:
                logging.error("output of pdf2htmlEX looks damaged")
                continue
            except IndexError:
                logging.error("output of pdf2htmlEX looks damaged, no CSS in there?")
                continue
            except ValueError:
                logging.error("probably error on counting columns")
                continue

            feature_df["doc_id"] = doc_id
            if False and self.debug:
                debug_html_path = labeled_html_path + ".debug.html"
                self.tfu = TrueFormatUpmarkerPDF2HTMLEX(debug=True)
                self.tfu.label_lookup = Lookup(self.tfu.label_strings)
                self.tfu.generate_css_tagging_document(html_read_from=labeled_html_path, html_write_to=debug_html_path)
                os.system(f"google-chrome {debug_html_path}")

            #feature_df['chars'] = feature_df.divs.apply(lambda div: sum(div.text.count(c) for c in string.ascii_letters))
            #feature_df['nums'] = feature_df.divs.apply(lambda div: sum(div.text.count(c) for c in string.digits))
            #feature_df['signs'] = feature_df.divs.apply(lambda div: sum(div.text.count(c) for c in string.punctuation))

            meta['soup'] = soup

            yield feature_df, meta




if __name__ == '__main__':
    latex_maker = LabeledFeatureMaker
    list(latex_maker.__call__(
        [("layouteagle/.layouteagle/tex_data/efd00a7cbb96f4b5e25d06863834b0e7/bare_jrnl.tex2.labeled.pdf.htm", {})]))




