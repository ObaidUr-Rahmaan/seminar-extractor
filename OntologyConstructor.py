from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
import numpy as np

import math
from textblob import TextBlob as tb
import re
from Cleaner import Cleaner
from nltk.corpus import stopwords


class OntologyConstructor:

    def __init__(self):
        pass

    @staticmethod
    def tf(word, blob):
        return float(blob.words.count(word)) / float(len(blob.words))

    @staticmethod
    def n_containing(word, bloblist):
        return float((sum(1 for blob in bloblist if word in blob)))

    def idf(self, word, bloblist):
        return float(math.log(len(bloblist) / float((1 + self.n_containing(word, bloblist)))))

    def tfidf(self, word, blob, bloblist):
        return float(float(self.tf(word, blob)) * self.idf(word, bloblist))

    @staticmethod
    def delete_stopwords(words):
        without_stopwords = []
        stop_words = stopwords.words('english')

        for word in words:
            if word not in stop_words:
                without_stopwords.append(word)

        return without_stopwords

    def get_important_words(self, emails, path=None):

        cleaner = Cleaner()

        complete_email_text = ''

        for email in emails:
            email_header = cleaner.delete_tags(email.header)
            email_body = cleaner.delete_tags(email.body)

            topic_line = re.findall(r'Topic.*\n', email_header)[0]
            topic_line = topic_line[6:].strip()

            complete_email_text = complete_email_text + topic_line + '\n' + email_body + '\n'

        # Cleaning the text
        complete_email_text = re.sub('\n', ' ', complete_email_text)
        complete_email_text = re.sub('\s', ' ', complete_email_text)
        complete_email_text = re.sub(' +', ' ', complete_email_text)

        complete_email_text = tb(complete_email_text)
        bloblist = [complete_email_text]

        words = []

        # Test
        # print(bloblist)

        for i, blob in enumerate(bloblist):
            scores = {word: self.tfidf(word, blob, bloblist) for word in blob.words}
            sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for word, score in sorted_words:
                words.append(word)

            # Delete Stop-Words
            words = self.delete_stopwords(words)

            if path is not None:
                with open(path, 'w') as current_file:
                    for word in words:
                        current_file.write('{}\n'.format(word))

        return words

    @staticmethod
    def minor_process_and_clean_of_text(text):
        text = re.sub('\n', ' ', text)
        text = re.sub('\s', ' ', text)
        text = text.lower()

        return text

    def get_words_from_email(self, email, my_words):
        words = []

        for w in my_words:
            if w in email.body:
                words.append(w)

        important_words = self.get_important_words([email])
        important_words = important_words[(len(important_words) - 10):]
        words.extend(important_words)

        return words

    """
    Classifies Emails into Topics
    """

    def classify_emails(self, emails_training, k_v_model):
        ontology = {
            'science': {
                'chemistry': [],
                'engineering': {
                    'computer': {
                        'vision': [],
                        'robotics': [],
                        'software': [],
                    },
                    'electronics': []
                },
                'physics': [],
                'mathematics': [],
                'biology': {
                    'environment': [],
                    'medicine': [],
                    'bio-chemistry': []
                },
                'neurology': [],
                'psychology': []
            }
        }

        FILE_PATH = './Data/Ontology/freq_words.txt'

        # Get important words and save them to file
        self.get_important_words(emails_training, FILE_PATH)

        words_file = open(FILE_PATH, 'r')
        my_words = words_file.readlines()
        my_words = [x.strip() for x in my_words]
        words_file.close()

        # Test
        # for word in my_words:
        #     print word

        print("This part of the system is incomplete...")

        # Classify emails
        for e in emails_training:
            pass

        return ontology
