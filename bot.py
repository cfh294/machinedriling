#!/usr/bin/env python3
"""
bot.py

Shitposting bot that attempts to create a tweet in the style of a "weird" Twitter account.
"""
import argparse
import pandas
import tensorflow
import numpy as np
import os
import re
import spacy
import collections
import pathlib
from six.moves import cPickle
from utils import clean_account_name, with_engine, with_sql, with_connection
from keras.models import Sequential, Model, load_model
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM, Input, Bidirectional
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from keras.metrics import categorical_accuracy

# suppress minor warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
_root = pathlib.PurePath(__file__).parent
_data_dir = _root / "data"
_nlp = spacy.load("en")


def with_cmd_line_args(f):
    """
    Decorator that handles command line arguments for this script.
    :param f: the function to be decorated
    :return:  the decorated function
    """
    def with_cmd_line_args_(*args, **kwargs):
        ap = argparse.ArgumentParser()
        ap.add_argument("-a", "--account", type=clean_account_name, required=True,
                        help="The account you want to emulate.", default="all")
        ap.add_argument("-c", "--count", type=int, default=1, help="Number of fake tweets to generate (default is 1).")
        ap.add_argument("-e", "--epochs", type=int, default=1, help="The model's total number of epochs.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_cmd_line_args_


def create_wordlist(doc):
    wl = []
    for word in doc:
        if word.text not in ("\n","\n\n",'\u2009','\xa0'):
            wl.append(word.text.lower())
    return wl


def generate_vocab(account, word_list):

    vocab_file_path = str(_data_dir / "vocab" / f"{account}.vocab")
    if not os.path.exists(vocab_file_path):
        word_counts = collections.Counter(word_list)

        # Mapping from index to word : that's the vocabulary
        # vocabulary_inv = list(sorted(word_counts.most_common(), key=lambda w: w[1]))
        vocabulary_inv = [x[0] for x in word_counts.most_common()]
        vocabulary_inv = list(sorted(vocabulary_inv))

        # Mapping from word to index
        vocab = {x: i for i, x in enumerate(vocabulary_inv)}
        words = [x[0] for x in word_counts.most_common()]

        with open(vocab_file_path, "wb") as out_file:
            cPickle.dump((words, vocab, vocabulary_inv), out_file)
    else:
        with open(vocab_file_path, "rb") as in_file:
            words, vocab, vocabulary_inv = cPickle.load(in_file)
    return words, vocab, vocabulary_inv


@with_engine
@with_sql("get_tweets.dml.sql")
def generate_wordlist(sql, engine, account):
    # We check for the existence of the wordlist here
    file_path = str(_data_dir / "words" / f"{account}.words")
    if not os.path.exists(file_path):
        wordlist = []
        for i, row in pandas.read_sql_query(sql, engine, params=dict(in_user=account)).iterrows():
            wordlist.extend(create_wordlist(_nlp(row["tweet_text"])))
        with open(file_path, "wb") as out_file:
            cPickle.dump(wordlist, out_file)
    else:
        with open(file_path, "rb") as in_file:
            wordlist = cPickle.load(in_file)
    return wordlist 

def generate_sequences(seq_length, word_list):
    sequences = []
    next_words = []
    for i in range(0, len(word_list) - seq_length, 1):
        sequences.append(word_list[i: i + seq_length])
        next_words.append(word_list[i + seq_length])
    return sequences, next_words


def generate_matrix(sequence_list, seq_length, vocab, next_words):
    vocab_size = len(vocab)
    sequence_collection_count = len(sequence_list)
    X = np.zeros((sequence_collection_count, seq_length, vocab_size), dtype=np.bool)
    y = np.zeros((sequence_collection_count, vocab_size), dtype=np.bool)
    for i, sentence in enumerate(sequence_list):
        for t, word in enumerate(sentence):
            X[i, t, vocab[word]] = 1
        y[i, vocab[next_words[i]]] = 1
    return X, y


def bidirectional_lstm_model(seq_length, vocab_size):
    rnn_size = 256 # size of RNN
    learning_rate = 0.001 #learning rate
    model = Sequential()
    model.add(Bidirectional(LSTM(rnn_size, activation="relu"),input_shape=(seq_length, vocab_size)))
    model.add(Dropout(0.6))
    model.add(Dense(vocab_size))
    model.add(Activation('softmax'))
    
    optimizer = Adam(lr=learning_rate)
    callbacks=[EarlyStopping(patience=2, monitor='val_loss')]
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=[categorical_accuracy])
    return model


@with_connection(auto_commit=True)
@with_cmd_line_args
def main(cmd_line, cnxn):
    seq_length = 30

    word_list = generate_wordlist(cmd_line.account)
    words, vocab, vocab_inventory = generate_vocab(cmd_line.account, word_list)

    sequences, next_words = generate_sequences(seq_length, word_list)
    X, y = generate_matrix(sequences, seq_length, vocab, next_words)

    model_dir = _data_dir / "models" / cmd_line.account
    if not os.path.isdir(str(model_dir)):
        os.mkdir(str(model_dir))


    model_path = str(model_dir / f"{cmd_line.account}.model")
    if not os.path.exists(model_path):

        model = bidirectional_lstm_model(seq_length, len(vocab))    
        batch_size = 32 # minibatch size

        callbacks=[EarlyStopping(patience=4, monitor='val_loss'),
                ModelCheckpoint(filepath=os.path.join(str(model_dir / cmd_line.account), ".{epoch:02d}-{val_loss:.2f}.hdf5"),\
                                monitor='val_loss', verbose=0, mode='auto', period=2)]
        #fit the model
        history = model.fit(X, y,
                        batch_size=batch_size,
                        shuffle=True,
                        epochs=cmd_line.epochs,
                        callbacks=callbacks,
                        validation_split=0.1)

        #save the model
        model.save(str(model_dir / f"{cmd_line.account}.model"))
        with open(str(model_dir / f"{cmd_line.account}.model"), "rb") as byte_file:
            data = byte_file.read()
            cur = cnxn.cursor()
            cur.execute("insert into wtm.model values (%s, %s)", [cmd_line.account, data])
            cur.close()
            del cur

    model = load_model(model_path)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()