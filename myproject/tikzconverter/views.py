from django.shortcuts import render
from .fsm.main import main

import os



def index1(request):
    if request.method == 'POST' and request.FILES['json_file']:
        uploaded_file = request.FILES['json_file']
        file_content = uploaded_file.read().decode('utf-8')
        tikz = main(file_content)
        return render(request, 'index.html', {'tikzCode': tikz})
    return render(request, 'index.html')

def index2(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        uploaded_file = request.FILES.get('json_file')
        if uploaded_file:
            file_content = uploaded_file.read().decode('utf-8')
            tikz_code = main(file_content, mode=mode)
            return render(request, 'index.html', {'tikzCode': tikz_code})

    return render(request, 'index.html')

from django.http import JsonResponse



def index(request):
    hyperparameters = {'repulsionwidth': 2, 'width': 4, 'height': 10}  # Default values

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
            tikz_code = main(file_content, mode=mode, hyperparameters=hyperparameters)
            return JsonResponse({'tikzCode': tikz_code})

    return render(request, 'index.html', {'hyperparameters': hyperparameters})