import spacy
import en_core_web_sm
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

def create_word_dict(doc, word_freq, stopwords, punctuation):
    word_freq={}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_freq.keys():
                    word_freq[word.text] = 1
                else:
                    word_freq[word.text] += 1
    return word_freq

def normalize(word_freq, max_freq):
    for word in word_freq.keys():
        word_freq[word] = word_freq[word]/max_freq
    return word_freq

def calculate_sentence_scores(sentence_scores, sentence_tokens, word_freq):
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_freq.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_freq[word.text.lower()]
                else:
                    sentence_scores[sent] += word_freq[word.text.lower()]
    return sentence_scores


def summarize(text):
    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    tokens = [token.text for token in doc]
    #punctuation = punctuation + "\n"
    word_freq = {}
    word_freq = create_word_dict(doc, word_freq, stopwords, punctuation)
    max_freq = max(word_freq.values())
    word_freq = normalize(word_freq, max_freq)
    sentence_tokens = [sentence for sentence in doc.sents]
    sentence_scores = {}
    sentence_scores = calculate_sentence_scores(sentence_scores, sentence_tokens, word_freq)
    select_length = int(len(sentence_tokens)*0.3)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_sum = [word.text for word in summary]
    summary = ' '.join(final_sum)
    print(summary)
    return summary

summarize("Text summarization is a method in natural language processing (NLP) for generating a short and precise summary of a reference document. Producing a summary of a large document manually is a very difficult task. Summarization of a text using machine learning techniques is still an active research topic. Before proceeding to discuss text summarization and how we do it, here is a definition of summary.")
