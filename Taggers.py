import re
from Email import Email
from nltk.tokenize import sent_tokenize


class Taggers:

    def __init__(self):
        pass

    """
    Tags Speaker Using Spacy NER Model
    """

    @staticmethod
    def tag_speakers(email, model):

        email_header = email.header
        email_body = email.body

        tagged_speaker_with_regex_and_spacy = False

        # Find Speaker lines in Header and Body
        regex_string = r'\s*[wW][hH][oO].*\n'
        body_speaker_regex = r'\s*Speaker.*\n'

        header_speaker_line_exists = list()
        body_speaker_line_exists = list()

        try:
            # Could throw an exception if none found
            header_speaker_line_exists = re.findall(regex_string, email_header)
            body_speaker_line_exists = re.findall(regex_string, email_body)
            body_speaker_line_2_exists = re.findall(body_speaker_regex, email_body)
        except IndexError:
            pass

        # Tag Speaker in Header with 'Who:' (if exists)
        if header_speaker_line_exists:
            header_doc = model(unicode(header_speaker_line_exists[0]))
            for ent in header_doc.ents:
                if ent.label_ == unicode('PERSON'):
                    speaker_name = ent.text.lstrip()
                    email_header = email_header.replace(speaker_name, "<speaker>" + speaker_name + "</speaker>")

            tagged_speaker_with_regex_and_spacy = True    # Successfully tagged Header

        # Tag Speaker in Body with 'Who:' (if exists)
        if body_speaker_line_exists:
            body_doc = model(unicode(body_speaker_line_exists[0]))
            for ent in body_doc.ents:
                if ent.label_ == unicode('PERSON') or ent.label == unicode('LAW'):
                    speaker_name = ent.text.lstrip()
                    email_body = email_body.replace(speaker_name, "<speaker>" + speaker_name + "</speaker>")

            tagged_speaker_with_regex_and_spacy = True   # Successfully tagged Body

        # Tag Speaker in Body with 'Speaker:' (if exists)
        if body_speaker_line_2_exists:
            body_doc = model(unicode(body_speaker_line_2_exists[0]))
            for ent in body_doc.ents:
                if ent.label_ == unicode('PERSON'):
                    speaker_name = ent.text.lstrip()
                    email_body = email_body.replace(speaker_name, "<speaker>" + speaker_name + "</speaker>")

            tagged_speaker_with_regex_and_spacy = True

        # Tag Speaker in Body normally (Last-Resort if unable to tag previous 3 ways)
        if not tagged_speaker_with_regex_and_spacy:
            body_doc = model(unicode(email_body))
            speaker = unicode("")
            for ent in body_doc.ents:
                # Get first PERSON tag and set it as the Speaker
                # Sometimes Speakers are identified as Named LAWs (for a reason I don't know)
                if ent.label_ == unicode('PERSON'):
                    speaker_name = ent.text.lstrip()
                    speaker = speaker_name
                    break

            email_body = email_body.replace(speaker, "<speaker>" + speaker + "</speaker>")

        tagged_email = Email(email_header, email_body, email.file_id)

        return tagged_email

    """
    Tags Locations via Regex
    """

    @staticmethod
    def tag_locations(email):
        email_header = email.header
        email_body = email.body

        location_line_regex_expression = r'Place.*\n'
        location_regex_expression = r':.*'

        location_line = list()

        try:
            # Could throw an exception if none found
            location_line = re.findall(location_line_regex_expression, email_header)[0]
        except IndexError:
            pass

        # Check if location line exists
        if location_line:
            # remove semicolon from beginning [1:]
            location = re.findall(location_regex_expression, location_line)[0][1:].strip()
            n_location = '<location>' + location + '</location>'
            # Spacing needed for clarity
            np_location = 'Place:    <location>' + location + '</location>\n'

            email_header = re.sub(location_line_regex_expression, np_location, email_header)
            email_body = re.sub(location, n_location, email_body)

        tagged_email = Email(email_header, email_body, email.file_id)

        return tagged_email

    """
    Tags Times via Regex
    """

    @staticmethod
    def tag_times(email):

        email_header = email.header
        email_body = email.body

        time_line_regex_expression = r'Time.*\n'
        time_regex_expression = r'\[0-9]+:[0-9][0-9]|[0-9]+:[0-9][0-9] +[APap]\.?[mM]'

        # time_regex_expression = r''    # <- Possible Improvement?

        # Tag Times in Header ------------------------

        times_tag = list()
        times = list()

        try:
            # Could throw an exception if none found
            time_line = re.findall(time_line_regex_expression, email_header)[0]
            times = re.findall(time_regex_expression, time_line)

            if len(times) == 1:
                times_tag.append('<stime>' + times[0] + '</stime>')
            elif len(times) == 2:
                times_tag.append('<stime>' + times[0] + '</stime>')
                times_tag.append('<etime>' + times[1] + '</etime>')

            for i in range(0, len(times)):
                time_line = re.sub(times[i], times_tag[i], time_line)

            email_header = re.sub(time_line_regex_expression, time_line, email_header)
        except IndexError:
            pass

        # Tag Times in Body ------------------------

        if len(times) > 0:
            # Strip times from header to contain only digits
            for i in range(0, len(times)):
                times[i] = re.findall(r'[0-9]+:[0-9][0-9]', times[i])[0]

            # Get all times from body
                body_times = re.findall(time_regex_expression, email_body)
                body_times_tags = list(body_times)

            # Tag the times from body based on header time tags
            for i in range(0, len(body_times)):
                if times[0] in body_times[i]:
                    body_times_tags[i] = '<stime>' + body_times[i] + '</stime>'

            if len(times) > 1:
                for i in range(0, len(body_times)):
                    if times[1] in body_times[i]:
                        body_times_tags[i] = '<etime>' + body_times[i] + '</etime>'

            # Put tagged times in body
            for i in range(0, len(body_times)):
                email_body = re.sub(body_times[i], body_times_tags[i], email_body)

        tagged_email = Email(email_header, email_body, email.file_id)

        return tagged_email

    """
    Tags Paragraphs - Checking where there is more than one '\n' char
    """

    @staticmethod
    def tag_paragraphs(email):
        # Escape 'Abstract: '
        email_body = email.body[9:].strip()

        split_paragraphs = [b for b in email_body.split("\n\n") if b != '']

        email_body = email.body

        for paragraph in split_paragraphs:
            if not paragraph.startswith(' '):
                email_body = email_body.replace(paragraph, '<paragraph>' + paragraph + '</paragraph>')

        tagged_email = Email(email.header, email_body, email.file_id)

        return tagged_email

    """
    Tags Sentences via Tokenizing
    """

    @staticmethod
    def tag_sentences(email):
        # Escape 'Abstract: '
        email_body = email.body[9:]

        body_sentences = [re.sub(r'\n', '', b) for b in sent_tokenize(email_body)]

        email_body = email.body

        for sentence in body_sentences:
            if not sentence.startswith(' ') and sentence[0].isalnum() and sentence.endswith('.'):
                email_body = email_body.replace(sentence, '<sentence>' + sentence + '</sentence>')

        tagged_email = Email(email.header, email_body, email.file_id)

        return tagged_email
