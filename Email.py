from nltk.corpus.reader import WordListCorpusReader
from os.path import isfile, join
from os import listdir
from Cleaner import Cleaner


class Email(object):

    def __init__(self, header, body, file_id):
        self.header = header
        self.body = body
        self.file_id = file_id

    """
    Read all text files,
    Cleans all text files,
    Divides each Email into a header and a body,
    Appends to a list of Email objects,
    
    Returns the list of Email objects
    """

    def read_emails(self, path):
        # Get all files
        files = [f for f in listdir(path) if isfile(join(path, f))]

        try:
            del(files[files.index('DS_Store')])
        except:
            pass

        reader = WordListCorpusReader(path, files)

        cleaner = Cleaner()

        emails = list()

        # Creates the Email Object out of each email file and appends to list
        for file_id in reader.fileids():
            with open(path + file_id, 'r') as current_file:
                cleaned_contents = cleaner.clean_file(current_file.read())
                split_email_header, split_email_body, split_email_file_id = self.divide(cleaned_contents, file_id)
                emails.append(Email(split_email_header, split_email_body, split_email_file_id))

        # Return list of Email objects
        return emails

    """
    Splits Email into header and body
    
    Returns the Email header and body
    """

    @staticmethod
    def divide(contents, file_id):

        header_start = 0
        header_end = contents.find('Abstract')

        body_start = header_end
        body_end = len(contents) - 1

        email_header = contents[header_start:header_end]
        email_body = contents[body_start:body_end]
        email_file_id = file_id

        return email_header, email_body, email_file_id
