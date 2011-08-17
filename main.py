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

from nwl import align, unknown_chars

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
data = 'input/sample.txt'
test = 'input/test.txt'
suffixless = read_1_col_file('input/suffixless.txt')
features = read_features('resources/features.txt')

data_align_list = []
test_align_list = []	

###############################################################################
'''We align all the words in our test data. '''

for pair in read_sample(data):
#	print pair
	try:
		data_align_list += [alignment[0] for alignment 
				in align(*pair,ft=features)]
	except TypeError:
		'''If our alignment fails for any reason, skip that pair.'''
		continue

###############################################################################
'''We use an Affix Learner object to find all the affixes in the list of alignments. '''

s = Affix_Learner()
for alignment in data_align_list:
	s.find_affixes(alignment, features)
#for affix in s.affixes:
#	print affix, s.affixes[affix][1]
#	print s.affixes[affix][0].on_left
#	print s.affixes[affix][0].on_right


###############################################################################
'''We align all the words in the test corpus. '''

for pair in read_sample(test):
	try:
		test_align_list += [alignment[0] for alignment 
				in align(*pair,ft=features)]
	except TypeError:
		'''If our alignment fails for any reason, skip that pair.'''
		continue

###############################################################################
'''We check validity of affixes in test data.'''

results = []
for alignment in test_align_list:
	results += (alignment, s.test_find_affixes(alignment, features))
print results

###############################################################################
'''Here we add suffixes to a list of test suffixless words. '''

#for word in suffixless:
#	s.add_suffix(word)
