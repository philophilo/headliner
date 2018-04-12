from nltk.stem.porter import PorterStemmer
from nltk.tokenize import sent_tokenize, TreebankWordTokenizer
from nltk.corpus import stopwords
import itertools
import string

_stop_words = stopwords.words('english')


class Term(object):
    def __init__(self, fullWord):
        self.fullWord = fullWord
        # TODO: Lemmantization
        self.stem = PorterStemmer().stem(fullWord).lower()

    def __eq__(self, other):
        return self.stem == other.stem

    def __hash__(self):
        return hash(self.stem)

    def __repr__(self):
        return "Term {}({})".format(
            self.stem.encode('utf8'), self.fullWord.encode('utf8'))

    def __str__(self):
        return repr(self)

    def is_punctuation(self):
        return self.stem in string.punctuation

    def is_stop_word(self):
        return self.fullWord in _stop_words


def stemAndTokenizeText(text):
    sents = sent_tokenize(text)
    tokens = list(itertools.chain(
        *[TreebankWordTokenizer().tokenize(sent) for sent in sents]))
    terms = [Term(token) for token in tokens]
    return filter(lambda term: not term.is_punctuation(), terms)


def toQueryTerms(queryRaw):
    return stemAndTokenizeText(queryRaw)


def toDocTerms(docRaw):
    return stemAndTokenizeText(docRaw)
