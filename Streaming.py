#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, subprocess, sys, ConfigParser, time, Queue, threading
from getpass import getpass
from tweetSoftalkError import StatusError
import tweepy
from tweepy import StreamListener, Stream, TweepError
from pit import Pit

SofTalk_Path =  '/cygdrive/c/Users/natsumesou/Documents/softalk/SofTalkw.exe'
SofTalk_Volume = 0
SofTalk_Speed = 0
SofTalk_Queue = Queue.Queue(0)
follow_list = []

tweet_speeds = []
# calculate tweets speed average
def speed_average(speed):
    global tweet_speeds
    if len(tweet_speeds)>4:
        tweet_speeds.pop(0)
        tweet_speeds.append(speed)
    else:
        tweet_speeds.append(speed)

    tweets = 0
    for ts in tweet_speeds:
        tweets += ts
    return tweets/len(tweet_speeds) if len(tweet_speeds) > 4 else SofTalk_Speed


def CallSofTalk(text, speed):
    text = text.strip('\n')

    """
    global SofTalk_Speed
    print 'speed:'+str(speed)
    print 'average:'+str(SofTalk_Speed)
    """

    options = '\'/X:1 /V:80 /S:%d /W:\"%s\"\'' % (speed, text)
    try:
        return subprocess.Popen([SofTalk_Path, options])
    except OSError, e:
        raise OSError, 'OS Error: SofTalk が起動しませんでした: ' + str(e)

# checking tweet what is user's TL or NOT
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

# around settings.ini
class Settings():
    CONFIG_FILE = 'settings.ini'
    def __init__(self):
        conf = ConfigParser.SafeConfigParser()
        if not conf.read(self.CONFIG_FILE):
            raise IOError, self.CONFIG_FILE + 'が存在しません'

        try:
            self.username = conf.get('Authentication', 'username')
            self.SofTalk_Path = conf.get('SofTalk', 'path')
            SofTalk_Volume = conf.get('SofTalk', 'volume')
            SofTalk_Speed = conf.get('SofTalk', 'speed')
            SofTalk_Speed_min = conf.get('SofTalk', 'min_speed')
        except ConfigParser.NoSectionError, e:
            print self.CONFIG_FILE + 'が破損しています:'
            raise

        try:
            self.SofTalk_Volume = int(SofTalk_Volume)
        except ValueError:
            raise ValueError, self.CONFIG_FILE+'の [SofTalk] にある volume の値が不正です。: ' + SofTalk_Volume
        try:
            self.SofTalk_Speed = int(SofTalk_Speed)
        except ValueError:
            raise ValueError, self.CONFIG_FILE+'の [SofTalk] にある speed の値が不正です。: ' + SofTalk_Speed
        try:
            self.SofTalk_Speed_min = int(SofTalk_Speed_min)
        except ValueError:
            raise ValueError, self.CONFIG_FILE+'の [SofTalk] にある min_speed の値が不正です。: ' + SofTalk_Speed_min

    # save speed and volume
    def save(self):
        global SofTalk_Speed
        speed = int(SofTalk_Speed)
        speed = str(speed)
        conf = ConfigParser.SafeConfigParser()
        conf.read(self.CONFIG_FILE)

        conf.set('SofTalk', 'speed', speed)
        f = open(self.CONFIG_FILE, 'w')
        conf.write(f)
        f.close()

# calculate tweets speed
class Check_Speed():
    global SofTalk_Speed
    def __init__(self, softalk_speed_min, softalk_speed_max):
        self.before_time = time.time()
        self.SofTalk_Speed_min = softalk_speed_min
        self.SofTalk_Speed_max = softalk_speed_max
        #self.chars = 0
    def get_speed(self, chars):
        now = time.time()
        before_time = self.before_time
        self.before_time = now
        #self.chars += chars
        speed = chars/(now - before_time)
        return self.get_adjusted_speed(speed)
    def get_adjusted_speed(self, speed=None):
        speed = SofTalk_Speed*speed*0.5 if speed else SofTalk_Speed
        if speed < self.SofTalk_Speed_min:
            speed = self.SofTalk_Speed_min
        if speed > self.SofTalk_Speed_max:
            speed = self.SofTalk_Speed_max


        return speed

def worker():
    global SofTalk_Speed
    while True:
        softalks = SofTalk_Queue.get()
        sprocess = CallSofTalk(softalks['text'], softalks['speed'])
        while sprocess.poll() == None:
            time.sleep(0.5)

# Custion StreamListener
class SofTalkStreamListener(StreamListener):
    global SofTalk_Queue
    def __init__(self, check_speed):
        StreamListener.__init__(self)
        thread = threading.Thread(target=worker)
        thread.setDaemon(True)
        thread.start()
        self.queue = SofTalk_Queue
        self.check_speed = check_speed

    def on_status(self, status):
        if check_tweet(status):
            global SofTalk_Speed

            print '[%s] %s\n' % (status.author.screen_name, status.text)
            try:
                speed = self.check_speed.get_speed(len(status.text))
                SofTalk_Speed = speed_average(speed)
                self.queue.put({'text': status.text, 'speed':speed})
                #CallSofTalk(status.text, speed)
            except Exception, e:
                print e
                raise
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

def main(settings):
    # for debug
    """
    conf = Pit.get('twitter.com')
    username = conf['username']
    passwd = conf['password']
    """

    # loading settings
    username = settings.username

    global SofTalk_Path
    global SofTalk_Volume
    global SofTalk_Speed

    SofTalk_Path = settings.SofTalk_Path
    SofTalk_Volume = settings.SofTalk_Volume
    SofTalk_Speed = settings.SofTalk_Speed
    softalk_speed_min = settings.SofTalk_Speed_min
    softalk_speed_max = 200

    # insert username and password
    if not username:
        username = raw_input('twitter username: ')
    else:
        print 'username: ' + username
    passwd = ''
    while not passwd:
        passwd = getpass('password: ')

    # checking user's follow ids
    global follow_list
    follow_list = tweepy.api.friends_ids(screen_name=username)
    follow_list.append(tweepy.api.get_user(username).id)

    print 'connecting to twitter.com ...'

    # start twitter UserStream
    stream = Stream(username, passwd, SofTalkStreamListener(Check_Speed(softalk_speed_min, softalk_speed_max)), timeout=None)
    stream.filter(follow=follow_list)

if __name__ == "__main__":
    try:
        print '<ctrl-c> End this program'
        settings = Settings()
        main(settings)
    except KeyboardInterrupt:
        settings.save()
        print 'bye'
    except Exception, e:
        print e
