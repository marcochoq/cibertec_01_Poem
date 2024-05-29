from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Poem
from .recommender import PoemRecommender
from django.conf import settings
import os
import gdown
import pandas as pd
from textblob import TextBlob

def index(request):
    recommendations = None
    theme = None
    if request.method == 'POST':
        theme = request.POST.get('theme')
        if theme:
            data_path = os.path.join(settings.BASE_DIR, 'recommender', 'data', 'dataPoemasTokenized.csv')

            if not os.path.exists(data_path):
                file_id = '1Jbf5WIkgtAxl65fnCxDIz2uNgyv6NLZP'
                url = f'https://drive.google.com/uc?export=download&id={file_id}'
                gdown.download(url, data_path, quiet=False)

            data = pd.read_csv(data_path)
            recommender = PoemRecommender(data)
            recommendations = recommender.recommend_poems(theme).to_dict(orient='records')
            
            # Añadir análisis de sentimientos
            for poem in recommendations:
                analysis = TextBlob(poem['Poem'])
                poem['sentiment'] = analysis.sentiment.polarity

    return render(request, 'index.html', {'recommendations': recommendations, 'theme': theme})

def poem_detail(request, poem_id):
    poem = get_object_or_404(Poem, pk=poem_id)
    return render(request, 'poem_detail.html', {'poem': poem})

def user_profile(request):
    return render(request, 'user_profile.html')

def save_poem(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        poet = request.POST.get('poet')
        content = request.POST.get('content')
        tags = request.POST.get('tags')
        
        Poem.objects.create(title=title, poet=poet, content=content, tags=tags)
        
        return HttpResponse(status=204)

def saved_poems(request):
    poems = Poem.objects.all()
    
    for poem in poems:
        analysis = TextBlob(poem.content)
        poem.sentiment = analysis.sentiment.polarity
        
       
        if poem.sentiment < -0.5:
            poem.color_class = 'bg-red-700'  # Rojo oscuro
        elif -0.5 <= poem.sentiment < 0:
            poem.color_class = 'bg-red-400'  # Rojo claro
        elif 0 <= poem.sentiment < 0.5:
            poem.color_class = 'bg-yellow-400'  # Amarillo
        elif 0.5 <= poem.sentiment < 1:
            poem.color_class = 'bg-green-400'  # Verde claro
        else:
            poem.color_class = 'bg-green-700'  # Verde oscuro

        poem.sentiment_percentage = abs(poem.sentiment) * 100

    return render(request, 'saved_poems.html', {'poems': poems})


def determine_color_class(sentiment):
    if sentiment > 0:
        return 'bg-green-500'  
    elif sentiment < 0:
        return 'bg-red-500'   
    else:
        return 'bg-yellow-500'  


def delete_poem(request, poem_id):
    poem = get_object_or_404(Poem, id=poem_id)
    if request.method == 'POST':
        poem.delete()
        return redirect('saved_poems')
    return render(request, 'saved_poems.html', {'poems': Poem.objects.all()})
