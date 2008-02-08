#!/usr/bin/env python
# encoding: utf-8
"""
BlogDetection.py

Detect whether or not something is a blog. Unfortunately will not tell you whether it's a good blog.

Criteria:
* Stuff hosted on Blogspot, WordPress or TypePad seem blogs almost by definition.
* Look for RSS feed, and check XML inside
* Look for authorship consistency
* Look for the words 'Comments', 'TrackBack', 'blogroll'
* Look for telltale signs of common blog widgets (MyBlogLog)
* Look for telltales of popular classnames and blog template markup structure
* Look for links to blogging software provider (MT, Blojsom, WordPress etc.)
* Look for links to popular add-ons (Akismet, Bad Behaviour)
* Look for links to popular blog causes
* XFN?
* Look for the word 'blog' (and in meta-tags)!
* Look for 'Submit to Digg/Reddit/del.icio.us' links
* Check Technorati

Created by Tom Morris on 2008-02-07.
"""

import sys, os, re, unittest, urllib2
from BeautifulSoup import BeautifulSoup

class BlogDetection:
  def __init__(self, uri):
    self.uri = uri
    self.probability = 0
    # get data
    
    # check to see if blogspot, wordpress, typepad
    if re.search("wordpress\.com", self.uri) is not None:
      self.probability = 1
    if re.search("blogspot\.com", self.uri) is not None:
      self.probability = 1
    if re.search("typepad\.com", self.uri) is not None:
      self.probability = 1
    if re.search("blogs\.com", self.uri) is not None:
      self.probability = 1
    
    self.data = urllib2.urlopen(self.uri)
    self.soup = BeautifulSoup(self.data)
    self.linkHunt()
    
  def linkHunt(self):
    # detect rss feeds
    if self.soup.find(['a', 'link'], {"href": True, "type": "application/rss+xml"}):
      self.probability += 0.2 * len(self.soup.findAll(['a', 'link'], {"href": True, "type": "application/rss+xml"}))
    
    # look for openid
    if self.soup.find(['a', 'link'], {"href": True, "rel": ["openid.server", "openid.delegate"]}):
      self.probability += 0.4
    
    # look for pingback
    if self.soup.find(['a', 'link'], {"rel": "pingback"}):
      self.probability += 0.3
    
    # look for rsd
    if self.soup.find(['a', 'link'], {"type": "application/rsd+xml"}):
      self.probability += 0.2
    
    # look for permalink
    if self.soup.find(text="Permalink") or self.soup.find(text="permalink"):
      self.probability += 0.4
    
    # detect xfn links to technorati (profiles - as per tantek.com)
    if self.soup.find(['a', 'link'], {"href": re.compile("technorati.com"), "rel": re.compile("me")}) is not None:
      self.probability += 0.6
  

class BlogDetectionTests(unittest.TestCase):
  def setUp(self):
    pass
  def test_class(self):
    self.assert_(BlogDetection)
  def test_hostingServicesShouldReturnTrue(self):
    blogs = ['http://stephenlaw.blogspot.com', 'http://epeus.blogspot.com/', 'http://eirepreneur.blogs.com/', 'http://unlimitededition.wordpress.com/', 'http://tupelobizbuzz.wordpress.com/', 'http://tantek.com/', 'http://scripting.com/', 'http://tommorris.org/blog/', 'http://cubicgarden.com/', 'http://danbri.org/words/', 'http://techcrunch.com/', 'http://adactio.com/journal/', 'http://backstage.bbc.co.uk/news/']
    for i in blogs:
      self.assertEqual(bool(int(round(BlogDetection(str(i)).probability))), True, str(i) + " should be detected as a blog")
  


if __name__ == '__main__':
  unittest.main()