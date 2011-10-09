#!/usr/bin/env python
#
# namepi.py - renames all the files in the current directory based on
#             episode info from imdb.
#             files to be renamed must have the season and episode
#             number in their file names, season number coming before
#             episode number - e.g. "Futurama S04 episode #05 - pilot"
#             NOTE: both season and episode number must exactly be two
#                   digits long
#             
# Copyright (C) 2009 Mansour <mansour@oxplot.com>
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
    print "Usage: namepi.py {imdb title number - e.g. tt0934814}"
    return
  url = 'http://www.imdb.com/title/%s/episodes' % sys.argv[1]

  # download the page  

  stderr("Downloading episodes name ...")
  page = urlopen(Request(url, headers={'User-Agent': useragent})).read()
  stderr("DONE\n")

  # extract the episode rows

  row_pat = re.compile('<div class="filter-all.+?</table>', re.DOTALL)
  rows = row_pat.findall(page)

  # extract season number, episode number and episode name

  number_pat = re.compile(r'Season (\d+), Episode (\d+)')
  name_pat = re.compile(r'<a href="/title/[^"]+">([^<]+)</a>',
                        re.DOTALL)
  episodes = {}
  for r in rows:
    digits = number_pat.findall(r)
    if digits:
      season, episode = [int(x) for x in digits[0]]
      name = name_pat.search(r).group(1).decode('iso-8859-1')
      episodes[(season, episode)] = stripspecial(decodehtml(name))

  # rename files

  avi_pat = re.compile(r'[^\d](\d{2})[^\d]*(\d{2})')

  files = [f.decode('utf8')
           for f in os.listdir(".") if avi_pat.search(f)]

  for f in files:
    season, episode = [unicode(int(x)).rjust(2, '0')
                       for x in avi_pat.findall(f)[0]]
    name = episodes[(int(season), int(episode))]
    if '.' in f:
      ext = u'.' + f.split(u'.')[-1]
    else:
      ext = u''
    new_f = season + episode + u'-' + name + ext
    if f != new_f:
      shutil.move(f, new_f)
      stderr((u"'%s' -> '%s'" % (f, new_f) + u'\n').encode('utf8'))

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
