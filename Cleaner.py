import re
from nltk.corpus import stopwords


class Cleaner:

    def __init__(self):
        pass

    """
    Cleans file - Pre-processing
    """

    @staticmethod
    def clean_file(text):

        while re.search(r']]*', text):
            text = re.sub(r']]*', '', text, re.M)

        while re.search(r'==*', text):
            text = re.sub(r'==*', '', text, re.M)

        while re.search(r'~~*', text):
            text = re.sub(r'~~*', '', text, re.M)

        while re.search(r'%%*', text):
            text = re.sub(r'%%*', '', text, re.M)

        while re.search(r'--*', text):
            text = re.sub(r'--*', '', text, re.M)

        while re.search(r'\[\[*', text):
            text = re.sub(r'\[\[*', '', text, re.M)

        while re.search(r'(<>)(<>)*', text):
            text = re.sub(r'(<>)(<>)*', '', text, re.M)

        while re.search(r'\*\**', text):
            text = re.sub(r'\*\**', '', text, re.M)

        while re.search(r'\|\|*', text):
            text = re.sub(r'\|\|*', '', text, re.M)

        while re.search(r'##*', text):
            text = re.sub(r'##*', '', text, re.M)

        while re.search(r'__*', text):
            text = re.sub(r'__*', '', text, re.M)

        return text

    """
    Deletes all the tags from the text
    """

    @staticmethod
    def delete_tags(text):
        tags = [r'<[s|e]time>', r'</[s|e]time>', r'<speaker>', r'</speaker>', r'<paragraph>',
                r'</paragraph>', r'<sentence>', r'</sentence>', r'<location>', r'</location>']

        for t in tags:
            while re.search(t, text):
                text = re.sub(t, '', text, re.M)

        return text

    """
    From a list of words removes the English stopwords
    """

    @staticmethod
    def del_stopwords(words):
        without_stopwords = []
        stop_words = stopwords.words('english')

        for word in words:
            if word not in stop_words:
                without_stopwords.append(word)

        return without_stopwords
