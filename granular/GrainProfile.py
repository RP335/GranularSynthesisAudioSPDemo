import numpy as np
import random
from scipy.interpolate import interp1d

class GrainProfile:

    def __init__(self, noiseSpectra, grains, weights=None):
        """
        
        grains: List of 1D np.arrays containing grains
        weights: Probability weights of choosing each grain
        """
        self.noiseSpectra = noiseSpectra
        self.grains = grains
        if (weights == None):
            weights = [1.0 for _ in range(len(self.grains))]
        self.weights = weights

    def getGrain(self, size):
        """
        Returns random grain.
        """
         # Get random index based on weights
        indices = list(range(len(self.grains)))
        selected_idx = random.choices(indices, weights=self.weights, k=1)[0]
        grain = self.grains[selected_idx]
        
        endSample = min(size, grain.size)
        return grain[:endSample], selected_idx

    # ********************************** NIKLAS **********************************
    def generateNoise(self, durationSamples):
        """
        Shape white noise to match previously substracted noise using multiplication of the spectra in
        the frequency domain.
        """
        if self.noiseSpectra is None or len(self.noiseSpectra) == 0:
            # Only white noise if no spectrum available
            noise = np.random.normal(0.0, 1.0, durationSamples)
            noise /= np.max(np.abs(noise)) + 1e-12
            return noise

        # FFT size
        half_len = len(self.noiseSpectra)
        N_fft = (half_len - 1) * 2

        # Choose hop size and window for overlap-add
        hop = N_fft // 2    # 50 % overlap
        win = np.hanning(N_fft)

        # How many frames needed
        n_frames = 1 + int(np.ceil(max(0, durationSamples - N_fft) / hop))
        total_len = (n_frames - 1) * hop + N_fft

        out = np.zeros(total_len)

        for i in range(n_frames):
            # Random phases for the bins in the one-sided spectrum
            phases = np.random.uniform(0, 2 * np.pi, half_len)

            # One-sided complex spectrum
            X_half = self.noiseSpectra * np.exp(1j * phases)

            # Mirror to build full complex spectrum 
            X_conj = np.conj(X_half[1:-1][::-1])
            X_full = np.concatenate((X_half, X_conj))

            # IFFT
            frame = np.fft.ifft(X_full).real

            # Window and overlap-add
            start = i * hop
            out[start:start + N_fft] += frame * win

        # Trim to duration
        out = out[:durationSamples]

        # Normalize to [-1, 1] to avoid clipping
        max_abs = np.max(np.abs(out)) + 1e-12
        out /= max_abs

        return out


    # ********************************** RAHUL **********************************
    def blend(self, grainProfile, weightBias):
        """
        Blends two grain profiles by combining their grain pools and taking a 
        weighted average of their noise spectra.
        """
        
        # Append grains
        grains = self.grains + grainProfile.grains

        # Calculate weights
        # Target probability mass for each list of grains (v in the paper is the weight bias)
        target1 = 1 - weightBias
        target2 = weightBias

        sum1 = sum(self.weights)
        sum2 = sum(grainProfile.weights)

        # Scale weights
        scaled1 = [w * target1 / sum1 for w in self.weights] if sum1 > 0 else []
        scaled2 = [w * target2 / sum2 for w in grainProfile.weights] if sum2 > 0 else []

        weights = scaled1.append(scaled2)

        blended_noise = (1.0 - weightBias) * self.noiseSpectra + weightBias * grainProfile.noiseSpectra

        # Average noises
        # TODO

        return GrainProfile(blended_noise, grains, weights)

    # ********************************** RAHUL **********************************

    def extract_overlapping_frames(self, grain, L=256, d=16):
        """
        Slices a 1D grain array into overlapping frames and pads with zeros.
        """
        frames = []
        # sliding a window of size L across the grain, stepping by d
        for i in range(0, len(grain) - L + 1, d):
            frame = grain[i : i + L]
            # Pad the frame with L zeros to make its length 2L (N_fft)
            padded_frame = np.pad(frame, (0, L), 'constant')
            frames.append(padded_frame)
        return frames

    def overlap_add_frames(self, frames, d=16):
        """
        Overlaps and adds morphed time-domain frames back into a single grain waveform.
        """
        if not frames:
            return np.array([])

        N_fft = len(frames[0])
        L = N_fft // 2
        
        # Create the window: Hann window for the first half, zeros for the second half
        window = np.concatenate((np.hanning(L), np.zeros(L)))
        
        # Calculate the total length of our final output grain
        total_length = d * (len(frames) - 1) + N_fft
        output = np.zeros(total_length)
        
        for i, frame in enumerate(frames):
            start_idx = i * d
            # Ensure we are only adding the real part of the IFFT output, multiplied by our window
            output[start_idx : start_idx + N_fft] += np.real(frame) * window
            
        return output


    def morph_power_spectra(self, a, b, v):
        """
        Morphs two power spectra by shifting their cumulative energy distributions.
        Based on Section 4.2 of the paper.
        """
        # To avoid division by zero issues
        eps = 1e-10
        
        # 1. Remove zero offset (Eq 13 & 16-17)
        p_a = np.min(a)
        p_b = np.min(b)
        a_0 = a - p_a
        b_0 = b - p_b
        
        # 2. Calculate normalization parameters (Eq 18-19)
        q_a = np.sum(a_0) + eps
        q_b = np.sum(b_0) + eps
        
        # 3. Normalize to get snorm (Eq 14)
        a_norm = a_0 / q_a
        b_norm = b_0 / q_b
        
        # 4. Cumulative sum (Eq 15 & 22)
        A_cum = np.cumsum(a_norm)
        B_cum = np.cumsum(b_norm)
        
        # Force the last value to be exactly 1.0 to avoid interpolation rounding errors
        A_cum[-1] = 1.0
        B_cum[-1] = 1.0
        
        # Create a generic frequency axis [0, 1, 2, ..., N]
        freq_axis = np.arange(len(a))
        
        # INVERT the functions (Eq 20): Swap X (frequency) and Y (cumulative energy)
        # Creating functions that let us input an Energy Level (y) and get back the Frequency (x)
        A_inv = interp1d(A_cum, freq_axis, bounds_error=False, fill_value=(0, len(a)-1))
        B_inv = interp1d(B_cum, freq_axis, bounds_error=False, fill_value=(0, len(b)-1))
        
        # Create an evenly spaced arbitrary energy axis (y in the paper) from 0 to 1
        y_axis = np.linspace(0, 1, len(a))
        
        # Calculate the weighted average of the inverses (Eq 20)
        F_ab_inv = v * A_inv(y_axis) + (1 - v) * B_inv(y_axis)
        
        #  INVERT BACK to cumulative frequency (Eq 22)
        X_ab_cum = interp1d(F_ab_inv, y_axis, bounds_error=False, fill_value=(0, 1))(freq_axis)
        
        # Differentiate (f[n] = F[n] - F[n-1]) to get the normalized power spectrum
        X_ab_norm = np.diff(X_ab_cum, prepend=0)
        # Ensure no negative values due to rounding
        X_ab_norm = np.clip(X_ab_norm, 0, None)
        
        # Denormalize (Eq 21)
        f_ab = (v * q_a + (1 - v) * q_b) * X_ab_norm + (v * p_a + (1 - v) * p_b)
        
        return f_ab


    def morph_grain_frames(self, frameA, frameB, v):
        """
        Applies FFT, morphs the power spectrum, mixes the phase, and applies Inverse FFT.
        Based on Section 4.4.3.
        """
        N_fft = len(frameA) # Should be 512 if L=256
        
        # Get complex FFT coefficients
        X_A = np.fft.fft(frameA)
        X_B = np.fft.fft(frameB)
        
        # We only care about the first half of the spectrum (0 to N_fft/2)
        half_idx = (N_fft // 2) + 1
        X_A_half = X_A[:half_idx]
        X_B_half = X_B[:half_idx]
        
        # 2. Calculate Power Spectra (E_A and E_B) (Eq 23)
        E_A = np.abs(X_A_half)**2
        E_B = np.abs(X_B_half)**2
        
        # 3. Extract Phase / Normalized complex spectra (C_A and C_B) (Eq 27)
        # Adding a tiny epsilon to prevent dividing by zero
        eps = 1e-10
        C_A = X_A_half / (np.abs(X_A_half) + eps)
        C_B = X_B_half / (np.abs(X_B_half) + eps)
        
        # 4. MORPH THE POWER SPECTRUM using our heavy math function!
        E_AB = self.morph_power_spectra(E_A, E_B, v)
        
        # 5. Recombine the morphed power with a weighted mix of the original phases (Eq 28)
        S_AB_half = (1 - v) * C_A * np.sqrt(E_AB) + v * C_B * np.sqrt(E_AB)
        
        # 6. Mirror the spectrum to recreate the full N_fft length (Eq 29)
        # We take the complex conjugate of the reversed second half
        S_AB_mirrored = np.conj(S_AB_half[1:-1][::-1]) 
        S_AB_full = np.concatenate((S_AB_half, S_AB_mirrored))
        
        # 7. Inverse FFT back to the time domain
        morphed_frame_time = np.fft.ifft(S_AB_full)
        
        # Return just the real part (imaginary parts should be ~0 due to mirroring)
        return np.real(morphed_frame_time)

    def calculate_grain_distance(self, grainA, grainB):
        """
        Calculates the 'distance' between two grains by comparing the cumulative 
        area of their average power spectra. (Section 4.4.2)
        """
        # Extract overlapping frames (L=256, d=16), run FFT, get Power Spectrums, and Average them
        framesA = self.extract_overlapping_frames(grainA, L=256, d=16)
        framesB = self.extract_overlapping_frames(grainB, L=256, d=16)
        
        # Calculate average power spectrum for the whole grain
        E_A_avg = np.mean([np.abs(np.fft.fft(f)[:len(f)//2 + 1])**2 for f in framesA], axis=0)
        E_B_avg = np.mean([np.abs(np.fft.fft(f)[:len(f)//2 + 1])**2 for f in framesB], axis=0)
        
        # Normalize cumulative sums (Eq 24)
        S_A = np.cumsum(E_A_avg) / np.sum(E_A_avg)
        S_B = np.cumsum(E_B_avg) / np.sum(E_B_avg)
        
        # Distance is the absolute area between the graphs
        return np.sum(np.abs(S_A - S_B))

    def pair_grains_stable_marriage(self,grains_A, grains_B):
        """
        Pairs grains using a modified stable marriage algorithm.
        """
        # Determine who is the Company (more grains) and who is the Applicant (less grains)
        if len(grains_A) >= len(grains_B):
            companies, applicants = grains_A, grains_B
            is_A_company = True
        else:
            companies, applicants = grains_B, grains_A
            is_A_company = False

        N_co = len(companies)
        N_ap = len(applicants)
        N = N_co / N_ap
        N_max = int(np.ceil(N)) # Maximum candidates a company can hire

        # 1. Calculate distance matrix between all applicants and all companies
        # distance_matrix[a][c] = distance between applicant 'a' and company 'c'
        dist_matrix = np.zeros((N_ap, N_co))
        for a in range(N_ap):
            for c in range(N_co):
                dist_matrix[a][c] = self.calculate_grain_distance(applicants[a], companies[c])

        # 2. Setup the Marriage Market
        # To keep this script from getting overly complex with multi-round rejections, 
        # we use a greedy approach to fulfill the paper's requirements: 
        # Every applicant gets exactly 1 match. Companies get up to N_max matches.
        
        matches = [] # Will hold tuples of (index_A, index_B)
        company_hires = {c: 0 for c in range(N_co)}
        
        for a in range(N_ap):
            # Sort companies by distance (preference) for this applicant
            preferred_companies = np.argsort(dist_matrix[a])
            
            for c in preferred_companies:
                if company_hires[c] < N_max:
                    # Hire them!
                    company_hires[c] += 1
                    if is_A_company:
                        matches.append((companies[c], applicants[a]))
                    else:
                        matches.append((applicants[a], companies[c]))
                    break # Move to next applicant
                    
        return matches
        
    def morph(self, grainProfile, morphFactor):
        """
        Morphs the tone color of this profile with another using cumulative energy 
        redistribution and grain pairing.
        """
        # Morph grains
        v = morphFactor

        # Average noises
        morphed_noise = self.morph_power_spectra(self.noiseSpectra, grainProfile.noiseSpectra, v)

        paired_grains = self.pair_grains_stable_marriage(self.grains, grainProfile.grains)
        morphed_grains = []

        for grainA, grainB in paired_grains:
            framesA = self.extract_overlapping_frames(grainA, L=256, d=16)
            framesB = self.extract_overlapping_frames(grainB, L=256, d=16)
            
            M_A = len(framesA)
            M_B = len(framesB)
            M_AB = int(round((1 - v) * M_A + v * M_B))

            morphed_frames = []
            for m in range(M_AB):
                m_A = int(round(m * M_A / M_AB))
                m_B = int(round(m * M_B / M_AB))
                m_A = min(m_A, M_A - 1)
                m_B = min(m_B, M_B - 1)


                morphed_frame_time_domain = self.morph_grain_frames(framesA[m_A], framesB[m_B], v)
                morphed_frames.append(morphed_frame_time_domain)
            final_morphed_grain = self.overlap_add_frames(morphed_frames, d=16)

            morphed_grains.append(final_morphed_grain)

        new_weights = [1.0 / len(morphed_grains)] * len(morphed_grains)
        return GrainProfile(morphed_noise, morphed_grains, new_weights)