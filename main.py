import argparse
from granular import GrainAssembler, GrainGenerator, Plotter
import numpy as np


def main(density, densityRandomness, numChannels):

	# TODO: I'm just testing now
	sampleRate = 44100

	sample = 0.1 * np.random.randn(sampleRate * 2)
	grainGenerator = GrainGenerator(
		sample=sample,
		startPosition=0,
		startRandomness=0,
		grainSize=0,
		sizeRandomness=0,
		window=0
	)
	grainAssembler = GrainAssembler(density, densityRandomness, grainGenerator, sampleRate)

	duration = 5 # Seconds
	output = grainAssembler.generateSignal(duration, numChannels)

	Plotter.plotAssemblerResponse(grainAssembler, duration, numChannels)




if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dens", type=float, default=2.0, help="Grain Density (Hz)")
	parser.add_argument("-dr", "--densran", type=float, default=0.2, help="Grain Density Random shift (Hz)")
	parser.add_argument("-c", "--channels", type=int, default=2, help="Number of channels")
	# TODO: Program arguments

	args = parser.parse_args()
	main(
		density = args.dens,
		densityRandomness = args.densran,
		numChannels = args.channels
	)