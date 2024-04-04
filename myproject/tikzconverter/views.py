from django.shortcuts import render
from .fsm.main import main
from django.http import JsonResponse
import os

from django.conf import settings



def index(request):
    hyperparameters = {'repulsionwidth': 2, 'width': 4, 'height': 10} 
    if request.method == 'POST':
        mode = request.POST.get('mode')
        uploaded_file = request.FILES.get('json_file')
        repulsionwidth = int(request.POST.get('repulsionwidth', hyperparameters['repulsionwidth']))
        width = int(request.POST.get('width', hyperparameters['width']))
        height = int(request.POST.get('height', hyperparameters['height']))
        hyperparameters['repulsionwidth'] = repulsionwidth
        hyperparameters['width'] = width
        hyperparameters['height'] = height
        if uploaded_file:

                file_content = uploaded_file.read().decode('utf-8')
                try:
                    tikz_code = main(file_content, mode=mode, hyperparameters=hyperparameters)
                    return JsonResponse({'tikzCode': tikz_code})
                except ValueError as e:
                    return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'index.html', {'hyperparameters': hyperparameters})