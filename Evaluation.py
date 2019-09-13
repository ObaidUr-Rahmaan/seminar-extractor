from Cleaner import Cleaner
import re


class Evaluation:

    def __init__(self):
        pass

    @staticmethod
    def evaluate_tags(gr_email, pred_email):

        cleaner = Cleaner()

        regex = {
            'time': r'<[s|e]time>.*?</[s|e]time>',
            'speaker': r'<speaker>.*?</speaker>',
            'location': r'<location>.*?</location>',
            'sentence': r'<sentence>.*?</sentence>',
            'paragraph': r'<paragraph>.*?</paragraph>'
        }

        # gr_email tags -----------------
        gr_email_header = gr_email.header
        gr_email_body = gr_email.body
        gr_email = gr_email_header + gr_email_body

        gr_email_tags = {}
        # Clean from 'newlines'
        gr_email = gr_email.replace('\n', '')

        for k in regex.keys():
            gr_email_tags[k] = re.findall(regex[k], gr_email, re.MULTILINE)
            for i in range(0, len(gr_email_tags[k])):
                gr_email_tags[k][i] = cleaner.clean_file(gr_email_tags[k][i])

        # pred_email tags -------------------
        pred_email_header = pred_email.header
        pred_email_body = pred_email.body
        pred_email = pred_email_header + pred_email_body

        pred_email_tags = {}
        # Clean from 'newlines'
        pred_email = pred_email.replace('\n', '')

        for k in regex.keys():
            pred_email_tags[k] = re.findall(regex[k], pred_email, re.M)
            for i in range(0, len(pred_email_tags[k])):
                pred_email_tags[k][i] = cleaner.clean_file(pred_email_tags[k][i])

        tp = 0
        fp = 0
        fn = 0

        # change gr_tags.keys() to ['key'] to evaluate a specific tag
        for k in gr_email_tags.keys():
            gr = gr_email_tags[k]
            pred = pred_email_tags[k]

            # removing all punctuations and spaces from both email tag lists
            for i in range(0, len(gr)):
                gr[i] = re.sub(r'[^\w\s]', '', gr[i])
                gr[i] = re.sub(' ', '', gr[i])

            for i in range(0, len(pred)):
                pred[i] = re.sub(r'[^\w\s]', '', pred[i])
                pred[i] = re.sub(' ', '', pred[i])

            # Calculating TP, FP, FN
            for t in gr:
                # print(t)
                if t in pred:
                    # print("Got here")
                    tp = tp + 1
                    pred.remove(t)
                else:
                    # print("Got here")
                    fn = fn + 1

            fp = fp + len(pred)

        return tp, fp, fn

    @staticmethod
    def calculate_accuracy(tp, fp, fn):

        tp = float(tp)
        fp = float(fp)
        fn = float(fn)

        try:
            precision = tp / (tp + fp)
            # print(precision)
            recall = tp / (tp + fn)
            # print(recall)
            fscore = (2 * precision * recall) / (precision + recall)
            # print(fscore)
            return precision, recall, fscore
        except ZeroDivisionError:
            print("Error: Unable to calculate True accuracy")
