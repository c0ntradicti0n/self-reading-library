import itertools
import logging
import os
import subprocess
from collections import defaultdict, OrderedDict
from itertools import cycle
from random import randint
from threading import Timer

from TexSoup import TexSoup, TexNode#, TokenWithPosition, TexText, TexEnv, OArg, RArg, TexCmd
from TexSoup.data import TexEnv, TexCmd

from layouteagle import config
from layouteagle.LatexReplacer import multicol_defs
from layouteagle.LatexReplacer.replacer import SoupReplacer
from layouteagle.helpers.cache_tools import file_persistent_cached_generator
from layouteagle.helpers.os_tools import get_path_filename_extension
from regex import regex

from layouteagle.helpers.str_tools import find_all
from layouteagle.pathant.Converter import converter


@converter("tex", "labeled.pdf")
class LatexReplacer(SoupReplacer):
    replacement_mapping_tag2tex = OrderedDict({
        None: ["document", "abstract", "keywords", None] + \
               ["name", "Author", "email", "corres", "affiliation", "affil", "corresp", "author", "markboth",
                        "email", "address", "adress", "emailAdd", "authorrunning", "institute", "ead", "caption",
                        "footnote", "tfootnote", "thanks"],

        #"title": ["Title", "title"],

        #"content": ["section*", "subsection", "subsection*", "subsubsection*",
        #            "section", "subsection", "subsubsection"],
    })

    def __init__(self, *args, max_cols=1, timout_sec=10, **kwargs):
        super().__init__(*args, replacements=self.replacement_mapping_tag2tex, **kwargs)

        self.max_cols = max_cols
        self.replacement_target = TexNode
        self.labeled_tex_path = lambda path: path + ".labeled.tex"
        self.pdf_path = lambda path: path + self.path_spec._to
        self.timeout_sec = timout_sec

        # TODO add new command support, as option to new commands enclosing text
        self.allowed_recursion_tags = ["revised", "textbf", "uppercase", "textit", "LARGE", "thanks", "Large", "large", "footnotesize",
                                       'texttt', "emph", "item", "bf", "IEEEauthorblockN", "IEEEauthorblockA", "textsc", "textsl"]
        self.allowed_oargs = ['title', 'author', 'section', 'item']
        self.forbidden_nargs = ['@sanitize', '@', "baselineskip", 'pdfoutput',  'vskip', 'topmargin', 'oddsidemargin',
                                'binoppenalty', 'def', 'href', 'providecommand', 'csname', "parindent", "parskip", "font"
                                "pdfminorversion"]
        self.skip_commands = self.forbidden_nargs
        self.forbidden_envs = ["$", "tikzpicture",  "eqnarray", "equation", "tabular", 'eqsplit', 'subequations']
        self.forbidden_envs = self.forbidden_envs + [env + "*" for env in self.forbidden_envs]

    def find_all(self, soup, tex_string):
        if tex_string==None:
            yield from soup
        else:
            _return = []
            try:
                texpr = list(soup.find_all(tex_string))
            except TypeError:
                logging.error(f'no {tex_string} in document')
            yield from  _return


    def insert_functionality(self, soup, file_content, col_num):
        document_class_element = soup.documentclass
        if document_class_element:
            insert_index = soup.expr._contents.index(document_class_element.expr) + 1
        else:
            insert_index = 7

        """if any(arg in file_content for arg in ["spconf", "lrec", "ieeeconf", "IEEEtran", "acmart", "twocolumn", "acl2020", "ansmath"]):
            soup.insert(insert_index, twocolumn_defs.defs)
            # TODO put multicol begin after first section(!) of doc and the rest to the end

            document_environment = soup.document.expr._contents
            document_environment.insert(0, twocolumn_defs.multicol_begin)
            document_environment.append(twocolumn_defs.multicol_end)

            return r"cc \currentcolumn{}"
        elif "multicol{" in file_content:"""

        orig_twocolumn = any(arg in file_content for arg in
                ["lrec", "ieeeconf", "IEEEtran", "acmart", "twocolumn", "acl2020", "ansmath", 'svjour', 'revtex4'])

        if col_num > 1:
            # start in document environment
            if orig_twocolumn:
                insert_definitions = "\n\onecolumn\n" +  multicol_defs.defs
            else:
                insert_definitions = multicol_defs.defs
            soup.insert(insert_index, insert_definitions)

            # make title should be before
            try:
                document_environment = soup.document.expr._contents
            except AttributeError:
                logging.warning("document without document environment")
                return "nix"

            if soup.find('maketitle'):
                maketitle_index = [
                             i
                             for i, pt in enumerate(soup.find('maketitle').parent.expr._contents)
                             if hasattr(pt, 'name') and pt.name == 'maketitle'][0] + 1
            else:
                maketitle_index = 0

            # when its twocolumn layout
            if orig_twocolumn:
                col_num = 2

            # begin and end multicol environment
            document_environment.insert(maketitle_index,  multicol_defs.multicol_begin % str(col_num))
            document_environment.append( multicol_defs.multicol_end)

            return r"cc \currentcolumn{}"
        else:
            # normal fill text
            if orig_twocolumn:
                insert_definitions = "\n\onecolumn\n"
            else:
                insert_definitions = multicol_defs.defs
            soup.insert(insert_index, insert_definitions)


            logging.info("No multi column instruction found, so its single col")
            return r"cc 1"

    @file_persistent_cached_generator(config.cache + 'replaced_tex_paths.json')
    def __call__(self, paths, compile=True, *args, **kwargs):
        """
        :param path_to_read_from:
        """
        with open(".layouteagle/log/unreplace.list", "w") as ur:

            for path_to_read_from, meta in paths:
                new_pdf_paths = self.work(path_to_read_from)
                if new_pdf_paths and len(new_pdf_paths):
                    if new_pdf_paths :
                        yield from [(new_pdf_path, meta) for new_pdf_path in new_pdf_paths]
                    else:
                        ur.write(path_to_read_from + "\n")


    def append_expression(self, possible_part_string, replaced_contents):
        replaced_contents.append(possible_part_string)

    def replace_this_text(self, possible_part_string, replaced_contents, replacement_string):
        expr_text = possible_part_string
        assert isinstance(expr_text, str)

        if replacement_string in expr_text:
            new_positional_string = TexText(possible_part_string)
            replaced_contents.append(new_positional_string)
            return
        else:

            content_generator = cycle([replacement_string])

            if '\currentcolumn{}' in replacement_string:
                effective_length = len(replacement_string) - int (len('\currentcolumn{}') *0.8)
            else:
                effective_length = len(replacement_string)

            new_contents = []
            for line in expr_text.split('\n'):
                if line.strip():
                    how_often = max(1, int((len(line) / effective_length)))

                    content_list = list(itertools.islice(content_generator, how_often))
                    if how_often > 60:
                        nl = randint(15,60)
                        content_list.insert(nl, r'\\')


                    new_contents.append(" ".join (content_list))
                else:
                    new_contents.append("")


            new_content = "\n".join(new_contents)

            new_positional_string = TexText(new_content)
            replaced_contents.append(new_positional_string)

    def make_replacement(self, where, replacement_string):
        if isinstance(replacement_string, str):
            replacement_string = replacement_string
        else:
            if replacement_string==None:
                replacement_string = " " + self.column_placeholder

        replaced_contents = []

        if isinstance(where, TexCmd):
            try:
                forth = where.args.all
                if where.name == 'item':
                    forth = where.args.all + where._contents
                    item_text_start = len(where.args.all)

                if not any(forth):
                    forth = []

                def _(x):
                    if not where.name == 'item':
                        where.args = x
                    else:
                        if x[:item_text_start] and any(x[:item_text_start]):
                            where.args = [x[:item_text_start]]
                        where._contents = x[item_text_start:]

                back = _
            except:
                forth = where.args

                def _(x):
                    where.args = x

                back = _

        elif isinstance(where, (TexEnv, TexNode)):
            forth = where._contents

            def _(x, ** kwargs):
                where._contents =  x
            back = _

        elif isinstance(where, (RArg, OArg)):
            forth = where.contents

            def _(x, ** kwargs):
                where.contents = x
            back = _

        else:
            logging.error("visited node not to visit")


        for i, node_to_replace in enumerate(forth):
            if isinstance(node_to_replace, OArg):
                try:
                    if where.name in self.allowed_oargs:
                        node_to_replace = self.make_replacement(node_to_replace, replacement_string)

                except AttributeError:
                    self.path_spec.logger.error(f"OArg without children in {node_to_replace}")
            elif isinstance(node_to_replace, RArg):
                    if hasattr(where, "args") and where.args and node_to_replace == where.args[-1] and where.name not in self.forbidden_nargs:
                        node_to_replace = self.make_replacement(node_to_replace, replacement_string)

            elif isinstance(node_to_replace, (TokenWithPosition, str)):

                if hasattr(where, 'name') and where.name == "item":

                    self.replace_this_text(node_to_replace, replaced_contents,
                                           replacement_string)
                    continue



            elif isinstance(node_to_replace, TexText) and not node_to_replace._text.strip():
                self.append_expression(node_to_replace, replaced_contents)
                continue

            elif isinstance(node_to_replace, TexEnv):
                if not node_to_replace.name in self.forbidden_envs:
                    node_to_replace = self.make_replacement(node_to_replace, replacement_string)
                else:
                    self.log_not_replace("environment", node_to_replace.name)

            elif isinstance(node_to_replace, TexText ):
                if i-1>=0 and isinstance(forth[i-1], TexCmd) and forth[i-1].name in self.skip_commands:
                    pass
                else:
                    self.replace_this_text(node_to_replace._text, replaced_contents,
                                        replacement_string)
                    continue


            elif isinstance(node_to_replace, TexCmd):
                if node_to_replace.name in self.allowed_recursion_tags:
                    node_to_replace = self.make_replacement(node_to_replace, replacement_string)
                else:
                    self.log_not_replace("command", node_to_replace.name)

            self.append_expression(node_to_replace, replaced_contents)

        back(replaced_contents)

        return where


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
                self.path_spec.logger.error(f'{tex_file_path} -->> compilation failed on \n""" {error_msg_at}"""')
                line_number_match = regex.search(r":(\d+):", error_msg_at)
                if line_number_match:
                    line_number = int(line_number_match.groups(1)[0])
                    try:
                        with open(filename) as f:
                            lines = f.readlines()

                    except UnicodeDecodeError:
                        self.path_spec.logger.error("Could not read latex file because of encoding")

                        os.chdir(cwd)
                        break
                    faulty_code = "\n".join(lines[max(0, line_number - 1):
                                                  min(len(lines), line_number + 1)])
                    self.path_spec.logger.error(f'  --->  see file {tex_file_path}: """\n{faulty_code}"""')
                os.chdir(cwd)
                break
        os.chdir(cwd)

        if process.returncode != 0:
            print (errors)
            return None
        self.path_spec.logger.info(f"{tex_file_path} compiled")
        pdf_path = path + "/"  + filename_without_extension + ".pdf"
        return pdf_path

    def work(self, path_to_read_from, compiling=True, inputing=False):
        path_to_read_from = path_to_read_from.replace(" ", "")

        if compiling:
            try:
                if not self.compiles(path_to_read_from, clean=True) and compiling:
                    self.path_spec.logger.error(f"Latex file '{path_to_read_from}' could not be compiled")
                    return
            except FileNotFoundError:
                logging.error (f"Input {path_to_read_from} not found! ")
                return



        results = []
        logging.info(f"Working on {path_to_read_from}")
        for col_num in range(1, self.max_cols + 1):
            try:
                with open(path_to_read_from, 'r') as f:
                    try:
                        f_content = f.read()
                    except UnicodeDecodeError:
                        self.path_spec.logger.error(f"Decode error on {[path_to_read_from]}")
                        return
            except FileNotFoundError:
                self.path_spec.logger.error("Included file in latex could not be found")
                raise

            try:
                # Texsoup fails with escaped chars
                f_content = regex.sub(r"(?<!\\)\\ "," ", f_content)

                soup = TexSoup(f_content)
                if not soup:
                    raise ValueError("Parse of texfile was None")
            except (TypeError, EOFError) as e:
                self.path_spec.logger.error(f"Error in Tex-file {path_to_read_from}:\n {e}")
                return

            try:
                if compiling:
                    self.column_placeholder = self.insert_functionality(soup, f_content, col_num)
            except Exception as e:
                self.path_spec.logger.error(f"Column functionality could not be inserted {e}")
                self.column_placeholder = self.insert_functionality(soup, f_content, col_num)

                return

            if r"\input{" in f_content:
                input_files = list(soup.find_all("input"))
                for input_file in input_files:
                    ipath, ifilename, iextension, ifilename_without_extension = get_path_filename_extension(path_to_read_from)
                    options = {#"with extension":
                               #         input_file.expr.args[-1].value + iextension,
                               "LatexInput solo":
                                        input_file.expr.args[-1].value}

                    for version, path in options.items():
                        if not path.endswith(".tex"):
                            path += ".tex"
                        try:
                            sub_instance = LatexReplacer
                            cwd = os.getcwd()
                            os.chdir(ipath)
                            new_path = sub_instance.work(path, compiling=False, inputing=True)
                            os.chdir(cwd)

                        except Exception as e:
                            self.path_spec.logger.error(f"LatexInput version {version} for {path} failed, because: \n{e}")
                            return

                    try: # self.labeled_tex_path()
                        input_file.args.all[-1].contents = [TexText(new_path[0])]
                    except TypeError:
                        logging.error(f"Input Tag bad: Failed to replace input tag {str(input_file)}")
                        return

                self.path_spec.logger.info(f"Replacing included input from {path_to_read_from}: {input_files}")


            # REPLACE

            super().__call__(soup)

            # WRITE BACK
            try:
                result = soup.__str__()
            except TypeError:
                logging.error("Soup damaged, continue")
                return

            out_path = self.labeled_tex_path(path_to_read_from + str(col_num))
            with open(out_path, 'w') as f:
                f.write(result)

            if compiling and not self.check_result(result):
                self.path_spec.logger.error(f"There was not much text replaced {path_to_read_from}, skip")
                return

            if compiling:
                pdf_path = self.compiles(out_path, n=4, clean=True)
                if pdf_path:
                    results.append(pdf_path)
                else:
                    self.path_spec.logger.error(f"Replaced result could not be parsed by pdflatex {out_path}")
                    return results
            elif inputing:
                results.append(out_path)

        return results

    def check_result(self, result):
        # for good results there will be less newlines than mentioning, that we are in column
        return True or result.count("column") > result.count ("\n") * 0.1

    not_replace = defaultdict(list)
    def log_not_replace(self, tex_structure, name):
        self.not_replace[tex_structure].append(name)



import unittest


class TestRegexReplacer(unittest.TestCase):

    def test_normal_math(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/normal_math.tex")


    def test_itemize_args(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/item_args.tex")


    def test_command_open_arg(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/cmd_open_arg.tex")


    def test_newlines(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/newlines.tex")

    def test_env(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/env.tex")

    def test_cmd(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/cmd.tex")

    def test_input(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/same_dir_input.tex")

    def test_multicol(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/multicolumn.tex")

    def test_stycol(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/single_feature/colsty.tex")


    def test_strange(self):
        latex_replacer = LatexReplacer
        latex_replacer.work("layouteagle/LatexReplacer/test/strange/strange.tex")




if __name__ == '__main__':
    unittest.main()
