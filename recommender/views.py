from django.shortcuts import render, get_object_or_404 ,redirect,HttpResponse
from .models import Poem
from .recommender import PoemRecommender
from django.conf import settings
import os
import gdown
import pandas as pd

def index(request):
    recommendations = None
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
            
            # Generar un ID para cada poema si no tiene uno
            for i, rec in enumerate(recommendations):
                rec['id'] = i + 1
    
    return render(request, 'index.html', {'recommendations': recommendations})

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
    return render(request, 'saved_poems.html', {'poems': poems})

def delete_poem(request, poem_id):
    poem = get_object_or_404(Poem, id=poem_id)
    if request.method == 'POST':
        poem.delete()
        return redirect('saved_poems')
    return render(request, 'saved_poems.html', {'poems': Poem.objects.all()})