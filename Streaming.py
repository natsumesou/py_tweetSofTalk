#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, subprocess, sys
from getpass import getpass
import tweepy
from tweepy import StreamListener, Stream, TweepError
from pit import Pit

path =  '/cygdrive/c/Users/natsumesou/Documents/softalk/SofTalkw.exe'
follow_list = []

def CallSofTalk2(text):
    text = text.strip('\n')
    options = '\'/X:1 /S:180 /W:\"%s\"\'' % (text)
    try:
        subprocess.Popen([path, options])
    except OSError, e:
        print 'OS Error: ' + e

def CallSofTalk(text):
    text = text.encode('utf-8')
    cmd = path + ' /X:1 /S:180 /W:"%s"' % (text)
    os.system(cmd)

def check_tweet(status):
    for id in follow_list:
        if status.author.id == id:
            return True
    return False

class SofTalkStreamListener(StreamListener):
    def on_status(self, status):
        if check_tweet(status):
            print '[%s] %s\n' % (status.author.screen_name, status.text)
            CallSofTalk2(status.text)
        else:
            pass
    def on_error(self, status_code):
        print 'an Error has Occured with status code : ' + str(status_code)
    def on_timeout(self):
        print 'twitter user stream is timeout'

def main():
    conf = Pit.get('twitter.com')
    username = conf['username']
    passwd = conf['password']
    #username = raw_input('twitter username: ')
    #passwd = getpass('twitter password: ')

    global follow_list
    follow_list = tweepy.api.friends_ids(screen_name=username)

    stream = Stream(username, passwd, SofTalkStreamListener(), timeout=None)
    stream.filter(follow=follow_list)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print 'bye'
