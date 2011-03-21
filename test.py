#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, subprocess, Queue, time, threading

SofTalk_Path =  '/cygdrive/c/Users/natsumesou/Documents/softalk/SofTalkw.exe'

def CallSofTalk(text, speed=100):
    global SofTalk_Path
    text = text.strip('\n')

    options = '\'/X:1 /V:80 /S:%d /W:\"%s\"\'' % (speed, text)
    try:
        print 'speak ' + text
        #return subprocess.Popen([SofTalk_Path, options])
        subprocess.call([SofTalk_Path, options])
    except OSError, e:
        raise OSError, 'OS Error: SofTalk が起動しませんでした: ' + str(e)

def worker():
    while True:
        try:
            text = queue.get()
            print 'get queue:' + text
            CallSofTalk(text)
            print 'spoke...'
            """
            sprocess = CallSofTalk(text)
            print 'spoke...'
            while sprocess.poll() == None:
                print 'sleeping'
                time.sleep(0.5)
            """
        except Exception, e:
            print type(e)
            print e

queue = Queue.Queue(0)
if __name__ == '__main__':
    try:
        print 'start'
        text = 'ほげふば、おなかすいたねん。'


        args = ()
        #t = tthread(target=worker)
        t = threading.Thread(target=worker)
        t.setDaemon(True)
        t.start()

        while True:
            text = raw_input('input:')
            if text == 'exit':
                print 'killed'
                break
            print 'put queue'
            queue.put(text)

    except KeyboardInterrupt:
        print 'end'
    except Exception, e:
        print type(e)
        print e
