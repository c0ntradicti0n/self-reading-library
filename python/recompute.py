import subprocess
import traceback
from pathlib import Path

from regex import regex
from config.ant_imports import *

# from debugger_tools import connect_debugger
from helpers.cache_tools import refactor_filename
from layout.annotation_thread import annotate_uploaded_file as layout_compute
from language.transformer.ElmoDifference import (
    annotate_uploaded_file as difference_compute,
)

ant = PathAnt()

docs = os.listdir(refactor_filename(ElmoDifference.cache_folder))
for doc, meta in ant("css.difference", "recompute")(metaize(docs)):
    try:
        try:
            id = regex.search(r"([a-z0-9]){15,1000}", doc).group(0)

        except:
            print(doc)
            id = Path(meta["doc_id"]).name

        assert id

        proc = (
            subprocess.check_output(
                f"find {config.hidden_folder} -maxdepth 7 -name '*{id}*'  -print ",
                shell=True,
            )
            .decode("utf-8")
            .split()
        )
        proc.sort(key=lambda x: -os.path.getmtime(x))

        for file_path in proc:
            backup_path = f".tmp/{file_path}"

            backup_dir = Path(backup_path).parent
            os.makedirs(backup_dir, exist_ok=True)
            if (
                str(Path(config.tex_data)) in backup_path
                and not "url" in meta
                and backup_path.endswith(".pdf")
            ):
                continue

            if not os.path.exists(backup_path):
                os.system(f"mv {file_path}  {backup_path}")

        difference_compute(
            meta["doc_id"],
            service_id="difference",
            url=meta["url"] if "url" in meta else meta["doc_id"],
            dont_save=True,
        )
        os.system("rm -r .tmp")
    except Exception as e:
        logging.error("Error on recompute, proceed", exc_info=True)
        with open("recompute_errors", "a") as f:
            f.write(traceback.format_exc() + " \n\n\n####\n\n\n")


c = ""
file_paths = [
    "doc_id",
    "html_path",
    "df_path",
    "pdf2htmlEX.html",
    "pdf_path",
    "pdf2htmlEX_wordi_path",
    "feat_path",
]
