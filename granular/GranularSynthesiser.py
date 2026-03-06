import numpy as np
import random

class GrainProfile:

	def __init__(self, noiseSpectra, grains, weights=None):
		"""
		
		grains: List of 1D np.arrays containing grains
		weights: Probability weights of choosing each grain
		"""
		self.noiseSpectra = noiseSpectra
		self.grains = grains
		if (weights == None):
			weights = [1.0 for _ in range(grains.size)]
		self.weights = weights

	def getGrain(self, size):
		"""
		Returns random grain.
		"""
		grain = random.choice(self.grains, weights=self.weights, k=1)
		endSample = min(size - 1, grain.size - 1)
		return grain[:endSample]

	# ********************************** NIKLAS **********************************
	def generateNoise(self, durationSamples):
		"""
		Shape white noise to match previously substracted noise using multiplication of the spectra in
		the frequency domain.
		"""
		# TODO
		output = np.zeros(durationSamples)

		return output

	# ********************************** RAHUL **********************************
	def blend(self, grainProfile, weightBias):
		
		# Append grains
		grains = self.grains.append(grainProfile.grains)

		# Calculate weights
		# Target probability mass for each list of grains
		target1 = 1 - weightBias
		target2 = bias

		sum1 = sum(self.weights)
		sum2 = sum(grainProfile.weights)

		# Scale weights
		scaled1 = [w * target1 / sum1 for w in self.weights] if sum1 > 0 else []
		scaled2 = [w * target2 / sum2 for w in grainProfile.weights] if sum2 > 0 else []

		weights = scaled1.append(scaled2)

		# Average noises
		# TODO

		return GrainProfile(noise, grains, weights)

	# ********************************** RAHUL **********************************
	def morph(self, grainProfile, morphFactor)
		# Morph grains
		# TODO

		# Average noises
		# TODO

		return GrainProfile()


class GranularSynthesiser:

	def setParameters(self, grainSize, sizeRandomness, density, densityRandomness, gainRandomness, noiseGain):
		"""
		Apply randomness factors to parameters.
		"""
		self.grainSize = grainSize
		self.density = density
		self.noiseGain = noiseGain

		self.sizeRandomness = sizeRandomness
		self.densityRandomness = densityRandomness
		self.gainRandomness = gainRandomness

		self.currentGrainSize = grainSize
		self.currentDensity = density
		self.currentGain = gain


	def updateParameters(self):
		if (self.sizeRandomness != 0):
				drift = np.random.randint(-(self.sizeRandomness / 2), self.sizeRandomness / 2, dtype=int)
			else:
				drift = 0

			self.currentGrainSize = self.grainSize + drift

			if (self.densityRandomness != 0):
				drift = np.random.randint(-(self.densityRandomness / 2), self.densityRandomness / 2, dtype=int)
			else:
				drift = 0

			self.currentDensity = self.density + drift

			if (self.gainRandomness != 0):
				drift = np.random.uniform(-(self.gainRandomness / 2), self.gainRandomness / 2, dtype=int)
			else:
				drift = 0

			self.currentGain = self.gain + drift


	# ********************************** SERGIO **********************************
	def generateSignal(self, grainProfile, durationSamples):

		# Apply noise
		output = grainProfile.generateNoise(durationSamples)

		# Add grains
		sampleIdx = 0

		while(sampleIdx < durationSamples):

			self.updateParameters()

			# Get grain
			grain = grainProfile.getGrain(self.currentSize)

			# Apply gain
			grain *= self.currentGain

			# Write grain to output
			startIdx = sampleIdx
			endIdx = min(durationSamples-1, startIdx + grain.size) # Check grain fits in output and truncate if needed
			output[startIdx : endIdx] += grain[0 : endIdx - startIdx]

			# Step sample index
			sampleIdx += self.currentDensity

		return output


	# ********************************** SERGIO **********************************
	def extendSignal(self, signalSource, numGrains, durationSamples):

		# Extract grain profile
		grainProfile = self.extractGrain(signalSource, numGrains)

		# Generate signal
		return self.generateSignal(grainProfile, durationSamples)


	# ********************************** SERGIO **********************************
	def blendSounds(self, signalA, signalB, durationSamples, numGrainsA=2, numGrainsB=2, weight=0.5):

		# Extract grains
		grainProfileA = self.extractGrain(signalA, numGrainsA)
		grainProfileB = self.extractGrain(signalB, numGrainsB)

		# Blend grains
		blendProfile = grainProfileA.blend(grainProfileB, weight)

		# Generate signal from blended profile
		return self.generateSignal(blendProfile)


	# ********************************** SERGIO **********************************
	def morphSound(self, signalA, signalB, duration, morphFactor):
		# Extract grains
		grainProfileA = self.extractGrain(signalA, numGrainsA)
		grainProfileB = self.extractGrain(signalB, numGrainsB)

		# Morph grains
		morphProfile = grainProfileA.morph(grainProfileB, morphFactor)

		# Generate signal from morphed profile
		return self.generateSignal(morphProfile)


	# ********************************** NIKLAS **********************************
	def extractGrain(self, signal, numGrains):
		# TODO
		"""
		Grain extraction:
			1. Extract noise using Spectral substraction.
			2. Grain extraction: Loudest parts of signal found from the smoothed envelope obtained with
			a moving average of the Hilbert transform of the signal.
		User specifies the number of grains to be extracted.
		Attenuate start and end of grains using an envelope (described in the paper)
		"""
		grains = [np.zeros(10) for _ in range(3)] # List of grains
		return GrainProfile(None, grains)
