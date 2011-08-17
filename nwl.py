print 'this is a version of the nwl alignment algorithm that uses features, \
instead of penalties/rewards to create the matrix. This, ideally, should be \
the way of the future, because (again, ideally) it will provide a way to \
fine-tune the alignment principles a little bit more.  This version of \
the module has been modified from the traditional in two ways: \
- it is more lax about what is considered a match (2 feature differences are \
acceptable) \
- it automatically assigns the value of the cell diagonally up and left of \
a given one provided \n'

###############################################################################
from numpy import zeros 
from resources.features import *
###############################################################################

###############################################################################
unknown_chars = []	# list for collecting unprocessed phonemes

###############################################################################
def compare_features(s1, s2, ft=FEATURES):
	'''this method returns a float score for a given pair of segments.

	arguments:
	s1 -----> the first input string
	s2 -----> the second input string
	ft -----> the features database
	n.b.
	s1 and s2 can be passed as a tuple, the usual python way.
	by default, ft is set to the in-built features database 
	located in this file below the definitions of scores for 
	different types of matches. 
	it must also be noted that at this time we are using a library
	of 26 features/phoneme, so he maximum score will always be
	multiple of 26 and whatever we decide to set as the reward for
	a perfect matchup for a given feature (in this case it is 1).

	'''
	score = 0
	for indx in range(26):
		try:
			if ft[s1][indx] != ft[s2][indx]:
				score += 1
		except IndexError:
#			print s1, s2
			score = None
#	print score, s1, s2
	return score
	

###############################################################################
def build_matrix(s1, s2, ft=FEATURES):
	''' this method returns a matrix or, in other words, a 2d array. Each
	cell of this matrix receives a value based on 
	a) the comparison of the corresponding substrings of the input strings
	b) the values of the cells left and above(diagonally), left, and above.
	the way this matrix is filled should facilitate traceback later on.
	
	arguments:
	s1 -----> the first word for our comparison
	s2 -----> the second word for our comparison
	ft -----> the features database
	n.b. 
	as one will notice, the arguments to this function are very similar to 
	those of the compare_features() method. The only difference is that here
	the strings are actually whole words, as opposed to substrings/phonemes
	in the case of the compare_features() method. 
	
	'''
	mat_rows = len(s1)
	mat_cols = len(s2)
	
	'''the below statements attempt to create a numpy n-dimensional array.
	these arrays are considered faster than regular 2-d python lists. They
	also contain some useful functionality like the .shape attribute, used
	later on in the program. 
	if for some reason, the numpy module was not imported successfully and
	the array fails to initialize this way, we simply create a regular
	2-d list using a list comprehension expression.
	this whole routine was borrowed from the code found at snippets.com
	(see acknowledgements), I'm not sure yet whether it is worthwhile
	to keep it.

	'''
	try:
        	mat = zeros((mat_rows, mat_cols))
    	except importError:
        	mat = [[0]*mat_cols for i in range(mat_rows)]

    	for row in range(mat_rows):
        	for col in range(mat_cols):
			up = mat[row-1][col]
			left = mat[row][col-1]
			diag = mat[row-1][col-1] 
			'''Find the score for comparing two segments'''
			if row == 0 and col == 0:
				pass
			elif s1[row] == '_':
				mat[row][col] = left - 26
			elif s2[col] == '_':
				mat[row][col] = up - 26
			else:
				try:
					score = compare_features(s1[row],
								 s2[col], ft)
				except KeyError, e:
					'''If a given segment is not found in
					our dictionary of features, we add the
					culprit character to the Skipped class's
					character list, then return nothing.
					'''
					unknown_chars.append(e)
					return None
				if score == None:
					print "please revise your input or define additional phonemes"
					break
				else:				
					if score <= 2:
						mat[row][col] = diag - score
					else:
						mat[row][col] = max(left-score, up-score)
    	return mat

###############################################################################
def find_further_steps(x,y,mat):
	'''this method returns a list of tuples that represent the coordinates
	of the cells that can be possible traceback steps from the current
	cell (designated by the variables x and y). 
	
	arguments:
	x ----> integer value for row
	y ----> integer value for column
	mat --> the matrix created in the previous method
	n.b. 
	we start this method by creating our output list and, for readability,
	some variables to store the values of the cells diagonally up and left,
	up, and left of our target cell.
	we then deal with the cases when our target cell is on the top
	or left border of the matrix, in which case there is only one possible
	continuation.
	if the target cell is somewhere in the middle of the matrix, though,
	we need to consider the following cases:
	- case a: the diagonal value is the greatest. If this is so, we add the
	coordinates of the diagonal cell (as a tuple) to our output list.
	- case b: the left value is the greatest. In this case, we need to add the
	coordinates of the cell on the left to our output list.
	- case c: the value above target is greatest. The actions are the same
	for this case as for all others except the coordinates being added are 
	those of the cell above the target.

	'''
	steps = []	# this will be our output
	diag = mat[x-1][y-1]
	up = mat[x-1][y]
	left = mat[x][y-1]
	if x == 0:	# this is if we are at the top end of the matrix
		steps.append((x,y-1))
	elif y == 0:	# this is if we are at the left end of it
		steps.append((x-1,y))
	else:
		if diag == max(diag, up, left):	# case A
			steps.append((x-1,y-1))
		if left == max(diag, up, left):	# case B
			steps.append((x,y-1))
		if up == max(diag, up, left):	# case C
			steps.append((x-1,y))
	return steps

