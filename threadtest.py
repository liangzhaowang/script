#coding=utf-8
import threading
import time

class scanner(threading.Thread):
    tlist=[] #用来存储队列的线程
    maxthreads=5 # int(sys.argv[2])最大的并发数量，此处我设置为100，测试下系统最大支持1000多个
    evnt=threading.Event()#用事件来让超过最大线程设置的并发程序等待
    lck=threading.Lock() #线程锁
    def __init__(self, method, *args):
        self._method = method
        self._args = args
        threading.Thread.__init__(self)
    def run(self):
        try:
            self._method(*self._args) 
            pass
        except Exception,e:
            print e.message
        #以下用来将完成的线程移除线程队列
        scanner.lck.acquire()
        scanner.tlist.remove(self)
        print "rm a t"

        #如果移除此完成的队列线程数刚好达到99，则说明有线程在等待执行，那么我们释放event，让等待事件执行
        if len(scanner.tlist)==scanner.maxthreads-1:
            scanner.evnt.set()
            print "to add a t"
            scanner.evnt.clear()
            print "not add a t"
        scanner.lck.release()
    @staticmethod
    def newthread(method, *args):
        scanner.lck.acquire()#上锁
        sc=scanner(method, *args)
        scanner.tlist.append(sc)
        print "add a t"
        scanner.lck.release()#解锁
        sc.start()

def func(index):
    time.sleep(2)
    print index
def runscan():
    for i in range(10):
        scanner.lck.acquire()
        #如果目前线程队列超过了设定的上线则等待。
        if len(scanner.tlist)>=scanner.maxthreads:
            scanner.lck.release()
            scanner.evnt.wait()#scanner.evnt.set()遇到set事件则等待结束
        else:
            scanner.lck.release()
        scanner.newthread(func, i)
        
    for t in scanner.tlist:
        t.join()#join的操作使得后面的程序等待线程的执行完成才继续

if __name__=="__main__":
    runscan()