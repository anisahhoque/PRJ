#TO DO:
#string handle the objects
from JSONParser import JSONInputParser
from SugiyamaFramework import SugiyamaFramework
data = {
  "states": [
    {
      "id": "#0",
      "name": "State A"
    },
    {
      "id": "#1",
      "name": "State B"
    },
    {
      "id": "#2",
      "name": "State C"
    },
    {
      "id": "#3",
      "name": "State D"
    },
    {
      "id": "#4",
      "name": "State E"
    }
  ],
  "transitions": [
    {
      "from": "#0",
      "to": "#1",
      "label": "Transition 1"
    },
    {
      "from": "#1",
      "to": "#2",
      "label": "Transition 2"
    },
    {
      "from": "#2",
      "to": "#0",
      "label": "Transition 3"
    },
    {
      "from": "#2",
      "to": "#3",
      "label": "Transition 4"
    },
    {
      "from": "#3",
      "to": "#4",
      "label": "Transition 5"
    },
    {
      "from": "#4",
      "to": "#0",
      "label": "Transition 6"
    }
  ],
  "initialState": "#0",
  "acceptingStates": ["#2", "#4"]
}


parse = JSONInputParser(data)
store = parse.validateJSON() # our object
print(store)
print(parse.inputValidate)
new = SugiyamaFramework(store)
new.removeCycles()
#print(parse.getTransitions())