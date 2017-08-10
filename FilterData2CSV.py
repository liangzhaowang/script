import os
import sys
import re
import csv
import argparse
import numpy as np
from datetime import datetime, date, time, timedelta

def taketimes(func):
    def _wrap(*args, **kwords):
        t0 = datetime.now()
        result = func(*args, **kwords)
        t = datetime.now() - t0        
        print "It takes %s.%s seconds.\n" % (str((datetime.now() - t0).seconds), str((datetime.now() - t0).microseconds/1000))
        return result
    return _wrap

@taketimes
def DataProcess(dataFile, preSeconds, isShowDetail):
    print "start filter the data..."
    #filestore
    #events = ['TIME_TO_DECODE_OSD_OP','TIME_TO_ENQUEUE','TIME_TO_INQUEUE','TIME_TO_PG_PROCESS','TIME_TO_PROCESS','TIME_TO_LIFE_CYCLE','FILESTORE_JOURNAL_LATENCY', 'FILEJOURNAL_AIO']
    #bluestore
    events = ['TIME_TO_DECODE_OSD_OP','TIME_TO_ENQUEUE','TIME_TO_INQUEUE','TIME_TO_PG_PROCESS','TIME_TO_PROCESS','SUB_OP_LATENCY', 'TIME_TO_LIFE_CYCLE', 'prepare', 'aio_wait', 'io_done', 'kv_queued', 'kv_committing', 'kv_done', 'deferred_queued', 'deferred_aio_wait', 'deferred_cleanup', 'finishing', 'done', 'kv_sync_thread latency', 'KV_BDEV_FLUSH', 'AIO_THREAD_CALLBACK_LATENCY', 'DEVICE_FLUSH'] 
    #events = ['TIME_TO_DECODE_OSD_OP','TIME_TO_ENQUEUE','TIME_TO_INQUEUE','TIME_TO_PG_PROCESS','TIME_TO_PROCESS','SUB_OP_LATENCY', 'TIME_TO_LIFE_CYCLE', 'prepare', 'aio_wait', 'io_done', 'kv_queued', 'kv_committing', 'kv_done', 'finishing']
    #event_name, be-called level
    st_events = [
            ["TIME_TO_LIFE_CYCLE",0], 
            ["TIME_TO_PROCESS",1], 
            ["TIME_TO_DECODE_OSD_OP",2],
            ["TIME_TO_ENQUEUE",2],
            ["TIME_TO_INQUEUE",2],
            ["TIME_TO_PG_PROCESS",2], 
            #["dequeue_op FUNC-ELAPSED",0], 
            ["do_op FUNC-ELAPSED",3], 
            ["execute_ctx FUNC-ELAPSED",4], 
            ["find_object_context FUNC-ELAPSED",5],
            ["getattr FUNC-ELAPSED",6],
            ["issue_repop FUNC-ELAPSED",5], 
            #["FILESTORE_JOURNAL_LATENCY",2], 
            #["op_commit FUNC-ELAPSED",2], 
            #["repop_all_committed FUNC-ELAPSED",3], 
            #["send_message FUNC-ELAPSED",3], 
            #["op_applied FUNC-ELAPSED",0],
            ["prepare", 6],
            ["_txc_add_transaction FUNC-ELAPSED", 7],
            ["get_onode FUNC-ELAPSED", 8],
            ["_do_write FUNC-ELAPSED", 8],
            ["fault_range FUNC-ELAPSED", 9],
            ["_do_write_data FUNC-ELAPSED", 9],
            ["_do_write_small FUNC-ELAPSED", 9],
            ["_do_read FUNC-ELAPSED", 9],
            ["_do_write_big FUNC-ELAPSED", 9],
            ["_do_alloc_write FUNC-ELAPSED", 9],
            ["_omap_setkeys FUNC-ELAPSED", 8],
            ["_setattr FUNC-ELAPSED", 8],
            ["_setattrs FUNC-ELAPSED", 8],
            ["aio_wait", 6],
            ["io_done", 6],
            ["kv_queued", 6],
            ["kv_committing", 6],
            ["kv_done", 6],
            ["deferred_queued", 6],
            ["deferred_aio_wait", 6],
            ["deferred_cleanup", 6],
            ["finishing", 6],
            ["done", 6],
            ["kv_sync_thread latency", 6],
            ["KV_BDEV_FLUSH", 7],
            ["submit_transaction FUNC-ELAPSED", 7],
            ["submit_transaction_sync FUNC-ELAPSED", 7],
            ["_fsync FUNC-ELAPSED", 8],
            ["_flush_range FUNC-ELAPSED", 9],
            ["wait_for_aio FUNC-ELAPSED", 9],
            ["flush_bdev FUNC-ELAPSED", 9],
            ["_flush_and_sync_log FUNC-ELAPSED", 9],
            ["_deferred_try_submit FUNC-ELAPSED", 7],
            ["_deferred_finish FUNC-ELAPSED", 0],
            ["AIO_THREAD_CALLBACK_LATENCY", 6],
            ["SUB_OP_LATENCY", 2],
            ["write_message FUNC-ELAPSED",1]
            ]
    p = re.compile(r'^\[(.*)(\.\d+)\] .*vpid = (?P<vpid>.*?),.*procname = \"(?P<procname>.*?)\" },.*oid = \"(?P<oid>.*?)\".*event = \"(?P<event>.*?)\".*context = \"(?P<context>.*?)\".*elapsed = (?P<elapsed>.*?),.*')
    result = []
    raw_result = [[''],['timestamp', 'vpid', 'procname', 'oid', 'event', 'context', 'elapsed']]
    statistical = {}
    startPoint = ""
    startToWrite = False
    with dataFile:
        for line in dataFile:
            m = re.search(p, line)
            if m and m.group(1):
                tmpTS = datetime.combine(date.today(), datetime.strptime(m.group(1), '%H:%M:%S').time())
                if not startPoint:
                    startPoint = tmpTS
                if startPoint.hour > tmpTS.hour:
                    tmpTS += timedelta(days=1)
                if startToWrite or (tmpTS >= startPoint + timedelta(seconds=preSeconds) and m.group("oid") and m.group("oid").startswith("rbd_data")):
                    startToWrite = True
                if startToWrite and m.group("event") and ((m.group("event") in events) or re.search(r'.*FUNC-ELAPSED.*', m.group("event"))):
                    raw_result.append([m.group(1) + m.group(2), m.group("vpid"), m.group("procname"), m.group("oid"), m.group("event"), m.group("context"), m.group("elapsed")])
                    if m.group("event") in statistical.keys():
                        statistical[m.group("event")]["count"] += 1
                        statistical[m.group("event")]["elapseds"].append(int(float(m.group("elapsed"))))
                    else:
                        statistical[m.group("event")] = {"count" : 1, "elapseds" : [int(float(m.group("elapsed")))]}

        result.append(['Statistical Results:'])
        result.append(['event', 'count', 'avg(us)', 'max(us)', '<=2(us)','4(us)','10(us)','20(us)','50(us)','100(us)','250(us)','500(us)','750(us)','1000(us)', '2(ms)','4(ms)','10(ms)','20(ms)','50(ms)','100(ms)','250(ms)','500(ms)','750(ms)','1000(ms)','2000(ms)','>2000(ms)'])
        
        for key in st_events:
            if statistical.has_key(key[0]):
                na = np.array(statistical[key[0]]["elapseds"])
                condList = getCondList([2,4,10,20,50,100,250,500,750,1000,2000,4000,10000,20000,50000,100000,250000,500000,750000,1000000,2000000],na)
                list_group = [[np.append(np.extract(cond,na),0).max(),cond.sum()] for cond in  condList]
                tmp = ["*"*key[1] + key[0], str(statistical[key[0]]["count"]), "{:.2f}".format(np.average(na)), str(np.max(na))]
                tmp.extend(formatData(statistical[key[0]]["count"], list_group))
                result.append(tmp)
            else:
                tmp = ["*"*key[1] + key[0], "0", "0", "0"]
                tmp.extend(["(0, 0.00%)"]*21)
                result.append(tmp)
        if isShowDetail:
            result.extend(raw_result)
    return result


def getCondList(splitList,na):
    result = [(na<=splitList[0])]
    for i in range(1,len(splitList)):
        result.append(((splitList[i-1])<na)&(na<=splitList[i]))
    result.append((na>splitList[-1]))
    return result
    
def formatData(count, list):
    result = []
    for i in list:
        result.append("(%s, %s)" % (i[0], "{:.2f}%".format(i[1]*100.0/count)))
    return result
    
@taketimes        
def WriteToCsv(datalines, ofile):
    print "start write to csv..."
    csvfile = file(ofile, 'wb')
    writer = csv.writer(csvfile)
    for line in datalines:
        writer.writerow(line)
    csvfile.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="filename of trace", type=file)
    parser.add_argument("-s", metavar="warmup seconds", help="ignore the seconds from begin. default: 0", default = 0, type=int)
    parser.add_argument("-o", metavar="output_file", help="output filename. default: result.csv", default="result.csv", type=str)
    parser.add_argument("--sd", help="show detail infomation", action='store_true')

    args = parser.parse_args()
    WriteToCsv(DataProcess(args.filename, args.s, args.sd), args.o)
