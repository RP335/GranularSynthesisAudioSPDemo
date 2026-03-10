import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

from granular.GranularSynthesiser import GranularSynthesiser


def test_extend_sound():
    # Read input sound
    fs, x = wavfile.read("soundA.wav")
    x = x.astype(np.float32)

    # If stereo, take one channel
    if x.ndim > 1:
        x = x[:, 0]

    # Normalize to [-1, 1]
    x /= np.max(np.abs(x)) + 1e-12

    # Create synthesiser and set parameters
    synth = GranularSynthesiser(fs)
    synth.setParameters(
        grainSize=2048,
        sizeRandomness=0,
        density=1024,
        densityRandomness=0,
        grainGainRandomness=0.2,
        noiseGain=0.5
    )

    # Generate sound
    duration = fs * 3
    numGrains = 10
    y = synth.extendSound(x, durationSamples=duration, numGrains=numGrains, plot=True)

    # Save result to listen
    y = y / (np.max(np.abs(y)) + 1e-12) * 0.9
    wavfile.write("synthesized_soundA.wav", fs, y.astype(np.float32))

    plt.show()

def test_extract_grains():
    fs, x = wavfile.read("soundA.wav")
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x[:, 0]
    x /= np.max(np.abs(x)) + 1e-12

    synth = GranularSynthesiser(fs)
    gp = synth.extractGrain(x, numGrains=5)

    print(f"Extracted {len(gp.grains)} grains")

    plt.figure(figsize=(10,8))
    plt.subplot(3,1,1)
    plt.title("Original signal")
    plt.plot(x)
    plt.xlim(0, len(x))

    plt.subplot(3,1,2)
    plt.title("Grain 1")
    plt.plot(gp.grains[0])

    if len(gp.grains) > 1:
        plt.subplot(3,1,3)
        plt.title("Grain 2")
        plt.plot(gp.grains[1])

    plt.tight_layout()
    plt.show()

def test_noise_subtraction():
    fs, x = wavfile.read("soundA.wav")
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x[:, 0]
    x /= np.max(np.abs(x)) + 1e-12

    synth = GranularSynthesiser(fs)
    gp, sc, g = synth.extractGrain(x, numGrains=1, debug=True)
    
    plt.figure(figsize=(10,8))

    plt.subplot(3,1,1)
    plt.title("Original signal")
    plt.plot(x)

    plt.subplot(3,1,2)
    plt.title("Denoised signal s_c[t]")
    plt.plot(sc)

    plt.subplot(3,1,3)
    plt.title("Smoothed envelope g[t]")
    plt.plot(g)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    #test_extend_sound()
    #test_extract_grains()
    test_noise_subtraction()