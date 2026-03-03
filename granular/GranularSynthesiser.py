import numpy as np

class GrainProfile:

	def __init__(self, noise, grains):
		self.noise = noise
		self.grains = grains

	def getGrain(self, size):
		grain = self.grains[np.random.randint(0, len(grains) - 1)]
		endSample = min(size, grain.size)
		return grain[:endSample]


class GranularSynthesiser:

	def setParameters(self, grainSize, sizeRandomness, density, densityRandomness, gainRandomness, noiseGain):
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


	def generateSignal(self, signalSource, numGrains, durationSamples):
		grainProfile = self._extractGrain(signalSource, numGrains)
		output = np.zeros(durationSamples)

		# Apply noise
		# TODO

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



	def blendSounds(self, signalA, signalB, durationSamples, numGrainsA=2, numGrainsB=2, weight=0.5, blockSize=64, overlap=32):
		output = np.zeros(durationSamples)

		# Extract grains
		grainProfileA = self._extractGrain(signalA, numGrainsA)
		grainProfileB = self._extractGrain(signalB, numGrainsB)

		# Average noises
		# TODO

		# Apply noise
		# TODO

		# Add grains
		sampleIdx = 0

		while(sampleIdx < durationSamples):

			self.updateParameters()

			# Get grain
			if np.random.random() < weight:
				grain = grainProfileA.getGrain(self.currentSize)
			else:
				grain = grainProfileB.getGrain(self.currentSize)

			# Apply gain
			grain *= self.currentGain

			# Write grain to output
			startIdx = sampleIdx
			endIdx = min(durationSamples-1, startIdx + grain.size) # Check grain fits in output and truncate if needed
			output[startIdx : endIdx] += grain[0 : endIdx - startIdx]

			# Step sample index
			sampleIdx += self.currentDensity

		return output


	def morphSound(self, signalA, signalB, duration, morphFactor):
		# TODO
		pass


	def _extractGrain(self, signal, numGrains):
		# TODO
		return GrainProfile(None, [np.zeros(10) for _ in range(3)])
