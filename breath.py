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
        self.ventilation_start = None
        self.ventilation_end = None
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

    # Funktion zum Ermitteln des Beatmungsbereiches
    def get_ventilation_area(self, start_index, reversed_func):
        ventilation_area_border = None
        new_start_index = None

        # For-Schleife läuft vom start_index solange durch, bis es einen Ausschlag (>1mbar) gefunden hat
        # durchläuft von links nach rechts
        if reversed_func is False:
            for i in range(start_index, len(self.mask_edf_data[0]) - 1):
                if self.mask_edf_data[0, i] > 1:
                    ventilation_area_border = i
                    break
        # durchläuft von rechts nach links
        elif reversed_func is True:
            for j in reversed(range(start_index)):
                if self.mask_edf_data[0, j] > 1:
                    ventilation_area_border = j
                    break

        # Test-Liste wird erstellt und mit Werten der nächsten 100sek befüllt
        pressure_test_values = []
        # durchläuft von links nach rechts
        if reversed_func is False:
            if ventilation_area_border is not None:
                for i in range(ventilation_area_border, min(ventilation_area_border + 10000, len(self.mask_edf_data[0]))):
                    pressure_test_values.append(self.mask_edf_data[0, i])
        # durchläuft von rechts nach links
        elif reversed_func is True:
            if ventilation_area_border is not None:
                for j in reversed(range(max(ventilation_area_border - 10000, 0), ventilation_area_border)):
                    pressure_test_values.append(self.mask_edf_data[0, j])

        pressure_values_sum = sum(pressure_test_values)
        pressure_values_count = len(pressure_test_values)
        average = pressure_values_sum / pressure_values_count
        # Durchschnitt wird berechnet um zu schauen, ob es der Beginn der Beatmung, oder nur ein Ausschlag in der Kurve war
        if pressure_test_values:
            # wenn Durchschnitt größer als 1 mbar, dann setze Beatmungsstartpunkt fest
            if average >= 1:
                return ventilation_area_border
            else:
                # suche nächsten Index, der unter 1mbar liegt.
                # durchläuft von links nach rechts
                if reversed_func is False:
                    for i in range(ventilation_area_border, len(self.mask_edf_data[0]) - 1):
                        if self.mask_edf_data[0, i] < 1:
                            new_start_index = i
                            break
                # durchläuft von rechts nach links
                if reversed_func is True:
                    for j in reversed(range(0, ventilation_area_border)):
                        if self.mask_edf_data[0, j] < 1:
                            new_start_index = j
                            break
                # Funktion wird rekursiv aufgerufen
                if new_start_index is not None:
                    return self.get_ventilation_area(new_start_index, reversed_func)

    # Funktion zur Ermittlung vom Anfang und Ende der Beatmung
    def get_ventilation_start_end(self):
        # Parameter auf True setzen, damit Funktion get_ventilation_area die Liste vorwärts durchläuft
        reversed_func = False

        # beginnt die Suche nach dem Beatmungsbereich, nach den Synchronisierungspunkten am Anfang
        start_index = int(float(self.start_analyses_index) * self.mask_edf_meta_data['sfreq'])
        ventilation_start = self.get_ventilation_area(start_index, reversed_func)

        # Parameter auf True setzen, damit Funktion get_ventilation_area die Liste rückwärts durchläuft
        reversed_func = True

        # beginnt die Suche nach dem Beatmungsbereich, nach den Synchronisierungspunkten am Ende
        start_index = int(float(self.end_analyses_index) * self.mask_edf_meta_data['sfreq'])
        ventilation_end = self.get_ventilation_area(start_index, reversed_func)

        return ventilation_start, ventilation_end

    # Funktion zum Ermitteln des am meist vorkommenden Drucks
    def get_pressure_median(self):
        start_index, end_index = self.get_ventilation_start_end()

        # Druckwerte >= 1 werden in Liste pressure_values durch List Comprehension gespeichert
        pressure_values = [i for i in self.mask_edf_data[0, start_index:end_index] if i >= 1]
        pressure_median = statistics.median(pressure_values)

        pressure_median_limit = pressure_median + (0.6 * pressure_median)

        return pressure_median_limit
