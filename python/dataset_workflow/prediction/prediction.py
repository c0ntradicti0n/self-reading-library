from dataset_workflow.imports import *
from layouteagle import config
from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathSpec import PathSpec
from dataset_workflow import model_helpers

@converter("feature", "prediction")
class Prediction(PathSpec):
    def __init__(self, *args, num_labels = 2, model_path = config.MODEL_PATH, **kwargs):
        super().__init__(*args,  **kwargs)
        self.model_path = model_path
        self.model = None
        self.processor = None
        self.num_labels = num_labels

    def __call__(self, x_meta, *args, **kwargs):
        for feature_df, meta in x_meta:

            df = model_helpers.post_process_df(feature_df)

            dataset = Dataset.from_pandas(df)

            for i in range(len(dataset)-1):
                example = dataset[i:i + 1]

                new_hash = str((example['x0'], example['x1'], example['y0'], example['y1']))


                self.load_model()

                encoded_inputs = \
                    model_helpers.preprocess_data(training=False)(example, return_tensors="pt")

                labels = encoded_inputs.pop('labels').squeeze().tolist()

                for k, v in encoded_inputs.items():
                    encoded_inputs[k] = v.to(config.DEVICE)
                outputs = self.model(**encoded_inputs)
                predictions = outputs.logits.argmax(-1).squeeze().tolist()
                token_boxes = encoded_inputs.bbox.squeeze().tolist()

                box_predictions = [config.id2label[prediction] for prediction, label in zip(predictions, labels) if label != -100]
                enc_boxes = [model_helpers.unnormalize_box(box, width, height) for box, label in zip(token_boxes, labels) if
                             label != -100]


                prediction = {}
                prediction['labels'] = box_predictions
                prediction['bbox'] = enc_boxes
                prediction['df'] = df.iloc[i:i+1]

                prediction = repaint_image_from_labels (prediction)

                yield prediction, meta

    def load_model(self):
        if not self.model:
            self.processor = LayoutLMv2Processor.from_pretrained("microsoft/layoutlmv2-base-uncased", revision="no_ocr")

            self.model = LayoutLMv2ForTokenClassification.from_pretrained('microsoft/layoutlmv2-base-uncased',
                                                                     num_labels=self.num_labels)
            self.model.load_state_dict(torch.load(self.model_path))
            self.model.eval()
            self.model.to(config.DEVICE)


