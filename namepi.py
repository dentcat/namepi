#!/usr/bin/env python
#
# namepi.py - renames all the files in the current directory based on
#             episode info from thetvdb.com
#             Following formats of episode and season numbers in the
#             filename are supported:
#             - my_fav_tv_show_S06E10.avi
#             
# Copyright (C) 2012 Mansour <mansour@oxplot.com>
#

import sys
import os
import re
import shutil
from urllib2 import urlopen, Request

########################################################################
# parameters
########################################################################

useragent = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.5)' \
            ' Gecko/2008121622 Ubuntu/8.04 (hardy) Firefox/3.0.5'

########################################################################
# main program
########################################################################

def main():

  # Usage: namepi.py {imdb title number - e.g. tt0934814}

  if len(sys.argv) < 2:
    print "Usage: namepi.py {thetvdb id - e.g. 73255}"
    return
  url = 'http://thetvdb.com/?tab=seasonall&id=%s' % sys.argv[1]

  # download the page  

  stderr("Downloading episodes name ...")
  page = urlopen(Request(url, headers={'User-Agent': useragent})).read()
  stderr("DONE\n")

  # extract the episode rows

  row_pat = re.compile(r'<tr>.*?>(\d+) - (\d+)</a>.*?>([^<]+)</a>',
                       re.DOTALL)
  episodes = dict(
    map(
      lambda a: (
        (int(a[0]), int(a[1])),
        stripspecial(decodehtml(a[2].decode('latin1')))
      ),
      row_pat.findall(page)
    )
  )

  # rename files

  avi_pat = re.compile(r'S(\d+)E(\d+)', re.I)
  files = [f.decode('utf8')
           for f in os.listdir(".") if avi_pat.search(f)]
  for f in files:
    season, episode = map(int, avi_pat.findall(f)[0])
    name = episodes[(season, episode)]
    if '.' in f:
      ext = u'.' + f.split(u'.')[-1]
    else:
      ext = u''
    new_f = u'%02d%02d-%s%s' % (season, episode, name, ext)
    shutil.move(f, new_f)

########################################################################
# polish names and strip off any special characters
########################################################################

def stripspecial(name):
  name = re.sub(r'[\'"]+', '', name)
  name = re.sub(r'[`~!@#$%^&*()+=_\][\\{};:\'"<>,.?/\r\n -]+',
                '_',
                name)
  name = name.strip('_').lower()
  return name

########################################################################
# standard output/error with flush
########################################################################

def stdout(data):
  sys.stdout.write(data)
  sys.stdout.flush()

def stderr(data):
  sys.stderr.write(data)
  sys.stderr.flush()

########################################################################
# decodes html entities
########################################################################

def decodehtml(data):
  def replacer(m):
    m = m.group(0)[1:-1]
    if m.startswith('#x'):
      return unichr(int(m[2:], 16))
    elif m.startswith('#'):
      return unichr(int(m[1:]))
    else:
      if m == 'amp': return u'&'
      elif m == 'quot': return u'"'
      elif m == 'apos': return u"'"
      elif m == 'lt': return u'<'
      elif m == 'gt': return u'>'
      else: return u'FIXME'
  return re.sub(r'&[^;]+;', replacer, data)

########################################################################
########################################################################

if __name__ == '__main__':
  main()
