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

    def preprocess_text(self, text):
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        return ' '.join(lemmatized_tokens)

    def recommend_poems(self, theme, top_n=3):
        # Preprocesar el tema
        processed_theme = self.preprocess_text(theme)
        
        # Transformar el tema procesado
        theme_count = self.count_vectorizer.transform([processed_theme])
        
        # Calcular las similitudes de coseno entre el tema y todos los poemas
        cosine_similarities = cosine_similarity(theme_count, self.poems_count_matrix).flatten()
        
        # Obtener los índices de los top_n poemas más similares
        top_poem_indices = cosine_similarities.argsort()[-top_n:][::-1]
        
        # Seleccionar los poemas recomendados usando los índices obtenidos
        recommended_poems = self.poems_dataset.iloc[top_poem_indices]
        
        return recommended_poems
