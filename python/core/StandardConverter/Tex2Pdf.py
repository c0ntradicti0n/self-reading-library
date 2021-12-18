from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
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

    def __call__(self, arg_meta, *args, **kwargs):
        for tex, meta in arg_meta:
            if not 'labeled' in tex:
                if pdf_path:=self.compiles(tex):
                    yield pdf_path, meta



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
                error_msg_at = output[where - 150:where + 150]
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
                return None
        os.chdir(cwd)

        if process.returncode != 0:
            print(errors)
            return None
        self.path_spec.logger.info(f"{tex_file_path} compiled")
        pdf_path = path + "/" + filename_without_extension + ".pdf"
        return pdf_path
