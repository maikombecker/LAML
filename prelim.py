'''
This file contains a mock up method for generalizing the features necessary for
a certain phonological rule to apply.
'''

from resources.features import FEATURES
def generalize(arg1, arg2, switch=None, ft=FEATURES):
	featlist = {}
	if switch == 'strings':
		for indx in range(26):
			try:
				if ft[arg1][indx] == ft[arg2][indx]:
					featlist[indx] = ft[arg1][indx]
			except IndexError:
				print "One of the phonemes was not found, please add it"
				break
	else:
		featlist = arg1
		for indx in featlist.keys():
			if ft[arg2][indx] != featlist[indx]:
				del featlist[indx]
	return featlist
gen = generalize('t','d', 'strings')
gen2 = generalize(gen,'g')
gen3 = generalize(gen,'a')
gen4 = generalize(gen,'b')
print gen4


