import os
import subprocess
import threading
from pathlib import Path

from regex import regex
from glob import glob

import config.config
from config.ant_imports import *

# from debugger_tools import connect_debugger
from helpers.cache_tools import refactor_filename
from helpers.time_tools import wait_for_change
from layout.annotation_thread import annotate_uploaded_file as layout_compute
from language.transformer.ElmoDifference import (
    annotate_uploaded_file as difference_compute,
)

ant = PathAnt()

docs = os.listdir(refactor_filename(ElmoDifference.cache_folder))
for doc, meta in ant("css.difference", "recompute")(metaize(docs)):
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

    for file_path in proc:
        backup_path = f".tmp/{file_path}"

        backup_dir = Path(backup_path).parent
        os.makedirs(backup_dir, exist_ok=True)
        if  str(Path(config.tex_data)) in backup_path and not meta['url'] and backup_path.endswith(".pdf"):
            continue

        if not os.path.exists(backup_path):
            os.system(f"mv {file_path}  {backup_path}")

    difference_compute(
         meta["doc_id"],
        service_id="difference",
        url=meta["url"] if "url" in meta else meta["doc_id"],
    )
    os.system("rm -r .tmp")


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
