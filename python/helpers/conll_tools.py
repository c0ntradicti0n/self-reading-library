import logging
import os
from pathlib import Path
from random import shuffle

import nltk
import regex
from allennlp.data.dataset_readers import Conll2003DatasetReader

from language.span.DifferenceSpanSet import Span
from language.transformer.old.bio_annotation import conll_line


def conll2annotation(content, swap=False):
    cols = list(
        zip(
            *[
                m.groups()
                for i, line in enumerate(content.split("\n"))
                if line and (m := conll_line.match(line.replace("\t", "  ")))
            ]
        )
    )
    if not cols:
        logging.error("could not read annotation file, no conll3 match")
    try:
        result = {
            "annotation": list(
                list(t)
                for t in zip(*[cols[0], cols[-1]] if not swap else [cols[-1], cols[0]])
            ),
            "pos": cols[1],
        }
    except:
        logging.error(f"Error reading annotation {cols=}\n{content=}", exc_info=True)
        raise
    return result


def conll_file2annotation(pickle_path, swap=False):
    with open(pickle_path, errors="ignore") as f:
        content = f.read()

    try:
        result = conll2annotation(content, swap=swap)
    except:
        os.remove(pickle_path)
        logging.error("Had to remove conll file")
        raise
    return result


def conll_concat_train_valid(dir):

    exclude = "train", "valid"
    samples = os.listdir(dir)
    shuffle(samples)
    split = int(len(samples) // 1.5)
    train = samples[:split]
    valid = samples[split:]
    conll_reader = Conll2003DatasetReader(coding_scheme="BIOUL")
    for n, s in [("train", train), ("valid", valid)]:
        out = f"{dir}/{n}.conll3"
        os.system(f"rm {out}")
        i = 0
        for t in s:
            t_p = f"{dir}/{t}"
            if not any(e in t for e in exclude):
                if not Path(t_p).read_text():
                    os.system(f"rm -rf {t_p}")
                    continue

                try:
                    list(conll_reader._multi_worker_islice(conll_reader._read(t_p)))
                except:
                    try:
                        txt = Path(t_p).read_text()
                        txt = regex.sub(r"\$\t\$", r"." + "\t" + r".", txt)
                        txt = regex.sub(r"\t\$\t", "\t.\t", txt)

                        tag_rex = r"([\w.,;$:?!\-()\[\]]+)"

                        txt = regex.sub(
                            rf"U-{tag_rex}\t(U|B)-(\w+)", r"B-\1" + "\t" + r"B-\2", txt
                        )
                        txt = regex.sub(
                            rf"L-{tag_rex}\tL-(\w+)", r"I-\1" + "\t" + r"I-\2", txt
                        )
                        txt = regex.sub(
                            rf"{tag_rex}\tO(\n|$)", r"O" + "\t" + r"O" + "\n", txt
                        )

                        txt = txt.replace("$", "")

                        with open(t_p, "w") as f:
                            f.write(txt)

                        list(conll_reader._multi_worker_islice(conll_reader._read(t_p)))

                    except:
                        logging.error(
                            "Corrupt conll could not be repaired", exc_info=True
                        )

                        continue

                a = conll_file2annotation(t_p)
                if any("SUBJECT" in aa[0] for aa in a["annotation"]):
                    annotation2conll_file(
                        [aa[::1] for aa in a["annotation"]], t, dir, pos=a["pos"]
                    )
                # os.system(f"echo \"# {i}\\n\" >> {out}")

                os.system(f"cat {t_p} >> {out}")
                os.system(f'echo "\\n\\n" >> {out}')
                i += 1
        txt = Path(out).read_text()
        txt = regex.sub(r"\$\t\$", r"." + "\t" + r".", txt)
        txt = regex.sub(r"\t\$\t", "\t.\t", txt)

        tag_rex = r"([\w.,;$:?!\-()\[\]]+)"

        txt = regex.sub(rf"U-{tag_rex}\tU-(\w+)", r"B-\1" + "\t" + r"B-\2", txt)
        txt = regex.sub(rf"L-{tag_rex}\tL-(\w+)", r"I-\1" + "\t" + r"I-\2", txt)
        txt = regex.sub(rf"{tag_rex}\tO\n", r"O" + "\t" + r"O" + "\n", txt)
        txt = txt.replace("$", "")

        with open(out, "w") as f:
            f.write(txt)


def annotation2conll_file(annotation, filename, new_folder, pos=None):
    tags, words = list(zip(*annotation))

    if not pos:
        logging.info(words)
        try:
            pos = nltk.pos_tag(words)

        except LookupError:
            nltk.download("averaged_perceptron_tagger")
            pos = nltk.pos_tag(words)
        pos = [p for w, p in pos]
    logging.info(pos)

    print(f"\n{annotation=} \n{pos=}\n")

    pos_tags = [p if "-" not in tag else tag[:2] + p for tag, p in zip(tags, pos)]
    print(f"\n{words=} \n{pos=} {pos_tags=} \n{tags=}\n")

    content = "\n".join("\t".join(t) for t in zip(words, pos, pos_tags, tags))
    if not os.path.isdir(new_folder):
        os.makedirs(new_folder)
    new_path = new_folder + "/" + filename
    with open(new_path, "w") as f:
        f.write(content)
    return new_path
