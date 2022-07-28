import signal
import time
from sys import stdout, stderr

from core import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from helpers.cache_tools import configurable_cache
from helpers.os_tools import get_path_filename_extension
import os
import subprocess
from threading import Timer
from regex import regex


@converter("tex", "pdf")
class Tex2Pdf(PathSpec):
    def __init__(self, timout_sec=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_sec = timout_sec

    @configurable_cache(config.cache + os.path.basename(__file__))
    def __call__(self, arg_meta, *args, **kwargs):
        for doc_id, meta in arg_meta:
            if doc_id.endswith('.tex'):
                if pdf_path := self.compiles(doc_id):
                    yield pdf_path, meta
            elif doc_id.endswith('.pdf'):
                yield doc_id, meta
            else:
                self.logger.error("dont know how to handle file " + doc_id)

    def compiles(self, tex_file_path, n=1, clean=False):
        path, filename, extension, filename_without_extension = get_path_filename_extension(tex_file_path)

        if clean:
            subprocess.run(['rm', '*.pdf.html'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '*.pdf'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '*.aux'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '*.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for i in range(n):
            print(f"trying to compile {path} + {filename}")
            process = subprocess.Popen(
                f'cd {path}  && echo $(pwd) && pdflatex -interaction=nonstopmode -halt-on-error -file-line-error {filename}'
                , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            time.sleep(self.timeout_sec)
            process.send_signal(signal.SIGINT)
            output = process.stdout.read().decode('utf-8', errors="ignore")
            #print(output)
            errors = process.stderr.read().decode('utf-8', errors="ignore")
            #print(errors)
            if (any(error in output.lower() for error in ["latex error", "fatal error"])):
                where = output.lower().index('error')
                error_msg_at = output[where - 150:where + 150]
                self.path_spec.logger.error(f'{tex_file_path} -->> compilation failed on \n""" {error_msg_at}"""')
                line_number_match = regex.search(r":(\d+):", error_msg_at)
                if line_number_match:
                    line_number = int(line_number_match.groups(1)[0])
                    try:
                        with open(path + "/" + filename) as f:
                            lines = f.readlines()

                    except UnicodeDecodeError:
                        self.path_spec.logger.error("Could not read latex file because of encoding")
                        break
                    faulty_code = "\n".join(lines[max(0, line_number - 1):
                                                  min(len(lines), line_number + 1)])
                    self.path_spec.logger.error(f'  --->  see file {tex_file_path}: """\n{faulty_code}"""')
                return None

        if process.returncode:
            print(errors)
            return None
        self.path_spec.logger.info(f"{tex_file_path} compiled")
        pdf_path = path + "/" + filename_without_extension + ".pdf"
        return pdf_path
