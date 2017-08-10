import os,sys,subprocess
lib_path = os.path.abspath(os.path.join('../conf/'))
sys.path.append(lib_path)
from conf import *
import time

outStr = common.bash("ceph status")
outList = outStr.split('\n')
if "mgr no daemons active" in outList:
    common.bash("ceph auth get-or-create mgr.admin mon 'allow *' && ceph-mgr -i admin")