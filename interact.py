"""Interact with a model"""

__author__ = "Guillaume Genthial"

from pathlib import Path
import functools
import json

import tensorflow as tf

from main import model_fn

LINE = 'The programme was declared open by Major General Azugaku Tsota Umuru, Director of Administration, Defence Headquarters, on behalf of the Chief of Defence Staff, Air Marshall Oluseyin Petinrin.'
DATADIR = 'CONLL2003'
PARAMS = './results/params.json'
MODELDIR = './results/model'


def pretty_print(line, preds):
    words = line.strip().split()
    lengths = [max(len(w), len(p)) for w, p in zip(words, preds)]
    padded_words = [w + (l - len(w)) * ' ' for w, l in zip(words, lengths)]
    padded_preds = [p.decode() + (l - len(p)) * ' ' for p, l in zip(preds, lengths)]
    print('words: {}'.format(' '.join(padded_words)))
    print('preds: {}'.format(' '.join(padded_preds)))


def predict_input_fn(line):
    # Words
    words = [w.encode() for w in line.strip().split()]
    nwords = len(words)

    # Chars
    chars = [[c.encode() for c in w] for w in line.strip().split()]
    lengths = [len(c) for c in chars]
    max_len = max(lengths)
    chars = [c + [b'<pad>'] * (max_len - l) for c, l in zip(chars, lengths)]

    # Wrapping in Tensors
    words = tf.constant([words], dtype=tf.string)
    nwords = tf.constant([nwords], dtype=tf.int32)
    chars = tf.constant([chars], dtype=tf.string)
    nchars = tf.constant([lengths], dtype=tf.int32)

    return ((words, nwords), (chars, nchars)), None


if __name__ == '__main__':
    with Path(PARAMS).open() as f:
        params = json.load(f)

    params['words'] = str(Path(DATADIR, 'vocab.words.txt'))
    params['chars'] = str(Path(DATADIR, 'vocab.chars.txt'))
    params['tags'] = str(Path(DATADIR, 'vocab.tags.txt'))
    params['glove'] = str(Path(DATADIR, 'glove.npz'))

    estimator = tf.estimator.Estimator(model_fn, MODELDIR, params=params)
    predict_inpf = functools.partial(predict_input_fn, LINE)
    for pred in estimator.predict(predict_inpf):
        pretty_print(LINE, pred['tags'])
        break
