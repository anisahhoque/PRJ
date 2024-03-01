#TO DO:
#string handle the objects
from JSONParser import JSONInputParser
from SugiyamaFramework import SugiyamaFramework
import json

def loadJSON(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def main():    
  data = loadJSON('input.json')
  parse = JSONInputParser(data)
  store = parse.validateJSON() # our object
  print(store)
  print(parse.inputValidate)
  new = SugiyamaFramework(store)
  cycles = new.detectCycles()
  print(cycles)
  x = new.returnTransitionsOfCycles(cycles)
  y = new.removeCycles(x)
  for i in y:
      print(i.fromState)
      print(i.toState)
      
if __name__ == "__main__":
    main()