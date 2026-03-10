import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class Plotter:

    def plotExtend(signalSource, numGrains, durationSamples, synth):

        # Extract grain profile
        grainProfile, denoisedSignal, g = synth.extractGrain(signalSource, numGrains, debug=True)

        plt.figure(figsize=(12, 6))

        # Plot grain extraction Spectrograms
        # Original Signal
        plt.subplot(3, 1, 1)
        f, t, Sxx = signal.spectrogram(signalSource, fs=synth.sampleRate)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.title("Input Signal Spectrogram")
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (sec)')
        plt.colorbar(label='Power (dB)')

        # Extracted Noise Frequency Magnitude Spectrum
        noiseSignal = grainProfile.generateNoise(durationSamples)
        plt.subplot(3, 1, 2)
        # Compute FFT and normalize
        # Spectrum (Welch)
        freq, mag = signal.welch(noiseSignal, fs=synth.sampleRate, nperseg=4096)
        plt.semilogx(freq, 10 * np.log10(mag + 1e-12))
        plt.title("Extracted Noise Magnitude Spectrum")
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')

        # Denoised Signal
        plt.subplot(3, 1, 3)
        f, t, Sxx = signal.spectrogram(denoisedSignal, fs=synth.sampleRate)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.title("Denoised Signal Spectrogram")
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (sec)')
        plt.colorbar(label='Power (dB)')

        # Show
        plt.tight_layout()
        plt.show()


    def plotBlend(signalA, signalB, durationSamples, numGrainsA, numGrainsB, synth):
        pass

    def plotMorph(signalA, signalB, durationSamples, numGrainsA, numGrainsB, synth):
        pass