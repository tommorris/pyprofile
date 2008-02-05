#!/usr/bin/env python
# encoding: utf-8
"""
ProfileGrab.py

Created by Tom Morris on 2008-01-25.

Name parsing ideas
2. Look for hCards with uid
3. Look for hCard with name that is over 75 percent levenshtein of the non-TLD components of names
4. Look for RSS feeds and parse the data out of there.
5. Look for linked FOAF data and SPARQL it out of there.
6. Look for mailtos and get the text, then run to see if it's "name-like"?
- parse 'posted by' from wordpress
"""

from BeautifulSoup import BeautifulSoup
import sys, os, unittest, urllib2, re

class ProfileGrab:
  def __init__(self, uri):
    self.uri = uri
    self.data = urllib2.urlopen(self.uri)
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
    
  
  
  def foaf(self, uri):
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
  def test_me(self):
    self.assertEqual(ProfileGrab("http://tommorris.org/").author, u"Tom Morris")
#	  self.assertEqual(ProfileGrab("http://factoryjoe.com/"), u"Chris Messina")
#	  self.assertEqual(ProfileGrab("http://www.cubicgarden.com/"), u"Ian Forrester")
#	  self.assertEqual(ProfileGrab("http://www.andybudd.com/"), u"Andy Budd")
#	  self.assertEqual(ProfileGrab("http://scienceblogs.com/pharyngula/"), u"PZ Myers")
#   self.assertEqual(ProfileGrab("http://aralbalkan.com/"), u"Aral Balkan")


if __name__ == '__main__':
  unittest.main()