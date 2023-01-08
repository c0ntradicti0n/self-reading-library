# -*- coding: utf-8 -*-
import logging
import re

max_sentence_len = 120
alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"


def chunker(iter, size):
    chunks = []
    if size < 1:
        raise ValueError("Chunk size must be greater than 0.")
    for i in range(0, len(iter), size):
        chunks.append(iter[i : (i + size)])
    return chunks


def split_into_sentences(
    text,
):
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    if "..." in text:
        text = text.replace("...", "<prd><prd><prd>")
    if "Ph.D" in text:
        text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(
        alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]",
        "\\1<prd>\\2<prd>\\3<prd>",
        text,
    )
    text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
    if "”" in text:
        text = text.replace(".”", "”.")
    if '"' in text:
        text = text.replace('."', '".')
    if "!" in text:
        text = text.replace('!"', '"!')
    if "?" in text:
        text = text.replace('?"', '"?')
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    sentences = [s for s in sentences if s]

    # split too long sentences also at ","
    comma_texts = []
    for i, sentence in enumerate(sentences):
        if len(sentence) > max_sentence_len:
            res = []
            if len(res) < 2:
                res = sentence.split(";")
            if len(res) < 2:
                res = sentence.split(", and")
            if len(res) < 2:
                res = sentence.split(", ")
            if len(res) < 2:
                res = sentence.split(" and ")
            if len(res) < 2:
                res = chunker(sentence.split(" "), 30)
            if len(res) > 1:
                comma_texts.append((i, sentence.split(", ")))
            else:
                logging.warning(f"Couldn't split too long sentence! {sentence=}")

    for i, cts in reversed(comma_texts):
        sentences.pop(i)
        for ct in reversed(cts):
            sentences.insert(i, ct)

    sentences = [sentence.strip() for sentence in sentences]

    if len(sentences) == 0 and text.strip():
        sentences = [text.strip()]
    return sentences
