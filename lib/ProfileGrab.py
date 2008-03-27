#!/usr/bin/env python
# encoding: utf-8
"""
ProfileGrab.py

Created by Tom Morris on 2008-01-25.

Name parsing ideas
2. Look for hCards with uid
3. Look for hCard with name that is over 75 percent levenshtein of the non-TLD components of names
5. Look for linked FOAF data and SPARQL it out of there.
- parse 'posted by' from wordpress
"""

from BeautifulSoup import BeautifulSoup
from DiskCacheFetcher import DiskCacheFetcher
from operator import itemgetter
import sys, os, unittest, urllib2, re, feedparser, autorss

class ProfileGrab:
  def __init__(self, uri):
    self.fetcher = DiskCacheFetcher('/tmp')
    self.uri = uri
    self.data = self.fetcher.fetch(uri, 43200)
    # presume it's html for now, we'll refactor to take into account other stuff
    self.soup = BeautifulSoup(self.data)
    self.author = None
    
    # 1. grab meta-author and meta-dc.creator tags
    metaauthor = self.meta_author()
    if metaauthor is not None:
      self.author = metaauthor
    
    # hCard
    if self.author is None:
      self.hcard()
    
    # 4. Look for RSS feeds and parse the names out of there
    if self.author is None:
      self.detectRss()
    
    if self.author is None:
      self.mailtoLinkDetect()
  
  def hcard(self):
    # declare
    regex_uid = re.compile('uid')
    regex_url = re.compile('url')
    regex_fn = re.compile('fn')
    
    self.loadHcards()
    selectedCard = None
    if len(self.hcards) is 1:
      selectedCard = self.hcards[0]
    else:
      for card in self.hcards:
        if card.findAll(['a', 'link'], {'class': regex_uid}):
          if card.findAll(['a', 'link'], {'class': regex_uid})[0]['href'] is self.uri:
            selectedCard = card
        else:
          for url in card.findAll(['a', 'link'], {'class': regex_url}):
            if url['href'] is self.uri:
              selectedCard = card
    if selectedCard is not None:
      selectedNames = selectedCard.findAll(True, {'class': regex_fn})
      if len(selectedNames) is 1 and self.author is None:
        self.author = unicode(''.join(selectedNames[0].findAll(text=True)).strip())
    
  
  def getFoafFromHtml(self):
    # get rdf/xml links
    data = rdflib.ConjunctiveGraph()
    for i in self.soup.query("link", {"type": "application/rdf+xml", "href": True}):
      data.add(str(i['href']))
    
    # get n3 links
    for i in self.soup.query("link", {"type": "application/n3", "href": True}):
      data.add(str(i['href']), 'n3')
    
    if len(data) is not 0:
      return data
    else:
      return False
  
  def getNameFromFoaf(self, uri):
    foaf = rdflib.ConjunctiveGraph(uri)
    queryString = """PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name WHERE {
      OPTIONAL {
        ?g a foaf:PersonalProfileDocument;
        foaf:primaryTopic ?person .
      }
      ?person foaf:name ?name .
    }"""
    results = foaf.query(queryString)
  
  def meta_author(self):
    authornames = self.soup.findAll('meta', {'name': ['author', 'DC.creator']})
    if len(authornames) is not 0:
      return unicode(authornames[0]['content'])
    else:
      return None
  
  def loadHcards(self):
    regex_hcard = re.compile('vcard')
    self.hcards = self.soup.findAll(True, {'class': regex_hcard})
  
  def detectRss(self):
    self.rss_feed = autorss.getRSSLinkFromHTMLSource(self.data)
    firstfeed = feedparser.parse(self.rss_feed, 43200)
    if hasattr(firstfeed, 'author_detail') is True:
      if firstfeed.author_detail.name is not None:
        self.author = unicode(firstfeed.author_detail.name)
    else:
      authorarray = []
      for i in firstfeed.entries:
        if hasattr(i, 'author'):
          authorarray += [i.author]
      if len(authorarray) is not 0:
        self.author = unicode(getMostPopularFromList(authorarray))
  
  def mailtoLinkDetect(self):
    mailtoLinks = self.soup.findAll(['a', 'link'], {'href': re.compile('mailto:')})
    if len(mailtoLinks) is not 0:
      self.author = unicode(mailtoLinks[0].contents[0])
  


def getMostPopularFromList(inlist):
  output = {}
  for i in inlist:
    if i in output:
      output[i] = (output.get(i) + 1)
    else:
      output[i] = 1
  items = output.items()
  items.sort(key = itemgetter(1), reverse=True)
  return items[0][0]


class ProfileGrabTests(unittest.TestCase):
  def setUp(self):
    pass
  def test_class(self):
    self.assert_(ProfileGrab)
  def test_jeremy(self):
    self.assertEqual(ProfileGrab("http://adactio.com/").author, u"Jeremy Keith")
  def test_brian(self):
    self.assertEqual(ProfileGrab("http://suda.co.uk/").author, u"Brian Suda")
  def test_tantek(self):
    self.assertEqual(ProfileGrab("http://tantek.com/").author, u"Tantek Çelik")
  def test_scoble(self):
    self.assertEqual(ProfileGrab("http://scobleizer.com/").author, u"Robert Scoble")
  def test_me(self):
    self.assertEqual(ProfileGrab("http://tommorris.org/").author, u"Tom Morris")
  def test_dave(self):
    self.assertEqual(ProfileGrab("http://scripting.com/").author, u"Dave Winer")
  def test_chrismessina(self):
    self.assertEqual(ProfileGrab("http://factoryjoe.com/blog/").author, u"Chris Messina")
  def test_ianforrester(self):
    self.assertEqual(ProfileGrab("http://www.cubicgarden.com/").author, u"Ian Forrester")
  def test_andybudd(self):
    self.assertEqual(ProfileGrab("http://www.andybudd.com/").author, u"Andy Budd")
  def test_colinschluter(self):
    self.assertEqual(ProfileGrab("http://www.colinschlueter.com/").author, u"Colin Schlüter")
  def test_molly(self):
    self.assertEqual(ProfileGrab("http://molly.com/").author, u"Molly Holzschlag")
  def test_aralbalkan(self):
    self.assertEqual(ProfileGrab("http://aralbalkan.com/").author, u"Aral Balkan")
  def test_pzmyers(self):
	  self.assertEqual(ProfileGrab("http://scienceblogs.com/pharyngula/").author, u"PZ Myers")


if __name__ == '__main__':
  unittest.main()