#TO DO:
#string handle the objects
from JSONParser import JSONInputParser
from SugiyamaFramework import SugiyamaFramework
import json

def loadJSON(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def main():    
  data = loadJSON('input2.json')
  parse = JSONInputParser(data)
  store = parse.validateJSON() # our object
  print(store)
  print(parse.inputValidate)
  new = SugiyamaFramework(store)
  while len(new.detectCycles()) > 0:
      new.detectCycles()
  print(new.feedbackSet)
  new.layerAssignment()

if __name__ == "__main__":
    main()