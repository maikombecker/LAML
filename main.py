'''
Edit 7/25
Most of the documentation for all files has been moved to README.txt
What remains here is the bare minimum.
'''

'''Edit 7/12
This file is something of a driver for our suffix-learning program. 
It doesn't define any objects of its own but instead imports and manipulates
classes and methods from all the other files.

Edit 8/3
Finally determined what algorithm to use for alignment, starting more intense
work on suffix acquisition. 
'''
###############################################################################
#import time	# this is in case we want to time our programme

from nwl import align
from morph import Affix_Learner
from resources.filereader import *
###############################################################################
'''This section is in case we want our program to run more interactively '''

#sample = raw_input("Please specify the name of the sample file. \
#Include the extension \n")
#data_txt = ''.join(['input/',data,'.txt'])
#test_txt = ''.join(['input/',test,'.txt'])

###############################################################################
'''This section opens/defines essential input/output variables. '''

#data = "allforms_nom_gen_sg.txt"
data = 'input/sample.txt' #we collect affixes from here 
test = 'input/test.txt' #we verify that the affixes here are grammatical 
features = read_features('resources/features.txt') #we provide feature lib 

data_align_list = [] 	 #list of alignments from learning data  
test_align_list = []	 #list of alignments from testing data

###############################################################################
'''We align all the words in our learning data. '''
print 'aligning...'
counter = 0
for pair in read_sample(data):
	try:
		data_align_list += [alignment[0] for alignment 
				in align(*pair,ft=features)]
		counter +=1
	except TypeError:
		'''If our alignment fails for any reason, skip that pair.'''
		continue
print 'Done aligning sample. Processed %d words' % counter

###############################################################################
'''We use an Affix Learner object to find all the affixes in the list of alignments. '''
print 'learing affixes...'
s = Affix_Learner()
for alignment in data_align_list:
	s.learn_affixes(alignment, features)
print 'Done learning affixes. Here they are: \n'
for affix in s.affixes.keys():
	p = s.affixes[affix]
	print affix, p.on_left, p.on_right, p.count, p.partner
	print 'Suffix: %s, Prefix: %s \n' % (p.suffix, p.prefix)

###############################################################################
'''We align all the words in the test data. '''
print 'aligning test data...'
for pair in read_sample(test):
	try:
		test_align_list += [alignment[0] for alignment 
				in align(*pair,ft=features)]
	except TypeError:
		'''If our alignment fails for any reason, skip that pair.'''
		continue
print 'Done aligning test data.'
print test_align_list

###############################################################################
#'''We check validity of affixes in test data.'''

results = []
for alignment in test_align_list:
	results += (alignment, s.verify_affixes(alignment, features))
for res in results:
	if res[0][1] == False:
		print res[0]
print 'Done checking affixes.'

###############################################################################
'''Here we add suffixes to a list of test suffixless words. '''

#for word in suffixless:
#	s.add_suffix(word)
