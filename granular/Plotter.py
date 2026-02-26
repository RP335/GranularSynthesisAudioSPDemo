import matplotlib.pyplot as plt
import numpy as np
from .GrainGenerator import GrainGenerator


class Plotter:

	def plotAssemblerResponse(grainAssembler, duration=3, numChannels=2):

		# Generate impulse
		impulseLength = 2
		impulse = np.zeros(impulseLength)
		impulse[0] = 1

		# Create grain generator with impulses
		impulseGrainGenerator = GrainGenerator(
			sample=impulse,
			startPosition=0,
			startRandomness=0,
			grainSize=impulseLength,
			sizeRandomness=0,
			window=0
		)

		# Keep current assembler's grain generator
		storedGrainGenerator = grainAssembler.grainGenerator

		# Temporary replace assembler's grain generator
		grainAssembler.grainGenerator = impulseGrainGenerator

		# Generate response
		response = grainAssembler.generateSignal(duration, numChannels)

		# Plot		
		plt.figure(figsize=(6,4))
		plt.suptitle("Granular Synthesiser Impulse Response")
		timeAxis = np.arange(response.shape[1]) / grainAssembler.sampleRate

		# Plot each channel
		for channelIdx in range(numChannels):
			plt.subplot(numChannels,1,channelIdx+1)
			plt.plot(timeAxis, response[channelIdx,:])
			plt.title(f"Channel {channelIdx}")
			plt.xlabel("Time (seconds)")
			plt.ylabel("Amplitude")

		plt.tight_layout()
		plt.show()