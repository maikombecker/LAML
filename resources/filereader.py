'''This file provides the functionality of reading data from various files
CHANGELOG:
Edit: 6/28
Added the ability to ignore blank and commented lines.
Comments must be introduced with a "#" symbol followed by a whitespace.

Edit: 7/12
Updated documentation for read_sample and read_features methods.
Changed the header variable from an integer counter to a boolean.

Edit: 7/13
Added method for reading in a 1-column input file and storing it as a list
of lists of strings.
'''
import re

###############################################################################
def read_score(f_name):
	'''Method returns the scores values taken from an input file.

	Argument:
	f_name ----> name of input file (string type, must have extension)
	'''
	matches_list = []
	with open(f_name) as file:
		for l in file:
			line = l.split()
			if line[0] != "#":
				matches_list.append((line[0], int(line[1])))
	return dict(matches_list)

###############################################################################
def read_sample(f_name):
	''' This method returns a list of pairs of words (as tuples)
	extracted from an input file.

	Arguments:
	f_name ---> name of input file (string type, must have extension)
	'''
	with open(f_name) as file:
		return [(line[0].split(), line[1].split()) for line in [line.split('\t') 
		for line in [line.rstrip('\n') for line in file] 
		if len(line) > 0 and re.match('#', line)==None]]

###############################################################################
def read_1_col_file(f_name):
	'''Method returns a list of lists of strings that represent words
	split up into phonemes.

	Argument:
	f_name ----> name of input file
	'''
	with open(f_name) as file:
		return [line.split() for line in file if len(line) > 0 
				and re.match('#', line)==None]

###############################################################################
def read_features(f_name):
	'''This method returns a dictionary where phonemes in their string
	representations are the keys, and lists of features are the values.

	Arguments:
	f_name ----> name of input file (string type, must have extension)
	N.B.
	Something must be said about how we store features in this method.
	Every list of features is just a list of integers ranging from 1 
	to 0 to -1. It is assumed that all the numbers in one column of
	the input file are the values of a certain feature for different
	phonemes. It is thus important, when creating the input file,
	to maintain the tabs between columns so that the right values are 
	stored in the list.

	'''
	feature_names = []
	feature_list = []
	header = True   #this variable is used to process the header specially
	with open(f_name) as file:
		for n in file:
			'''we split every line of the file...'''
			line = n.split()
			if len(line) != 0 and line[0] != '#':
				if header:
					'''We treat the header of the table
					in a special way: we just collect the
					feature names and store them in a list
					In the future, this may be used, but 
					currently the feature is just there.

					'''
					feature_names = [word for word in line]
					header = False   #now we are past header
				else:
					'''All lines starting with the second
					are processed the same way: we use the
					first member of the line as a key in a
					dictionary and place all of the features
					into a corresponding value.
		
					'''
					features = [int(line[i]) for i in 
						range(len(line)) if i != 0]
					'''we create a list for every phoneme,
					the first member is the phoneme string,
					the second is the list of features.

					'''
					phoneme = [line[0],features]
					'''we create a master list of phonemes'''
					feature_list.append(phoneme)
			else:
				continue
	'''We turn the master list into a dictionary.'''
	return dict(feature_list)				
#testing
#print read_features("features.txt")
