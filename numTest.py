#!/usr/bin/python
# -*- coding: utf-8 -*-   
'''
Created on 2015年7月22日

@author: LiBiao
'''
import datetime,time
import threading
import subprocess
import os, base64
import sys
import Queue

queue = Queue.Queue()


#需要手动配置的参数

#启动序号
SLEEP_TIME = 0

#直播地址
FULL_ADDR = {}

#需要手动配置的参数
RTMP_ADDR = 'rtmp://192.168.1.208:1935/live/'
HTTP_ADDR = 'http://192.168.1.208:80/live'
liveID = '100002750'   #来自于万视无忧中创建的直播
urlKey = 'a1e5c680f7bfc85851de8ab2e63b0a33'   #来自于万视无忧安全设置模块
liveResCode = '71ac6c06d3'    #直播源码


#生成MD5值
def getMD5_Value(inputdata):
    try:
        import hashlib
        hash = hashlib.md5(inputdata.encode('utf-8'))
    except ImportError:
        #for python << 2.5
        import md5
        hash = md5.new()

    return hash.hexdigest()


#直播地址组装
def build_live_addr():
    t = time.strftime('%Y%m%d%H%M%S',time.localtime())[2:]
    data = '%s#%s#%s' %(liveID, t, urlKey)
    secret = getMD5_Value(data)
    rtmp_addr = '%s%s?liveID=%s&time=%s&secret=%s' %(RTMP_ADDR, liveResCode, liveID, t, secret)
    http_addr = '%s/%s/playlist.m3u8?liveID=%s&time=%s&secret=%s' %(HTTP_ADDR, liveResCode, liveID, t, secret)
    FULL_ADDR['rtmp'] = rtmp_addr
    FULL_ADDR['http'] = http_addr
    return FULL_ADDR

#获取本机ip地址，用来产生区别于其他机器的数据
def get_local_ip():
    try:
        ip = os.popen("ifconfig | grep 'inet addr' | awk '{print $2}'").read()
        ip = ip[ip.find(':') + 1:ip.find('\n')]
    except Exception,e:
        print e
    return ip


class Video_To_Live(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        liveAddr = self.queue.get()
        #print liveAddr
        try:
            print liveAddr
            subprocess.call('./ffmpeg -i \"%s\" -c:v copy -c:a copy -bsf:a aac_adtstoasc -y -f flv -timeout 4000 /dev/null 2>/dev/null' %liveAddr,stdout=subprocess.PIPE,shell=True)
        except Exception as e:
            wiriteLog('ERROR',str(e))
        self.queue.task_done()


if __name__ == "__main__":
    time.sleep(SLEEP_TIME)
    parser = argparse.ArgumentParser(description = "Live Play")
    parser.add_argument('--liveType',action = "store",dest = "liveType",required = False)
    parser.add_argument('--pnum',action = "store",dest = "pnum",type = int,required = False)
    parser.add_argument('--itime',action = "store",dest = "itime",required = False)
    given_args = parser.parse_args()

    liveType = given_args.liveType 
    threadNum = given_args.pnum
    intervalTime = given_args.itime

    print "%d 个 %s 进程开始运行........" %(threadNum, Video_To_Live)
    for i in xrange(threadNum):
        videotolive = Video_To_Live(queue)
        videotolive.setDaemon(True)
        videotolive.start()

    for i in xrange(threadNum):
        if liveType in ["http","rtmp"]:
               addr = build_live_addr()
            liveaddr = addr[liveType]
        queue.put(liveaddr)
        time.sleep(intervalTime)
    queue.join()
    print "进程退出"