import codecs
import logging
import os
import subprocess
from collections import Callable
from functools import partial
from itertools import cycle
from threading import Timer

from TexSoup import TexSoup, TexNode, TokenWithPosition, TexText, TexEnv, OArg, RArg

from layouteagle import config
from layouteagle.LatexReplacer import twocolumn_defs, multicol_defs
from layouteagle.LatexReplacer.replacer import SoupReplacer
from layouteagle.helpers.cache_tools import persist_to_file
from layouteagle.helpers.os_tools import get_path_filename_extension
from layouteagle.helpers.str_tools import find_all, insert
from regex import regex


class LatexReplacer(SoupReplacer):
    def __init__(self, add_extension, timout_sec=20):
        self.replacement_target = TexNode
        self.add_extension = lambda path: path + add_extension
        self.timeout_sec = timout_sec

        identity =  lambda x: x
        self.allowed_recursion_tags = ["textit", "LARGE", "title", "author", "footnote", "thanks", 'texttt', "emph", "item", "bf"]
        self.forbidden_envs = ["$", "tikzpicture",  "eqnarray", "equation", "tabular"]
        self.forbidden_envs = self.forbidden_envs + [env + "*" for env in self.forbidden_envs]

        self.what = {
            lambda soup: soup.title: (identity, self.make_replacement("title")),
            lambda soup: soup.find_all("author"): (identity, self.make_replacement("author")),
            lambda soup: soup.find_all("email"): (identity, self.make_replacement("author")),
            lambda soup: soup.find_all("adress"): (identity, self.make_replacement("author")),
            lambda soup: soup.abstract: (identity, self.make_replacement("abstract")),
            lambda soup: soup.find_all("caption"): (identity, self.make_replacement("caption")),
            lambda soup: soup.find_all("footnote"): (identity, self.make_replacement("footnote")),
            lambda soup: soup.find_all("thanks"): (identity, self.make_replacement("footnote")),
            lambda soup: soup.find_all("section"): (identity, self.make_replacement("section")),
            lambda soup: soup.find_all("subsection"): (identity, self.make_replacement("section")),
            lambda soup: soup.find_all("subsubsection"): (identity, self.make_replacement("section")),

            lambda soup: soup.document: (
                identity,
                self.make_replacement(lambda: self.column_placeholder )
            )
        }

    def insert_functionality(self, soup, file_content):
        document_class_element = soup.documentclass
        if document_class_element:
            insert_index = soup.expr._contents.index(document_class_element.expr) + 1
        else:
            insert_index = 7

        if any(arg in file_content for arg in ["ieeeconf", "IEEEtran", "acmart", "twocolumn"]):
            soup.insert(insert_index, twocolumn_defs.defs)
            # put multicol begin after first section(!) of doc and the rest to the end
            insert_index = soup.expr._contents.index(document_class_element.expr) + 1

            document_environment = soup.document.expr._contents
            document_environment.insert(0, twocolumn_defs.multicol_begin)
            document_environment.append(twocolumn_defs.multicol_end)

            return b"column \currentcolumn{}".decode('unicode_escape')
        elif "multicol{" in file_content:
            soup.insert(insert_index, multicol_defs.defs)

            return b"column \currentcolumn{}".decode('unicode_escape')
        else:
            logging.info("no multi column instruction found, so its single col")
            return b"column 1".decode('unicode_escape')

    @persist_to_file(config.scrape_cache + 'labeled_tex_paths.json')
    def __call__(self, paths, compile=True):
        """

        :param path_to_read_from:
        """

        labeled_paths = []
        for path_to_read_from in paths:
            path_to_read_from = path_to_read_from.replace(" ", "")
            if not self.compiles(path_to_read_from) and compile:
                logging.error(f"Latex file {path_to_read_from} could not be compiled")
                continue

            with open(path_to_read_from, 'r') as f:
                try:
                    f_content = f.read()
                except UnicodeDecodeError:
                    logging.error(f"decode error on {[path_to_read_from]}")
                    continue

            if "\input{" in f_content:
                input_files = soup.find_all("input")
                for input_file in input_files:
                    logging.info(f"replacing included input from {path_to_read_from}: {input_file}")
                    self(input_file, compile=False)
                continue

            try:
                soup = TexSoup(f_content)
                if not soup:
                    raise ValueError("parse of texfile was None")
            except Exception as e:
                logging.error(f"error in Tex-file {path_to_read_from}:\n {e}")
                continue

            logging.info(f"working on {path_to_read_from}")
            try:
                self.column_placeholder = self.insert_functionality(soup, f_content)
            except Exception:
                logging.error("column functionality could not be inserted")
                continue
            super().__call__(soup)

            result = str(soup.__repr__())

            out_path = self.add_extension(path_to_read_from)
            with open(out_path, 'w') as f:
                f.write(result)

            if compile:
                pdf_path = self.compiles(out_path, n=4)
                if pdf_path:
                    labeled_paths.append(pdf_path)
                else:
                    logging.error(f"replaced result could not be parsed by pdflatex {out_path}")
                    continue
        return labeled_paths

    def append_expression(possible_part_string, replaced_contents):
        replaced_contents.append(possible_part_string.expr)

    def replace_this_text(self, content_generator, possible_part_string, replaced_contents, replacement_string):
        new_lines = list(find_all(possible_part_string.expr._text, '\n'))
        try:
            how_often = int(len(possible_part_string.expr._text) / int(len(replacement_string)) + 0.99)
        except:
            raise
        new_content = " " + " ".join(next(content_generator) for i in range(how_often)) + " "
        for j in new_lines:
            if j == 0:
                new_content = '\n' + new_content
            else:
                new_content = new_content + ' '
        new_positional_string = TokenWithPosition(new_content)
        replaced_contents.append(new_positional_string)

    def make_replacement(self, string, recursive=True):

        bing  = string
        def replace_it_with(where):
            if isinstance(bing, Callable):
                replacement_string = " " + bing()
            else:
                replacement_string = " " + string

            content_generator = cycle([replacement_string])

            replaced_contents = []

            contents_to_visit = list(where.all)

            for possible_part_string in contents_to_visit:
                if isinstance(possible_part_string.expr, OArg):
                    LatexReplacer.append_expression(possible_part_string, replaced_contents)
                elif isinstance(possible_part_string.expr, RArg):
                    LatexReplacer.append_expression(possible_part_string, replaced_contents)

                elif isinstance(possible_part_string.expr, TexText) and not possible_part_string.expr._text.strip():
                    LatexReplacer.append_expression(possible_part_string, replaced_contents)

                elif isinstance(possible_part_string.expr, TexEnv):
                    if not possible_part_string.expr.name in self.forbidden_envs:
                        possible_part_string = replace_it_with(possible_part_string)
                        #LatexReplacer.append_expression(possible_part_string, replaced_contents)
                    else:
                        logging.warning(f"environment {possible_part_string.expr.name} is not to be replaced")

                elif isinstance(possible_part_string.expr, TexText):
                    self.replace_this_text(content_generator, possible_part_string, replaced_contents,
                                            replacement_string)
                else: # LaTex Commands are left
                    try:
                        expression_is_in_args_of_command = \
                            possible_part_string.expr in [content for arg in where.args.all
                                                          for content in arg.contents]
                    except AttributeError:
                        logging.warning(f"strange args of latex commands: some arg {list(where.args.all)} was a str and has no '.contents'")
                        expression_is_in_args_of_command = True

                    if expression_is_in_args_of_command:
                        if hasattr(possible_part_string, "name"):
                            if possible_part_string.name in self.allowed_recursion_tags:
                                possible_part_string = replace_it_with(possible_part_string)
                            else:
                                logging.warning(f"command {possible_part_string.name} is not to be replaced")

                    LatexReplacer.append_expression(possible_part_string, replaced_contents)

            try:
                where.expr.args[0].contents = replaced_contents
            except:
                where.expr._contents = replaced_contents
            new_node = TexNode(where.expr, [])
            return new_node

        return replace_it_with

    def compiles(self, tex_file_path, n=1, clean=False):
        path, filename, extension, filename_without_extension = get_path_filename_extension(tex_file_path)
        cwd = os.getcwd()
        try:
            os.chdir(path)
        except:
            raise
        if clean:
            subprocess.run(['rm', '*.labeled.*'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '*.pdf.html'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '*.pdf'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '*.aux'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '*.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for i in range(n):
            process = subprocess.Popen(
                ['pdflatex',
                    '--nonstopmode',
                    '-halt-on-error',
                    '-file-line-error',
                    filename
                 ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            timer = Timer(self.timeout_sec, process.kill)
            try:
                timer.start()
                stdout, stderr = process.communicate()
            finally:
                timer.cancel()
            output = stdout.decode('latin1')
            errors = stderr.decode('latin1')

            if (any(error  in output.lower() for error in ["latex error", "fatal error"])):
                where = output.lower().index('error')
                error_msg_at = output[where-150:where+150]
                logging.error(f'compilation failed on \n""" {error_msg_at}"""')
                line_number_match = regex.search(r":(\d+):", error_msg_at)
                if line_number_match:
                    line_number = int(line_number_match.groups(1)[0])
                    with open(filename) as f:
                        lines = f.readlines()
                    faulty_code = "\n".join(lines[max(0, line_number - 1):
                                                  min(len(lines), line_number + 1)])
                    logging.error(f'  --->  see file {tex_file_path}: """\n{faulty_code}"""')
                break


        os.chdir(cwd)

        if process.returncode != 0:
            return None
        logging.warning(f"{tex_file_path} compiled")
        pdf_path = path + "/"  + filename_without_extension + ".pdf"
        return pdf_path


import unittest


class TestRegexReplacer(unittest.TestCase):
    def test_integration(self):
        latex_replacer = LatexReplacer(add_extension="labeled.tex")
        f = lambda: (x for x in ["./tex_data/7c6b2116adae604a504099c4d08483e7/main.tex"])
        assert all(os.path.exists(r) and latex_replacer.compiles(r, n=10) for r in latex_replacer(f))


if __name__ == '__main__':
    unittest.main()
