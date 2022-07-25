import os
import sys
sys.path.append(".")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging

os.environ["LD_LIBRARY_PATH"] = '/usr/local/cuda-11.0/targets/x86_64-linux/lib/'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TOKENIZERS_PARALLELISM'] = 'true'
from traceback_with_variables import activate_by_import

from traceback_with_variables import Format, ColorSchemes, is_ipython_global

fmt = Format(
    before=5,
    after=3,
    max_value_str_len=-1,
    max_exc_str_len=-1,
    ellipsis_='...',
    color_scheme=ColorSchemes.synthwave,
    skip_files_except=['my_project', 'site-packages'],
    brief_files_except='my_project',
    custom_var_printers=[  # first matching is used
        ('password', lambda v: '...hidden...'),  # by name, print const str
        (list, lambda v: f'list{v}'),  # by type, print fancy str
        (lambda name, type_, filename, is_global: is_global, lambda v: None),  # custom filter, skip printing
        (is_ipython_global, lambda v: None),  # same, handy for Jupyter
        (['secret', dict, (lambda name, *_: 'asd' in name)], lambda v: '???'),  # by different things, print const str
    ]
)
import tensorflow as tf

tf.config.list_physical_devices('GPU')
tf.get_logger().setLevel(3)
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
import numpy

numpy.set_printoptions(threshold=sys.maxsize)

logging.getLogger('allennlp').setLevel(logging.ERROR)

logging.getLogger('pytorch_pretrained_bert').setLevel(logging.ERROR)
logging.getLogger('pytorch_transformers').setLevel(logging.ERROR)
logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.basicConfig(format="""%(asctime)s-%(levelname)s: %(message)s""", datefmt="%H:%M:%S")

from GPUtil import showUtilization as gpu_usage
import torch

path_prefix = "./"


def free_gpu_cache():
    print("Initial GPU Usage")
    gpu_usage()

    torch.cuda.empty_cache()

    cuda.select_device(0)
    cuda.close()
    cuda.select_device(0)

    print("GPU Usage after emptying the cache")
    gpu_usage()


import torch

torch.cuda.empty_cache()

try:
    free_gpu_cache()
except Exception as e:
    logging.error("No cuda/gpu available!")

feature_fuzz_ranges = (-0.02, 0.04, 0.02),
sys.path.append(os.getcwd())

logging_level = logging.INFO
logging_config = '/home/finn/PycharmProjects/LayoutEagle/python/config/logging.yaml'
model_config = "elmo_lstm3_feedforward4_crf_straight.json"
jobs = 32
max_time_per_call = 30
# "elmo_multi_head_self_attention_crf_straight_fitter.config"
parse_pdf2htmlEX = True
n_layout_training_documents = 500
max_windows_per_text = 100
recursive = True
NORMAL_HEIGHT = 100
page_array_model = 100
layout_model_next_text_boxes = 5
hidden_folder = ".layouteagle/"
cache = hidden_folder + "cache/"
tex_data = hidden_folder + "/pdfs/"
models = hidden_folder + "models/"
tex_source = "http://arxiv.org"
INDEX_WRAP_TAG_NAME = 'z'
wordlist = '../pdfetc2txt/wordlist.txt'
reader_width = 700
basewidth = 2500

reader_height = numpy.sqrt(2) * reader_width

page_margin_bottom = 0.06
page_margin_top = 0.15

pdf_dir = ""
topics_dump = hidden_folder + "/topics/topics.pickle"
markup_dir = pdf_dir
markup_suffix = "pdflayout.html"

pdf2htmlEX = "pdf2htmlEX"

difference_model_train_output = hidden_folder + f"/over_{model_config}/"
difference_model_config = f"language/transformer/experiment_configs/{model_config}"

wordninjalanguagemodel = "language/english.txt.gz"
layout_model_path = hidden_folder + "/layout_model/"
saved_layout_model_dir = hidden_folder + "/layout_model_saved/"
collected_features_path = ".core/labeled_features.pickle"
use_pdf2htmlex_features = False
cols_to_use = ["page_number",
               "number_of_lines",
               "x", "y", "x0", "x1", "y0", "y1", "height", "width"]
array_cols_to_use = []
N = 7
DEVICE = torch.device('cpu')
#        torch.device('cuda' if torch.cuda.is_available() else 'cpu')
TEXT_BOX_MODEL_PATH = hidden_folder + "text_box_models/"
PREDICTION_PATH = hidden_folder + "prediction/"
NOT_COLLECTED_PATH = hidden_folder + "non_collection/"
COLLECTION_PATH = hidden_folder + "collection/"
LABELS = ['NONE', 'c1', 'c2', 'c3', 'wh', 'h', 'pn', 'fn', 'fg', 'tb']
TEXT_LABELS = ['c1', 'c2', 'c3', 'wh']
TITLE = ['h']
MAX_PAGES_PER_DOCUMENT = 25
label2id = {t: i for i, t in enumerate(LABELS)}
label2color = {'c1': 'blue',
               'c2': 'green',
               'c3': 'orange',
               'NONE': 'violet',
               'none': 'violet',
               'None': 'violet',
               'other': 'yellow',
               None: 'violet',
               'pn': 'yellow',
               'h': 'red',
               'wh': 'purple',
               'fg': 'brown',
               'fn': 'grey',
               'tb': 'beige'}
id2label = {v: k for k, v in label2id.items()}
LABELS = [label2id[L] for L in LABELS]
from datasets import Features, Sequence, ClassLabel, Value, Array2D, Array3D
FEATURES = Features({
    'image': Array3D(dtype="int64", shape=(3, 224, 224)),
    'input_ids': Sequence(feature=Value(dtype='int64')),
    'attention_mask': Sequence(Value(dtype='int64')),
    'token_type_ids': Sequence(Value(dtype='int64')),
    'bbox': Array2D(dtype="int64", shape=(512, 4)),
    'labels': Sequence(ClassLabel(names=LABELS + [max(LABELS) + 1]))
})
NUM_LABELS = len(LABELS)
PROCESSOR_PICKLE = f"processor_module{NUM_LABELS}.pickle"
MODEL_PICKLE = f"model_module{NUM_LABELS}.pickle"
EPOCHS_LAYOUT = 84
PDF_UPLOAD_DIR = hidden_folder + "/pdf_upload/"
ELMO_DIFFERENCE_MODEL_PATH = hidden_folder + "elmo_difference_models"
ELMO_DIFFERENCE_COLLECTION_PATH = hidden_folder + "elmo_difference_collection"
PORT = 7789

TOPIC_TEXT_LENGTH = 180
spacy_model_name = 'en_core_web_trf'
audio_format = "ogg"
