import numpy as np

class GrainGenerator:

    def __init__(self, sample, startPosition, startRandomness, grainSize, sizeRandomness, window):
        self.sample = np.asarray(sample, dtype=float)
        if self.sample.ndim != 1:
            raise ValueError("sample must be a 1D mono array of audio samples")
        self.sample=sample
        self.startPosition=startPosition
        self.startRandomness=startRandomness
        self.grainSize=grainSize
        self.sizeRandomness=sizeRandomness
        self.window=window


    def generateGrain(self):

        # TODO
        # randomising start position
        if self.startRandomness > 0:
            offset=np.random.randint(-self.startRandomness, self.startRandomness)
        else:
            offset=0

        start = self.startPosition + offset

        # randomise grain size
        if self.sizeRandomness > 0:
            sizeDrift = np.random.randint(-self.sizeRandomness, self.sizeRandomness)
        else:
            sizeDrift=0

        currentSize = max(2, self.grainSize + sizeDrift)

        # clamping to valid range
        start = max(0, min(start, len(self.sample) - currentSize))
        end = start + currentSize

        # extract slice
        grain = self.sample[start: end].copy()

        if self.window !=0 and len(grain)>1:
            if self.window == "hann" or self.window == 1:
                win = np.hanning(len(grain))

            elif self.window == "hamming":
                win = np.hamming(len(grain))

            else:
                win = np.hanning(len(grain))

            grain *= win


        # Dummmy implementation (impulse)
        output = np.zeros(10)
        output[0] = 1

        assert(output.ndim ==1 ) # Grain must be mono
        return output