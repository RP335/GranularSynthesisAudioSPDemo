import matplotlib.pyplot as plt
import numpy as np
from .GrainGenerator import GrainGenerator


class Plotter:
	"""
	Helper class for plotting granular synthesis signals and responses.

	This class provides static plotting utilities for visualizing signals
	produced by `GrainAssembler` and `GrainGenerator` objects, such as impulse responses.
	"""

	@staticmethod
	def plotAssemblerResponse(grainAssembler, duration=3, numChannels=2):
		"""
		Plot the impulse response of a `GrainAssembler`.

		This method temporarily replaces the assembler's grain generator
		with an impulse grain generator, generates the response signal,
		and plots each channel over time in seconds.

		Parameters
		----------
		grainAssembler : GrainAssembler
			The granular synthesizer object whose impulse response will be plotted.
		duration : float, optional
			Duration of the generated response signal in seconds. Default is 3 seconds.
		numChannels : int, optional
			Number of channels to generate and plot. Default is 2 (stereo).

		Returns
		-------
		None
			This function only produces a plot and does not return any data.

		Notes
		-----
		- The method temporarily replaces the `grainGenerator` of the assembler
		with an impulse-based generator and restores the original generator afterward.
		- The x-axis is in seconds, computed using the assembler's `sampleRate`.
		- Each channel is plotted in a separate subplot for clarity.
		"""
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

		# Replace back the original grain generator
		grainAssembler.grainGenerator = storedGrainGenerator

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