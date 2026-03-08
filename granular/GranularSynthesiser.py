import numpy as np
import random
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

from .GrainProfile import GrainProfile


class GranularSynthesiser:

    def setParameters(self, grainSize, sizeRandomness, density, densityRandomness, grainGainRandomness, noiseGain):
        self.grainSize = grainSize
        self.density = density
        self.noiseGain = noiseGain
        self.grainGain = 1.0 - grainGainRandomness

        self.sizeRandomness = sizeRandomness
        self.densityRandomness = densityRandomness
        self.grainGainRandomness = grainGainRandomness

        self.currentGrainSize = grainSize
        self.currentDensity = density
        self.currentGrainGain = self.grainGain


    def updateParameters(self):
        """
        Apply randomness factors to parameters.
        """
        if (self.sizeRandomness != 0):
            drift = np.random.randint(-(self.sizeRandomness // 2), self.sizeRandomness // 2, dtype=int)
        else:
            drift = 0
        self.currentGrainSize = self.grainSize + drift

        if (self.densityRandomness != 0):
            drift = np.random.randint(-(self.densityRandomness // 2), self.densityRandomness // 2, dtype=int)
        else:
            drift = 0

        self.currentDensity = self.density + drift

        if (self.grainGainRandomness != 0):
            drift = np.random.uniform(-(self.grainGainRandomness / 2), self.grainGainRandomness / 2)
        else:
            drift = 0

        self.currentGrainGain = self.grainGain + drift


    # ********************************** SERGIO **********************************
    def generateSignal(self, grainProfile, durationSamples, plot=False):

        # Apply noise
        output = grainProfile.generateNoise(durationSamples)

        # Add grains
        sampleIdx = 0

        if plot:
            # Plot noise
            plt.plot(output, color="0.5", alpha=0.7, label="Noise")
            plt.legend()

            # Allocate memory for plotting grains
            plotData = np.zeros_like(output)

        while(sampleIdx < durationSamples):

            self.updateParameters()

            # Get grain
            grain = grainProfile.getGrain(self.currentGrainSize)

            # Apply gain
            grain *= self.currentGrainGain

            # Write grain to output
            startIdx = sampleIdx
            endIdx = min(durationSamples-1, startIdx + grain.size) # Check grain fits in output and truncate if needed

            #print(f"DEBUG: startIdx: {startIdx}, endIdx: {endIdx}, grain.size: {grain.size} ")
            output[startIdx : endIdx] += grain[0 : endIdx - startIdx]

            # Step sample index
            sampleIdx += self.currentDensity

            if plot:
                # Plot grain
                plotData[startIdx : endIdx] += grain[0 : endIdx - startIdx]
                plt.plot(plotData)
                plotData[:] = 0.0


        return output


    # ********************************** SERGIO **********************************
    def extendSound(self, signalSource, durationSamples, numGrains, plot=False):

        # Extract grain profile
        grainProfile = self.extractGrain(signalSource, numGrains)

        if plot:
            plt.figure(figsize=(10, 6))
            plt.subplot(2, 1, 1)
            plt.plot(signalSource)
            plt.subplot(2, 1, 2)

        # Generate signal
        output = self.generateSignal(grainProfile, durationSamples, plot)

        if plot:
            plt.tight_layout()
            plt.show()

        return  output


    # ********************************** SERGIO **********************************
    def blendSounds(self, signalA, signalB, durationSamples, numGrainsA=2, numGrainsB=2, blendFactor=0.5, plot=False):

        # Extract grains
        grainProfileA = self.extractGrain(signalA, numGrainsA)
        grainProfileB = self.extractGrain(signalB, numGrainsB)

        # Blend grains
        blendProfile = grainProfileA.blend(grainProfileB, blendFactor)
        	
        if plot:
            plt.figure(figsize=(10, 6))
            plt.suptitle("Granular Synthesis Sound Blending")
            plt.subplot(3, 1, 1)
            plt.title("Source A")
            plt.xlabel("Time (samples)")
            plt.ylabel("Amplitude")
            plt.plot(signalA)
            plt.subplot(3, 1, 2)
            plt.title("Source B")
            plt.xlabel("Time (samples)")
            plt.ylabel("Amplitude")
            plt.plot(signalB)
            plt.subplot(3, 1, 3)
            plt.title("Blended Sound")
            plt.xlabel("Time (samples)")
            plt.ylabel("Amplitude")

        # Generate signal from blended profile
        output = self.generateSignal(blendProfile, durationSamples, plot)

        if plot:
            plt.tight_layout()
            plt.show()

        return output

    # ********************************** SERGIO **********************************
    def morphSounds(self, signalA, signalB, duration, numGrainsA, numGrainsB, morphFactor, plot=False):
        # Extract grains
        grainProfileA = self.extractGrain(signalA, numGrainsA)
        grainProfileB = self.extractGrain(signalB, numGrainsB)

        # Morph grains
        morphProfile = grainProfileA.morph(grainProfileB, morphFactor)

        if plot:
            plt.figure(figsize=(10, 6))
            plt.suptitle("Granular Synthesis Sound Morphing")
            plt.subplot(3, 1, 1)
            plt.title("Source A")
            plt.xlabel("Time (samples)")
            plt.ylabel("Amplitude")
            plt.plot(signalA)
            plt.subplot(3, 1, 2)
            plt.title("Source B")
            plt.xlabel("Time (samples)")
            plt.ylabel("Amplitude")
            plt.plot(signalB)
            plt.subplot(3, 1, 3)
            plt.title("Morphed Sound")
            plt.xlabel("Time (samples)")
            plt.ylabel("Amplitude")

		# Generate signal from morphed profile
        output = self.generateSignal(morphProfile, duration, plot)

        if plot:
            plt.tight_layout()
            plt.show()

        return output


    # ********************************** NIKLAS **********************************
    def extractGrain(self, signal, numGrains):
        # TODO
        # currently what's written is too 
        """
        Grain extraction:
            1. Extract noise using Spectral substraction.
            2. Grain extraction: Loudest parts of signal found from the smoothed envelope obtained with
            a moving average of the Hilbert transform of the signal.
        User specifies the number of grains to be extracted.
        Attenuate start and end of grains using an envelope (described in the paper)
        """
        grain_length = 2048 # A quick ~46ms snippet of audio
        grains = []
        
        # simple window to fade the grain in and out so it doesn't click
        window = np.hanning(grain_length)
        
        for _ in range(numGrains):
            if len(signal) > grain_length:
                # Pick a random starting point
                start = np.random.randint(0, len(signal) - grain_length)
                # Slice the audio and apply the fade
                grain = signal[start : start + grain_length] * window
                grains.append(grain)
            else:
                grains.append(signal * np.hanning(len(signal)))
        
        # Fake a flat noise spectrum (length 257 to match an N_fft of 512)
        fake_noise_spectra = np.ones(257)
        
        # Give every grain an equal chance of being played
        weights = [1.0 / numGrains] * numGrains
        
        return GrainProfile(fake_noise_spectra, grains, weights)
