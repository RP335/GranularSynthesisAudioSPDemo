import numpy as np

class GrainGenerator:

	#def __init__(self, ...):


	def generateGrain(self):

		# TODO
		# Dummmy implementation (impulse)
		output = np.zeros(10)
		output[0] = 1

		assert(output.ndim ==1 ) # Grain must be mono
		return output