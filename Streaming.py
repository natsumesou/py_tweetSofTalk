#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, subprocess, sys, ConfigParser
from getpass import getpass
from tweetSoftalkError import StatusError
import tweepy
from tweepy import StreamListener, Stream, TweepError
from pit import Pit

SofTalk_Path =  '/cygdrive/c/Users/natsumesou/Documents/softalk/SofTalkw.exe'
SofTalk_Volume = 0
SofTalk_Speed = 0
follow_list = []


def CallSofTalk2(text):
    text = text.strip('\n')
    options = '\'/X:1 /V:80 /S:180 /W:\"%s\"\'' % (text)
    try:
        subprocess.Popen([SofTalk_Path, options])
    except OSError, e:
        print 'OS Error: SofTalk が起動しませんでした'
        raise
    except IOError, e:
        print 'SofTalkw.exe NOT Found: '
        raise

def CallSofTalk(text):
    text = text.encode('utf-8')
    cmd = SofTalk_Path + ' /X:1 /V:80 /S:180 /W:"%s"' % (text)
    try:
        os.system(cmd)
    except OSError, e:
        print 'OS Error: SofTalk が起動しませんでした'
        raise
    except IOError, e:
        print 'SofTalkw.exe NOT Found: '
        raise


def check_tweet(status):
    for id in follow_list:
        #checking tweet what is folloing user's or not
        if status.author.id == id:
            # checking mention what is folloing or not
            if not status.in_reply_to_user_id:
                return True
            else:
                for mention_id in follow_list:
                    if status.in_reply_to_user_id == mention_id:
                        return True
                return False
    return False

class Settings():
    CONFIG_FILE = 'settings.ini'
    username = ''
    SofTalk_Path = ''
    SofTalk_Volume = 0
    SofTalk_Speed = 0
    def __init__(self):
        conf = ConfigParser.SafeConfigParser()
        if not conf.read(self.CONFIG_FILE):
            raise IOError, self.CONFIG_FILE + 'が存在しません'

        try:
            self.username = conf.get('Authentication', 'username')
            self.SofTalk_Path = conf.get('SofTalk', 'path')
            SofTalk_Volume = conf.get('SofTalk', 'volume')
            SofTalk_Speed = conf.get('SofTalk', 'speed')
        except ConfigParser.NoSectionError, e:
            print self.CONFIG_FILE + 'が破損しています:'
            raise


        try:
            self.SofTalk_Volume = int(SofTalk_Volume)
        except ValueError, e:
            print self.CONFIG_FILE+'の [SofTalk] にある volume の値が不正です。: '
            #sys.exit()
            raise
        try:
            self.SofTalk_Speed = int(SofTalk_Speed)
        except ValueError, e:
            print self.CONFIG_FILE+'の [SofTalk] にある speed の値が不正です。: '
            #sys.exit()
            raise


class SofTalkStreamListener(StreamListener):
    def on_status(self, status):
        if check_tweet(status):
            print '[%s] %s\n' % (status.author.screen_name, status.text)
            CallSofTalk2(status.text)
        else:
            pass
    def on_error(self, status_code):
        try:
            raise StatusError(status_code)
        except StatusError, e:
            print e
            raise
    def on_timeout(self):
        print 'twitter user stream is timeout'

def main():
    # for debug
    """
    conf = Pit.get('twitter.com')
    username = conf['username']
    passwd = conf['password']
    """

    settings = Settings()
    username = settings.username

    global SofTalk_Path
    global SofTalk_Volume
    global SofTalk_Speed

    SofTalk_Path = settings.SofTalk_Path
    SofTalk_Volume = settings.SofTalk_Volume
    SofTalk_Speed = settings.SofTalk_Speed

    if not username:
        username = raw_input('twitter username: ')
    else:
        print 'username: ' + username
    passwd = getpass('password: ')

    global follow_list
    follow_list = tweepy.api.friends_ids(screen_name=username)
    follow_list.append(tweepy.api.get_user(username).id)

    stream = Stream(username, passwd, SofTalkStreamListener(), timeout=None)
    stream.filter(follow=follow_list)

    # add ownself for check_tweet

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print 'bye'
    except Exception, e:
        print e
