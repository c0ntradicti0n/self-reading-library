import gc
import logging
import threading
import tracemalloc

from helpers.cache_tools import configurable_cache
from helpers.hash_tools import hashval
from layout.imports import *
from core import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from layout import model_helpers

tracemalloc.start()
import pyarrow as pa
import pyarrow.parquet as pq


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
        if 'model_path' not in self.flags and 'layout_model_path' not in self.flags:
            raise Exception(
                f"layout model path must be set via pipeline flags, these are the keywords in the call args, {self.flags=}")
        model_path = self.flags['model_path'] if 'model_path' in self.flags else self.flags['layout_model_path']

        self.model_path = model_path

        for pdf_path, meta in x_meta:


            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            print("[ Top 10 ]")
            for stat in top_stats[:10]:
                print(stat)

            try:
                feature_df = meta['final_feature_df']
            except:
                logging.error("final feature df must be there!")
                continue

            predictions_metas_per_document = []

            df = model_helpers.post_process_df(feature_df)

            dataset = Dataset.from_pandas(
                df.loc[:, df.columns != 'chars_and_char_boxes']
            )

            for page_number in range(len(dataset)):
                example = dataset[page_number:page_number + 1]

                self.load_model()

                encoded_inputs = \
                    model_helpers.preprocess_data(training=False)(example, return_tensors="pt")

                labels = encoded_inputs.pop('labels').squeeze().tolist()

                for k, v in encoded_inputs.items():
                    encoded_inputs[k] = v.to(config.DEVICE)
                outputs = Layout2ReadingOrder.model(**encoded_inputs)
                predictions = outputs.logits.argmax(-1).squeeze().tolist()
                token_boxes = encoded_inputs.bbox.squeeze().tolist()

                image = Image.open(example['image_path'][0][0])
                image = image.convert("RGB")
                width, height = image.size

                box_predictions = [config.id2label[prediction] for prediction, label in zip(predictions, labels) if
                                   label != -100]
                enc_boxes = [model_helpers.unnormalize_box(box, width, height) for box, label in
                             zip(token_boxes, labels) if
                             label != -100]

                prediction = {}
                prediction['labels'] = box_predictions
                prediction['bbox'] = enc_boxes
                prediction['df'] = df.iloc[page_number:page_number + 1]
                prediction['image'] = Image.open(example['image_path'][0][0])
                prediction['page_number'] = page_number
                prediction['text'] = prediction['df']['text'].tolist()[0]

                del prediction['df']['chars_and_char_boxes']
                prediction['df_path'] = f"{config.tex_data}--{hashval(pdf_path)}-{page_number}.df"
                table = pa.Table.from_pandas(prediction['df'])
                pq.write_table(table, prediction['df_path'])

                if "ignore_incomplete" in self.flags:
                    if len(box_predictions) != len(example['text'][0]):
                        print(len(box_predictions), box_predictions, len(example['text'][0]), example['text'][0])
                        self.logger.error(f"predicted less labels than textfields on the page, continuing!")

                pagenumber = page_number + 1
                self.logger.info(f"Predicted {pagenumber=}/{len(dataset)} with {box_predictions=}")
                for thread in threading.enumerate():
                    print(thread.name)

                prediction_meta = model_helpers.repaint_image_from_labels((pdf_path, prediction))

                human_image_path = f"{pdf_path}.{page_number}.layout_prediction.png"
                prediction_meta[1]['human_image'].save(human_image_path)
                prediction_meta[1]['human_image_path'] = human_image_path
                prediction_meta[1]['image_path'] =  example['image_path'][0][0]
                del prediction_meta[1]['human_image']
                del prediction_meta[1]['image']
                del prediction_meta[1]['df']

                predictions_metas_per_document.append((pdf_path, prediction))

            annotation = predictions_metas_per_document

            df['LABEL'] = [prediction['labels'] for id, prediction in annotation]

            try:
                title_texts = [_t for _t in
                               [[(i, tag) for i, tag in enumerate(l) if tag in config.TITLE] for l in df['LABEL']] if
                               _t]
                used_titles = [df['text'].tolist()[0][i] for i, h in title_texts[0]]
                used_titles = (used_titles[0] if len(used_titles) > 0 else meta['html_path']).replace("\n", " ")
            except:
                logging.error("Failure setting title", exc_info=True)
                used_titles = meta["html_path"]
            meta['title'] = used_titles

            used_label_is = [
                self.sort_by_label([(i, l) for i, l in enumerate(an[1]['labels']) if l in config.TEXT_LABELS]) for an in
                annotation]
            used_texts = [[annotation[i][1]['text'][ull] for ull in ul] for i, ul in
                          enumerate(used_label_is)]
            used_boxes = [[annotation[i][1]['bbox'][ull] for ull in ul] for i, ul in enumerate(used_label_is)]

            sorted_texts = self.sort_by_box(used_texts, used_boxes)

            meta['used_text_boxes'] = sorted_texts

            enumerated_texts = self.enumerate_words(sorted_texts)

            del df['chars_and_char_boxes']
            meta['df_path'] = config.tex_data + hashval(pdf_path) + ".df"
            meta['layout_predictions'] = annotation
            table = pa.Table.from_pandas(df)
            pq.write_table(table, meta['df_path'])
            if 'df' in meta:
                del meta['df']

            del meta['final_feature_df']

            meta['enumerated_texts'] = enumerated_texts

            gc.collect()

            yield pdf_path, meta

    def load_model(self):
        if not Layout2ReadingOrder.model:
            Layout2ReadingOrder.processor = model_helpers.PROCESSOR
            Layout2ReadingOrder.model = model_helpers.MODEL
            logging.info(f"Loading {self.model_path}")
            Layout2ReadingOrder.model.load_state_dict(torch.load(self.model_path, map_location="cpu"))
            Layout2ReadingOrder.model.eval()
            Layout2ReadingOrder.model.to(config.DEVICE)

    def sort_by_label(self, i_l):
        return [i for i, l in sorted(i_l, key=lambda x: config.TEXT_LABELS.index(x[1]))]

    def sort_by_box(self, all_texts, all_boxes):
        return list(
            sorted(zip(texts, boxes), key=lambda x: x[1][0] + x[1][1]) for texts, boxes in zip(all_texts, all_boxes))

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
