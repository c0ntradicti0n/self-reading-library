import os
import sys
import logging
from helpers.nested_dict_tools import flatten

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
from numba import cuda

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

try:
    free_gpu_cache()
except Exception as e:
    logging.error("No cuda available!", e)

feature_fuzz_ranges = (-0.02, 0.04, 0.02),
sys.path.append(os.getcwd())

logging_config = '/home/finn/PycharmProjects/LayoutEagle/python/logging.yaml'
model_config = "elmo_lstm3_feedforward4_crf_straight.config"
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

doc_port = 5180
app_port = 5181
annotation_port = 5182
science_port = 5183

hidden_folder = ".layouteagle/"
cache = hidden_folder + "cache/"
tex_data = hidden_folder + "tex_data/"
models = hidden_folder + "models/"

tex_source = "http://arxiv.org"

INDEX_WRAP_TAG_NAME = 'z'

log_files = {
    "ccapp": "./CorpusCookApp/log.log",
    "cc": "../CorpusCook/log.log",
    "dist": "../Distinctiopus4/log.log"
}

science_map_corpus_path = "../ScienceMap/manual_corpus/"
science_map_working_dir = "../ScienceMap/"
science_map = "../ScienceMap/GUI.py"
science_map_venv = "../ScienceMap/venv/bin/activate"
science_map_csv = "../ScienceMap/manual_corpus/relations.csv"

ampligraph_working_dir = "../KnowledgeScience/"
ampligraph_venv = "../KnowledgeScience/venv/bin/activate"
ampligraph = "../KnowledgeScience/csv_ampligraph.py"
ampligraph_coords = "CONSTRASTSUBJECT"

all_coordinates = "../KnowledgeScience/knowledge_graph_coords/knowledge_graph_3d_choords.csv"
ke_path = "../KnowledgeScience/knowledge_graph_coords/tsne_clusters_mean_points.csv"
ke_colors = "../KnowledgeScience/knowledge_graph_coords/kn_clusters_mean_points.csv"
hal = '"../hal/target/hal-1-jar-with-dependencies.jar"'
video_dir = '../view_control_web/WebContent/resources/media/'

wordlist = '../pdfetc2txt/wordlist.txt'

reader_width = 700
import numpy

reader_height = numpy.sqrt(2) * reader_width

page_margin_bottom = 0.06
page_margin_top = 0.15

pdf_dir = "../test/"
topics_dump = "./topics.pickle"
markup_dir = pdf_dir
markup_suffix = "pdflayout.html"

pdf2htmlEX = "pdf2htmlEX"

difference_model_train_output = hidden_folder + f"/over_{model_config}/"
difference_model_config = hidden_folder + f"/over_{model_config}/config.json"

wordninjalanguagemodel = "language/english.txt.gz"
logging_level = logging.INFO

layout_model_path = hidden_folder + "/layout_model/"
saved_layout_model_dir = hidden_folder + "/layout_model_saved/"

collected_features_path = ".core/labeled_features.pickle"

use_pdf2htmlex_features = False

"""
cols_to_use = [
    *(['width','ascent', 'descent',
    'x1', 'y1', 'x2', 'y2',
    'dxy1', 'dxy2', 'dxy3', 'dxy4',
    #'sin1', 'sin2', 'sin3', 'sin4',
    #'probsin1', 'probsin2', 'probsin3', 'probsin4',
    'probascent', 'probdescent',
    *list(flatten([[f'nearest_{k}_center_x', f'nearest_{k}_center_y']
                   for k in range(layout_model_next_text_boxes)]))]
      if use_pdf2htmlex_features else [
        'len', 'height', 'font-size', 'line-height', 'x', 'y'
    ])

]"""
cols_to_use = ["page_number",
               "number_of_lines",
               "x", "y", "x0", "x1", "y0", "y1", "height", "width"]

# array_cols_to_use = ['angle', 'distance_vector', 'x_profile', 'y_profile', 'xy_profile'
#                     ]

array_cols_to_use = []  # ["box_schema"]
N = 7

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
TEXT_BOX_MODEL_PATH = hidden_folder + "text_box_models/"

PREDICTION_PATH = hidden_folder + "prediction/"
NOT_COLLECTED_PATH = hidden_folder + "non_collection/"

COLLECTION_PATH = hidden_folder + "collection/"
# label2id = {'NONE': 0, 'c1': 1, 'c2': 2, 'c3': 3}
LABELS = ['NONE', 'c1', 'c2', 'c3', 'wh', 'h', 'pn', 'fn', 'fg', 'tb']

TEXT_LABELS = ['c1', 'c2', 'c3', 'wh', 'h']

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

# we need to define custom features
from datasets import Features, Sequence, ClassLabel, Value, Array2D, Array3D

LABELS = [label2id[L] for L in LABELS]
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


ELMO_DIFFERENCE_MODEL_PATH=hidden_folder + "elmo_difference_models"
ELMO_DIFFERENCE_COLLECTION_PATH=hidden_folder + "elmo_difference_collection"