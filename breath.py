from collections import Counter  # ermöglicht das Erstellen von Histogrammen
import numpy as np
import statistics

class AtemzugValidierungBreaths:
    def __init__(self):
        self.breath_list = None
        self.breath_list_valid_data = None
        self.breath_list_invalid_data = None
        self.breath_list_commented_data = None
        self.mask_edf_meta_data = None
        self.mask_edf_data = None
        self.pressure_median = None
        # Start- und Endpunkt in denen das Programm die Atemzüge ermittelt
        self.start_analyses_index = 0.0
        self.end_analyses_index = 0.0

    # Funktion zur Ermittlung der einzelnen Atemzüge
    def get_breaths(self):
        breaths = []
        breathing = False
        breath_start = None
        breath_no = 1
        value_status = 1
        value_comment = "-"

        # Start- und Endpunkt. Ab wo bis wo werden Atemzüge erfasst
        start_index, end_index = self.get_ventilation_start_end()
        # Schwellwert wird berechnet
        self.pressure_median = self.get_pressure_median()

        for i in range(start_index, end_index):
            if self.mask_edf_data[0, i] >= self.pressure_median and self.mask_edf_data[0, i + 1] > self.pressure_median:
                if not breathing:
                    breathing = True
                    breath_start = i / 100
            elif breathing:
                breath_end = i / 100
                # Aufzeichnung von atemzügen, welche mindesten 0,2 Sek lang sind
                if breath_end - breath_start >= 0.2:
                    # setzt Status und Kommentar für alle Atemzüge in den ersten 5 Minuten fest
                    if breath_start < ((start_index / 100) + 300):
                        value_status = 0
                        value_comment = "Atemzug befindet sich innerhalb der ersten 5 Minuten!"

                    # setzt Status und Kommentar für alle Atemzüge in den letzten 5 Minuten fest
                    if breath_start > ((end_index / 100) - 300):
                        value_status = 0
                        value_comment = "Atemzug befindet sich innerhalb der letzten 5 Minuten!"

                    breaths.append((breath_no, breath_start, breath_end, value_status, value_comment))
                    breath_no += 1
                    value_status = 1
                    value_comment = "-"
                breathing = False

        return breaths

    # Funktion zur Ermittlung vom Anfang und Ende der Beatmung
    # V1
    '''def get_ventilation_start_end(self):
        ventilation_start = None
        ventilation_end = None

        start_index = int(float(self.start_analyses_index) * self.mask_edf_meta_data['sfreq'])

        # For-Schleife läuft vom start_index solange durch, bis es den Anfang der Beatmung ermittelt hat
        for i in range(start_index, len(self.mask_edf_data[0]) - 1):
            if self.mask_edf_data[0, i] > 1:
                ventilation_start = i / 100
                break

        start_index = int(float(self.end_analyses_index) * self.mask_edf_meta_data['sfreq'])

        # For-Schleife läuft rückwärts vom start_index solange durch, bis es das Ende der Beatmung ermittelt hat
        for i in reversed(range(start_index)):
            if self.mask_edf_data[0, i] > 1:
                ventilation_end = i / 100
                break

        ventilation_start = int(ventilation_start * self.mask_edf_meta_data['sfreq'])
        ventilation_end = int(ventilation_end * self.mask_edf_meta_data['sfreq'])

        return ventilation_start, ventilation_end'''

    # V2
    '''def get_ventilation_start_end(self):
        window_size = 5
        ventilation_start = None
        ventilation_end = None

        start_index = int(float(self.start_analyses_index) * self.mask_edf_meta_data['sfreq'])
        end_index = int(float(self.end_analyses_index) * self.mask_edf_meta_data['sfreq'])

        # Berechne den gleitenden Durchschnitt
        moving_average = np.convolve(self.mask_edf_data[0], np.ones(window_size) / window_size, mode='valid')

        # For-Schleife läuft vom start_index solange durch, bis es den Anfang der Beatmung ermittelt hat
        for i in range(start_index, len(moving_average)):
            if moving_average[i] > 1:
                ventilation_start = i + window_size - 1
                break

        # For-Schleife läuft rückwärts vom end_index solange durch, bis es das Ende der Beatmung ermittelt hat
        for i in reversed(range(end_index - window_size)):
            if moving_average[i] > 1:
                ventilation_end = i + window_size - 1
                break

        return ventilation_start, ventilation_end'''

    # V3
    def get_ventilation_start_end(self):
        ventilation_start = None
        ventilation_end = None

        start_index = int(float(self.start_analyses_index) * self.mask_edf_meta_data['sfreq'])

        # For-Schleife läuft vom start_index solange durch, bis es den Anfang der Beatmung ermittelt hat
        for i in range(start_index, len(self.mask_edf_data[0]) - 1):
            if self.mask_edf_data[0, i] > 1:
                ventilation_start = i
                # Test-Liste wird erstellt und mit Werten der nächsten 10sek befüllt
                test_values = []
                for index in range(ventilation_start, min(ventilation_start + 1000, len(self.mask_edf_data[0]))):
                    test_values.append(self.mask_edf_data[0, index])
                # Durchschnitt wird berechnet um zu schauen, ob es der Beginn der Beatmung, oder nur ein Ausschlag in der Kurve war
                values_sum = sum(test_values)
                values_count = len(test_values)
                if values_count > 0:
                    average = values_sum / values_count
                    # wenn Durchschnitt größer als 1, dann setze Beatmungsstartpunkt fest
                    if average >= 1:
                        break
                    else:
                        ventilation_start = None

        start_index = int(float(self.end_analyses_index) * self.mask_edf_meta_data['sfreq'])

        # For-Schleife läuft rückwärts vom start_index solange durch, bis es das Ende der Beatmung ermittelt hat
        # gleicher Algorithmus wie zuvor, nur rückwärts
        for i in reversed(range(start_index)):
            if self.mask_edf_data[0, i] > 1:
                ventilation_end = i
                test_values = []
                for index in reversed(range(max(ventilation_end - 1000, 0), ventilation_end)):
                    test_values.append(self.mask_edf_data[0, index])
                values_sum = sum(test_values)
                values_count = len(test_values)
                if values_count > 0:
                    average = values_sum / values_count
                    if average >= 1:
                        break
                    else:
                        ventilation_start = None

        return ventilation_start, ventilation_end

    # Funktion zum Ermitteln des am meist vorkommenden Drucks
    def get_pressure_median(self):
        start_index, end_index = self.get_ventilation_start_end()

        # Druckwerte >= 1 werden in Liste pressure_values durch List Comprehension gespeichert
        pressure_values = [i for i in self.mask_edf_data[0, start_index:end_index] if i >= 1]
        pressure_median = statistics.median(pressure_values)

        # ist diese Berechnung notwendig?
        '''pressure_median_limit = pressure_median + (0.6 * pressure_median)'''

        return pressure_median
