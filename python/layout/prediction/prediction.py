from layout.imports import *
from core import config
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from layout import model_helpers

@converter("feature", "prediction")
class Prediction(PathSpec):
    def __init__(self, *args, num_labels = config.NUM_LABELS, **kwargs):
        super().__init__(*args,  **kwargs)

        self.model = None
        self.processor = None
        self.num_labels = num_labels

    def __call__(self, x_meta, *args, **kwargs):
        model_path = self.flags['layout_model_path']
        if not model_path:
            raise Exception(f"layout model path must be set via pipeline flags, these are the keywords in the call args, {self.flags=}")
        self.model_path = model_path


        for feature_df, meta in x_meta:

            predictions_metas_per_document = []

            df = model_helpers.post_process_df(feature_df)

            dataset = Dataset.from_pandas(df.loc[:, df.columns != 'chars_and_char_boxes'])

            for page_number in range(len(dataset)-1):
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

                image = Image.open(config.path_prefix + example['image_path'][0][0])
                image = image.convert("RGB")
                width, height = image.size

                box_predictions = [config.id2label[prediction] for prediction, label in zip(predictions, labels) if label != -100]
                enc_boxes = [model_helpers.unnormalize_box(box, width, height) for box, label in zip(token_boxes, labels) if
                             label != -100]


                prediction = {}
                prediction['labels'] = box_predictions
                prediction['bbox'] = enc_boxes
                prediction['df'] = df.iloc[page_number:page_number+1]
                prediction['image'] = Image.open(config.path_prefix + example['image_path'][0][0])
                prediction['page_number'] = page_number

                if "ignore_incomplete" in self.flags:
                    if len(box_predictions) != len(example['text'][0]):
                        print (len(box_predictions), box_predictions, len(example['text'][0]), example['text'][0])
                        self.logger.error(f"predicted less labels than textfields on the page, continuing!")
                        continue
                else:

                    self.logger.info(f"predicted {page_number =} with labels {box_predictions =}")

                    prediction_meta = model_helpers.repaint_image_from_labels ((prediction, meta))
                    prediction_meta[0]['human_image'].save(f"{config.PREDICTION_PATH}/boxes_{page_number}.png")

                    predictions_metas_per_document.append(prediction_meta)

            yield predictions_metas_per_document, meta

    def load_model(self):
        if not self.model:
            self.processor = model_helpers.PROCESSOR
            self.model = model_helpers.MODEL

            self.model.load_state_dict(torch.load(self.model_path, map_location="cpu"))
            self.model.eval()
            self.model.to(config.DEVICE)


