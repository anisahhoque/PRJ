from django.shortcuts import render
from .fsm.main import main
from django.http import JsonResponse
import os

from django.conf import settings



def index(request):
    hyperparameters = {'bend':15, 'width': 4, 'height': 5} 
    if request.method == 'POST':
        mode = request.POST.get('mode')
        uploaded_file = request.FILES.get('json_file')
        bend= int(request.POST.get('width', hyperparameters['bend']))
        width = int(request.POST.get('width', hyperparameters['width']))
        height = int(request.POST.get('height', hyperparameters['height']))
        
        hyperparameters['width'] = width
        hyperparameters['height'] = height
        if uploaded_file:
            if uploaded_file.name.endswith('.json'):
                file_content = uploaded_file.read().decode('utf-8')
                try:
                    tikz_code = main(file_content, hyperparameters=hyperparameters)
                    return JsonResponse({'tikzCode': tikz_code})
                except ValueError as e:
                    return JsonResponse({'error': str(e)}, status=400)
            else:
                return JsonResponse({'error': 'Invalid file type. Please upload a JSON file.'}, status=400)
    return render(request, 'index.html', {'hyperparameters': hyperparameters})