import json
import argparse

def convert(dataPath, outputPath):
    with open(dataPath) as dataFile:
        #print dataFile.read()[:-2]
        jsonObj = json.loads("[" + dataFile.read()[:-2] + "]")
        prettyStr = json.dumps(jsonObj, indent=4)
        #print prettyStr
    outputFile = open(outputPath, "w")
    outputFile.write(prettyStr)
    outputFile.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="json data path")
    parser.add_argument("--output", help="json data path")
    args = parser.parse_args()
    convert(args.input, args.output)
