#!/usr/bin/env python3
"""
tweet_generator.py

Create a tweet in the style of a "weird" Twitter account.
"""
import argparse
import pandas
import numpy as np
import os
import re
import spacy
import collections
import pathlib
from io import BytesIO
from datetime import datetime
from six.moves import cPickle
from sqlalchemy import func
from utils import clean_account_name, with_engine, with_sql, with_connection, with_session, ModelData, Tweet, AttrDict, CreatedTweet, session_maker
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
        ap.add_argument("-c", "--count", required=True, type=int, default=1, help="Number of fake tweets to generate (default is 1).")
        ap.add_argument("-e", "--epochs", type=int, default=1, help="The model's total number of epochs.")
        ap.add_argument("-u", "--update-model", action="store_true", default=False, help="Force an update on a model, if it already exists.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_cmd_line_args_


def create_wordlist(doc):
    wl = []
    for word in doc:
        if word.text not in ("\n","\n\n",'\u2009','\xa0'):
            wl.append(word.text.lower())
    return wl


def get_model_data(session, account):
    result = session.query(ModelData).filter_by(tweet_user=account).first()
    if not result:
        result = ModelData(tweet_user=account)
        session.add(result)
    return result


def generate_vocab(session, model_data, account, word_list):

    if not model_data.vocab:
        word_counts = collections.Counter(word_list)

        # Mapping from index to word : that's the vocabulary
        vocabulary_inv = [x[0] for x in word_counts.most_common()]
        vocabulary_inv = list(sorted(vocabulary_inv))

        # Mapping from word to index
        vocab = {x: i for i, x in enumerate(vocabulary_inv)}
        words = [x[0] for x in word_counts.most_common()]

        model_data.words = cPickle.dumps(words)
        model_data.vocab = cPickle.dumps(vocab)
        model_data.vocab_inv = cPickle.dumps(vocabulary_inv)
        session.commit()
    else:
        words = cPickle.loads(model_data.words)
        vocab = cPickle.loads(model_data.vocab)
        vocabulary_inv = cPickle.loads(model_data.vocab_inv)
    return words, vocab, vocabulary_inv


def get_tweets(session, tweet_user=None):
    query = session.query(Tweet)
    if tweet_user:
        query = query.filter_by(tweet_user=tweet_user)
    return query.all()


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def generate_sentence(model, seq_length, vocab, vocab_inv, words):
    words_number = 30 # number of words to generate
    #seed_sentences = "nolan avance sur le chemin de pierre et grimpe les marches ." #seed sentence to start the generating.
    seed_sentences = ""
    vocab_size = len(words)

    #initiate sentences
    generated = ''
    sentence = []

    #we shate the seed accordingly to the neural netwrok needs:
    for i in range (seq_length):
        sentence.append("a")

    seed = seed_sentences.split()

    for i in range(len(seed)):
        sentence[seq_length-i-1]=seed[len(seed)-i-1]

    generated += ' '.join(sentence)

    #the, we generate the text
    for i in range(words_number):
        #create the vector
        x = np.zeros((1, seq_length, vocab_size))
        for t, word in enumerate(sentence):
            x[0, t, vocab[word]] = 1.

        #calculate next word
        preds = model.predict(x, verbose=0)[0]
        next_index = sample(preds, 0.33)
        next_word = vocab_inv[next_index]

        #add the next word to the text
        generated += " " + next_word
        # shift the sentence by one, and and the next word at its end
        sentence = sentence[1:] + [next_word]
    return " ".join(sentence)

def generate_wordlist(session, model_data, account):
    if model_data.words:
        wordlist = cPickle.loads(model_data.words)
    else:
        wordlist = []
        for tweet in get_tweets(session, account):
            wordlist.extend(create_wordlist(_nlp(tweet.tweet_text)))
        model_data.words = cPickle.dumps(wordlist)
        session.commit()
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


def generate_model(session, model_data, account, epochs, seq_length, update_model=False):
    
    
    word_list = generate_wordlist(session, model_data, account)
    session.commit()
    word_list = generate_wordlist(session, model_data, account)
    words, vocab, vocab_inventory = generate_vocab(session, model_data, account, word_list)
    sequences, next_words = generate_sequences(seq_length, word_list)
    X, y = generate_matrix(sequences, seq_length, vocab, next_words)
    

    if not model_data.model or update_model:
        model = bidirectional_lstm_model(seq_length, len(vocab))    
        batch_size = 32 # minibatch size
        model_bytes = BytesIO()
        model_bytes.name = "model_bytes"
        checkpoint = ModelCheckpoint(model_bytes.name, monitor='val_loss', verbose=0, mode='auto', period=2)
        callbacks = [EarlyStopping(patience=4, monitor="val_loss"), checkpoint]    

        #fit the model
        model.fit(X, y, batch_size=batch_size, shuffle=True, epochs=epochs, callbacks=callbacks,
                        validation_split=0.1)

        #save the model
        model_data.model = cPickle.dumps(model)
        model_bytes.close()
        session.commit()
    else:
        model = cPickle.loads(model_data.model)
    return model, words, vocab, vocab_inventory


@with_cmd_line_args
@with_session()
def main(session, cmd_line):
    seq_length = 30
    # check if user has tweets in system
    valid = session.query(Tweet).filter_by(tweet_user=cmd_line.account).count() > 0
    if valid:
        model_data = get_model_data(session, cmd_line.account)
        model, words, vocab, vocab_inv = generate_model(session, model_data, cmd_line.account, cmd_line.epochs, seq_length, cmd_line.update_model)
        for i in range(cmd_line.count):
            sentence = generate_sentence(model, seq_length, vocab, vocab_inv, words)
            session.add(
                CreatedTweet(tweet_user=cmd_line.account, tweet_text=sentence, create_date=datetime.now())
            )
            session.commit()
            print(sentence)
    else:
        print(f"Specified account ({cmd_line.account}) has 0 tweets in the database.")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()