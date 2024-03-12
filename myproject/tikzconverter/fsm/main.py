from .JSONParser import JSONInputParser
from .SugiyamaFramework import SugiyamaFramework
import json

def loadJSON(fileContent):
    return json.loads(fileContent)

def main(fileName):    
  data = loadJSON(fileName)
  parse = JSONInputParser(data)
  store = parse.validateJSON() # our object

  storeFramework = SugiyamaFramework(store)
  while len(storeFramework.detectCycles()) > 0:
      storeFramework.detectCycles()

  storelayers = storeFramework.layerAssignment()
  storeFramework.vertexArrangement(storelayers)
  tikzCode = storeFramework.generate_tikz_code()
  #storeFramework.compile(tikzCode)
  #print(tikzCode)
  return(tikzCode)
