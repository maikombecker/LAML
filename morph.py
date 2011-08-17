'''
TO-DOS: 
- split infix enviros into the ones on the right and the ones on the left
This will require the creation of two methods. 
DONE - 7/18
- consider taking the reverse statements out of specific methods and placing
them in find_affixes routine. This will make some things a bit more explicit.
DONE - 7/18
- search for affixes in general, not prefixes, suffixes, etc.  The hardest part
about this change is to be able, at the end, to speculatively say which affixes
are suffixes, which prefixes, which infixes.

the affix lib will contain the following information:
list of suffix occurrences, for freqdist purposes
list of enviros that correspond to a given suffix
DONE - 7/25

CHANGELOG:
7/18
- added tracking of number of times a certain environment occurs for a given affix
- added support for infixes, tested on one word, not yet tested on corpus
- tested suffix addition on one word, works fine.
7/25
made a generic affix finder

'''

###############################################################################
import re
from nwl import compare_features
from resources.features import *

###############################################################################
class Affix_Lib:
	def __init__(self):
		self.on_right = []
		self.on_left = []

	def add(self, string, name):
		if name == 'r':
			lib = self.on_right
		elif name == 'l':
			lib = self.on_left
		lib += [string]

	def generalize(self, string, name, ft=FEATURES):
		print string
		if name == 'r':
			lib = self.on_right
		elif name == 'l':
			lib = self.on_left
		featlist = {}
		if type(lib[0]) == str:
			if lib[0] != '' and string != '':
				for indx in range(26):
					try:
						if ft[lib[0]][indx] == ft[string][indx]:
							featlist[indx] = ft[lib[0]][indx]
					except IndexError:
						print "One of the phonemes was not found, please add it"
						break
			else:
				pass
		elif type(lib[0]) == dict:
			featlist = lib[0]
			for indx in lib[0].keys():
				if ft[string][indx] != lib[0][indx]:
					del featlist[indx]
		else:
			print 'error'
			pass
		return featlist

###############################################################################
class Affix_Learner:
	def __init__(self):
		self.affixes = {}
						
	def find_affixes(self, alignment, features):			
#------------------------------------------------------------------------------
		def create_affix(aff):
			if not re.match('_', aff):
				if self.affixes.has_key(aff):
					self.affixes[aff][1] += 1
					self.affixes[aff][0].generalize(r_edge, 'r')
					self.affixes[aff][0].generalize(l_edge, 'l')
				else:
					self.affixes[aff] = [Affix_Lib(), 1.0]
					self.affixes[aff][0].add(r_edge, 'r')
					self.affixes[aff][0].add(l_edge, 'l')

		switch = False
		aff1, aff2  = '', ''

		for indx in range(len(alignment)):
			
			if indx == 0:
				previous = ('','')
			else:	# collecting enviro
				previous = alignment[indx-1]
		
			pair = alignment[indx]
			if compare_features(pair[0], pair[1], ft=features) > 1:
				# we check if one of string contains another
				nomatch1 = pair[0] not in pair[1]
				nomatch2 = pair[1] not in pair[0]
				if nomatch1 and nomatch2:
					aff2 =''.join([aff2, pair[1]])
					aff1 =''.join([aff1, pair[0]])
					if not switch:
						l_edge = previous[0]
						switch = True
			else:
				if switch:
					r_edge = pair[0]		
					create_affix(aff1)
					create_affix(aff2)
					aff1, aff2  = '', ''
					switch = False
			if indx == len(alignment)-1:
				if switch:
					r_edge = ''
					create_affix(aff1)
					create_affix(aff2)
	
###############################################################################
###############################################################################
	def test_find_affixes(self, alignment, features):
#------------------------------------------------------------------------------
		def create_affix(aff):
			if not re.match('_', aff):
				return (aff, l_edge, r_edge) 

#------------------------------------------------------------------------------
		def test_affix(aff):
			if aff != None:
				if self.affixes.has_key(aff[0]):
					enviro = self.affixes[aff[0]][0]
					if enviro.on_left.has_key(aff[1]):
						if enviro.on_right.has_key(aff[2]):
							answer = (aff, True)
						else:
							answer = (aff, False)
					else:
						answer = (aff, False)
				else:
					answer = (aff, False)
				return answer
			else:
				pass

		answers = []
		switch = False
		aff1, aff2 = '', ''
		for indx in range(len(alignment)):
			pair = alignment[indx]
			
			if indx == 0:
				previous = ('','')
			else:	
				previous = alignment[indx-1]
			
			if compare_features(pair[0], pair[1], ft=features) > 1:
				nomatch1 = pair[0] not in pair[1]
				nomatch2 = pair[1] not in pair[0]
				if nomatch1 and nomatch2:
					aff2 =''.join([aff2, pair[1]])
					aff1 =''.join([aff1, pair[0]])
					if not switch:
						l_edge = previous[0]
						switch = True
			else:
				if switch:
					r_edge = pair[0]
					answers.append(test_affix(create_affix(aff1)))
					answers.append(test_affix(create_affix(aff2)))
					aff1, aff2  = '', ''
					switch = False

			if indx == len(alignment)-1:
				if switch:
					r_edge = ''
					answers.append(test_affix(create_affix(aff1)))
					answers.append(test_affix(create_affix(aff2)))
		#print [x for x in answers if x != None]
		return [x for x in answers if x != None]
	

################################################################################
# testing section
#a = [('a','_'),('b','b'),('c','c'),('_','o'),('r','r'),('t','t'),('a','_')]
#b = [('a','_'),('b','b'),('a','e'),('c','c'),('_','o'),('r','r'),('t','t'),('a','_')]
#s = Affix_Learner()
#s.find_affixes(a, FEATURES)
#for affix in s.affixes:
	#print affix, s.affixes[affix][1]
	#print s.affixes[affix][0].on_left
	#print s.affixes[affix][0].on_right
#s.test_find_affixes(b, FEATURES)
