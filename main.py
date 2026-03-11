import scipy.io.wavfile as wavfile
import numpy as np
from granular import GranularSynthesiser, GrainProfile

def main(operation, files, duration, grainSize, sizeRandomness, density, densityRandomness,
        grainGainRandomness, noiseGain, numGrains, factor, plot):

    # Load sound files
    print("Loading audio files...")
    signals = []
    for audioFile in files:
        sample_rate, signal = wavfile.read(audioFile) # Asume all files have same sample rate
        # Make mono
        if len(signal.shape) > 1: signal = signal[:, 0]

        # Normalize the audio signals to be between -1.0 and 1.0
        signal = signal.astype(np.float64) / np.max(np.abs(signal))

        signals.append(signal)
    
    
    # Calculate duration in samples
    duration_samples = int(sample_rate * duration)
    grainSize = int(grainSize * sample_rate)
    sizeRandomness = int(sizeRandomness * sample_rate)
    densityRandomness = int(sample_rate // (density / densityRandomness))
    density = int(sample_rate // density)

    #Setup the Synthesizer
    synth = GranularSynthesiser(sample_rate)
    synth.setParameters(grainSize, sizeRandomness, density, 
                        densityRandomness, grainGainRandomness, noiseGain)


    # Process the Audio
    if operation == "extend":
        print("Extending sound")
        output = synth.extendSound(signals[0], duration_samples,
            numGrains=numGrains[0], plot=plot)

    elif operation == "blend":
        print("Blending sounds")
        output = synth.blendSounds(signals[0], signals[1], duration_samples,
            numGrainsA=numGrains[0], numGrainsB=numGrains[1], blendFactor=factor, plot=plot)


    elif operation == "morph":
        print("Morphing sounds")
        output = synth.morphSounds(signals[0], signals[1], duration_samples,
            numGrainsA=numGrains[0], numGrainsB=numGrains[1], morphFactor=factor, plot=plot)


    # Save the output
    print(f"Saving to {operation}ed_sound.wav")
    # Convert back to standard 16-bit audio format
    output_int = np.int16(output / np.max(np.abs(output)) * 32767)
    wavfile.write(f"{operation}ed_sound.wav", sample_rate, output_int)
    
    print(f"Done {operation}ing and saving audio")



import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-op", "--operation", default="morph", help="Opeation (extend, blend, morph)")
    parser.add_argument("-f", "--files", nargs='+', default=["soundA.wav", "soundB.wav"], help="Sound Source Files (e.g. main -f soundA.wav soundB.wav)")
    parser.add_argument("-dur", "--duration", type=float, default=3.0, help="Output Signal Duration (seconds)")
    parser.add_argument("-s", "--size", type=float, default=200.0, help="Grain Size (miliseconds)")
    parser.add_argument("-sr", "--sizeran", type=float, default=100.0, help="Grain Size Random Shift (miliseconds)")
    parser.add_argument("-d", "--dens", type=float, default=2.0, help="Grain Density (Hz)")
    parser.add_argument("-dr", "--densran", type=float, default=0.2, help="Grain Density Random Shift (Hz)")
    parser.add_argument("-gr", "--gainran", type=float, default=0.125, help="Grain Gain Random Shift")
    parser.add_argument("-ng", "--noisegain", type=float, default=0.5, help="Noise Gain")
    parser.add_argument("-n", "--grains", type=int, default=[3, 3], nargs='+', help="Number of Grains For Each Source (e.g. main -n 5 3)")
    parser.add_argument("-fc", "--factor", type=float, default=0.5, help="Blend / Morph Factor In Range [0.0, 1.0]")

    parser.add_argument("-p", '--plot', action='store_true', help="Generate Plots")

    args = parser.parse_args()

    # Validate input
    error = False
    if args.operation == "extend":
        if len(args.files) < 1:
            print("ERROR: 1 source file must be provided to extend operation")
            error = True
        if len(args.grains) < 1:
            print("ERROR: 1 number of grain must be provided to extend operation")
            Error = True
    if args.operation == "blend" or args.operation == "morph":
        if len(args.files) < 2:
            print("ERROR: 2 source file must be provided to blend and morph operations")
            error = True
        if len(args.grains) < 2:
            print("ERROR: 2 numbers of grains must be provided to blend and morph operations")
            error = True

    if error:
        print("Check main -h for help")
        exit()

    main(
        operation = args.operation,
        files = args.files,
        duration = args.duration,
        grainSize = args.size * 0.001,
        sizeRandomness = args.sizeran * 0.001,
        density = args.dens,
        densityRandomness = args.densran,
        grainGainRandomness = args.gainran,
        noiseGain = args.noisegain,
        numGrains = args.grains,
        factor = args.factor,
        plot = args.plot
    )