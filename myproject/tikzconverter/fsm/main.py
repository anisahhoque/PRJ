from .JSONParser import JSONInputParser
from .SugiyamaFramework import SugiyamaFramework
import json

def loadJSON(fileContent):
    return json.loads(fileContent)


def main(fileName, mode, hyperparameters):
    data = loadJSON(fileName)

    parse = JSONInputParser(data)
    
    store = parse.validateJSON()
    
    storeFramework = SugiyamaFramework(store)
    
    storeFramework.hyperparameters['repulsionwidth'] = hyperparameters['repulsionwidth']
    storeFramework.hyperparameters['width'] = hyperparameters['width']
    storeFramework.hyperparameters['height'] = hyperparameters['height']
    
    while len(storeFramework.detectCycles()) > 0:
        
        storeFramework.detectCycles()

    if mode == 'original':
        storelayers = storeFramework.layerAssignment4()
    elif mode == 'compact':
        storelayers = storeFramework.layerAssignment()
    else:
        raise ValueError(f"Invalid mode: {mode}")

    storeFramework.vertexArrangement(storelayers)
    tikzCode = storeFramework.generate_tikz_code()
    storeFramework.compile_tikz(tikzCode)
    return tikzCode