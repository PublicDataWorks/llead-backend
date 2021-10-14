import itertools

import spacy
import textdistance

from utils.constants import OFFICER_MATCH_THRESHOLD


class NLP:
    def __init__(self):
        self.spacy_parser = spacy.load('en_core_web_sm')

    def extract_lines(self, text):
        sententces = self.spacy_parser(text).sents
        lst = []
        for sent in sententces:
            lst.append(sent.text)
        return lst

    def find_best_match(self, name, officers):
        similarity_calc = [
            (officer_name, textdistance.jaro_winkler.similarity(name, officer_name))
            for officer_name in officers.keys()
        ]
        best_match, score = max(similarity_calc, key=lambda x: x[1])

        return {
            'officer_ids': officers.get(best_match),
            'score': score,
        }

    def process(self, text, officers):
        text_parsed = self.spacy_parser(text)
        parsed_names = set(ee.text for ee in text_parsed.ents if ee.label_ == 'PERSON')

        matches = [self.find_best_match(name, officers) for name in parsed_names]

        best_matches = [match for match in matches if match['score'] > OFFICER_MATCH_THRESHOLD]

        officers_ids = set(itertools.chain(*[element['officer_ids'] for element in best_matches]))

        return officers_ids
