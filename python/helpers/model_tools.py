import os
import regex
model_regex = r"(?P<shape>\d+)_(?P<f1>0,?\d*)_(?P<epoch>\d+)"
import logging
from pprint import pprint

def find_best_model(model_dir):
    models = os.listdir(model_dir)
    try:
        best_model_path, scores = \
            max([(model_dir + "/" + p, next(m, regex.match(model_regex, "0_0,0_0")))
                  for p in models if (m := regex.finditer(model_regex, p))],
                key=lambda t: t[1] and float(t[1][0].replace(",", ".")))
    except ValueError:
        logging.warning(f"No models found in {model_dir}")
        return None, None

    print(scores, f" {best_model_path =}")
    return best_model_path, scores


def model_in_the_loop(model_dir, collection_path, on_train, on_predict, training_rate_mode = 'ls', training_rate_file=None):
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)
    if not os.path.isdir(collection_path):
        os.makedirs(collection_path)

    loops = []

    while True:
        samples_files = os.listdir(collection_path)

        if training_rate_mode == 'ls':
            n_samples = len(samples_files)

        if training_rate_mode == 'size':
            n_samples = os.path.getsize(training_rate_file)



        best_model_path, scores = find_best_model(model_dir)
        full_model_path = best_model_path

        if scores:
            training_rate = (int(scores.groups()[0]) / n_samples)
        else:
            training_rate = 0

        loops.append(training_rate)

        if loops.count(training_rate) > 2:
            logging.error("Going in circles!")


        print(f"{training_rate = }")
        if training_rate < 0.8:
            # let's train

            model_meta = on_train(
                {'samples_files': samples_files,
                'training_rate':samples_files})
            pprint(model_meta)
            model_path = model_meta[0][0]
        else:
            # let's make more samples

            try:
                on_predict(
                    {'best_model_path': best_model_path,
                     'training_rate': training_rate}
                )
            except KeyboardInterrupt as e:

                exit = input("Exit? [y]/n")

                if exit.startswith('n'):
                    continue
                else:
                    break