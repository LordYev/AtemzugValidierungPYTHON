import numpy as np  # numpy ist eine Bibliothek für numerische Berechnungen in Python
import matplotlib.pyplot as plt  # Bibliothek für die Erstellung von Grafiken und Diagrammen in Python
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import loadmat  # ermöglicht das Lesen und Schreiben von MATLAB-Dateien
import mne


class AtemzugValidierungLogic:
    def __init__(self):
        # Instanzvariablen (können nur innerhalb der Klasse verwendet werden)
        self.y_min = -5.0  # y-Achse Minimalwert
        self.y_max = 40.0  # y-Achse Maximalwert
        self.interval = 30.0  # Beatmungsintervall
        self.starting_point = 0.0  # Startpunkt des Intervalls
        self.duration_to_next_anomaly = 0  # Dauer bis zur nächsten Anomalie
        self.duration_to_previous_anomaly = 0  # Dauer bis zur vorherigen Anomalie
        self.canvas = None
        self.raw_mask_edf_data = None
        self.raw_device_edf_data = None
        self.mask_edf_meta_data = None
        self.mask_edf_data = None
        self.mask_edf_times = None
        self.duration_mask = None
        self.device_edf_meta_data = None
        self.device_edf_data = None
        self.device_edf_times = None
        self.duration_device = None
        self.scale_factor = None
        self.time_difference_start = None
        self.time_difference_end = None
        self.pressure_median = None
        self.breath_search_start_point = None
        self.breath_search_end_point = None

    # Funktion zur Übergabe der Eingabe des Benutzers an die Variable starting_point
    def set_starting_point(self, starting_point_entry, starting_point, backward, forward, fast_backward, fast_forward):
        start_point = float(starting_point)

        # Hier wird geschaut ob der Benutzer rückwerts oder vorwärts im Plot navigieren möchte,
        # oder ob nur ein Intervall festgelegt wurde
        if backward is True:
            self.starting_point = start_point - self.interval
        elif forward is True:
            self.starting_point = start_point + self.interval
        elif fast_backward is True:
            self.starting_point = start_point - self.duration_to_previous_anomaly
        elif fast_forward is True:
            self.starting_point = start_point + self.duration_to_next_anomaly
        else:
            self.starting_point = float(starting_point_entry)

    # Funktion zum Setzen eines Intervalls (Zeitspanne der Beatmung)
    def set_interval(self, value):
        self.interval = value

    # Funktion zum Aufrufen mehrerer Funktionen zeitgleich
    def use_multiple_funcs(self, starting_point_entry, starting_point, backward, forward, fast_backward, fast_forward, breath_start, breath_end):
        self.set_starting_point(starting_point_entry, starting_point, backward, forward, fast_backward, fast_forward)
        self.plot_edf_interval(self.mask_edf_meta_data, self.mask_edf_data, self.device_edf_meta_data, self.device_edf_data, self.starting_point,
                               self.interval, breath_start, breath_end)

    # Funktion zum Erstellen einer Matplotlib-Figur
    def create_figure(self):
        # erstellt eine Matplotlib-Figur mit einer Zeile & Spalte (Breite x Höhe)
        fig, ax = plt.subplots(1, 1, figsize=(9, 4))
        ax.set_ylim(self.y_min, self.y_max)
        ax.set_ylabel("Druck in mbar")
        ax.set_xlabel("Zeit in Sekunden")
        ax.grid(True)

        # Setze die Schritte für die y-Achse auf 2,5
        ax.yaxis.set_major_locator(plt.MultipleLocator(2.5))

        return fig, ax

    # Funktion zum Ermitteln der Synchronisierungspunkte
    def get_sync_points(self):
        start_sync_point = None
        end_sync_point = None

        start_index = int(0 * self.mask_edf_meta_data["sfreq"])

        # For-Schleife läuft vom start_index solange durch, bis es den Anfang des 1ten Synchronisierungspunktes ermittelt hat
        for i in range(start_index, len(self.mask_edf_data[0]) - 1):
            if self.mask_edf_data[0, i] > 2:
                start_sync_point = i / 10000
                break

        start_index = int((self.duration_mask - 1) * self.mask_edf_meta_data["sfreq"])

        # For-Schleife läuft rückwärts vom start_index solange durch, bis es das Ende des 2ten Synchronisierungspunktes ermittelt hat
        for i in reversed(range(start_index)):
            if self.mask_edf_data[0, i] > 2:
                end_sync_point = i / 10000
                break

        # Festlegen der Punkte zwischen welchen die Atemzüge ermittelt werden sollen
        self.breath_search_start_point = int((start_sync_point + 0.6) * self.mask_edf_meta_data["sfreq"])
        self.breath_search_end_point = int((end_sync_point - 0.6) * self.mask_edf_meta_data["sfreq"])

        # Startpunkt wird um 5sec und Endpunkt um 30sec nach links verschoben
        start_sync_point = int((start_sync_point - 0.05) * self.mask_edf_meta_data["sfreq"])
        end_sync_point = int((end_sync_point - 0.3) * self.mask_edf_meta_data["sfreq"])

        return start_sync_point, end_sync_point

    # Funktion zum Synchronisieren der beiden Kurven aus den EDF-Dateien
    def sync_edf_data(self):
        # Beide Synchronisierungspunkte werden definiert
        start_sync_point, end_sync_point = self.get_sync_points()
        sync_point = start_sync_point
        time_difference_start = None
        time_difference_end = None
        results = [time_difference_start, time_difference_end]

        for i in range(len(results)):
            # Bestimme Start- und Endpunkt des 1ten Synchronisierungspunktes
            start_index = int(sync_point * self.mask_edf_meta_data["sfreq"])
            end_index = int((sync_point + 60) * self.mask_edf_meta_data["sfreq"])

            # Begrenze beide Kurven auf das Intervall zwischen start_index und end_index
            mask_timeframe = self.mask_edf_data[:, start_index:end_index]
            device_timeframe = self.device_edf_data[:, start_index:end_index]

            # Finde die Indexe der Maximalwerte im festgelegten Zeitrahmen
            mask_max_index = np.argmax(mask_timeframe, axis=1)
            device_max_index = np.argmax(device_timeframe, axis=1)

            # Finde die Zeitpunkte der maximalen Werte
            mask_sync_point_times = (start_index + mask_max_index) / self.mask_edf_meta_data["sfreq"]
            device_sync_point_times = (start_index + device_max_index) / self.device_edf_meta_data["sfreq"]

            # Errechnet die Zeitdifferenz zwischen den beiden Maximalwerten der Kurven
            results[i] = mask_sync_point_times - device_sync_point_times
            sync_point = end_sync_point

        time_difference_start, time_difference_end = results

        """# Ausgaben in der Konsole zur Kontrolle
        print(f"ENDZEIT: {end_index}")
        print("Mask: ", mask_sync_points)
        print("Device: ", device_sync_points)
        print("Mask Zeitpunkte: ", mask_sync_point_times)
        print("Device Zeitpunkte: ", device_sync_point_times)
        print("Differenz: ", time_difference)"""

        return time_difference_start, time_difference_end

    # Funktion zum erneuten Plotten der Daten in einem 30-Sekunden Intervall
    def plot_edf_interval(self, mask_edf_meta_data, mask_edf_data, device_edf_meta_data, device_edf_data, starting_point, interval,
                          breath_start, breath_end):
        try:
            # Berechnet den Endzeitpunkt des Intervalls
            end_point = starting_point + interval

            # Start- und Endindex für Mask- und Device-Kurve berechnen (Zeitpunkt * Abtastrate)
            mask_start_index = int(starting_point * mask_edf_meta_data["sfreq"])
            mask_end_index = int(end_point * mask_edf_meta_data["sfreq"])

            device_start_index = int((starting_point - self.time_difference_start[0]) * device_edf_meta_data["sfreq"])
            device_end_index = int((end_point - self.time_difference_end[0]) * device_edf_meta_data["sfreq"])

            # Skalierung der Device-Kurve
            scaled_device_data = self.scale_factor * device_edf_data[0, device_start_index:device_end_index]

            # Zeitintervall für Mask und Device erzeugen
            mask_interval = np.arange(starting_point, end_point, 1 / mask_edf_meta_data["sfreq"])
            device_interval = np.arange(starting_point, end_point, 1 / mask_edf_meta_data["sfreq"])

            # Bestimme das kürzere Array aus Mask oder Device
            min_length = min(len(mask_interval), len(device_interval))

            # Passe die Längen der Arrays (Zeitpunkte) an
            mask_interval = mask_interval[:min_length]
            device_interval = device_interval[:min_length]
            scaled_device_data = scaled_device_data[:min_length]

            # Erstellt/Aktualisiert die vorhandene Figur und Achsen
            ax = plt.gca()

            # Entfernt alle vorhandenen Linien in den Achsen
            for line in ax.lines:
                line.remove()

            # Plottet die neuen Linien für das Intervall
            ax.plot(mask_interval, mask_edf_data[0, mask_start_index:mask_end_index][:min_length], label="Mask", color="blue")
            ax.plot(device_interval, scaled_device_data, label="Device", color="red")
            ax.axhline(self.pressure_median, label="Grenzwert", color="green", linestyle="dashed")

            # Wenn die übergebenen Variablen Zeitpunkte haben, dann soll dort jeweils eine Senkrechte Linie geplottet werden
            if breath_start and breath_end is not None:
                ax.axvline(float(breath_start), color='cyan')
                ax.axvline(float(breath_end), color='orange')

            # Setzt die Grenzen der x-Achse entsprechend den Zeitintervallen
            ax.set_xlim(mask_interval[0], device_interval[-1])

            # Aktualisierung des Labels zum Anzeigen der aktuellen Intervalldauer
            ax.set_xlabel(f"Zeit in Sekunden (aktuelle Intervalldauer: {int(self.interval)}sek)")

            ax.legend(loc="upper center", ncol=3)
            # Aktualisiert das Plot Fenster
            plt.draw()

            # Zeigt mir die Anzahl aktuell geöffneter Plots
            """num_figures = len(plt.get_fignums())
            print("Anzahl der geöffneten Figuren:", num_figures)"""

        except Exception as error_code:
            print(f"\033[93mFehler beim Plotten der Daten: {error_code}\033[0m")

    # Funktion um EDF-Datei zu einzulesen
    def read_edf_file(self, mask_edf_file_path, device_edf_file_path):
        # try-except Block welcher den gesamten Graphen plottet
        try:
            if self.raw_mask_edf_data is None or self.raw_device_edf_data is None:
                # EDF Daten werden in ein Raw-Objekt geladen
                self.raw_mask_edf_data = mne.io.read_raw_edf(mask_edf_file_path, preload=True)
                self.raw_device_edf_data = mne.io.read_raw_edf(device_edf_file_path, preload=True)

            # Daten für mask.edf Datei
            self.mask_edf_meta_data = self.raw_mask_edf_data.info
            self.mask_edf_data = self.raw_mask_edf_data.get_data()
            self.mask_edf_times = self.raw_mask_edf_data.n_times
            # Dauer der Beatmung = Gesamtanzahl der Zeitpunkte / Abtastrate (sfreq)
            self.duration_mask = self.mask_edf_times / self.mask_edf_meta_data["sfreq"]

            # Daten für device.edf Datei
            self.device_edf_meta_data = self.raw_device_edf_data.info
            self.device_edf_data = self.raw_device_edf_data.get_data()
            self.device_edf_times = self.raw_device_edf_data.n_times
            self.duration_device = self.device_edf_times / self.device_edf_meta_data["sfreq"]

            self.plot_edf_data()

        # sollte ein Fehler beim Plotten der EDF-Datei auftreten, gib diese Meldung aus
        except Exception as error_code:
            print(f"\033[93mFehler beim Verarbeiten der EDF-Datei: {error_code}\033[0m")

    # Funktion um EDF-Datei zu plotten
    def plot_edf_data(self):
        # Schließt alle geöffneten Plots
        plt.close("all")
        self.time_difference_start, self.time_difference_end = self.sync_edf_data()

        # Erstellt eine Figur in der geplottet wird
        fig, ax = self.create_figure()

        # Skalierungsfaktor für die Device-Kurve um diese passend zu stauchen/strecken
        self.scale_factor = (1 + self.time_difference_end[0] - self.time_difference_start[0])

        # Skalierung der Device-Kurve
        scaled_device_data = self.scale_factor * self.device_edf_data[0, :]

        # Erzeugt Arrays mit zeitpunkten für Mask- und Device-Kurve
        mask_time = np.arange(0, self.duration_mask, 1 / self.mask_edf_meta_data["sfreq"])
        device_time = np.arange(0 + self.time_difference_start[0],
                                self.duration_device + self.time_difference_end[0], 1 / self.device_edf_meta_data["sfreq"])

        # Bestimmt das kürzere Array aus Mask oder Device
        min_length = min(len(mask_time), len(device_time))

        # Passt die Längen der Arrays (Zeitpunkte) an
        mask_time = mask_time[:min_length]
        device_time = device_time[:min_length]
        scaled_device_data = scaled_device_data[:min_length]

        # Plot der Mask-Kurve und der skalierten Device-Kurve
        ax.plot(mask_time, self.mask_edf_data[0, :min_length], label="Mask", color="blue")
        ax.plot(device_time, scaled_device_data, label="Device", color="red")
        ax.legend(loc="upper center", ncol=3)

        # Tkinter-Canvas-Objekt wird erstellt und Figur wird gezeichnet
        canvas = FigureCanvasTkAgg(fig)
        canvas.draw()
        self.canvas = canvas

        # Zeigt mir die Anzahl aktuell geöffneter Plots
        """num_figures = len(plt.get_fignums())
        print("Anzahl der geöffneten Figuren:", num_figures)"""

    # Funktion um MAT-Datei zu plotten
    def read_mat_file(self, mat_file_path):
        try:
            mat_file = loadmat(mat_file_path)  # öffnet die MAT-Datei mit scipy und speichert die Daten in mat_file

            # Abfrage ob Schlüssel "rawDevice" in der MAT-Datei enthalten ist
            if "rawDevice" in mat_file:
                my_data = mat_file["rawDevice"]  # extrahiert die Daten unter dem Schlüssel "rawDevice" und speichert diese unter my_data
                self.plot_mat_data(my_data)
                print(my_data)  # druckt zum Test die Daten in der Konsole aus (NICHT NOTWENDIG)

            # Abfrage ob Schlüssel "rawMask" in der MAT-Datei enthalten ist
            elif "rawMask" in mat_file:
                my_data = mat_file["rawMask"]
                self.plot_mat_data(my_data)
                print(my_data)  # druckt zum Test die Daten in der Konsole aus (NICHT NOTWENDIG)

            else:
                print("Schlüssel 'my_data' nicht gefunden in der .mat-Datei.")

        # es wird eine Fehlermeldung angezeigt, sollte ein Fehler beim Aufrufen einer MAT-Datei auftreten
        except Exception as error_code:
            print(f"\033[93mFehler beim Verarbeiten der MAT-Datei: {error_code}\033[0m")

    def plot_mat_data(self, my_data):
        fig, ax = plt.subplots(1, 1, figsize=(10, 4))
        ax.plot(my_data)
        ax.set_xlabel("X-Achse")
        ax.set_ylabel("Y-Achse")
        ax.set_title("Grafische Darstellung der Daten aus der .mat-Datei")
        canvas = FigureCanvasTkAgg(fig)

        if hasattr(self, "canvas") and self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = canvas