###############################################################################
def full_traceback(mat,paths,starter,row,col,pth=[]):
	'''This method is a bit peculiar in the sense that it doesn't return 
	anything. Instead it, recursively, modifies one of the input variables, 
	paths, adding new possible alignments as lists of sequences of cells
	(denoted by their coordinates as tuples). The job of returning this list
	is left up to the higher level method, find_all_aligns()
	
	Arguments:
	mat ------> our indispensible matrix
	paths ----> the list of all possible paths
	starter --> the coordinates of the starting point, given as a tuple
	row ------> integer row coordinate of a given point
	col ------> integer column coordinate of a given point
	pth ------> list that represents a specific path, by default left empty

	'''
	pth.append((row,col))
	global PATH	# we need to have an instance-independent variable
	PATH = pth	
	possible_solutions = find_further_steps(row,col,mat)
	for member in possible_solutions:
		if member == (0,0):
			pth.append(member)
			paths.append(pth)
			PATH = pth[:pth.index(starter)]
		else:
			if len(possible_solutions) > 1:	
				#this is the case of branching
				full_traceback(mat,paths,member,*member,pth=PATH)
			else:
				full_traceback(mat,paths,starter,*member,pth=PATH)

###############################################################################
def find_all_aligns(mat,start):
	'''This is the master method for finding all the possible alignments,
	given a matrix and a starting point. It creates a list, adds alignments
	to it with the full_traceback method and returns the list.
	
	Arguments:
	- mat -----> the Matrix!
	- start ---> a starting point, represented by a tuple of its coordinates

	'''
	paths = []
	full_traceback(mat,paths,start,*start,pth=[])
	return paths

###############################################################################
def create_strings(str1,str2,mat,paths):
	"""this method converts our sequences of cell coordinates to sequences
	of pairs of strings, representing the final product of the alignment
	process.

	arguments:
	str1 ---> our first input word
	str2 ---> our second input word
	mat ----> the matrix
	paths --> a list of all the possible alignments for the given strings

	"""
#------------------------------------------------------------------------------
	def calc_align_score(alignment, mat):
		'''This method calculates the overall score for a given alignment.
		this is later used to compare alignment scores to find the optimal one.

		arguments:
		alignment --> a sequence of tuples represents one possible alignment
		mat --------> the ever-present matrix
		
		'''
		return sum([mat[point[0]][point[1]] for point in alignment])

#------------------------------------------------------------------------------
	def path_score(paths,mat):
		'''A method for converting a list of possible alignments
		into a list of said alignments paired with their corresponding scores
		as tuples.

		arguments:
		paths ----> a list of lists of tuples, the list of possible paths
		mat ----> the matrix, used to calculate the overall score for
		a given alignment/path

		'''
		return [(calc_align_score(path,mat), path) for path in paths]

#------------------------------------------------------------------------------
	def direction(point1,point2):
		'''Method for returning the difference between the
		coordinates of two cells. This method was defined because I know
		of no in-built way to subtract one tuple from another. I use this method
		to figure out what direction a given path is going in in the matrix.
		this, in turn is used to determine how to align strings based on a 
		sequence of coordinates.
		
		arguments:
		point1 --> a tuple of coordinates for the first point
		point2 --> a tuple of coordinates for the second point

		'''
		return (point1[0]-point2[0], point1[1]-point2[1])

#------------------------------------------------------------------------------
	
	align_scores = path_score(paths,mat)
	pairs_list = []
	for score in range(len(align_scores)):
		diagonal = (1,1)
		up = (1,0)
		left = (0,1)
		alignment = []
		seq = align_scores[score][1]
		for indx in range(len(seq)):
			if indx+1 in range(len(seq)):
				if direction(seq[indx],seq[indx+1]) == diagonal:
#					print 'diagonal'
					alignment.insert(0,(str1[seq[indx][0]],
							 str2[seq[indx][1]]))
				elif direction(seq[indx],seq[indx+1]) == up:
#					print 'up'
					alignment.insert(0,(str1[seq[indx][0]],
								 '_'))
				elif direction(seq[indx],seq[indx+1]) == left:
#					print 'left'
					alignment.insert(0,('_',
							 str2[seq[indx][1]]))
			else:
				break
		pairs_list += [(alignment,align_scores[score][0])]
	return pairs_list

###############################################################################
def align(str1,str2,ft=FEATURES):
	'''this method returns all the possible alignments for a given pair of
	strings. These alignments are presented as lists of pairs of segments.
	
	arguments:
	str1 --> the first input string
	str2 --> the second input string
	ft ----> the library of features, by default set to the one defined in
	this file
	
	'''
	str1.insert(0,'_') 
	str2.insert(0, '_')
	matrix = build_matrix(str1,str2,ft)
#	print matrix
	if matrix == None:
		return
	else:
		starting_cell = (matrix.shape[0]-1,matrix.shape[1]-1)
		all_aligns = find_all_aligns(matrix,starting_cell)
#		print create_strings(str1,str2,matrix,all_aligns)
#		print '#'*70, '\n'
		return create_strings(str1,str2,matrix,all_aligns)
