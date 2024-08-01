import numpy as np  # numpy ist eine Bibliothek für numerische Berechnungen in Python
import matplotlib.pyplot as plt  # Bibliothek für die Erstellung von Grafiken und Diagrammen in Python
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
        self.mask_sampling_frequency = None
        self.mask_edf_data = None
        self.mask_edf_times = None
        self.duration_mask = None
        self.device_sampling_frequency = None
        self.device_edf_data = None
        self.device_edf_times = None
        self.duration_device = None
        self.scale_factor = None
        self.time_difference_start = None
        self.time_difference_end = None
        self.pressure_median = None
        self.breath_search_start_point = None
        self.breath_search_end_point = None

    # Funktion zum Setzen eines Intervalls (Zeitspanne der Beatmung)
    def set_interval(self, value):
        self.interval = value

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

    # Funktion zum erneuten Plotten der Daten in einem 30-Sekunden Intervall
    def plot_edf_interval(self, starting_point, interval, breath_start, breath_end):
        try:
            # Berechnet den Endzeitpunkt des Intervalls
            end_point = starting_point + interval

            # Start- und Endindex für Mask- und Device-Kurve berechnen (Zeitpunkt * Abtastrate)
            mask_start_index = int(starting_point * self.mask_sampling_frequency)
            mask_end_index = int(end_point * self.mask_sampling_frequency)

            device_start_index = int((starting_point - self.time_difference_start[0]) * self.device_sampling_frequency)
            device_end_index = int((end_point - self.time_difference_end[0]) * self.device_sampling_frequency)

            # Skalierung der Device-Kurve
            scaled_device_data = self.scale_factor * self.device_edf_data[0, device_start_index:device_end_index]

            # Zeitintervall für Mask und Device erzeugen
            mask_interval = np.arange(starting_point, end_point, 1 / self.mask_sampling_frequency)
            device_interval = np.arange(starting_point, end_point, 1 / self.mask_sampling_frequency)

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

            # Plottet die neuen Kurven für das Intervall
            ax.plot(mask_interval, self.mask_edf_data[0, mask_start_index:mask_end_index][:min_length], label="Mask", color="blue")
            ax.plot(device_interval, scaled_device_data, label="Device", color="red")
            ax.axhline(self.pressure_median, label="Schwellenwert", color="green", linestyle="dashed")

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

        except Exception as error_code:
            print(f"\033[31m ERROR \033[33m Fehler beim Plotten der Daten: \033[93m {error_code} \033[0m")
            print(f"\033[33m Klasse: \033[93m AtemzugValidierungLogic \033[33m / Funktion: \033[93m plot_edf_interval() \033[0m")

    # Funktion ruft zwei weiter Funktionen auf, um Startpunkt des Intervalls festzulegen und zu plotten
    def create_interval_window(self, starting_point_entry, starting_point, backward, forward, fast_backward, fast_forward, breath_start, breath_end):
        self.set_starting_point(starting_point_entry, starting_point, backward, forward, fast_backward, fast_forward)
        self.plot_edf_interval(self.starting_point, self.interval, breath_start, breath_end)

    # Funktion zum Ermitteln der Synchronisierungspunkte
    def get_sync_points(self):
        start_sync_point = None
        end_sync_point = None

        start_index = 0
        # For-Schleife läuft vom start_index solange durch, bis es den Anfang des 1ten Synchronisierungspunktes ermittelt hat
        for i in range(start_index, len(self.mask_edf_data[0]) - 1):
            if self.mask_edf_data[0, i] > 2:
                start_sync_point = i / self.mask_sampling_frequency
                break

        start_index = int((self.duration_mask - 1) * self.mask_sampling_frequency)
        # For-Schleife läuft rückwärts vom start_index solange durch, bis es das Ende des 2ten Synchronisierungspunktes ermittelt hat
        for i in reversed(range(start_index)):
            if self.mask_edf_data[0, i] > 2:
                end_sync_point = i / self.mask_sampling_frequency
                break

        # Festlegen der Punkte zwischen welchen die Atemzüge ermittelt werden sollen
        self.breath_search_start_point = int(start_sync_point + 60)
        self.breath_search_end_point = int(end_sync_point - 60)

        # Startpunkt wird um 5sec und Endpunkt um 30sec nach links verschoben
        start_sync_point = int(start_sync_point - 5)
        end_sync_point = int(end_sync_point - 30)

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
            start_index = int(sync_point * self.mask_sampling_frequency)
            end_index = int((sync_point + 60) * self.mask_sampling_frequency)

            # Begrenze beide Kurven auf das Intervall zwischen start_index und end_index
            mask_timeframe = self.mask_edf_data[:, start_index:end_index]
            device_timeframe = self.device_edf_data[:, start_index:end_index]

            # Finde die Indexe der Maximalwerte im festgelegten Zeitrahmen
            mask_max_index = np.argmax(mask_timeframe, axis=1)
            device_max_index = np.argmax(device_timeframe, axis=1)

            # Finde die Zeitpunkte der maximalen Werte
            mask_sync_point_times = (start_index + mask_max_index) / self.mask_sampling_frequency
            device_sync_point_times = (start_index + device_max_index) / self.device_sampling_frequency

            # Errechnet die Zeitdifferenz zwischen den beiden Maximalwerten der Kurven
            results[i] = mask_sync_point_times - device_sync_point_times
            sync_point = end_sync_point

        time_difference_start, time_difference_end = results

        return time_difference_start, time_difference_end

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
        mask_time = np.arange(0, self.duration_mask, 1 / self.mask_sampling_frequency)
        device_time = np.arange(0 + self.time_difference_start[0], self.duration_device + self.time_difference_end[0],
                                1 / self.device_sampling_frequency)

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

    # Funktion um EDF-Datei zu einzulesen
    def read_edf_file(self, mask_edf_file_path, device_edf_file_path):
        try:
            if self.raw_mask_edf_data is None or self.raw_device_edf_data is None:
                # EDF Daten werden in ein Raw-Objekt geladen
                self.raw_mask_edf_data = mne.io.read_raw_edf(mask_edf_file_path)
                self.raw_device_edf_data = mne.io.read_raw_edf(device_edf_file_path)

                # Daten für mask.edf Datei
                self.mask_sampling_frequency = self.raw_mask_edf_data.info["sfreq"]  # gibt Abtastrate (sfreq "Sampling Frequency") zurück
                self.mask_edf_data = self.raw_mask_edf_data.get_data()  # gibt Kanäle und Zeitpunkte zurück (n_channels, n_times)
                self.mask_edf_times = self.raw_mask_edf_data.n_times  # gibt Anzahl der Zeitpunkte zurück
                # Dauer der Beatmung = Anzahl der Zeitpunkte / Abtastrate
                self.duration_mask = self.mask_edf_times / self.mask_sampling_frequency

                # Daten für device.edf Datei
                self.device_sampling_frequency = self.raw_device_edf_data.info["sfreq"]
                self.device_edf_data = self.raw_device_edf_data.get_data()
                self.device_edf_times = self.raw_device_edf_data.n_times
                self.duration_device = self.device_edf_times / self.device_sampling_frequency

            self.plot_edf_data()

        # sollte ein Fehler beim Plotten der EDF-Datei auftreten, gib diese Meldung aus
        except Exception as error_code:
            print(f"\033[31m ERROR \033[33m Fehler beim Verarbeiten der EDF-Datei: \033[93m {error_code} \033[0m")
            print(f"\033[33m Klasse: \033[93m AtemzugValidierungLogic \033[33m / Funktion: \033[93m read_edf_file() \033[0m")
