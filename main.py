
from JSONParser import JSONInputParser
from SugiyamaFramework import SugiyamaFramework
import json

def loadJSON(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def main():    
  data = loadJSON('rhrh1.json')
  parse = JSONInputParser(data)
  store = parse.validateJSON() # our object

  new = SugiyamaFramework(store)
  while len(new.detectCycles()) > 0:
      new.detectCycles()

  storelayers = new.layerAssignment()
  new.vertexArrangement(storelayers)
  
  print(new.generate_tikz_code())


if __name__ == "__main__":
    main()