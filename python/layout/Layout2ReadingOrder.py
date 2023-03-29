import gc
import logging
import tracemalloc

import numpy
from transformers import pipeline

from core.microservice import microservice

from helpers.cache_tools import configurable_cache
from helpers.hash_tools import hashval
from helpers.latex_tools import latex_replace
from helpers.nested_dict_tools import flatten
from helpers.str_tools import str_ascii
from layout.imports import *
from config import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from layout import model_helpers

tracemalloc.start()
import pyarrow as pa
import pyarrow.parquet as pq


def cast_array_list(sample):
    if isinstance(sample, dict):
        for k, v in sample.items():
            sample[k] = cast_array_list(v)
    if isinstance(sample, list):
        return numpy.asarray(sample, dtype=object)
    else:
        return sample


def titelize(text):
    text = latex_replace(text)[:1024]
    summarizer = pipeline(
        "summarization"
    )
    title = summarizer(
        text,
        min_length=1,
        max_length=23
    )[0]["summary_text"]

    print(f"{title=}")
    return title


@microservice
@converter("feature", "reading_order")
class Layout2ReadingOrder(PathSpec):
    def __init__(self, *args, num_labels=config.NUM_LABELS, **kwargs):
        super().__init__(*args, **kwargs)

        self.processor = None
        self.num_labels = num_labels

    model = None

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, x_meta, *args, **kwargs):
        from datasets import Dataset
        from transformers import pipeline

        for pdf_path, meta in x_meta:

            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")

            try:
                feature_df = meta["final_feature_df"]
            except:
                logging.error("final feature df must be there!")
                continue

            predictions_metas_per_document = []

            df = model_helpers.post_process_df(feature_df)

            dataset = Dataset.from_pandas(
                df.loc[:, df.columns != "chars_and_char_boxes"]
            )

            for page_number in range(len(dataset)):
                example = dataset[page_number : page_number + 1]
                image = Image.open(example["image_path"][0][0])
                image = image.convert("RGB")
                width, height = image.size

                box_predictions, prediction = self.predict(example, height, width)

                prediction["df"] = df.iloc[page_number : page_number + 1]
                prediction["image"] = Image.open(example["image_path"][0][0])
                prediction["page_number"] = page_number
                prediction["text"] = prediction["df"]["text"].tolist()[0]

                del prediction["df"]["chars_and_char_boxes"]
                pandas.options.mode.chained_assignment = None  # default='warn'

                prediction["df"]["LABEL"] = [box_predictions]

                prediction[
                    "df_path"
                ] = f"{config.tex_data}--{hashval(pdf_path)}-{page_number}.df"
                table = pa.Table.from_pandas(prediction["df"])
                pq.write_table(table, prediction["df_path"])

                if "ignore_incomplete" in self.flags:
                    if len(box_predictions) != len(example["text"][0]):
                        print(
                            len(box_predictions),
                            box_predictions,
                            len(example["text"][0]),
                            example["text"][0],
                        )
                        self.logger.error(
                            f"predicted less labels than textfields on the page, continuing!"
                        )

                pagenumber = page_number + 1
                self.logger.info(''
                    f"Labels {pagenumber}/{len(dataset)}:\n\t\t {'·'.join(box_predictions)}"
                )

                prediction_meta = model_helpers.repaint_image_from_labels(
                    (pdf_path, prediction)
                )

                human_image_path = f"{pdf_path}.{page_number}.layout_prediction.png"
                prediction_meta[1]["human_image"].save(human_image_path)
                prediction_meta[1]["human_image_path"] = human_image_path
                prediction_meta[1]["image_path"] = example["image_path"][0][0]
                del prediction_meta[1]["human_image"]
                del prediction_meta[1]["image"]
                del prediction_meta[1]["df"]

                predictions_metas_per_document.append((pdf_path, prediction))

            annotation = predictions_metas_per_document

            df["LABEL"] = [prediction["labels"] for id, prediction in annotation]

            try:
                title_texts = [
                    _t
                    for _t in [
                        [(i, tag) for i, tag in enumerate(l) if tag in config.TITLE]
                        for l in df["LABEL"]
                    ]
                    if _t
                ]
                used_titles = [df["text"].tolist()[0][i] for i, h in title_texts[0]]
                used_titles = (
                    used_titles[0] if len(used_titles) > 0 else meta["html_path"]
                ).replace("\n", " ")
            except:
                logging.error("Failure setting title", exc_info=True)
                used_titles = meta["html_path"]

            used_label_is = [
                self.sort_by_label(
                    [
                        (i, l)
                        for i, l in enumerate(an[1]["labels"])
                        if l in config.TEXT_LABELS
                    ]
                )
                for an in annotation
            ]
            used_texts = [
                [annotation[i][1]["text"][ull] for ull in ul]
                for i, ul in enumerate(used_label_is)
            ]
            used_boxes = [
                [annotation[i][1]["bbox"][ull] for ull in ul]
                for i, ul in enumerate(used_label_is)
            ]

            used_texts = list(map(lambda l: map(str_ascii, l), used_texts))
            sorted_texts = self.sort_by_box(used_texts, used_boxes)

            meta["used_text_boxes"] = sorted_texts

            enumerated_texts = self.enumerate_words(sorted_texts)

            del df["chars_and_char_boxes"]
            meta["df_path"] = config.tex_data + hashval(pdf_path) + ".df"
            meta["layout_predictions"] = annotation
            table = pa.Table.from_pandas(df)
            pq.write_table(table, meta["df_path"])
            if "df" in meta:
                del meta["df"]

            del meta["final_feature_df"]

            meta["enumerated_texts"] = enumerated_texts

            text= latex_replace("\n\n".join(prediction["text"]))
            title= titelize(text)
            meta["title"] = title

            gc.collect()

            yield pdf_path, meta

    def predict(self, example, height, width):
        print(example, height, width)
        cast_array_list(example)

        encoded_inputs = model_helpers.preprocess_data(training=False)(
            example, return_tensors="pt"
        )
        labels = encoded_inputs.pop("labels").squeeze().tolist()

        for k, v in encoded_inputs.items():
            encoded_inputs[k] = v.to(self.DEVICE)

        outputs = self.model(**encoded_inputs)

        predictions = outputs.logits.argmax(-1).squeeze().tolist()

        token_boxes = encoded_inputs.bbox.squeeze().tolist()
        box_predictions = [
            config.id2label[prediction]
            for prediction, label in zip(predictions, labels)
            if label != -100
        ]
        enc_boxes = [
            model_helpers.unnormalize_box(box, width, height)
            for box, label in zip(token_boxes, labels)
            if label != -100
        ]
        prediction = {}
        prediction["labels"] = box_predictions
        prediction["bbox"] = enc_boxes
        return box_predictions, prediction

    def load(self):
        import torch

        logging.info(torch.__version__)
        import os

        import shutil

        from pprint import pprint, pformat

        import pandas

        import torch

        from matplotlib import colors

        from torch.utils.data import DataLoader

        from datasets import load_metric

        from GPUtil import showUtilization as gpu_usage

        from sklearn.preprocessing import MinMaxScaler

        from datasets import Dataset

        from PIL import Image, ImageFilter

        from transformers import LayoutLMv2Processor

        from datasets import Features, Sequence, ClassLabel, Value, Array2D, Array3D

        import torch

        from tqdm import tqdm

        from PIL import Image, ImageDraw, ImageFont

        font = ImageFont.load_default()

        self.DEVICE = torch.device("cpu")

        self.model_path = config.layout_model_path
        print(f" - {config.layout_model_path}")

        self.processor = model_helpers.LayoutModelParts().PROCESSOR
        print(f" - {self.processor=}")

        self.model = model_helpers.LayoutModelParts().MODEL

        self.model.load_state_dict(torch.load(self.model_path, map_location="cpu"))
        logging.info(f" - loaded state dict")

        self.model.eval()
        logging.info(f" - eval")

        self.model.to(self.DEVICE)
        logging.info(f" - using {self.DEVICE}")

    def sort_by_label(self, i_l):
        return [i for i, l in sorted(i_l, key=lambda x: config.TEXT_LABELS.index(x[1]))]

    def sort_by_box(self, all_texts, all_boxes):
        return list(
            sorted(zip(texts, boxes), key=lambda x: x[1][0] + x[1][1])
            for texts, boxes in zip(all_texts, all_boxes)
        )

    def enumerate_words(self, all_texts):
        i = 0
        all_enumeration = []
        for texts in all_texts:
            enumeration = []
            for word in " ".join([text for text, box in texts]).split(" "):
                enumeration.append((i, word))
                i += 1
            enumeration.append((i, "\n    "))
            i += 1
            all_enumeration.append(enumeration)

        return all_enumeration


if __name__ == "__main__":
    Layout2ReadingOrder.application.run()
