import codecs
import logging
import os
import subprocess
from collections import Callable, defaultdict, OrderedDict
from functools import partial
from itertools import cycle
from threading import Timer

from TexSoup import TexSoup, TexNode, TokenWithPosition, TexText, TexEnv, OArg, RArg, TexCmd

from layouteagle import config
from layouteagle.LatexReplacer import twocolumn_defs, multicol_defs
from layouteagle.LatexReplacer.replacer import SoupReplacer
from layouteagle.helpers.cache_tools import persist_to_file, file_persistent_cached_generator
from layouteagle.helpers.os_tools import get_path_filename_extension
from layouteagle.helpers.str_tools import find_all, insert
from regex import regex

from pathant.Converter import converter


@converter("tex", "labeled.pdf")
class LatexReplacer(SoupReplacer):
    replacement_mapping_tag2tex = OrderedDict({
        None: ["document", "abstract", "keywords"],

        "title": ["Title", "title"],
        "staff": ["name", "Author", "email", "corres", "affiliation", "affil", "corresp", "author", "markboth",
                  "email", "address", "adress", "emailAdd", "authorrunning", "institute", "ead", "caption",
                  "footnote", "tfootnote", "thanks"],
        "content": ["section*", "subsection", "subsection*", "subsubsection*",
                    "section""subsection", "subsubsection"],
    })

    def __init__(self, *args, timout_sec=10, **kwargs):
        super().__init__(*args, replacements=self.replacement_mapping_tag2tex, **kwargs)

        self.replacement_target = TexNode
        self.add_extension = lambda path: path + self.path_spec._to
        self.timeout_sec = timout_sec

        # TODO add new command support, as option to new commands enclosing text
        self.allowed_recursion_tags = ["revised", "textbf", "uppercase", "textit", "LARGE", "thanks", "Large", "large", "footnotesize",
                                       'texttt', "emph", "item", "bf", "IEEEauthorblockN", "IEEEauthorblockA", "textsc", "textsl"]
        self.allowed_oargs = ['title', 'author', 'section', 'item']
        self.forbidden_nargs = ["baselineskip"]
        self.forbidden_envs = ["$", "tikzpicture",  "eqnarray", "equation", "tabular"]
        self.forbidden_envs = self.forbidden_envs + [env + "*" for env in self.forbidden_envs]

    def find_all(self, soup, tex_string):
        if tex_string==None:
            yield from soup
        else:
            yield from soup.find_all(tex_string)


    def insert_functionality(self, soup, file_content):
        document_class_element = soup.documentclass
        if document_class_element:
            insert_index = soup.expr._contents.index(document_class_element.expr) + 1
        else:
            insert_index = 7

        if any(arg in file_content for arg in ["lrec", "ieeeconf", "IEEEtran", "acmart", "twocolumn", "acl2020", "ansmath"]):
            soup.insert(insert_index, twocolumn_defs.defs)
            # TODO put multicol begin after first section(!) of doc and the rest to the end

            document_environment = soup.document.expr._contents
            document_environment.insert(0, twocolumn_defs.multicol_begin)
            document_environment.append(twocolumn_defs.multicol_end)

            return r"column \currentcolumn{}"
        elif "multicol{" in file_content:
            soup.insert(insert_index, multicol_defs.defs)

            return b"column \currentcolumn{}".decode('unicode_escape')
        else:
            logging.info("No multi column instruction found, so its single col")
            return b"column 1".decode('unicode_escape')

    @file_persistent_cached_generator(config.cache + 'labeled_tex_paths.json')
    def __call__(self, paths, compile=True):
        """
        :param path_to_read_from:
        """
        for path_to_read_from, meta in paths:
            new_pdf_path = self.work(path_to_read_from)
            if new_pdf_path:
                yield  new_pdf_path, meta


    def append_expression(self, possible_part_string, replaced_contents):
        replaced_contents.append(possible_part_string.expr)

    def replace_this_text(self, content_generator, possible_part_string, replaced_contents, replacement_string):
        try:
            try:
                expr_text = next(possible_part_string.text)
            except StopIteration:
                expr_text = possible_part_string.expr._text
        except AttributeError:
            expr_text = possible_part_string.expr

        new_lines = list(find_all(expr_text, '\n'))
        try:
            how_often = int(len(expr_text) / int(len(replacement_string)) + 0.99)
        except:
            raise
        new_content = " " + " ".join(next(content_generator) for i in range(how_often)) + " "
        for j in new_lines:
            if j == 0:
                new_content = '\n' + new_content
            else:
                new_content = new_content + ' '
        new_positional_string = TexText(new_content)
        replaced_contents.append(new_positional_string)

    def make_replacement(self, where, replacement_string):
        if isinstance(replacement_string, str):
            replacement_string = " " + replacement_string
        else:
            if replacement_string==None:
                replacement_string = " " + self.column_placeholder

        content_generator = cycle([replacement_string])

        replaced_contents = []
        normal_write_back = True
        if isinstance(where.expr, TexCmd):
            contents_to_visit = list(TexNode(child) for child in where.args)
            if not contents_to_visit:
                if where.expr._contents:
                    contents_to_visit = list(TexNode(child) for child in where.expr._contents)
                    normal_write_back = "_contents"

        elif isinstance(where.expr, TexEnv):
            contents_to_visit = list(TexNode(child) for child in where.expr._contents)
        elif isinstance(where.expr, TexNode):
            contents_to_visit = list(TexNode(child) for child in where.expr._contents)
        elif isinstance(where.expr, (RArg, OArg)):
            contents_to_visit = list(TexNode(child) for child in where.expr.contents)
        else:
            logging.error("visited node not to visit")


        for node_to_replace in contents_to_visit:
            if isinstance(node_to_replace.expr, OArg):
                if where.name in self.allowed_oargs:
                    node_to_replace = self.make_replacement(node_to_replace, replacement_string)

                    self.append_expression(node_to_replace, replaced_contents)
                else:
                    self.append_expression(node_to_replace, replaced_contents)
            elif isinstance(node_to_replace.expr, RArg):
                try:
                    if where.args and node_to_replace.expr == where.args[-1] and where.name not in self.forbidden_nargs:
                        node_to_replace = self.make_replacement(node_to_replace, replacement_string)
                        self.append_expression(node_to_replace, replaced_contents)
                    else:
                        self.append_expression(node_to_replace, replaced_contents)
                except AttributeError:
                    logging.error("RArg without children (it's blocks like {\"a})")
                    self.append_expression(node_to_replace, replaced_contents)


            elif isinstance(node_to_replace.expr, (TokenWithPosition, str)):
                if where.name == "item":
                    self.replace_this_text(content_generator, node_to_replace, replaced_contents,
                                           replacement_string)
                else:
                    try:
                        self.append_expression(node_to_replace, replaced_contents)
                    except AttributeError:
                        logging.error("function object has no attribute")

            elif isinstance(node_to_replace.expr, TexText) and not node_to_replace.expr._text.strip():
                self.append_expression(node_to_replace, replaced_contents)

            elif isinstance(node_to_replace.expr, TexEnv):
                if not node_to_replace.expr.name in self.forbidden_envs:
                    node_to_replace = self.make_replacement(node_to_replace, replacement_string)
                    self.append_expression(node_to_replace, replaced_contents)
                else:
                    self.log_not_replace("environment", node_to_replace.name)
                    self.append_expression(node_to_replace, replaced_contents)

            elif isinstance(node_to_replace.expr, TexText):
                self.replace_this_text(content_generator, node_to_replace, replaced_contents,
                                        replacement_string)

            elif isinstance(node_to_replace.expr, TexCmd):
                if node_to_replace.expr.name in self.allowed_recursion_tags:
                    node_to_replace = self.make_replacement(node_to_replace, replacement_string)
                    self.append_expression(node_to_replace, replaced_contents)
                else:
                    self.log_not_replace("command", node_to_replace.name)
                    self.append_expression(node_to_replace, replaced_contents)

            else:
                self.append_expression(node_to_replace, replaced_contents)

        if not all(isinstance(rc, (TexCmd, TexEnv, TexText))
                        for rc in replaced_contents):
            for i, content in enumerate(replaced_contents):
                if isinstance(content, TokenWithPosition):
                    replaced_contents[i] = content



        if isinstance(where.expr, TexEnv) or normal_write_back=='_contents':
            where.expr._contents = replaced_contents
        elif isinstance(where.expr, TexCmd):
            where.expr.args.all = replaced_contents
        elif isinstance(where.expr, (RArg, OArg)):
            where.expr.contents = replaced_contents
        else:
            logging.error("replacing something else")
            where.expr._contents = replaced_contents

        return TexNode(where)


    def compiles(self, tex_file_path, n=1, clean=False):
        path, filename, extension, filename_without_extension = get_path_filename_extension(tex_file_path)
        cwd = os.getcwd()
        try:
            os.chdir(path)
        except:
            raise
        if clean:
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

            if (any(error in output.lower() for error in ["latex error", "fatal error"])):
                where = output.lower().index('error')
                error_msg_at = output[where-150:where+150]
                logging.error(f'compilation failed on \n""" {error_msg_at}"""')
                line_number_match = regex.search(r":(\d+):", error_msg_at)
                if line_number_match:
                    line_number = int(line_number_match.groups(1)[0])
                    try:
                        with open(filename) as f:
                            lines = f.readlines()
                    except UnicodeDecodeError:
                        logging.error("Could not read latex file because of encoding")
                        break
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

    def work(self, path_to_read_from, compile=True):
        path_to_read_from = path_to_read_from.replace(" ", "")

        if compile:
            try:
                if not self.compiles(path_to_read_from, clean=True) and compile:
                    logging.error(f"Latex file '{path_to_read_from}' could not be compiled")
                    return
            except FileNotFoundError:
                logging.error ("Input not found! ")
                return

        try:
            with open(path_to_read_from, 'r') as f:
                try:
                    f_content = f.read()
                except UnicodeDecodeError:
                    logging.error(f"Decode error on {[path_to_read_from]}")
                    return
        except FileNotFoundError:
            logging.error("Included file in latex could not be found")
            raise

        try:
            soup = TexSoup(f_content)
            if not soup:
                raise ValueError("Parse of texfile was None")
        except Exception as e:
            logging.error(f"Error in Tex-file {path_to_read_from}:\n {e}")
            return


        logging.info(f"Working on {path_to_read_from}")
        try:
            if compile:
                self.column_placeholder = self.insert_functionality(soup, f_content)
        except Exception:
            logging.error("Column functionality could not be inserted")
            return

        if r"\input{" in f_content:
            input_files = list(soup.find_all("input"))
            for input_file in input_files:
                ipath, ifilename, iextension, ifilename_without_extension = get_path_filename_extension(path_to_read_from)
                options = {"with extension":
                                    self.add_extension(input_file.expr.args[-1].value + iextension),
                           "LatexInput solo":
                                    self.add_extension(input_file.expr.args[-1].value + ".tex")}

                for version, path in options.items():
                    try:
                        sub_instance = LatexReplacer(add_extension=self.add_extension, timout_sec=self.timeout_sec)
                        new_path = sub_instance.work(path, compile=False)
                    except Exception as e:
                        logging.error(f"LatexInput version {version} for {path} failed, because: \n{e}")
                        return

                try:
                    input_file.args.all[-1] = RArg(new_path[:-(len(iextension))])
                except TypeError:
                    logging.error(f"Input Tag bad: Failed to replace input tag {str(input_file)}")
                    return

            logging.info(f"Replacing included input from {path_to_read_from}: {input_files}")


        # REPLACE

        super().__call__(soup)

        # WRITE BACK
        result = str(soup.__repr__())

        if compile and not self.check_result(result):
            logging.error("There was not much text replaced, skip")
            return

        out_path = self.add_extension(path_to_read_from)
        with open(out_path, 'w') as f:
            f.write(result)

        if compile:
            pdf_path = self.compiles(out_path, n=4)
            if pdf_path:
                return pdf_path
            else:
                logging.error(f"Replaced result could not be parsed by pdflatex {out_path}")
                return
        return out_path

    def check_result(self, result):
        # for good results there will be less newlines than mentioning, that we are in column
        return result.count("column") > result.count ("\n") * 0.5

    not_replace = defaultdict(list)
    def log_not_replace(self, tex_structure, name):
        self.not_replace[tex_structure].append(name)



import unittest


class TestRegexReplacer(unittest.TestCase):
    def test_strange(self):
        latex_replacer = LatexReplacer(add_extension=".labeled.tex")
        latex_replacer.work("strange.tex")

    def test_1(self):
        latex_replacer = LatexReplacer(add_extension=".labeled.tex")
        latex_replacer.work("test/few/Palatini_quantum-FINAL.tex")

    def test_2(self):
        latex_replacer = LatexReplacer(add_extension=".labeled.tex")
        latex_replacer.work("test/test2/main.tex")

    def test_3(self):
        latex_replacer = LatexReplacer(add_extension=".labeled.tex")
        latex_replacer.work("test/test3/main.tex")


    def test_integration(self):
        latex_replacer = LatexReplacer(add_extension=".labeled.tex")
        f = lambda: (x for x in ["./tex_data/7c6b2116adae604a504099c4d08483e7/main.tex"])
        assert all(os.path.exists(r) and latex_replacer.compiles(r, n=10) for r in latex_replacer(f))


if __name__ == '__main__':
    unittest.main()
