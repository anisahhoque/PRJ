#JSON To TikZ Converter
This  provides a web-based tool that allows you to upload JSON files of finite state machines and convert them into TikZ code.

## Features
Upload JSON files
Edit features such as diagram size and orientation
Download TikZ code as a TeX file
Download PDF of the graph
Download a sample JSON input

## Set Up
Requires an installation of Python 3.x

cd path/to/myproject
pip install -r requirements.txt
python manage.py runserver

## Expected JSON input format

{
  "states": [
    {
      "id": "1"
    },
    {
      "id": "2"
    } 
  ],
  "transitions": [
    {
      "from": "#1",
      "to": "#2",
      "label": "A"
    }
  ],
  "initialState": "#1",
  "acceptingStates": ["#2"]
}