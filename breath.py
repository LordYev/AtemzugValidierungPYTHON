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
        self.min_pressure = None
        self.max_pressure = None
        self.min_duration = None
        self.max_duration = None
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

        breath_list = self.mark_anomalie_data(breaths)

        return breath_list

    # Funktion zum Ermitteln des maximalen Drucks eines Atemzuges
    def get_pressure_peak(self, start_index, end_index):
        # Star und Ende werden umgerechnet, da es Kommazahlen mit zwei Nachkommastellen sind
        start_index = int(start_index * 100)
        end_index = int(end_index * 100)
        pressure_list = []
        # ermittelt jeden Druckwert zwischen Start und Ende, speichert diese in Liste pressure_list ab
        for i in range(start_index, end_index):
            pressure_list.append(self.mask_edf_data[0, i])

        # höchster Druckwert wird ermittelt
        pressure_max = np.max(pressure_list)

        return pressure_max

    # Funktion ermittelt Atemzüge mit einer Anomalie und markiert diese
    def mark_anomalie_data(self, breath_list):
        # breath_list wird in Liste umgewandelt um Einträge bearbeiten zu können
        breath_list = [list(item) for item in breath_list]
        breath_duration_list = []
        pressure_peak_list = []

        # ermittelt höchsten Druckwert und Dauer jedes Atemzuges. Speichert Parameter in zugehöriger Liste ab
        for i in breath_list:
            pressure_peak = self.get_pressure_peak(i[1], i[2])
            breath_duration = i[2] - i[1]
            pressure_peak_list.append(pressure_peak)
            breath_duration_list.append(breath_duration)

        # Median und Standardabweichung von Druck- und Dauerliste werden ermittelt
        pressure_peak_median = statistics.median(pressure_peak_list)
        pressure_peak_std_dev = statistics.stdev(pressure_peak_list)
        breath_duration_median = statistics.median(breath_duration_list)
        breath_duration_std_dev = statistics.stdev(breath_duration_list)

        # Grenzwerte für Druck und Dauer, zwischen denen ein Atemzug als valide gilt, werden ermittelt
        self.min_pressure = pressure_peak_median - 2 * pressure_peak_std_dev
        self.max_pressure = pressure_peak_median + 2 * pressure_peak_std_dev
        self.min_duration = breath_duration_median - 2 * breath_duration_std_dev
        self.max_duration = breath_duration_median + 2 * breath_duration_std_dev

        # Atemzugliste wird durchlaufen und auf Anomalien geprüft
        breath_index = 0
        for data in breath_list:
            duration_out_of_valid_area = False
            pressure_out_of_valid_area = False

            if breath_duration_list[breath_index] < self.min_duration or breath_duration_list[breath_index] > self.max_duration:
                duration_out_of_valid_area = True

            if pressure_peak_list[breath_index] < self.min_pressure or pressure_peak_list[breath_index] > self.max_pressure:
                pressure_out_of_valid_area = True

            # nur Werte, welche nicht in den ersten und letzten 5 Min vorhanden sind, betrachten
            if data[4] == "-":
                # markiert alle Anomalien mit entsprechendem Kommentar
                if duration_out_of_valid_area is True and pressure_out_of_valid_area is False:
                    data[3] = 3
                    data[4] = f"ANOMALIE. Dauer: {breath_duration_list[breath_index]:.2f}sek"
                elif duration_out_of_valid_area is False and pressure_out_of_valid_area is True:
                    data[3] = 3
                    data[4] = f"ANOMALIE. max Druck: {pressure_peak_list[breath_index]:.2f}mbar"
                elif duration_out_of_valid_area is True and pressure_out_of_valid_area is True:
                    data[3] = 3
                    data[4] = f"ANOMALIE. Dauer: {breath_duration_list[breath_index]:.2f}sek, max Druck: {pressure_peak_list[breath_index]:.2f}mbar"

            breath_index += 1

        self.get_pressure_peak(breath_list[2004][1], breath_list[2004][2])
        # Liste wird wieder in die ursprüngliche Form (Tupel) umgewandelt
        breath_list = [tuple(item) for item in breath_list]

        return breath_list

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

        pressure_median_limit = pressure_median + (0.6 * pressure_median)

        return pressure_median_limit
