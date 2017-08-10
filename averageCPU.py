import os
import math
import json
import argparse

def AvgLat(path):
    dataPath = os.path.join(path, "result.json")
    if os.path.exists(dataPath):
        #resp = os.popen("cat " + dataPath + " |grep 99.99th%|awk '{print $2}' ").readlines()
        #lats = [float(x.replace(",\n", "")) for x in resp]
        with open(dataPath) as dataFile:
            dataObj = json.load(dataFile)
            allIdles = []
            serverList = dataObj["ceph"]["cpu"].keys()
            serverList.sort()
            for server in serverList:
                if len(server.split("_")) > 2 and server.split("_")[2] != "all":
                    continue
                idleList = dataObj["ceph"]["cpu"][server][u"%idle"]
                allIdles.extend(idleList)
                print server + " : " + "{:.3f}".format(sum(idleList)/len(idleList)) 
            print "All : " + "{:.3f}".format(sum(allIdles)/len(allIdles))
        #print "{:.3f}".format(sum(idleList)/len(idleList))
        #print "{:.3f}".format(sum(lats)/len(lats))
    else:
        print "file %s not exists!" % (dataPath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="data path")
    args = parser.parse_args()
    AvgLat(args.path)
