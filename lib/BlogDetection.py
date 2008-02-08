#!/usr/bin/env python
# encoding: utf-8
"""
BlogDetection.py

Detect whether or not something is a blog. Unfortunately will not tell you whether it's a good blog.

Criteria:
* Stuff hosted on Blogspot, WordPress or TypePad seem blogs almost by definition.
* Look for RSS feed
* Look for authorship consistency
* Look for the words 'Comments', 'TrackBack', 'blogroll'
* Look for telltale signs of common blog widgets (MyBlogLog)
* Look for telltales of popular classnames and blog template markup structure
* XFN?
* Look for the word 'blog'!
* Look for 'Submit to Digg/Reddit/del.icio.us' links

Created by Tom Morris on 2008-02-07.
"""

import sys, os, re, unittest

class BlogDetection:
  def __init__(self, uri):
    self.uri = uri
    self.probability = 0
    # get data
    
    # check to see if blogspot, wordpress, typepad
    if re.search("wordpress\.com", self.uri) is not None:
      self.probablity = 1
    if re.search("blogspot\.com", self.uri) is not None:
      self.probability = 1
    if re.search("typepad\.com", self.uri) is not None:
      self.probability = 1
    if re.search("blogs\.com", self.uri) is not None:
      self.probability = 1


class BlogDetectionTests(unittest.TestCase):
	def setUp(self):
		pass
	def test_class(self):
	  self.assert_(BlogDetection)
	def test_hostingServicesShouldReturnTrue(self):
	  print BlogDetection("http://tantek.com/").probability
	  self.assertEqual(bool(int(BlogDetection("http://tantek.com/").probability)), False)
	  self.assertEqual(bool(int(BlogDetection("http://epeus.blogspot.com/").probability)), True)


if __name__ == '__main__':
	unittest.main()