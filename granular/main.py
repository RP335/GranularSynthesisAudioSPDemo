import scipy.io.wavfile as wavfile
import numpy as np
from GranularSynthesiser import GranularSynthesiser
from GranularSynthesiser import GrainProfile

if __name__ == "__main__":

    # Convert them to 1D arrays (mono)
    print("Loading audio files...")
    sample_rate_A, signal_A = wavfile.read("soundA.wav")
    sample_rate_B, signal_B = wavfile.read("soundB.wav")
    
    # make mono
    if len(signal_A.shape) > 1: signal_A = signal_A[:, 0]
    if len(signal_B.shape) > 1: signal_B = signal_B[:, 0]
    
    # Normalize the audio signals to be between -1.0 and 1.0
    signal_A = signal_A.astype(np.float64) / np.max(np.abs(signal_A))
    signal_B = signal_B.astype(np.float64) / np.max(np.abs(signal_B))

    #Setup the Synthesizer
    synth = GranularSynthesiser()
    
    # grainSize, sizeRand, density, densityRand, gainRand, noiseGain
    synth.setParameters(grainSize=2048, sizeRandomness=100, density=1024, 
                        densityRandomness=50, gainRandomness=0.2, noiseGain=0.0, gain = 0.5)

    # Process the Audio
    duration_samples = sample_rate_A * 3 # Generate 3 seconds of audio
    
    print("Morphing sounds")
    # 50 50 morph
    morphed_audio = synth.morphSound(signal_A, signal_B, duration_samples, numGrainsA=50, numGrainsB=50, morphFactor=0.5)

    # Save the output
    print("Saving to morphed_output.wav")
    # Convert back to standard 16-bit audio format
    morphed_audio_int = np.int16(morphed_audio / np.max(np.abs(morphed_audio)) * 32767)
    wavfile.write("morphed_output.wav", sample_rate_A, morphed_audio_int)
    
    print("Done morphing and saving audio")