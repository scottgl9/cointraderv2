import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from typing import List, Tuple, Optional
from collections import deque

from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline

class ElliottWaveIndicator(Indicator):
    def __init__(self, name='elliott_wave', period=500, sensitivity=1.0):
        """
        Initialize the Elliott Wave Indicator.

        :param name: Name of the indicator.
        :param period: Number of recent Klines to consider for wave analysis.
        :param sensitivity: Sensitivity factor for peak/trough detection.
                            Higher values lead to fewer detected peaks/troughs.
        """
        super().__init__(name)
        self.period = period
        self.sensitivity = sensitivity
        self.klines = deque(maxlen=self.period)
        self.wave_counts = []
        self.waves = []  # List of waves identified
        self.current_wave = []
        self.phase = 'impulse'  # 'impulse' or 'corrective'
        self.min_distance = 5  # Minimum number of Klines between peaks/troughs
        self.min_prominence = 0.5  # Minimum prominence of peaks/troughs

    def reset(self):
        """
        Reset the Elliott Wave indicator to its initial state.
        """
        self.klines.clear()
        self.wave_counts = []
        self.waves = []
        self.current_wave = []
        self.phase = 'impulse'

    def _extract_prices(self) -> pd.Series:
        """
        Extract the closing prices from the Klines.

        :return: Pandas Series of closing prices.
        """
        return pd.Series([k.close for k in self.klines])

    def _identify_peaks_troughs(self, prices: pd.Series) -> Tuple[List[int], List[int]]:
        """
        Identify peaks (local maxima) and troughs (local minima) in the price series.

        :param prices: Pandas Series of closing prices.
        :return: Tuple containing lists of peak indices and trough indices.
        """
        # Identify peaks
        peaks, _ = find_peaks(prices, distance=self.min_distance, prominence=self.min_prominence * self.sensitivity)

        # Identify troughs by inverting the prices
        troughs, _ = find_peaks(-prices, distance=self.min_distance, prominence=self.min_prominence * self.sensitivity)

        return peaks.tolist(), troughs.tolist()

    def _assign_waves(self, peaks: List[int], troughs: List[int]):
        """
        Assign identified peaks and troughs to Elliott Waves based on their sequence.

        :param peaks: List of peak indices.
        :param troughs: List of trough indices.
        """
        # Combine peaks and troughs
        extrema = sorted(peaks + troughs)
        wave_sequence = []
        for idx in extrema:
            if idx in peaks:
                wave_sequence.append(('peak', idx))
            else:
                wave_sequence.append(('trough', idx))

        # Assign waves based on impulse and corrective phases
        for point in wave_sequence:
            wave_type, idx = point
            price = self.klines[idx].close
            time = self.klines[idx].time

            if not self.current_wave:
                # Start the first wave
                self.current_wave.append({'type': wave_type, 'index': idx, 'price': price, 'time': time})
                continue

            last_wave = self.current_wave[-1]

            # Ensure waves alternate between peak and trough
            if last_wave['type'] != wave_type:
                self.current_wave.append({'type': wave_type, 'index': idx, 'price': price, 'time': time})
            else:
                # If two consecutive peaks or troughs, keep the more extreme one
                if wave_type == 'peak' and price > last_wave['price']:
                    self.current_wave[-1] = {'type': wave_type, 'index': idx, 'price': price, 'time': time}
                elif wave_type == 'trough' and price < last_wave['price']:
                    self.current_wave[-1] = {'type': wave_type, 'index': idx, 'price': price, 'time': time}

        # After assigning, analyze wave counts
        self._analyze_waves()

    def _analyze_waves(self):
        """
        Analyze the current wave sequence to identify Elliott Waves.
        """
        # Elliott Waves consist of 5 impulse waves and 3 corrective waves
        # This simplistic implementation counts sequences accordingly

        wave_types = [wave['type'] for wave in self.current_wave]

        # Check for impulse waves (5 waves)
        if len(wave_types) >= 5:
            # A simplistic check: 5 alternating peaks/troughs
            last_five = wave_types[-5:]
            if all(last_five[i] != last_five[i+1] for i in range(4)):
                # Assign wave numbers
                wave_numbers = list(range(1, 6))
                for i, wave in enumerate(self.current_wave[-5:]):
                    wave['elliott_wave'] = wave_numbers[i]
                self.waves.extend(self.current_wave[-5:])
                print(f"Elliott Wave Phase: Impulse completed at index {self.current_wave[-1]['index']}")
        
        # Check for corrective waves (3 waves)
        if len(wave_types) >= 3:
            last_three = wave_types[-3:]
            if all(last_three[i] != last_three[i+1] for i in range(2)):
                # Assign wave numbers
                corrective_wave_numbers = ['A', 'B', 'C']
                for i, wave in enumerate(self.current_wave[-3:]):
                    wave['elliott_wave'] = corrective_wave_numbers[i]
                self.waves.extend(self.current_wave[-3:])
                print(f"Elliott Wave Phase: Corrective completed at index {self.current_wave[-1]['index']}")
        
        # Reset current_wave to prevent overlap
        if len(self.current_wave) > 8:
            self.current_wave = self.current_wave[-8:]

    def update(self, kline: Kline) -> Optional[List[Dict[str, float]]]:
        """
        Update the Elliott Wave indicator with a new Kline.

        :param kline: The new Kline data.
        :return: List of identified waves or None if not ready.
        """
        self.klines.append(kline)

        if len(self.klines) < 10:
            # Not enough data to identify waves
            return None

        prices = self._extract_prices()
        peaks, troughs = self._identify_peaks_troughs(prices)
        self._assign_waves(peaks, troughs)

        if len(self.waves) > 0:
            return self.waves.copy()
        else:
            return None

    def get_last_waves(self) -> Optional[List[Dict[str, float]]]:
        """
        Get the list of identified Elliott Waves.

        :return: List of waves with details or None.
        """
        if len(self.waves) > 0:
            return self.waves.copy()
        return None

    def plot_elliott_waves(self):
        """
        Plot the price chart with identified Elliott Waves.

        Note: This function requires matplotlib and should be called after waves are identified.
        """
        if len(self.waves) == 0:
            print("No Elliott Waves to plot.")
            return

        # Prepare data
        dates = [k.time for k in self.klines]
        prices = [k.close for k in self.klines]
        df = pd.DataFrame({
            'Date': dates,
            'Price': prices
        })
        df.set_index('Date', inplace=True)

        plt.figure(figsize=(15, 8))
        plt.plot(df.index, df['Price'], label='Close Price', color='blue')

        # Annotate waves
        for wave in self.waves:
            wave_time = wave['time']
            wave_price = wave['price']
            wave_label = wave.get('elliott_wave', '')
            plt.scatter(wave_time, wave_price, marker='o', color='red')
            plt.text(wave_time, wave_price, wave_label, fontsize=9, ha='right')

        plt.title('Elliott Wave Analysis')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.show()
