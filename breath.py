from collections import Counter  # ermöglicht das Erstellen von Histogrammen


class AtemzugValidierungBreaths:
    def __init__(self):
        self.breath_list = None
        self.mask_edf_meta_data = None
        self.mask_edf_data = None
        self.pressure_limit = None
        # Start- und Endpunkt in denen das Programm die Atemzüge ermittelt
        self.start_analyses_index = 0.0
        self.end_analyses_index = 0.0

    # Funktion zur Ermittlung der einzelnen Atemzüge
    def get_breaths(self):
        breaths = []
        breathing = False
        breath_start = None
        breath_no = 1

        # Start- und Endpunkt. Ab wo bis wo werden Atemzüge erfasst
        start_index, end_index = self.get_ventilation_start_end()
        # Grenzwert wird berechnet
        self.pressure_limit = self.get_pressure_limit()

        for i in range(start_index, end_index):
            if self.mask_edf_data[0, i] >= self.pressure_limit and self.mask_edf_data[0, i + 1] > self.pressure_limit:
                if not breathing:
                    breathing = True
                    breath_start = i / 100
            else:
                if breathing:
                    breath_end = i / 100
                    # Aufzeichnung von atemzügen, welche mindesten 0,2 Sek lang sind
                    if breath_end - breath_start >= 0.2:
                        breaths.append((breath_no, breath_start, breath_end))
                        breath_no += 1
                    breathing = False

        return breaths

    # Funktion zur Ermittlung vom Anfang und Ende der Beatmung
    def get_ventilation_start_end(self):
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

        return ventilation_start, ventilation_end

    # Funktion zum Ermitteln des am meist vorkommenden Drucks
    def get_most_frequent_pressure(self):
        start_index, end_index = self.get_ventilation_start_end()

        # Druckwerte >= 1 werden in Liste pressure_values durch List Comprehension gespeichert
        pressure_values = [i for i in self.mask_edf_data[0, start_index:end_index] if i >= 0]

        # Histogramm wird erstellt. Häufigkeit der Druckwerte wird gezählt
        counted_pressure_values = Counter(pressure_values)

        # Meist vorkommender Druckwert wird ermittelt
        most_frequent_pressure = counted_pressure_values.most_common(1)[0][0]
        print("Häufigster Druck: " + str(most_frequent_pressure))

        return most_frequent_pressure

    # Funktion zum Festlegen des Grenzwertes, welcher überschritten werden muss, um Atemzüge zu ermitteln
    def get_pressure_limit(self):
        most_frequent_pressure = self.get_most_frequent_pressure()
        pressure_limit = most_frequent_pressure + (0.6 * most_frequent_pressure)

        return pressure_limit
