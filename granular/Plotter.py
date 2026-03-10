import numpy as np
from scipy import signal

import matplotlib.pyplot as plt

class Plotter:

    def plotExtraction(signalSource, numGrains, durationSamples, synth, title):

        # Extract grain profile
        grainProfile, denoisedSignal, smoothedEnvelope, startTimes = synth.extractGrain(signalSource, numGrains, debug=True)

        plt.figure(figsize=(12, 6))
        plt.suptitle(title)

        # Plot grain extraction Spectrograms
        # Original Signal
        plt.subplot(2, 2, 1)
        f, t, Sxx = signal.spectrogram(signalSource, fs=synth.sampleRate)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.title("Input Signal Spectrogram")
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (sec)')
        plt.colorbar(label='Power (dB)')

        # Denoised Signal
        plt.subplot(2, 2, 3)
        f, t, Sxx = signal.spectrogram(denoisedSignal, fs=synth.sampleRate)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.title("Denoised Signal Spectrogram")
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (sec)')
        plt.colorbar(label='Power (dB)')

        # Extracted Noise Frequency Magnitude Spectrum
        plt.subplot(2, 2, 2)
        frequencies = np.linspace(0, synth.sampleRate/2, len(grainProfile.noiseSpectra))
        plt.loglog(frequencies, grainProfile.noiseSpectra)
        plt.xlim([20.0, synth.sampleRate/2])
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.title("Extracted Noise Magnitude Spectrum")
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')


        # Plot grains
        time = np.linspace(0, durationSamples / synth.sampleRate, len(signalSource))
        grainPlot = np.zeros_like(signalSource)
        plt.subplot(2,2,4)
        plt.plot(time, signalSource, color="0.3", label="Original Signal")
        plt.plot(time, smoothedEnvelope, alpha = 0.5, linestyle='--', label="Smoothed Envelope")
        plt.ylim([-1.0, 1.0])
        plt.legend()
        for grainIdx in range(len(grainProfile.grains)):
            grain = grainProfile.grains[grainIdx]
            startSample = startTimes[grainIdx]
            endSample = min(len(signalSource), startSample + len(grain) - 1)
            grainPlot[startSample:endSample] = grain[:endSample - startSample]
            plt.plot(time, grainPlot, alpha=0.7)
            grainPlot[:] = 0.0
        plt.title("Original Signal With Extracted Grains")
        plt.xlabel("Time (sec)")
        plt.ylabel("Amplitude")

        # Show
        plt.tight_layout()
        plt.show()


    def plotExtend(signalSource, numGrains, durationSamples, synth):
        # Plot signal and where are the extracted grains
        Plotter.plotExtraction(signalSource, numGrains, durationSamples, synth, "Grain Profile Extraction")


    def plotBlend(signalA, signalB, durationSamples, numGrainsA, numGrainsB, synth):
        Plotter.plotExtraction(signalA, numGrainsA, durationSamples, synth, "Grain Profile Extraction (Signal A)")
        Plotter.plotExtraction(signalB, numGrainsB, durationSamples, synth, "Grain Profile Extraction (Signal B)")

        grainProfileA, denoisedSignalA, gA, startTimesA = synth.extractGrain(signalA, numGrainsA, debug=True)
        grainProfileB, denoisedSignalB, gB, startTimesB = synth.extractGrain(signalB, numGrainsB, debug=True)

        verticalShift = 0.0
        totalShift = 10.0
        numPlots = 6
        blendFactors = np.linspace(0.0, 1.0, numPlots)
        
        plt.figure(figsize=(10, 6))

        # Plot blended noise
        for blendFactor in blendFactors:
            blendProfile = grainProfileA.blend(grainProfileB, blendFactor)
            frequencies = np.linspace(0, synth.sampleRate/2, len(blendProfile.noiseSpectra))
            plt.loglog(frequencies, blendProfile.noiseSpectra + verticalShift, label=f"Blend Factor = {blendFactor:.2f}")
            verticalShift += totalShift / numPlots

        plt.xlim([20.0, synth.sampleRate/2])
        plt.ylim([0.1, 15.0])
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.title("Blended Noise Magnitude Spectra (Vertically Shifted)")
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.legend()
        plt.tight_layout()
        plt.show()


    def plotMorph(signalA, signalB, durationSamples, numGrainsA, numGrainsB, synth):
        Plotter.plotExtraction(signalA, numGrainsA, durationSamples, synth, "Grain Profile Extraction (Signal A)")
        Plotter.plotExtraction(signalB, numGrainsB, durationSamples, synth, "Grain Profile Extraction (Signal B)")

        grainProfileA, denoisedSignalA, gA, startTimesA = synth.extractGrain(signalA, numGrainsA, debug=True)
        grainProfileB, denoisedSignalB, gB, startTimesB = synth.extractGrain(signalB, numGrainsB, debug=True)

        verticalShift = 0.0
        totalShift = 10.0
        numPlots = 6
        morphFactors = np.linspace(0.0, 1.0, numPlots)

        # Plot morphed noise
        plt.figure(figsize=(10, 6))

        for morphFactor in morphFactors:
            morphProfile = grainProfileA.morph(grainProfileB, morphFactor)
            frequencies = np.linspace(0, synth.sampleRate/2, len(morphProfile.noiseSpectra))
            plt.loglog(frequencies, morphProfile.noiseSpectra + verticalShift, label=f"Morph Factor = {morphFactor:.2f}")
            verticalShift += totalShift / numPlots

        plt.xlim([20.0, synth.sampleRate/2])
        plt.ylim([0.1, 15.0])
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.title("Morphed Noise Magnitude Spectra (Vertically Shifted)")
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        
        plt.legend()
        plt.tight_layout()
        plt.show()


        # Plot morphed grains
        plt.figure(figsize=(10, 6))
        plt.suptitle("Morphed Grains Magnitude Spectra (Vertically Shifted)")
        morphProfile = grainProfileA.morph(grainProfileB, 0.5)
        numGrains = len(morphProfile.grains)
        verticalShift = 0.0

        for morphFactor in morphFactors:
            morphProfile = grainProfileA.morph(grainProfileB, morphFactor)

            for idx in range(numGrains):
                plt.subplot(1, numGrains, idx + 1)
                plt.title(f"Grain Pair {idx} Morphing")
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Magnitude')
                plt.xlim([20.0, synth.sampleRate/2])
                plt.ylim([0.1, 15.0])

                # Frequency Spectrum
                fft_result = np.fft.fft(morphProfile.grains[idx])
                freq = np.fft.fftfreq(len(morphProfile.grains[idx]), d=1.0 / synth.sampleRate)
                magnitude = np.abs(fft_result)[:len(fft_result)//2]
                freq_plot = freq[:len(freq)//2]
                
                # Apply smoothing (choose one method)
                # Method 2 (Savitzky-Golay) often works best for spectra
                if len(magnitude) > 64:  # Ensure enough points for smoothing
                    mag_smooth = signal.savgol_filter(magnitude, window_length=64, polyorder=3)
                else:
                    mag_smooth = magnitude
                    
                plt.plot(freq_plot, mag_smooth + verticalShift, label=f"Morph Factor = {morphFactor:.2f}") 
                
            verticalShift += totalShift / numPlots

        plt.legend(bbox_to_anchor=(0, -0.15), loc='upper left', frameon=True)
        plt.tight_layout()
        plt.show()    
