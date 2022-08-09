from layout.imports import *
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec
from core import config
import pandas
from helpers import pandas_tools
from layout import model_helpers
from helpers import os_tools


@converter("annotation.collection", "model")
class Training(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, num_labels=config.NUM_LABELS, **kwargs)

    def __call__(self, x_meta, *args, **kwargs):
        if 'collection_step' not in self.flags:
            raise Exception("Declare collection step, that expresses for which set of features we trained this model")
        else:
            self.collection_step = self.flags['collection_step']

        df_paths_meta = list(x_meta)
        feature_dfs = [path_meta[0] for path_meta in df_paths_meta]
        model_path = f"{config.TEXT_BOX_MODEL_PATH}/{self.collection_step}"

        if os.path.exists(model_path):
            os_tools.rm_r(model_path)

        os.makedirs(model_path)

        feature_df = pandas.concat(
            [
                df for p in feature_dfs
                if (df := pandas_tools.load_pandas_file(
                        config.COLLECTION_PATH + p
                    )) is not None
            ]
        )

        print("LABEL", feature_df["LABEL"].tolist())

        feature_df = feature_df[feature_df.image_path.map(lambda path: not os.path.exists(path[0]))]

        dataset = Dataset.from_pandas(feature_df)

        dataset = dataset.train_test_split(shuffle=False)

        print(dataset)

        f1_to_new_model_paths = {}

        with open(model_path + "/.log", 'w') as log:
            fun = model_helpers.preprocess_data(training=True)
            train_dataset = dataset['train'].map(
                fun,
                batched=True,
                remove_columns=dataset['train'].column_names,
                features=config.FEATURES,
            )
            test_dataset = dataset['test'].map(
                fun,
                batched=True,
                remove_columns=dataset['test'].column_names,
                features=config.FEATURES,
            )

            model_helpers.PROCESSOR.tokenizer.decode(train_dataset['input_ids'][0])

            train_dataset.set_format(type="torch", device=config.DEVICE)
            test_dataset.set_format(type="torch", device=config.DEVICE)

            train_dataloader = DataLoader(train_dataset, batch_size=2, shuffle=True)
            test_dataloader = DataLoader(test_dataset, batch_size=1)

            for x in range(0, 10):
                example = dataset['train'][x:x + 1]
                image = Image.open(example['image_path'][0][0])
                image = image.convert("RGB")
                width, height = image.size
                draw = ImageDraw.Draw(image)
                for word, box, label in zip(example['text'][0], model_helpers.compute_bbox(example)[0],
                                            example['LABEL'][0]):
                    actual_label = label
                    box = model_helpers.unnormalize_box(box, width, height)
                    draw.rectangle(box, outline=config.label2color[actual_label], width=2)
                    draw.text((box[0] + 10, box[1] - 10), actual_label, fill=config.label2color[actual_label],
                              font=font)

            batch = next(iter(train_dataloader))

            model = model_helpers.MODEL

            model.to(config.DEVICE)
            optimizer = AdamW(model.parameters(), lr=1e-5, weight_decay=0.1)

            global_step = 0
            num_train_epochs = config.EPOCHS_LAYOUT
            t_total = len(train_dataloader) * num_train_epochs  # total number of training steps

            # put the model in training mode
            model.train()
            for epoch in range(num_train_epochs):
                print("Epoch:", epoch)
                with tqdm(train_dataloader, total=train_dataloader.dataset.num_rows) as tdqm_train_dataloader:
                    for batch in tdqm_train_dataloader:
                        tdqm_train_dataloader.set_description(f"Epoch {epoch}")
                        # zero the parameter gradients
                        optimizer.zero_grad()

                        # forward + backward + optimize
                        outputs = model(**batch)
                        loss = outputs.loss
                        # print loss every 100 steps
                        if global_step % 30 == 0:
                            print(f" .")
                            tdqm_train_dataloader.set_postfix(loss=loss.item())

                        loss.backward()
                        optimizer.step()
                        global_step += 1

                metric = load_metric("seqeval")

                # put model in evaluation mode
                model.eval()
                for batch in tqdm(test_dataloader, desc="Evaluating"):
                    with torch.no_grad():
                        input_ids = batch['input_ids'].to(config.DEVICE)
                        bbox = batch['bbox'].to(config.DEVICE)
                        image = batch['image'].to(config.DEVICE)
                        attention_mask = batch['attention_mask'].to(config.DEVICE)
                        token_type_ids = batch['token_type_ids'].to(config.DEVICE)
                        labels = batch['labels'].to(config.DEVICE)

                        # forward pass
                        outputs = model(input_ids=input_ids, bbox=bbox, image=image, attention_mask=attention_mask,
                                        token_type_ids=token_type_ids, labels=labels)

                        # predictions
                        predictions = outputs.logits.argmax(dim=2)

                        # Remove ignored index (special tokens)
                        true_predictions = [
                            [config.id2label[p.item()] for (p, l) in zip(prediction, label) if l != -100]
                            for prediction, label in zip(predictions, labels)
                        ]
                        true_labels = [
                            [config.id2label[l.item()] for (p, l) in zip(prediction, label) if l != -100]
                            for prediction, label in zip(predictions, labels)
                        ]

                        metric.add_batch(predictions=true_predictions, references=true_labels)

                final_score = metric.compute()
                pprint(final_score)
                log.write(f"""EPOCH {epoch}
                {pformat(final_score, indent=10)}
                """)

                f1 = final_score['overall_f1']
                n_samples = len(feature_df)
                print(f"{dataset.shape = }")
                path = f"{config.TEXT_BOX_MODEL_PATH}_{str(n_samples)}_{str(f1).replace('.', ',')}_{epoch}"
                f1_to_new_model_paths[f1] = path

                torch.save(model.state_dict(),
                           path)

        best_model_path = max(f1_to_new_model_paths.items(), key=lambda x: x[0])[1]
        yield best_model_path, df_paths_meta
