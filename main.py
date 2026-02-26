import argparse
from granular import GrainAssembler, GrainGenerator


def main(density, densityRandomness):

	# TODO: I'm just testing now
	sampleRate = 44100
	grainGenerator = GrainGenerator()
	grainAssembler = GrainAssembler(density, densityRandomness, grainGenerator, sampleRate)

	duration = 5 # Seconds
	output = grainAssembler.generateSignal(duration)


	# TEST
	print(output.shape)
	# Plot (Maybe should be in a different file)
	import matplotlib.pyplot as plt
	plt.figure(figsize=(6,4))
	plt.subplot(2,1,1)
	plt.plot(output[0,:])
	plt.subplot(2,1,2)
	plt.plot(output[1,:])
	plt.show()



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dens", type=float, default=2.0, help="Grain Density (Hz)")
	parser.add_argument("-dr", "--densran", type=float, default=0.2, help="Grain Density Random shift (Hz)")
	# TODO: Program arguments

	args = parser.parse_args()
	main(
		density = args.dens,
		densityRandomness = args.densran
	)