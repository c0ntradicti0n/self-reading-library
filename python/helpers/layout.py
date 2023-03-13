label_strings = ["c1", "c2", "c3", "NONE"]


def determine_layout_label_from_text(text):
    return next(
        (label for label in label_strings[0:-1] if label in text.replace(" ", "")),
        label_strings[-1],
    )
