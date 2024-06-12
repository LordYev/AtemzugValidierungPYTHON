import tkinter as tk  # tkinter wird zum Bau der GUI verwendet
from tkinter import ttk # ermöglicht den Bau des Treeview (Listenbereich mit den Atemzügen)
from tkinter import filedialog  # filedialog = Modul aus tkinter um Dateien auswählen zu können
from logic import AtemzugValidierungLogic
from breath import AtemzugValidierungBreaths
import os


class AtemzugValidierungGUI(tk.Tk):
    # Konstruktor der Klasse AtemzugValidierungGUI()
    def __init__(self, master=None):
        super().__init__(master)  # erstellt das Hauptfenster "self"
        self.logic = AtemzugValidierungLogic()
        self.breath = AtemzugValidierungBreaths()
        self.mask_edf_path = None
        self.device_edf_path = None  # Instanzvariable um den Pfad der EDF-Datei speichern
        self.title("Atemzug Validierung")  # legt Titel für Hauptfenster fest
        self.geometry("1250x1000")  # legt Fenster größe fest
        self.starting_point_entry = None
        self.starting_point = None
        self.forward = False
        self.backward = False
        self.backwards_button = None
        self.forwards_button = None
        self.interval_button = None
        self.save_interval_button = None
        self.full_graph_button = None
        self.breath_list_area = None

        # Folgend werden GUI Elemente gebaut
        '''self.load_mat_file_button = tk.Button(self, text="MAT Datei auswählen", command=lambda: self.load_mat_file(self.mat_file_path_text))
        self.load_mat_file_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")'''

        self.load_edf_file_button = tk.Button(self, text="EDF Ordner auswählen", command=lambda: self.load_edf_files(self.folder_path_text))
        self.load_edf_file_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        '''self.mat_file_path_text = tk.Text(self, height=1, width=100, wrap=tk.NONE)
        self.mat_file_path_text.grid(row=0, column=1, columnspan=10, padx=5, pady=5, sticky="w")'''

        self.folder_path_text = tk.Text(self, height=1, width=100, wrap=tk.NONE)
        self.folder_path_text.grid(row=1, column=1, columnspan=10, padx=5, pady=5, sticky="w")

        self.gui_edf_plot_area()
        self.gui_list_area()

    # Funktion zur erstellung der GUI Elemente für den EDF-Graphen
    def gui_edf_plot_area(self):
        # Label für starting_point_entry
        starting_point_label = tk.Label(self, text="Startpunkt des Intervalls:")
        starting_point_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Eingabefeld zur Eingabe des gewünschten Startpunktes
        self.starting_point_entry = tk.Entry(self, width=8)
        self.starting_point_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Label für interval_entry
        interval_label = tk.Label(self, text="Gewünschtes Intervall (Standard sind 30sek festgelegt):")
        interval_label.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Button zum Festlegen eines 30sek Intervalls
        thirty_sec_interval_button = tk.Button(self, text="30sek", command=lambda: self.logic.set_interval(30))
        thirty_sec_interval_button.grid(row=3, column=3, padx=5, pady=5)

        # Button zum Festlegen eines 60sek Intervalls
        sixty_sec_interval_button = tk.Button(self, text="60sek", command=lambda: self.logic.set_interval(60))
        sixty_sec_interval_button.grid(row=3, column=4, padx=5, pady=5)

        # Eingabefeld zur Eingabe des gewünschten Intervalls
        interval_entry = tk.Entry(self, width=8)
        interval_entry.grid(row=3, column=5, padx=5, pady=5, sticky="w")

        # Button zum Speichern des Intervalls
        self.save_interval_button = tk.Button(self, text="Intervall speichern",
                                              command=lambda: self.logic.set_interval(float(interval_entry.get())), state="disabled")
        self.save_interval_button.grid(row=3, column=6, padx=5, pady=5)

        # Button um die ganze Grafik wieder anzuzeigen
        self.full_graph_button = tk.Button(self, text="Gesamten Graphen anzeigen",
                                           command=lambda: self.plot_back_edf_file(self.mask_edf_path, self.device_edf_path), state="disabled")
        self.full_graph_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        # Button zum Anzeigen eines Intervalls in der Messung
        self.interval_button = tk.Button(self, text="Intervall anzeigen", command=lambda: self.set_starting_point(), state="disabled")
        self.interval_button.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Button zum rückwärts Navigieren im Plot
        self.backwards_button = tk.Button(self, text="<", command=lambda: self.go_backwards(), state="disabled")
        self.backwards_button.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Button zum vorwärts Navigieren im Plot
        self.forwards_button = tk.Button(self, text=">", command=lambda: self.go_forwards(), state="disabled")
        self.forwards_button.grid(row=4, column=2, padx=50, pady=5, sticky="w")

    # Funktion zur erstellung des Bereiches, in dem die Liste der Atemzüge angezeigt werden soll
    def gui_list_area(self):
        # Erstellt ein Frame für die Liste und Scrollbar
        frame = ttk.Frame(self)
        frame.grid(row=5, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.breath_list_area = ttk.Treeview(frame, columns=("column_number", "column_start", "column_end", "column_is_breath", "column_comment"),
                                             height=15)

        self.breath_list_area.column("#0", width=0, stretch=tk.NO)  # Phantomspalte. Ist immer da, wird aber nicht benötigt
        self.breath_list_area.column("column_number", anchor="e", width=40, minwidth=40)
        self.breath_list_area.column("column_start", anchor="e", width=100, minwidth=100)
        self.breath_list_area.column("column_end", anchor="e", width=100, minwidth=100)
        self.breath_list_area.column("column_is_breath", anchor="e", width=70, minwidth=70)
        self.breath_list_area.column("column_comment", anchor="w", width=600, minwidth=600)

        # self.breath_list_area.heading("#0", text="Test", anchor="w")
        self.breath_list_area.heading("column_number", text="Nr", anchor="w")
        self.breath_list_area.heading("column_start", text="Start", anchor="w")
        self.breath_list_area.heading("column_end", text="Ende", anchor="w")
        self.breath_list_area.heading("column_is_breath", text="Atemzug?", anchor="w")
        self.breath_list_area.heading("column_comment", text="Kommentar", anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.breath_list_area.yview)
        self.breath_list_area.configure(yscrollcommand=scrollbar.set)

        self.breath_list_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # beim Auswählen eines Atemzuges in der Liste wird eine Aktion ausgeführt
        '''self.breath_list_area.bind("<<TreeviewSelect>>", self.on_tree_select)'''

        # Funktion, welche beim Auswählen ines Datensatzes ausgeführt werden soll
    '''def on_tree_select(self, event):
        selected_item = self.breath_list_area.selection()[0]  # Erster ausgewählter Eintrag
        item_values = self.breath_list_area.item(selected_item, "values")
        print("Ausgewählter Datensatz:", item_values[1], item_values[2])'''

    # Funktion zum Befüllen der list_area
    def fill_list_area(self):
        for i in self.breath.breath_list:
            # Die Zeitpunkte werden auf zwei Nachkommastellen formatiert
            value2 = f"{i[1]:.2f}"
            value3 = f"{i[2]:.2f}"

            self.breath_list_area.insert("", "end", values=(i[0], value2, value3, "1", "-"))

    # Funktion zum Leeren der list_area
    def clear_list_area(self):
        for item in self.breath_list_area.get_children():
            self.breath_list_area.delete(item)

    # Funktion um den Startpunkt des Intervalls in einer Variable abzuspeichern
    # Zusätzlich werden die Buttons backwards_button & forwards_button freigegeben
    def set_starting_point(self):
        self.backwards_button.config(state="normal")
        self.forwards_button.config(state="normal")
        self.starting_point = self.starting_point_entry.get()
        self.logic.use_multiple_funcs(self.starting_point_entry, self.starting_point, self.forward, self.backward)
        self.determine_breaths_in_interval(self.starting_point, self.logic.interval)

    # Funktion um im Plot rückwärts zu navigieren
    def go_backwards(self):
        self.backward = True
        self.logic.use_multiple_funcs(self.starting_point_entry, self.starting_point, self.backward, self.forward)
        self.starting_point = self.logic.starting_point
        self.determine_breaths_in_interval(self.starting_point, self.logic.interval)
        self.backward = False

    # Funktion um im Plot vorwärts zu navigieren
    def go_forwards(self):
        self.forward = True
        self.logic.use_multiple_funcs(self.starting_point_entry, self.starting_point, self.backward, self.forward)
        self.starting_point = self.logic.starting_point
        self.determine_breaths_in_interval(self.starting_point, self.logic.interval)
        self.forward = False

    # Funktion um einen festen Graphen wieder zugeben
    def update_canvas(self):
        canvas = self.logic.canvas.get_tk_widget()
        canvas.grid(row=2, column=0, columnspan=10, padx=5, pady=5, sticky='w')

    def determine_breaths(self):
        # Übergabe der Zeitpunkte zwischen welchen die Atemzüge ermittelt werden
        self.breath.start_analyses_index = self.logic.breath_search_start_point
        self.breath.end_analyses_index = self.logic.breath_search_end_point

        # Atemzüge werden ermittelt und in Liste gespeichert
        self.breath.breath_list = self.breath.get_breaths()
        # Übergibt Grenzwert aus breath an logic
        self.logic.pressure_limit = self.breath.pressure_limit

        # Entsperrt Buttons
        self.interval_button.config(state="normal")
        self.save_interval_button.config(state="normal")
        self.full_graph_button.config(state="normal")

        self.clear_list_area()
        self.fill_list_area()

    def determine_breaths_in_interval(self, interval_start, interval_duration):
        self.clear_list_area()
        interval_end = int(interval_start) + int(interval_duration)

        # Ermittlung des ersten Atemzuges im Intervall
        first_breath_start = None
        for i in self.breath.breath_list:
            if i[1] >= int(interval_start):
                first_breath_start = i[0] - 1
                break

        # Füllt die Liste mit den im Plot angezeigten Atemzügen
        for i in self.breath.breath_list[first_breath_start:]:
            if interval_end >= i[2]:
                value2 = f"{i[1]:.2f}"
                value3 = f"{i[2]:.2f}"
                self.breath_list_area.insert("", "end", values=(i[0], value2, value3, "1", "-"))
            else:
                break

    # Funktion zum Auswählen eines Dateipfades/einer MAT-Datei und Anzeigen des MAT-Grafen
    def load_mat_file(self, mat_file_path_text):
        mat_file_path = filedialog.askopenfilename(filetypes=[("MAT Files", "*.mat")])
        if mat_file_path:
            mat_file_path_text.delete(1.0, tk.END)
            mat_file_path_text.insert(tk.END, mat_file_path)
            self.logic.read_mat_file(mat_file_path)

            self.update_canvas()

    # Funktion zum Auswählen eines Ordners mit zwei EDF-Dateien (mask.edf & device.edf)
    def load_edf_files(self, folder_path_text):
        folder_path = filedialog.askdirectory()
        try:
            if folder_path:
                folder_path_text.delete(1.0, tk.END)
                folder_path_text.insert(tk.END, folder_path)
                mask_edf_file_path = None
                device_edf_file_path = None
                for file_name in os.listdir(folder_path):
                    if file_name.endswith("mask.edf"):
                        mask_edf_file_path = os.path.join(folder_path, file_name)
                        self.mask_edf_path = mask_edf_file_path
                    elif file_name.endswith("device.edf"):
                        device_edf_file_path = os.path.join(folder_path, file_name)
                        self.device_edf_path = device_edf_file_path
                # Raw_Objekt soll wieder auf None gesetzt werden, damit eine neue EDF-Datei geladen werden kann
                self.logic.raw_mask_edf_data = None
                self.logic.raw_device_edf_data = None

                self.logic.read_edf_file(mask_edf_file_path, device_edf_file_path)
                self.update_canvas()

                # Übergibt Daten aus logic an breath
                # Aus breath kann man nicht direkt z.B. auf Daten in mask_edf_meta_data in logic zugreifen -> None
                self.breath.mask_edf_meta_data = self.logic.mask_edf_meta_data
                self.breath.mask_edf_data = self.logic.mask_edf_data

                self.determine_breaths()

                # Sperrt beide buttons
                # hier werden die Buttons erneut gesperrt, da diese Funktion zum wiederholten Plotten verwendet wird
                self.backwards_button.config(state="disabled")
                self.forwards_button.config(state="disabled")

        except Exception as error_code:
            print(f"Fehler beim laden der EDF-Dateien: {error_code}")

    def plot_back_edf_file(self, mask_edf_file_path, device_edf_file_path):
        try:
            self.logic.read_edf_file(mask_edf_file_path, device_edf_file_path)
            self.update_canvas()

            # Leert und befüllt die Liste wieder mit allen Atemzügen
            self.clear_list_area()
            self.fill_list_area()

            # Sperrt beide buttons
            self.backwards_button.config(state="disabled")
            self.forwards_button.config(state="disabled")

        except Exception as error_code:
            print(f"\033[93mFehler beim Darstellen des EDF-Graphen: {error_code}\033[0m")
