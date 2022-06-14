import logging

from helpers.cache_tools import configurable_cache
from layout.imports import *
from core import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from layout import model_helpers


@converter("feature", "reading_order")
class Layout2ReadingOrder(PathSpec):
    def __init__(self, *args, num_labels=config.NUM_LABELS, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = None
        self.processor = None
        self.num_labels = num_labels

    @configurable_cache(
        filename=config.cache + os.path.basename(__file__),
    )
    def __call__(self, x_meta, *args, **kwargs):
        if  'model_path' not in self.flags and  'layout_model_path' not in self.flags:
            raise Exception(
                f"layout model path must be set via pipeline flags, these are the keywords in the call args, {self.flags=}")
        model_path = self.flags['model_path'] if 'model_path' in self.flags else self.flags['layout_model_path']

        self.model_path = model_path

        for pdf_path, meta in x_meta:
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

            for page_number in range(len(dataset) - 1):
                example = dataset[page_number:page_number + 1]

                self.load_model()

                encoded_inputs = \
                    model_helpers.preprocess_data(training=False)(example, return_tensors="pt")

                labels = encoded_inputs.pop('labels').squeeze().tolist()

                for k, v in encoded_inputs.items():
                    encoded_inputs[k] = v.to(config.DEVICE)
                outputs = self.model(**encoded_inputs)
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

                if "ignore_incomplete" in self.flags:
                    if len(box_predictions) != len(example['text'][0]):
                        print(len(box_predictions), box_predictions, len(example['text'][0]), example['text'][0])
                        self.logger.error(f"predicted less labels than textfields on the page, continuing!")
                        continue
                else:
                    pagenumber = page_number + 1
                    self.logger.info(f"Predicted {pagenumber=}/{len(dataset) - 1} with {box_predictions=}")

                    prediction_meta = model_helpers.repaint_image_from_labels((prediction, meta))
                    prediction_meta[0]['human_image'].save(f"{config.PREDICTION_PATH}/boxes_{page_number}.png")
                    prediction_meta[0]['human_image'].save(
                        f"{os.path.dirname(meta['html_path'])}/layout_boxes_{page_number}.png")

                    predictions_metas_per_document.append(prediction_meta)

            annotation = predictions_metas_per_document

            try:
                title = [[(i, l) for i, l in enumerate(an[0]['labels']) if l in config.TITLE] for an in annotation]
                used_titles = [annotation[0][0]['df']['text'].tolist()[0][i] for i, h in title[0]]
                used_titles = used_titles[0] if len(used_titles) > 1 else meta['html_path']
            except:
                logging.error("Failure setting title", exc_info=True)
                used_titles = meta["html_path"]
            meta['title'] = used_titles

            used_label_is = [
                self.sort_by_label([(i, l) for i, l in enumerate(an[0]['labels']) if l in config.TEXT_LABELS]) for an in
                annotation]
            used_texts = [[annotation[i][0]['df']['text'].tolist()[0][ull] for ull in ul] for i, ul in
                          enumerate(used_label_is)]
            used_boxes = [[annotation[i][0]['bbox'][ull] for ull in ul] for i, ul in enumerate(used_label_is)]

            sorted_texts = self.sort_by_box(used_texts, used_boxes)

            meta['used_text_boxes'] = sorted_texts

            enumerated_texts = self.enumerate_words(sorted_texts)
            if 'df' in meta:
                del meta['df']
            del meta['chars_and_char_boxes']
            del meta['final_feature_df']

            meta['enumerated_texts'] = enumerated_texts
            yield pdf_path, meta

    def load_model(self):
        if not self.model:
            self.processor = model_helpers.PROCESSOR
            self.model = model_helpers.MODEL

            self.model.load_state_dict(torch.load(self.model_path, map_location="cpu"))
            self.model.eval()
            self.model.to(config.DEVICE)

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


