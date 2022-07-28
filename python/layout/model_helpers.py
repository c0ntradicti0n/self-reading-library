from PIL.Image import Resampling

from layout.imports import *
from core import config
import random
import pickle
from regex import regex

def compute_bbox(examples):
    bbox = list(list(zip(*b)) for b in zip(examples['x0'], examples['y0'], examples['x1'], examples['y1']))

    assert min(min(min(bbox))) > 0, "should be >= 0"
    assert max(max(max(bbox))) < 1000, "should be < 1000"

    return bbox


def post_process_df(feature_df):
    feature_df = feature_df.head((int(len(feature_df))))

    if "box_schema" in feature_df:
        feature_df = feature_df.drop("box_schema", axis=1)

    feature_df['x0'] = feature_df['x0'] / feature_df['page_width'] * 999 + 1
    feature_df['x1'] = feature_df['x1'] / feature_df['page_width'] * 999 + 1
    feature_df['y0'] = (feature_df['y0'] / feature_df['page_height'] * -1 + 1) * 999 + 1
    feature_df['y1'] = (feature_df['y1'] / feature_df['page_height'] * -1 + 1) * 999 + 1

    feature_df.loc[feature_df.x0 < 1, 'x0'] = 1
    feature_df.loc[feature_df.x0 > 999, 'x0'] = 999

    feature_df.loc[feature_df.x1 < 1, 'x1'] = 1
    feature_df.loc[feature_df.x1 > 999, 'x1'] = 999

    feature_df.loc[feature_df.y0 < 1, 'y0'] = 1
    feature_df.loc[feature_df.y0 > 999, 'y0'] = 999

    feature_df.loc[feature_df.y1 < 1, 'y1'] = 1
    feature_df.loc[feature_df.y1 > 999, 'y1'] = 999

    feature_df[['x0', 'x1', 'y0', 'y1']] = feature_df[['x0', 'x1', 'y0', 'y1']].astype(int)

    xmask = feature_df['x1'] < feature_df['x0']
    feature_df.loc[xmask, 'x1'], feature_df.loc[xmask, 'x0'] = feature_df.x0[xmask], feature_df.x1[xmask]
    xmask = feature_df['x1'] >= feature_df['x0']
    assert (all(xmask))

    ymask = feature_df['y1'] < feature_df['y0']
    feature_df.loc[ymask, 'y1'], feature_df.loc[ymask, 'y0'] = feature_df.y0[ymask], feature_df.y1[ymask]
    ymask = feature_df['y1'] >= feature_df['y0']
    assert (all(ymask))

    feature_df['label'] = feature_df.LABEL.map(config.label2id)

    page_groups = feature_df.groupby(['page_number', "doc_id"])
    feature_df = page_groups.agg({col: (lambda x: list(x)) for col in feature_df.columns})
    feature_df['len'] = feature_df.LABEL.map(len)

    feature_df.drop(feature_df[feature_df.len > 190].index, inplace=True)

    return feature_df

if os.path.isfile(config.PROCESSOR_PICKLE):
    with open(config.PROCESSOR_PICKLE, "rb") as f:
        PROCESSOR = pickle.load(f)
else:
    PROCESSOR = LayoutLMv2Processor.from_pretrained("microsoft/layoutlmv2-base-uncased", revision="no_ocr")
    with open(config.PROCESSOR_PICKLE, "wb") as f:
        pickle.dump(PROCESSOR, f)

if os.path.isfile(config.MODEL_PICKLE):
    with open(config.MODEL_PICKLE, "rb") as f:
        MODEL = pickle.load(f)
else:
    MODEL = LayoutLMv2ForTokenClassification.from_pretrained(
        'microsoft/layoutlmv2-base-uncased',
         num_labels=config.NUM_LABELS
    )
    with open(config.MODEL_PICKLE, "wb") as f:
        pickle.dump(MODEL, f)


def preprocess_data(training=False):
    def _preprocess(examples, **kwargs):
        global PROCESSOR

        words = [[" ".join(word.split()[:4] #+ word.split()[-2:]
                           )  for word in text] for text in examples['text']]

        boxes = compute_bbox(examples)

        word_labels = ([[0] * (len(examples['label'][0]))]) if not training else [[config.label2id[l] for l in L] for L in examples['LABEL']]

        if training:
            print (f"{word_labels = }")

        images = [Image.open(path[0]).convert("RGB") for path in examples['image_path']]

        images = [resize(image, 255) for image in images]

        encoded_inputs = PROCESSOR(images, words, boxes=boxes, word_labels=word_labels,
                                   padding="max_length", truncation=True, return_overflowing_tokens=False, **kwargs)

        return encoded_inputs
    return _preprocess






def unnormalize_box(bbox, width, height):
    return [
        width * (bbox[0] / 1000),
        height * (bbox[1] / 1000),
        width * (bbox[2] / 1000),
        height * (bbox[3] / 1000),
    ]


def resize(image, basesize):
    wpercent = (basesize / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    img = image.resize((basesize, hsize), Resampling.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(4))
    return img


def repaint_image_from_labels(data_meta):
    id, data = data_meta
    labels = data['labels']
    bbox = data['bbox']
    _image = data['image']
    image = _image.copy()
    draw = ImageDraw.Draw(image, "RGBA")

    for box, label in zip(bbox, labels):
        actual_label = label
        fill_color = tuple([*[int(x * 255) for x in colors.to_rgb(config.label2color[actual_label])], 127])
        draw.rectangle(box, fill=fill_color)
        draw.text((box[0] + 10, box[1] + 10), actual_label, fill=config.label2color[actual_label], font=font)

    data['human_image'] = image
    return (id, data)