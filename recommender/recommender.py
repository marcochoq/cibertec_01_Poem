import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob, Word

class PoemRecommender:

    def __init__(self, poems_dataset, vectorizer_path='pickles_files/vectorizer.pickle', matrix_path='pickles_files/poems_count_matrix.pickle'):
        self.poems_dataset = poems_dataset
        self.lemmatizer = WordNetLemmatizer()
        
        base_path = os.path.dirname(__file__)
        vectorizer_full_path = os.path.join(base_path, vectorizer_path)
        matrix_full_path = os.path.join(base_path, matrix_path)
        
        try:
            with open(vectorizer_full_path, 'rb') as file:
                self.count_vectorizer = pickle.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo de vectorizador en {vectorizer_full_path}. Por favor, asegúrese de que el archivo exista.")

        try:
            with open(matrix_full_path, 'rb') as file:
                self.poems_count_matrix = pickle.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo de matriz de conteo en {matrix_full_path}. Por favor, asegúrese de que el archivo exista.")

    def get_synonyms(self, word):
        blob_word = Word(word)
        synonyms = blob_word.synsets
        synonyms_list = []
        for syn in synonyms:
            for lemma in syn.lemmas():
                synonyms_list.append(lemma.name())
        return set(synonyms_list)

    def get_synonyms_tokenized(self, text):
        tokens = TextBlob(text).words    
        total_words = set()
        for word in tokens:
            synonyms = self.get_synonyms(word)
            if synonyms:
                total_words.update(synonyms)
            else:
                total_words.add(word)
        return ' '.join(total_words)

    def preprocess_text(self, text):
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        return ' '.join(lemmatized_tokens)

    def recommend_poems(self, theme, top_n=3):
        # Preprocess the theme and expand with synonyms
        expanded_theme = self.get_synonyms_tokenized(theme)
        processed_theme = self.preprocess_text(expanded_theme)
        
        # Transform the processed theme
        theme_count = self.count_vectorizer.transform([processed_theme])
        
        # Calculate cosine similarities between the theme and all poems
        cosine_similarities = cosine_similarity(theme_count, self.poems_count_matrix).flatten()
        
        # Get the indices of the top_n most similar poems
        top_poem_indices = cosine_similarities.argsort()[-top_n:][::-1]
        
        # Select the recommended poems using the obtained indices
        recommended_poems = self.poems_dataset.iloc[top_poem_indices]
        
        return recommended_poems