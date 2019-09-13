from nltk.tag.util import untag
from nltk.corpus import treebank
from sklearn_crfsuite import CRF
import pickle
import nltk

"""
Conditional Random Field POSTagger
"""


class POSTagger:

    def __init__(self):
        self.classifier = None

    def load_pos_tagger(self, path):
        try:
            model_pkl = open(path, 'rb')
            clf = pickle.load(model_pkl)
            self.classifier = clf
        except ValueError:
            print("Pre-Trained Model doesn't exist. Train first")

    def train_pos_tagger(self, path):
        # Just to make sure
        nltk.download('treebank')

        tagged_sentences = treebank.tagged_sents()

        train_size = int(.80 * len(tagged_sentences))
        training_sentences = tagged_sentences[:train_size]

        X_train, y_train = self.transform_to_dataset(training_sentences)

        model = CRF()

        print('Training started...')
        model.fit(X_train, y_train)
        print('Training finished.')

        # Save classifier to file
        model_pkl = open(path, 'wb')
        pickle.dump(model, model_pkl)
        model_pkl.close()

        print("POSTagger saved.")

        self.classifier = model

    """
      Features of a word used for classification
      with the Conditional Random Field.
      sentence: [word1, word2, ...], 
      index: the index of the word 
    """
    @staticmethod
    def features(sentence, index):
        """ sentence: [w1, w2, ...], index: the index of the word """
        return {
            'word': sentence[index],
            'is_first': index == 0,
            'is_last': index == len(sentence) - 1,
            'is_capitalized': sentence[index][0].upper() == sentence[index][0],
            'is_all_caps': sentence[index].upper() == sentence[index],
            'is_all_lower': sentence[index].lower() == sentence[index],
            'prefix-1': sentence[index][0],
            'prefix-2': sentence[index][:2],
            'prefix-3': sentence[index][:3],
            'suffix-1': sentence[index][-1],
            'suffix-2': sentence[index][-2:],
            'suffix-3': sentence[index][-3:],
            'prev_word': '' if index == 0 else sentence[index - 1],
            'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
            'has_hyphen': '-' in sentence[index],
            'is_numeric': sentence[index].isdigit(),
            'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
        }

    """
    Transforms the training tagged sentences to dataset format
    X: list of word features
    y: expected POS tag
    """
    def transform_to_dataset(self, tagged_sentences):
        X, y = [], []

        for tagged in tagged_sentences:
            X.append([self.features(untag(tagged), index) for index in range(len(tagged))])
            y.append([tag for _, tag in tagged])

        return X, y

    def pos_tag(self, sentence):
        sentence_features = [self.features(sentence, index) for index in range(len(sentence))]
        return list(zip(sentence, self.classifier.predict([sentence_features])[0]))
