from Email import Email
from POSTagger import POSTagger
from Taggers import Taggers
from Evaluation import Evaluation
from OntologyConstructor import OntologyConstructor
from gensim.models import KeyedVectors
import spacy
import string
import pprint


class Application:

    def __init__(self):
        pass

    """
    Set-up Environment
    """
    def setup_environment(self):

        email = Email('object', 'object', 0)

        EMAILS_TRAINING_PATH = './Data/training/'
        EMAILS_TEST_UNTAGGED_PATH = './Data/seminars_testdata/test_untagged/'
        EMAILS_TEST_TAGGED_PATH = './Data/seminars_testdata/test_tagged/'
        POS_TAGGER_PATH = './Data/Models/pos_tagger_dt.pkl'

        emails_training = email.read_emails(EMAILS_TRAINING_PATH)
        emails_test_untagged = email.read_emails(EMAILS_TEST_UNTAGGED_PATH)
        emails_test_tagged = email.read_emails(EMAILS_TEST_TAGGED_PATH)

        pos_tagger = POSTagger()

        print("Application started.")

        # Ask user about POSTagger
        self.print_model_menu()

        user_input = raw_input()

        while True:
            if user_input.isdigit():
                if 3 >= int(user_input) >= 1:
                    if int(user_input) == 1:
                        pos_tagger.train_pos_tagger(POS_TAGGER_PATH)
                        break
                    elif int(user_input) == 2:
                        print("Loading POSTagger Model...")
                        pos_tagger.load_pos_tagger(POS_TAGGER_PATH)
                        print("POSTagger loaded.")
                        break
                    elif int(user_input) == 3:
                        print("Shutting down application...")
                        quit()
                else:
                    print("Invalid input")
                    self.print_model_menu()
                    user_input = raw_input()
            else:
                print("Invalid input")
                self.print_model_menu()
                user_input = raw_input()

        # Load Spacy model
        print("Loading Spacy Model...")
        spacy_model = spacy.load('en_core_web_sm')
        print("Spacy Model loaded.")

        # -----------------------------------------------------------------

        # Make sure to download Google News Data set and save to Models folder. Otherwise, can not classify emails
        print("Loading Google News Data-set...")
        # Will throw an exception if no Data Set found (of course)
        k_v_model = KeyedVectors.load_word2vec_format('./Data//Models/GoogleNews-vectors-negative300.bin', binary=True)
        print("Google News Data-set loaded.")

        # -----------------------------------------------------------------

        taggers = Taggers()

        self.start_up(emails_training, emails_test_untagged, emails_test_tagged,
                      pos_tagger, spacy_model, k_v_model, taggers)

    def start_up(self, emails_training, emails_test_untagged, emails_test_tagged,
                 pos_tagger, spacy_model, k_v_model, taggers):

        self.print_menu()

        user_input = raw_input()

        while True:
            if user_input.isdigit():
                if 3 >= int(user_input) >= 1:
                    if int(user_input) == 1:
                        # (add parameter 'spacy_model' before taggers when finished)
                        self.tag_seminars(emails_test_untagged, emails_test_tagged, spacy_model, taggers, pos_tagger)
                        self.print_menu()
                        user_input = raw_input()
                    elif int(user_input) == 2:
                        self.construct_ontology(emails_training, k_v_model)
                        self.print_menu()
                        user_input = raw_input()
                    elif int(user_input) == 3:
                        print("Shutting down application...")
                        quit()
                else:
                    print("Invalid input")
                    self.print_model_menu()
                    user_input = raw_input()
            else:
                print("Invalid input")
                self.print_model_menu()
                user_input = raw_input()

    @staticmethod
    def print_model_menu():
        print("\nPOSTagger:\nTrain on Treebank Data-set - 1\nLoad Pre-Trained Model - 2\nQuit Application - 3")

    @staticmethod
    def print_menu():
        print("\nMenu:\nTag Seminars - 1\nConstruct Ontology - 2\nQuit Application - 3")

    @staticmethod
    def tag_seminars(emails_test_untagged, emails_test_tagged, spacy_model, taggers, pos_tagger):
        # Main - Tag Untagged Emails
        print ("Tagging Seminars...")

        for i in range(0, len(emails_test_untagged)):
            emails_test_untagged[i] = \
                taggers.tag_paragraphs(  # 5 - Tag Paragraphs
                    taggers.tag_sentences(  # 4 - Tag Sentences
                        taggers.tag_locations(  # 3 - Tag Locations
                            taggers.tag_times(  # 2 - Tag Times
                                taggers.tag_speakers(emails_test_untagged[i], spacy_model)  # 1 - Tag Speakers
                            )
                        )
                    )
                )

        print ("Tagging Complete.")

        # Evaluate Tagging Algorithm
        print ("Evaluating Algorithm...")

        evaluation = Evaluation()

        tp, fp, fn = 0, 0, 0

        for tagged_email in emails_test_tagged:
            gr_email = tagged_email
            pred_email = None

            for untagged_email in emails_test_untagged:
                if untagged_email.file_id == tagged_email.file_id:
                    pred_email = untagged_email
                    break

            ntp, nfp, nfn = evaluation.evaluate_tags(gr_email, pred_email)

            tp += ntp
            fp += nfp
            fn += nfn

        print ("Evaluation complete.")

        print
        print("---------------------------------")

        print
        print("Calculating Accuracy...")

        print(tp, fp, fn)
        precision, recall, fscore = evaluation.calculate_accuracy(tp, fp, fn)

        print
        print("Accuracy:\n")

        # Print Accuracy Score
        print("Precision: {}".format(precision))
        print("Recall: {}".format(recall))
        print("F1-Score: {}".format(fscore))
        print("---------------------------------")

        print
        print("Seminar Tagging complete.")

    @staticmethod
    def construct_ontology(emails_training, k_v_model):

        print("Constructing Ontology...")

        ontology_constructor = OntologyConstructor()

        ontology_classification = ontology_constructor.classify_emails(emails_training, k_v_model)

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(ontology_classification)

        print
        print("Ontology Construction complete.")
