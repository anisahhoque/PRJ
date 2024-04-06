from django.shortcuts import render
from .fsm.main import main
from django.http import JsonResponse
import os

from django.conf import settings



def index(request):
    hyperparameters = {'bend':15, 'width': 4, 'height': 5, 'orientation' : 'horizontal'} 
    if request.method == 'POST':
        
        uploaded_file = request.FILES.get('json_file')
        bend= int(request.POST.get('bend', hyperparameters['bend']))
        width = int(request.POST.get('width', hyperparameters['width']))
        height = int(request.POST.get('height', hyperparameters['height']))
        orientation = str(request.POST.get('orientation', hyperparameters['orientation']))
       

        hyperparameters['orientation'] = orientation
        hyperparameters['width'] = width
        hyperparameters['height'] = height
        hyperparameters['bend'] = bend
     
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