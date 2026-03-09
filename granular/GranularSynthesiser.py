import numpy as np
import random
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy.signal import hilbert

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
    def extractGrain(self, signal, numGrains, debug=False):
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
        # FRAMES
        N_fft = 1024    # frame
        hop = 32    # frame increment
        win = np.hamming(N_fft)

        # Pad signal so an integer number of frames fits
        if len(signal) < N_fft:
            padded = np.pad(signal, (0, N_fft - len(signal)))
        else:
            # Make (len(padded) - N_fft) divisible by hop
            pad_len = (hop - (len(signal) - N_fft) % hop) % hop
            padded = np.pad(signal, (0, pad_len))

        n_frames = 1 + (len(padded) - N_fft) // hop

        # For each frame store complex FFT and magnitude spectrum
        mags = []
        spectra = []

        for i in range(n_frames):
            start = i * hop
            frame = padded[start:start + N_fft] * win
            X = np.fft.rfft(frame)
            spectra.append(X)
            mags.append(np.abs(X))

        mags = np.array(mags)
        spectra = np.array(spectra)


        # GAUSSIAN SMOOTHING
        n = np.arange(34)   # indices 0-33
        b, c = 16, 3.0  # center and width of the Gaussian
        h = np.exp(-(n - b) ** 2 / (2 * c**2))
        h /= np.sum(h)  # normalize so sum(h) = 1

        # Convolve every magnitude spectrum with the Gaussian FIR in frequency
        mags_smooth = np.array([np.convolve(m, h, mode="same") for m in mags])

        
        # NOISE SPECTRUM ESTIMATION
        energies = np.sum(mags_smooth**2, axis=1)
        k = max(1, int(0.15 * n_frames))    # 15% of frames, at least 1
        quiet_idx = np.argsort(energies)[:k]    # quietest frames

        # Average of the smoothed spectra of the quiet frames
        noiseSpectra = np.mean(mags_smooth[quiet_idx, :], axis=0)


        # NOISE SUBTRACTION
        eps = 1e-12 # Avoid division by zero

        Sa_prime = np.maximum(mags_smooth - noiseSpectra[None, :], 0.0)

        # Reconstruct complex spectra with reduced amplitude
        Sc_half = []
        for m in range(n_frames):
            X = spectra[m]  # original complex spectrum
            mag = np.abs(X) + eps   # original amplitude
            target_mag = Sa_prime[m]    # reduced amplitude

            # Replace magnitude but keep phase
            Xc = (X / mag) * target_mag
            Sc_half.append(Xc)

        Sc_half = np.array(Sc_half)

        # Mirror to get full spectrum, then IFFT and overlap-add
        sc_padded = np.zeros_like(padded, dtype=float)

        for m in range(n_frames):
            X_half = Sc_half[m]
            # Build full spectrum:
            X_conj = np.conj(X_half[1:-1][::-1])
            X_full = np.concatenate((X_half, X_conj))

            frame_time = np.fft.ifft(X_full).real   # inverse FFT
            start = m * hop
            sc_padded[start:start + N_fft] += frame_time * win  # overlap-add

        # Trim back to original signal length
        sc = sc_padded[:len(signal)]


        # HILBERT ENVELOPE AND SMOOTHING
        analytic = hilbert(sc)
        g_prime = np.abs(analytic)

        # Smoothed envelope g[t] with moving average of length 100
        win_env = np.ones(100) / 100.0
        g = np.convolve(g_prime, win_env, mode="same")


        # GRAIN EXTRACTION FROM LOUDEST PARTS
        grains = []
        env = g.copy()

        # Window extents around the envelope peak tau
        # w_s and w_e assumed to be 2048 samples
        w_s = 2048
        w_e = 2048

        for _ in range(numGrains):
            # Stop if there's no non-zeros
            if np.all(env <= 0):
                break

            # tau is index of global maximum of current envelope
            tau = int(np.argmax(env))
            if env[tau] <= 0:
                break

            # Find t_s
            start_s = max(0, tau - w_s)
            if tau > start_s:
                ts = start_s + np.argmin(env[start_s:tau])
            else:
                ts = tau

            # Find t_e
            end_e = min(len(env) - 1, tau + w_e)
            if end_e > tau:
                te = tau + 1 + np.argmin(env[tau + 1:end_e + 1])
            else:
                te = tau

            # Sanity check
            if te <= ts:
                break

            # Extract grain from signal
            grain = sc[ts:te + 1].copy()
            length = len(grain)


            # APPLY ENVELOPE
            t = np.arange(length)
            t_abs = ts + t  # Absolute sample positions
            a = np.ones_like(grain)

            # Left side: t_s <= t < tau
            if tau > ts:
                mask_l = t_abs < tau
                t_l = t_abs[mask_l] - ts
                a[mask_l] = np.power(t_l / (tau - ts), 0.25)

            # Right side: tau <= t <= t_e
            if te > tau:
                mask_r = t_abs >= tau
                t_r = t_abs[mask_r] - tau
                a[mask_r] = np.power(1.0 - t_r / (te - tau), 0.25)

            grain *= a
            grains.append(grain)

            # Delete the extracted part from s_c and the envelope so the next iteration finds the next loudest part
            sc[ts:te + 1] = 0.0
            env[ts:te + 1] = 0.0

        # If something goes wrong and no grains were found, use the whole signal as a single grain
        if not grains:
            grains = [sc]

        # Equal probability for each grain when synthesizing later
        weights = [1.0 / len(grains)] * len(grains)

        if debug:
            # Palauta myös denoised signal sc ja smoothed envelope g
            return GrainProfile(noiseSpectra, grains, weights), sc, g
        else:
            return GrainProfile(noiseSpectra, grains, weights)