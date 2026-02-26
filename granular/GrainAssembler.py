import numpy as np
from .GrainGenerator import GrainGenerator

class GrainAssembler:
	"""
	Assembles grains into a continuous audio signal for granular synthesis.

	This class generates multi-channel audio by placing grains produced by
	a `GrainGenerator` at intervals defined by a base density and optional randomness.

	Attributes
	----------
	sampleRate : int
		The sample rate of the output signal in Hz.
	density : int
		The nominal number of samples between consecutive grains.
	densityRandomness : int
		The maximum random variation in samples added to `density` for grain placement.
	grainGenerator : GrainGenerator
		An instance of a `GrainGenerator` used to produce individual grains.
	"""

	def __init__(self, density, densityRandomness, grainGenerator, sampleRate):
		"""
		Parameters
		----------
		density : float
			Grain density in Hz, i.e., how many grains per second.
		densityRandomness : float
			Maximum randomness in grain placement density in Hz.
		grainGenerator : GrainGenerator
			A grain generator object responsible for producing individual grains.
		sampleRate : int
			Sample rate in Hz for the output signal.
		"""
		self.sampleRate = sampleRate
		self.density = int( 1 / density * sampleRate) # Convert Hz to samples
		self.densityRandomness = int(densityRandomness * sampleRate) # Convert Hz to samples
		self.grainGenerator = grainGenerator


	def generateSignal(self, duration, numChannels=2):
		"""
		Generate a multi-channel audio signal composed of grains.

		Grains are placed sequentially in time, with optional randomness applied
		to the spacing between grains. Each channel is generated independently,
		leading to different signals in each channel.

		Parameters
		----------
		duration : float
			Length of the output signal in seconds.
		numChannels : int, optional
			Number of output channels. Default is 2 (stereo).

		Returns
		-------
		np.ndarray
			A 2D NumPy array of shape `(numChannels, signalLength)` containing
			the generated audio signal. Each row corresponds to one channel.

		Notes
		-----
		- Grain placement can include randomness if `densityRandomness` is non-zero.
		- If a grain would extend beyond the signal length, it is truncated.
		"""
		signalLength = duration * self.sampleRate

		# Allocate output
		output = np.zeros((numChannels, signalLength))

		# Generate signal
		for channelIdx in range(numChannels):
			
			sampleIdx = 0

			# Fill one channel at a time (different signal in each channel)
			while(sampleIdx < signalLength):

				# Get grain
				grain = self.grainGenerator.generateGrain()

				# Write grain to output
				startIdx = sampleIdx
				endIdx = min(signalLength-1, startIdx + grain.size) # Check grain fits in output and truncate if needed
				output[channelIdx, startIdx : endIdx] += grain[0 : endIdx - startIdx]

				# Add randomness to density
				if (self.densityRandomness != 0):
					drift = np.random.randint(-(self.densityRandomness / 2), self.densityRandomness / 2, dtype=int)
				else:
					drift = 0

				currentDensity = self.density + drift

				# Step sample index
				sampleIdx += currentDensity

		return output