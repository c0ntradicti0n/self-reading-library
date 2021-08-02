import os
import sys
import logging
from helpers.nested_dict_tools import flatten
import sys
sys.path.append(".")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel(3)
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

logging.getLogger('allennlp').setLevel(logging.ERROR)
logging.getLogger('pdfminer').setLevel(logging.ERROR)

logging.basicConfig(format="""%(asctime)s-%(levelname)s: %(message)s""", datefmt="%H:%M:%S")

feature_fuzz_ranges = (-0.03, 0.03, 0.02), (-0.03, 0.03, 0.02), (-0.03, 0.03, 0.02)
sys.path.append(os.getcwd())

logging_config = '/home/finn/PycharmProjects/LayoutEagle/python/logging.yaml'
model_config = "elmo_lstm3_feedforward4_crf_straight.config"
jobs = 16
#"elmo_multi_head_self_attention_crf_straight_fitter.config"
parse_pdf2htmlEX = True
n_layout_training_documents = 500
max_windows_per_text = 100
recursive = True
max_len = 200
NORMAL_HEIGHT = 100
page_array_model = 100
layout_model_next_text_boxes = 5

doc_port        = 5180
app_port        = 5181
annotation_port = 5182
science_port    = 5183

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

science_map_corpus_path="../ScienceMap/manual_corpus/"
science_map_working_dir="../ScienceMap/"
science_map="../ScienceMap/GUI.py"
science_map_venv="../ScienceMap/venv/bin/activate"
science_map_csv="../ScienceMap/manual_corpus/relations.csv"

ampligraph_working_dir="../KnowledgeScience/"
ampligraph_venv="../KnowledgeScience/venv/bin/activate"
ampligraph="../KnowledgeScience/csv_ampligraph.py"
ampligraph_coords="CONSTRASTSUBJECT"


all_coordinates="../KnowledgeScience/knowledge_graph_coords/knowledge_graph_3d_choords.csv"
ke_path=  "../KnowledgeScience/knowledge_graph_coords/tsne_clusters_mean_points.csv"
ke_colors="../KnowledgeScience/knowledge_graph_coords/kn_clusters_mean_points.csv"
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

wordninjalanguagemodel = "nlp/english.txt.gz"
logging_level = logging.INFO


layout_model_path = hidden_folder + "/layout_model/"
saved_layout_model_dir = hidden_folder + "/layout_model_saved/"


collected_features_path = ".layouteagle/labeled_features.pickle"

use_pdf2htmlex_features = False

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
                'len', 'height', 'font-size', 'line-height', 'x', 'y', 'coarse_grained_pdf', 'fine_grained_pdf'
            ])
        ]