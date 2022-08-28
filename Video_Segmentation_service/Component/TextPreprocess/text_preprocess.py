"""
# TOPICS DESCOVERY
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jun-30
"""

import os
from Const.const import (PREPROCESSED_FILE_PATH, TRANSCRIPT_PATH, NUMBER_OF_TOPICS, RANDOME_STATE, CHUNK_SIZE, PASSES, LDA_TOPIC_FILE_PATH, 
                        KEY_WORD_FILE_PATH, TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, TEXT_PREPROCESS_ERROR_LOG, MAIN_TOPIC_FOLDER_PATH)
from rake_nltk import Rake
from nltk import sent_tokenize
from nltk.corpus import stopwords
from gensim.utils import simple_preprocess
from gensim.models import Phrases, LdaMulticore
from gensim.models.phrases import Phraser
from spacy import load
from Config.Logger.Logger import Logger
from gensim.corpora import Dictionary
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from flask import jsonify

class Text_preprocess:
    def __init__(self, lec_id, lec_name): # file path required for aws
        try:
            self.lec_id = lec_id
            self.lec_name = lec_name
            self.key_words = []
            self.lda_topics = []
            self.debug = Logger()
            if os.path.exists(MAIN_TOPIC_FOLDER_PATH):
                self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG,"Audio_extraction|Started|File exsist " + MAIN_TOPIC_FOLDER_PATH + ".")
            else: # MAIN_TOPIC_FOLDER_PATH
                os.mkdir(MAIN_TOPIC_FOLDER_PATH)
                os.mkdir(KEY_WORD_FILE_PATH)
                os.mkdir(LDA_TOPIC_FILE_PATH)

            self.lda_model = None
            self.preprocessed_lda_topcs = []
            self.lemmatizer = WordNetLemmatizer()
            self.rake = Rake()
            self.nlp = load("en_core_web_lg", disable = ['parser', 'ner'])
            self.allowed_postags = ['NOUN', 'ADJ', 'VERB', 'ADV']
            with open(TRANSCRIPT_PATH , "r") as f:
                self.text = f.read()
        except Exception as e:
            self.debug.error_log(TEXT_PREPROCESS_ERROR_LOG, e, TEXT_PREPROCESS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    
    def keyword_extraction(self):
        try:
            self.debug = Logger()
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "keyword_extraction started.")
            keys = []
            self.rake.extract_keywords_from_text(self.text)
            for rating, keyword in set(self.rake.get_ranked_phrases_with_scores()):
                if rating > 5:
                    keys.append(keyword)
            joined_text = ",".join(keys)
            key_token = set(word_tokenize(joined_text))
            key_token.remove(",")
            joined_text = " ".join(key_token) # JOIN TEXT WITH SPACE TO USE IN SPACY FOR PREPROCESSING

            doc = self.nlp(joined_text)
            removal= ['ADV','PRON','CCONJ','PUNCT','PART','DET','ADP','SPACE', 'NUM', 'SYM']
            filter_lda_topics = [token.lemma_.lower() for token in doc if token.pos_ not in removal and not token.is_stop and token.lemma_.isalpha() == True]
            for word in filter_lda_topics:
                if len(word)>2:
                    self.key_words.append(word) # CHECK WORD LENGTH > 2
            key_word = list(set(self.key_words))

            filePathToKeyWord = os.path.join(KEY_WORD_FILE_PATH, self.lec_name + "_" + self.lec_id + "_keywordList" +".txt") # SAVNING PATH FOR EXTRACTED TOPICS LIST FILE
            file1 = open(filePathToKeyWord, "w")
            file1.write(str(key_word))
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "Saved extracted key file in path: " + filePathToKeyWord + ".")
            return filePathToKeyWord # SAVED FILE PATH

        except Exception as e:
            self.debug.error_log(TEXT_PREPROCESS_ERROR_LOG, e, TEXT_PREPROCESS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def train_lda_model(self):
        try:
            self.debug = Logger()
            corpus, id2word = self.text_normalization() # PREPROCESS TEXT
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "text_normalization complete for LDA model.")
            lda_model = LdaMulticore(corpus = corpus,
                                        id2word = id2word,
                                        num_topics = NUMBER_OF_TOPICS, 
                                        random_state = RANDOME_STATE,
                                        chunksize = CHUNK_SIZE,
                                        passes = PASSES,
                                        per_word_topics = False) # BUILD LDA MODEL
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "LDA model training finished.")

            for topic_list in lda_model.print_topics():
                for topic_word in topic_list:
                    self.lda_topics.append(str(topic_word) + "\n")
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "LDA topics extraction complete.")

        except Exception as e:
            self.debug.error_log(TEXT_PREPROCESS_ERROR_LOG, e, TEXT_PREPROCESS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def lda_topic_preprocess(self):
        try:
            self.debug = Logger()
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "LDA topic preprocess started...")
            joined_text = " ".join(self.lda_topics)
            lda_topics_list = [joined_text]
            lines = lda_topics_list[0].split("\n")
            names = []
            for line in lines:
                split_by_star = line.split("*")
                for line_1 in split_by_star:
                    split_by_plus = line_1.split("+")
                    for line_2 in split_by_plus:
                        if  line_2.strip().isnumeric() == False and isinstance(line_2.strip(), float) == False and len(line_2)>2:
                            name = line_2.strip().replace('"', "")
                            name = name.replace("'", "")
                            names.append(name.rstrip())
            test_list = list(set([self.lemmatizer.lemmatize(i) for i in names if i]))
            joined_text = " ".join(test_list)
            joined_text = joined_text.split("_")
            joined_text = " ".join(joined_text)
            joined_text = joined_text.split()
            joined_text.remove('example') if 'example' in joined_text else None # IF EXAMPLE EXSIT IN LIST REMOVE IT FROM LIST
            joined_text.remove('eg') if 'eg' in joined_text else None # IF EG EXSIT IN LIST REMOVE IT FROM LIST
            joined_text.remove('ex') if 'ex' in joined_text else None # IF EX EXSIT IN LIST REMOVE IT FROM LIST
            topic_list = " ".join(joined_text)

            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "Sending preprocessed text to spacy.")
            doc = self.nlp(topic_list)
            removal= ['ADV','PRON','CCONJ','PUNCT','PART','DET','ADP','SPACE', 'NUM', 'SYM']
            self.preprocessed_lda_topcs = [token.lemma_.lower() for token in doc if token.pos_ not in removal and not token.is_stop and token.lemma_.isalpha() == True] # CLEANING NON ALPHABATICAL TEXTS AND PREPROCESS TEXT
            lda_topics = list(set(self.preprocessed_lda_topcs)) # REMOVING DUPLICATES

            filePathToKeyWord = os.path.join(LDA_TOPIC_FILE_PATH, self.lec_name + "_LDA_keywordList" + ".txt") # PATH TO SAVE THE EXTRACTED LDA TOPIC LIST
            file1 = open(filePathToKeyWord, "w")
            file1.write(str(lda_topics))
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "Saved extracted lda topics to file: " + filePathToKeyWord + ".")
            return filePathToKeyWord

        except Exception as e:
            self.debug.error_log(TEXT_PREPROCESS_ERROR_LOG, e, TEXT_PREPROCESS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def text_normalization(self):
        try:
            self.debug = Logger()
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "text_normalization preprocess started...")
            sentences = sent_tokenize(self.text)
            data_words = list(self.sent_to_words(sentences))
            bigram = Phrases(data_words, min_count = 5, threshold = 100) # BUILD THE BIGRAM. HIGHER THRESHOLD FEWER PHRASES.
            trigram = Phrases(bigram[data_words], threshold = 100) # TRIGAM MODELS
            bigram_mod = Phraser(bigram) # SENTENCE CLUBBED(FASTER METHOD)
            trigram_mod = Phraser(trigram) # SENTENCE CLUBBED(FASTER METHOD)

            stop_words = stopwords.words('english')
            stop_words.extend(['Welcome', 'week', '\n\n', 'Okay', 'use', 'get', 'got', 'take', 'taken', 'took', 'taking', 'put', 'putting',
                            'use', 'person'])
            data_words_nostops = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in data_words] # REMOVE STOP WORDS
            data_words_bigrams = [trigram_mod[bigram_mod[doc]] for doc in data_words_nostops] # FORM BIGRAM

            data_lemmatized = [] 
            for sent in data_words_bigrams: # LEMMATIZATION 
                doc = self.nlp(" ".join(sent)) 
                data_lemmatized.append([token.lemma_ for token in doc if token.pos_ in self.allowed_postags])
            
            id2word = Dictionary(data_lemmatized) # CREATE DICTIONARY
            texts = data_lemmatized # CREATE CORPUS
            corpus = [id2word.doc2bow(text) for text in texts] # TERM DOCUMENT FREQUENCY
            self.debug.debug(TEXT_PREPROCESS, TEXT_PREPROCESS_LOG, "Generating corpus and id2word complete.")
            return corpus, id2word

        except Exception as e:
            self.debug.error_log(TEXT_PREPROCESS_ERROR_LOG, e, TEXT_PREPROCESS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def sent_to_words(self, sentences):
        for sentence in sentences:
            yield(simple_preprocess(str(sentence), deacc=True))  # deacc=True REMOVES PUNCTUATIONS