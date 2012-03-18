#!/usr/bin/env python2

import json, sys, httplib, urllib
from datetime import datetime, timedelta
from time import sleep

## Get the data we need to log into the API
f = open('user.json', 'r')
data = json.load(f)
f.close()

days = data['days']
user = data['user']
passwd = data['passwd']

## Load our json which should be all the user's history
f = open('data.json', 'r')
data = json.load(f)
f.close()

# Every thing before this time will be deleted
before_time = datetime.now() - timedelta(days=days)

## Fill an array of IDs that are to be deleted
deletion_ids = []
for d in data:
    date = datetime.fromtimestamp(d['created'])
    if date < before_time:
        deletion_ids.append(d)

if len(deletion_ids) == 0:
    print "Couldn't find any posts to delete"
    exit(0)


## This part logs you in.
headers = {"Content-type": "application/x-www-form-urlencoded"}
conn = httplib.HTTPSConnection('ssl.reddit.com')
params = urllib.urlencode({
    'user': user,
    'passwd': passwd,
    'api_type': 'json'})
conn.request("POST", "/api/login/%s" % user, params, headers)
http = conn.getresponse()
tmp = json.loads(http.read())['json']['data']
headers.update({'Cookie': 'reddit_session=%s' % tmp['cookie']})
modhash = tmp['modhash']

print '# Headers: %s' % headers

for dat in deletion_ids:
    print u'''{time} {subreddit}: {text}...'''.format(
        subreddit = dat['subreddit'],
        id = dat['id'],
        time = datetime.fromtimestamp(dat['created']).date(),
        text = dat[u'body'][:20])
    # And now for the deleting
    conn = httplib.HTTPConnection('www.reddit.com')
    params = urllib.urlencode({
        'id': dat['id'],
        'uh': modhash,
        'api_type': 'json'})
    conn.request('POST', '/api/del', params, headers)
    http = conn.getresponse()
    print http.getheaders(), http.read()
    break
    #sleep(2)