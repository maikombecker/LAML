'''
TO-DOS: 
- split infix enviros into the ones on the right and the ones on the left
This will require the creation of two methods. 
DONE - 7/18
- consider taking the reverse statements out of specific methods and placing
them in learn_affixes routine. This will make some things a bit more explicit.
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

8/19
Reworked some of the nitty-gritty of how acquired affixes are stored
'''

###############################################################################
import re
from nwl import compare_features
from resources.features import FEATURES as features

###############################################################################
class Affix:
	def __init__(self, affix_name, affix_partner):
		self.name = affix_name
		self.count = 1
		self.partner = []
		self.partner += [affix_partner]
		self.on_right = {}
		self.on_left = {}
		self.suffix = False
		self.prefix = False
#------------------------------------------------------------------------------
	def add_enviro(self, string, name, ft):
		if name == 'r':
			lib = self.on_right
		elif name == 'l':
			lib = self.on_left
		
		def generalize(string):
			featlist = lib
			for indx in lib.keys():
				if ft[string][indx] != lib[indx]:
					del featlist[indx]
				else:
					pass
			return featlist
		#end definition of generalize()
		
		if string == '' and name == 'r':
			self.suffix = True
		elif string == '' and name == 'l':
			self.prefix = True
		else:
			if len(lib) > 0:
				lib = generalize(string)
			else:
				for indx in range(len(ft[string])):
					lib[indx] = ft[string][indx]


###############################################################################
class Affix_Learner:
	def __init__(self):
		self.affixes = {}
						
	def learn_affixes(self, alignment, ft=features):			
#------------------------------------------------------------------------------
		def create_affix(aff, aff2):
			if not re.match('_', aff):
				if self.affixes.has_key(aff):
					self.affixes[aff].count += 1
					self.affixes[aff].partner += [aff2]
					self.affixes[aff].add_enviro(r_edge, 'r', ft)
					self.affixes[aff].add_enviro(l_edge, 'l', ft)
				else:
					self.affixes[aff] = Affix(aff, aff2)
					self.affixes[aff].add_enviro(r_edge, 'r', ft)
					self.affixes[aff].add_enviro(l_edge, 'l', ft)
		# end definition of create_affix()

		switch = False
		aff1, aff2  = '', ''

		for indx in range(len(alignment)):
			if indx == 0:
				previous = ('','')
			else:	# collecting enviro
				previous = alignment[indx-1]
			
			pair = alignment[indx]
			if compare_features(pair[0], pair[1], ft=features) > 1:
				nomatch1 = pair[0] not in pair[1]
				nomatch2 = pair[1] not in pair[0]
				if nomatch1 and nomatch2:
					# we check if one string contains another
					aff2 =''.join([aff2, pair[1]])
					aff1 =''.join([aff1, pair[0]])
					if not switch:
						l_edge = previous[0]
						switch = True
			else:
				if switch:
					r_edge = pair[0]		
					create_affix(aff1, aff2)
					create_affix(aff2, aff1)
					aff1, aff2  = '', ''
					switch = False
			if indx == len(alignment)-1:
				if switch:
					r_edge = ''
					create_affix(aff1, aff2)
					create_affix(aff2, aff1)
	
###############################################################################
###############################################################################
	def verify_affixes(self, alignment, features):
#------------------------------------------------------------------------------
		def create_affix(aff):
			if not re.match('_', aff):
				return (aff, l_edge, r_edge) 
		#end create_affix() definition
#------------------------------------------------------------------------------
		def logic_and(bool1, bool2):
			if bool1 == True and bool2 == True:
				return True
			else:
				return False
		#end logic_and() definition

		def test_env(lib, string):
			print string
			for indx in lib.keys():
				if features[string][indx] != lib[indx]:
					print indx, features[string][indx], lib[indx]
					return False
				else:
					pass
			return True
#------------------------------------------------------------------------------
		def test_affix(aff):
			if aff != None:
				if self.affixes.has_key(aff[0]):
					print 'affix exists'
					affix = self.affixes[aff[0]]
					right, left = False, False
					if affix.suffix and aff[2] == '':
						print 'suspect it\'s a suffix'
						right = True
						left = test_env(affix.on_left, aff[1])
					elif affix.prefix and aff[1] == '':
						left = True
						right = test_env(affix.on_right, aff[1])
					else:
						right = test_env(affix.on_right, aff[0])
						left = test_env(affix.on_left, aff[1])
					return (aff, logic_and(right, left))
				else:
					return (aff, False)
			else:
				pass
		#end test_affix() definition

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

			if indx == len(alignment)-1 and switch:
				r_edge = ''
				answers.append(test_affix(create_affix(aff1)))
				answers.append(test_affix(create_affix(aff2)))
		return [x for x in answers if x != None]
	

################################################################################
# testing section
#a = [('a','_'),('b','b'),('c','c'),('_','o'),('r','r'),('t','t'),('a','_')]
#b = [('a','_'),('t','t'),('c','c'),('o','o'),('r','r'),('b','b'),('a','_')]
#c = [('a','_'),('b','b'),('a','e'),('c','c'),('_','o'),('r','r'),('t','t'),('a','_')]
#s = Affix_Learner()
#s.learn_affixes(a, features)
#s.learn_affixes(b, features)
#print s.verify_affixes(c, features)
