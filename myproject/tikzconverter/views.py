from django.shortcuts import render
from .fsm.main import main

import os



def index(request):
    if request.method == 'POST' and request.FILES['json_file']:
        uploaded_file = request.FILES['json_file']
        # Read the file content
        file_content = uploaded_file.read().decode('utf-8')
        # Pass the file content to your main function
        tikz = main(file_content)
        return render(request, 'index.html', {'tikzCode': tikz})
    return render(request, 'index.html')
