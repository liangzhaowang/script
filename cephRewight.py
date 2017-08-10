import sys
import subprocess
import time

target = 0.05
max_time_re = 300
max_count_re = 1000
t_start = time.time()
t_end = 0
count_re = 0
result = []
minDiff = 1

def Reweight(oload, max_change, max_change_osds):
    subprocess.Popen("ceph osd reweight-by-pg %s %s %s" % (oload, max_change, max_change_osds), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def GetPgs():
    p = subprocess.Popen("ceph osd df | awk '{print $9}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    tmpList =  [x.replace('\n','') for x in p.stdout.readlines() if x != '\n']
    if 'PGS' in tmpList:
        wightList = [int(x) for x in tmpList[tmpList.index('PGS')+1 : ]]
        return wightList
    else:
        print tmpList
        return []

def GetValueDiff(pgs):
    global minDiff
    if pgs:
        diff = round((max(pgs)-min(pgs))*1.0/max(pgs),3)
    else:
        diff = -1
    result.append([count_re, diff])
    print count_re, diff, pgs
    minDiff = diff if diff > 0 and minDiff > diff else  minDiff
    return diff

if __name__ == "__main__":
    while True:
        diff = GetValueDiff(GetPgs())
        t_end = time.time()
        count_re += 1
        if diff < target or max_count_re < count_re or max_time_re < t_end - t_start:
            break
        else:
            Reweight(sys.argv[1], sys.argv[2], sys.argv[3])
    while True:
        diff2 = GetValueDiff(GetPgs())
        count_re += 1
        if diff2 <= minDiff or 2*max_count_re < count_re:
            print "The min Diff is %s" % str(diff2)
            break
        else:
            Reweight(sys.argv[1], sys.argv[2], sys.argv[3])
    #print result
