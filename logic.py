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
        self.pressure_limit = None

    # Funktion zur Übergabe der Eingabe des Benutzers an die Variable starting_point
    def set_starting_point(self, starting_point_entry, starting_point, backward, forward):
        start_point = float(starting_point)

        # Hier wird geschaut ob der Benutzer rückwerts oder vorwärts im Plot navigieren möchte,
        # oder ob nur ein Intervall festgelegt wurde
        if backward is True:
            self.starting_point = start_point - self.interval
        elif forward is True:
            self.starting_point = start_point + self.interval
        else:
            self.starting_point = float(starting_point_entry.get())

    # Funktion zum Setzen eines Intervalls (Zeitspanne der Beatmung)
    def set_interval(self, value):
        self.interval = value

    # Funktion zum Aufrufen mehrerer Funktionen zeitgleich
    def use_multiple_funcs(self, starting_point_entry, starting_point, backward, forward):
        self.set_starting_point(starting_point_entry, starting_point, backward, forward)
        self.plot_edf_interval(self.mask_edf_meta_data, self.mask_edf_data, self.device_edf_meta_data, self.device_edf_data, self.starting_point,
                               self.interval)

    # Funktion zum Erstellen einer Matplotlib-Figur
    def create_figure(self):
        # erstellt eine Matplotlib-Figur mit einer Zeile & Spalte (Breite 10 & Höhe 6 Einheiten)
        fig, ax = plt.subplots(1, 1, figsize=(9, 4))
        ax.set_ylim(self.y_min, self.y_max)
        ax.set_ylabel('Druck in mbar')
        ax.set_xlabel('Zeit in Sekunden')
        ax.grid(True)

        # Setze die Schritte für die y-Achse auf 2,5
        ax.yaxis.set_major_locator(plt.MultipleLocator(2.5))

        return fig, ax

    # Funktion zum Synchronisieren der beiden Kurven aus den EDF-Dateien
    def sync_edf_data(self):
        # Bestimme Start- und Endpunkt der ersten 2000sek
        start_index = int(0 * self.mask_edf_meta_data['sfreq'])
        end_index = int(2000 * self.mask_edf_meta_data['sfreq'])

        # Begrenze beide Kurven auf 2000sek
        mask_1k_s_timeframe = self.mask_edf_data[:, start_index:end_index]
        device_1k_s_timeframe = self.device_edf_data[:, start_index:end_index]

        # Finde die Indexe der Maximalwerte im festgelegten Zeitrahmen
        mask_max_index = np.argmax(mask_1k_s_timeframe, axis=1)
        device_max_index = np.argmax(device_1k_s_timeframe, axis=1)

        # Finde die Zeitpunkte der maximalen Werte
        mask_sync_point_times = (start_index + mask_max_index) / self.mask_edf_meta_data['sfreq']
        device_sync_point_times = (start_index + device_max_index) / self.device_edf_meta_data['sfreq']

        # Errechnet die Zeitdifferenz zwischen den beiden Maximalwerten der Kurven
        time_difference_start = mask_sync_point_times - device_sync_point_times

        # Finde die Maximalwerte im festgelegten Zeitrahmen (NUR ZUM ANZEIGEN DER Y-WERTE)
        '''mask_sync_points = np.max(mask_1k_s_timeframe, axis=1)
        device_sync_points = np.max(device_1k_s_timeframe, axis=1)'''

        # ------------Ab hier gleicher Prozess für die letzten 2000sek------------

        # Bestimme Start- und Endpunkt der letzten 2000sek
        start_index_end = int((self.duration_mask - 2000) * self.mask_edf_meta_data['sfreq'])
        end_index_end = int(self.duration_mask * self.mask_edf_meta_data['sfreq'])

        # Begrenze beide Kurven auf 2000sek
        mask_1k_s_timeframe_end = self.mask_edf_data[:, start_index_end:end_index_end]
        device_1k_s_timeframe_end = self.device_edf_data[:, start_index_end:end_index_end]

        # Finde die Indexe der Maximalwerte im festgelegten Zeitrahmen
        mask_max_index_end = np.argmax(mask_1k_s_timeframe_end, axis=1)
        device_max_index_end = np.argmax(device_1k_s_timeframe_end, axis=1)

        # Finde die Zeitpunkte der maximalen Werte
        mask_sync_point_times_end = (start_index_end + mask_max_index_end) / self.mask_edf_meta_data['sfreq']
        device_sync_point_times_end = (start_index_end + device_max_index_end) / self.device_edf_meta_data['sfreq']

        # Errechnet die Zeitdifferenz zwischen den beiden Maximalwerten der Kurven
        time_difference_end = mask_sync_point_times_end - device_sync_point_times_end

        """# Ausgaben in der Konsole zur Kontrolle
        print(f"ENDZEIT: {end_index}")
        print("Mask: ", mask_sync_points)
        print("Device: ", device_sync_points)
        print("Mask Zeitpunkte: ", mask_sync_point_times)
        print("Device Zeitpunkte: ", device_sync_point_times)
        print("Differenz: ", time_difference)"""

        return time_difference_start, time_difference_end

    # Funktion zum erneuten Plotten der Daten in einem 30-Sekunden Intervall
    def plot_edf_interval(self, mask_edf_meta_data, mask_edf_data, device_edf_meta_data, device_edf_data, starting_point, interval):
        try:
            # Berechnet den Endzeitpunkt des Intervalls
            end_point = starting_point + interval

            # Start- und Endindex für Mask- und Device-Kurve berechnen (Zeitpunkt * Abtastrate)
            mask_start_index = int(starting_point * mask_edf_meta_data['sfreq'])
            mask_end_index = int(end_point * mask_edf_meta_data['sfreq'])
            '''device_start_index = int(starting_point * device_edf_meta_data['sfreq'])
            device_end_index = int(end_point * device_edf_meta_data['sfreq'])'''
            device_start_index = int((starting_point - self.time_difference_start[0]) * device_edf_meta_data['sfreq'])
            device_end_index = int((end_point - self.time_difference_end[0]) * device_edf_meta_data['sfreq'])

            # Skalierung der Device-Kurve
            scaled_device_data = self.scale_factor * device_edf_data[0, device_start_index:device_end_index]

            # Zeitintervall für Mask und Device erzeugen
            '''mask_interval = np.arange(starting_point, end_point, 1 / mask_edf_meta_data['sfreq'])
            device_interval = np.arange(starting_point + self.time_difference_start[0],
                                        end_point + self.time_difference_end[0], 1 / mask_edf_meta_data['sfreq'])'''
            mask_interval = np.arange(starting_point, end_point, 1 / mask_edf_meta_data['sfreq'])
            device_interval = np.arange(starting_point, end_point, 1 / mask_edf_meta_data['sfreq'])

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
            ax.plot(mask_interval, mask_edf_data[0, mask_start_index:mask_end_index][:min_length], label='Mask', color='blue')
            ax.plot(device_interval, scaled_device_data, label='Device', color='red')

            ax.axhline(self.pressure_limit, label='Grenzwert', color='green', linestyle='dashed')
            ax.legend(loc='upper center', ncol=3)

            ###################################################################
            # TEST ATEMZUG MARKIERUNG
            # Atemzug Nr. 120 und 121. NACHFRAGEN
            ax.axvline(15901.76, color='cyan')
            ax.axvline(15901.84, color='orange')

            ax.axvline(15901.96, color='cyan')
            ax.axvline(15902.07, color='orange')

            ax.axvline(15902.12, color='cyan')
            ax.axvline(15902.27, color='orange')

            ##########################################################################################

            # Setzt die Grenzen der x-Achse entsprechend den Zeitintervallen
            ax.set_xlim(mask_interval[0], device_interval[-1])

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
            self.duration_mask = self.mask_edf_times / self.mask_edf_meta_data['sfreq']

            # Daten für device.edf Datei
            self.device_edf_meta_data = self.raw_device_edf_data.info
            self.device_edf_data = self.raw_device_edf_data.get_data()
            self.device_edf_times = self.raw_device_edf_data.n_times
            self.duration_device = self.device_edf_times / self.device_edf_meta_data['sfreq']

            self.plot_edf_data()

        # sollte ein Fehler beim Plotten der EDF-Datei auftreten, gib diese Meldung aus
        except Exception as error_code:
            print(f"\033[93mFehler beim Verarbeiten der EDF-Datei: {error_code}\033[0m")

    # Funktion um EDF-Datei zu plotten
    def plot_edf_data(self):
        # Schließt alle geöffneten Plots
        plt.close('all')
        self.time_difference_start, self.time_difference_end = self.sync_edf_data()

        # Erstellt eine Figur in der geplottet wird
        fig, ax = self.create_figure()

        # Skalierungsfaktor für die Device-Kurve um diese passend zu stauchen/strecken
        self.scale_factor = (1 + self.time_difference_end[0] - self.time_difference_start[0])

        # Skalierung der Device-Kurve
        scaled_device_data = self.scale_factor * self.device_edf_data[0, :]

        # Erzeugt Arrays mit zeitpunkten für Mask- und Device-Kurve
        mask_time = np.arange(0, self.duration_mask, 1 / self.mask_edf_meta_data['sfreq'])
        device_time = np.arange(0 + self.time_difference_start[0],
                                self.duration_device + self.time_difference_end[0], 1 / self.device_edf_meta_data['sfreq'])

        # Bestimmt das kürzere Array aus Mask oder Device
        min_length = min(len(mask_time), len(device_time))

        # Passt die Längen der Arrays (Zeitpunkte) an
        mask_time = mask_time[:min_length]
        device_time = device_time[:min_length]
        scaled_device_data = scaled_device_data[:min_length]

        # Plot der Mask-Kurve und der skalierten Device-Kurve
        ax.plot(mask_time, self.mask_edf_data[0, :min_length], label='Mask', color='blue')
        ax.plot(device_time, scaled_device_data, label='Device', color='red')
        ax.legend(loc='upper center', ncol=3)

        '''self.pressure_limit = self.get_pressure_limit()
        ax.axhline(self.pressure_limit, label='Grenzwert', color='green', linestyle='dashed')
        '''

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
            if 'rawDevice' in mat_file:
                my_data = mat_file['rawDevice']  # extrahiert die Daten unter dem Schlüssel "rawDevice" und speichert diese unter my_data
                self.plot_mat_data(my_data)
                print(my_data)  # druckt zum Test die Daten in der Konsole aus (NICHT NOTWENDIG)

            # Abfrage ob Schlüssel "rawMask" in der MAT-Datei enthalten ist
            elif 'rawMask' in mat_file:
                my_data = mat_file['rawMask']
                self.plot_mat_data(my_data)
                print(my_data)  # druckt zum Test die Daten in der Konsole aus (NICHT NOTWENDIG)

            else:
                print('Schlüssel "my_data" nicht gefunden in der .mat-Datei.')

        # es wird eine Fehlermeldung angezeigt, sollte ein Fehler beim Aufrufen einer MAT-Datei auftreten
        except Exception as error_code:
            print(f"\033[93mFehler beim Verarbeiten der MAT-Datei: {error_code}\033[0m")

    def plot_mat_data(self, my_data):
        fig, ax = plt.subplots(1, 1, figsize=(10, 4))
        ax.plot(my_data)
        ax.set_xlabel('X-Achse')
        ax.set_ylabel('Y-Achse')
        ax.set_title('Grafische Darstellung der Daten aus der .mat-Datei')
        canvas = FigureCanvasTkAgg(fig)

        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = canvas
