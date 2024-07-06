import tkinter as tk  # tkinter wird zum Bau der GUI verwendet
from tkinter import ttk # ermöglicht den Bau des Treeview (Listenbereich mit den Atemzügen)
from tkinter import filedialog  # filedialog = Modul aus tkinter um Dateien auswählen zu können
from logic import AtemzugValidierungLogic
from breath import AtemzugValidierungBreaths
import os
import csv


class AtemzugValidierungGUI(tk.Tk):
    # Konstruktor der Klasse AtemzugValidierungGUI()
    def __init__(self, master=None):
        super().__init__(master)  # erstellt das Hauptfenster "self"
        self.logic = AtemzugValidierungLogic()
        self.breath = AtemzugValidierungBreaths()
        self.mask_edf_path = None
        self.device_edf_path = None  # Instanzvariable um den Pfad der EDF-Datei speichern
        self.title("Atemzug Validierung")  # legt Titel für Hauptfenster fest
        self.geometry("950x1000")  # legt Fenster größe fest (Breite x Höhe)
        self.starting_point = None
        self.forward = False
        self.backward = False
        self.fast_forward = False
        self.fast_backward = False
        self.breath_list_area = None
        self.breath_start = None
        self.breath_end = None
        self.selected_breath = None
        self.selected_breath_index = None
        self.interval_is_showen = False
        self.column_headers = None
        # Ab hier Buttons und Eingabe in Reihenfolge der Implementierung
        self.starting_point_entry = None
        self.interval_button = None
        self.backwards_button = None
        self.forwards_button = None
        self.full_graph_button = None
        self.interval_entry = None
        self.save_interval_button = None
        self.thirty_sec_interval_button = None
        self.sixty_sec_interval_button = None
        self.invalid_breath_button = None
        self.export_button = None


        # Folgend werden GUI Elemente gebaut
        '''self.load_mat_file_button = tk.Button(self, text="MAT Datei auswählen", command=lambda: self.load_mat_file(self.mat_file_path_text))
        self.load_mat_file_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")'''

        self.load_edf_file_button = tk.Button(self, text="EDF Ordner auswählen", command=lambda: self.load_edf_files(self.folder_path_text),
                                              height=2, width=12, wraplength=120)
        self.load_edf_file_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        '''self.mat_file_path_text = tk.Text(self, height=1, width=100, wrap=tk.NONE)
        self.mat_file_path_text.grid(row=0, column=1, columnspan=10, padx=5, pady=5, sticky="w")'''

        self.folder_path_text = tk.Text(self, height=1, width=100, wrap=tk.NONE)
        self.folder_path_text.grid(row=1, column=1, columnspan=10, padx=5, pady=5, sticky="w")

        self.gui_edf_plot_area()
        self.gui_list_area()

    # Funktion zum Testen auf was der Fokus liegt
    '''def check_focus(self):
        focused_widget = self.focus_get()
        print(f"Fokus liegt auf: {focused_widget}")'''

    # Funktion zur erstellung der GUI Elemente für den EDF-Graphen
    def gui_edf_plot_area(self):
        # Label für starting_point_entry
        starting_point_label = tk.Label(self, text="Startpunkt des Intervalls:", width=16)
        starting_point_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Eingabefeld zur Eingabe des gewünschten Startpunktes
        self.starting_point_entry = tk.Entry(self, width=8, state="readonly")
        self.starting_point_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Funktion startet set_starting_point und leert das Eingabefeld
        def set_starting_point_and_clear():
            self.set_starting_point()
            # Leert das Eingabefeld (NACHFARGEN OB GEBRAUCHT WIRD) - auch in Zeile 77
            '''self.starting_point_entry.delete(0, tk.END)'''

        # Button zum Anzeigen eines Intervalls in der Messung
        self.interval_button = tk.Button(self, text="Intervall anzeigen", command=lambda: set_starting_point_and_clear(), state="disabled", height=2,
                                         width=12, wraplength=120)
        self.interval_button.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Ersetzt das Klicken auf den interval_button durch einen Klick auf die Enter Taste. Button ist weiterhin aktiv.
        def trigger_interval_button(event):
            self.set_starting_point()
            self.focus()
            # Leert das Eingabefeld (NACHFARGEN OB GEBRAUCHT WIRD) - auch in Zeile 65
            '''self.starting_point_entry.delete(0, tk.END)'''
        self.starting_point_entry.bind("<Return>", trigger_interval_button)

        # Button zum rückwärts Navigieren im Plot
        self.backwards_button = tk.Button(self, text="<", command=lambda: self.go_backwards(), state="disabled", height=2, width=4)
        self.backwards_button.grid(row=3, column=3, columnspan=10, padx=45, pady=5, sticky="w")

        # Button zum vorwärts Navigieren im Plot
        self.forwards_button = tk.Button(self, text=">", command=lambda: self.go_forwards(), state="disabled", height=2, width=4)
        self.forwards_button.grid(row=3, column=3, columnspan=10, padx=115, pady=5, sticky="w")

        # Button für Fast-Validation rückwärts
        self.fast_backwards_button = tk.Button(self, text="<<", command=lambda: self.go_fast_backwards(), state="disabled", height=2, width=1)
        self.fast_backwards_button.grid(row=3, column=3, columnspan=10, padx=5, pady=5, sticky="w")

        # Button für Fast-Validation vorwärts
        self.fast_forwards_button = tk.Button(self, text=">>", command=lambda: self.go_fast_forwards(), state="disabled", height=2, width=1)
        self.fast_forwards_button.grid(row=3, column=3, columnspan=10, padx=180, pady=5, sticky="w")

        # Folgenden beiden Funktionen (1 & 2) ersetzen das Klicken auf die Buttons backwards_button & forwards_button durch das Nutzen der Pfeiltasten
        # Funktion 1
        def trigger_backwards_button(event):
            try:
                self.go_backwards()
            except Exception as error_code:
                print(f"\033[93mFehler beim rückwärts Navigieren: {error_code}\033[0m")
        self.bind("<Left>", trigger_backwards_button)

        # Funktion 2
        def trigger_forwards_button(event):
            try:
                self.go_forwards()
            except Exception as error_code:
                print(f"\033[93mFehler beim vorwärts Navigieren: {error_code}\033[0m")
        self.bind("<Right>", trigger_forwards_button)

        # Button um die ganze Grafik wieder anzuzeigen
        self.full_graph_button = tk.Button(self, text="Gesamten Graphen anzeigen",
                                           command=lambda: self.plot_back_edf_file(self.mask_edf_path, self.device_edf_path), state="disabled",
                                           height=2, width=12, wraplength=120)
        self.full_graph_button.grid(row=3, column=4, padx=5, pady=5, sticky="w")

        # Label für interval_entry
        interval_label = tk.Label(self, text="Gewünschtes Intervall (Standardmäßig sind 30sek festgelegt):", width=16, wraplength=160)
        interval_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        # Eingabefeld zur Eingabe des gewünschten Intervalls
        self.interval_entry = tk.Entry(self, width=8, state="readonly")
        self.interval_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Button zum Speichern des Intervalls
        self.save_interval_button = tk.Button(self, text="Intervall speichern",
                                              command=lambda: self.logic.set_interval(float(self.interval_entry.get())), state="disabled",
                                              height=2, width=12, wraplength=120)
        self.save_interval_button.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Ersetzt das Klicken auf den save_interval_button durch einen Klick auf die Enter Taste. Button ist weiterhin aktiv.
        def trigger_save_interval_button(event):
            self.logic.set_interval(float(self.interval_entry.get()))
            self.focus()
        self.interval_entry.bind("<Return>", trigger_save_interval_button)

        def trigger_empty_set_interval(value):
            self.logic.set_interval(value)
            self.interval_entry.delete(0, tk.END)

        # Button zum Festlegen eines 30sek Intervalls
        self.thirty_sec_interval_button = tk.Button(self, text="30sek", command=lambda: trigger_empty_set_interval(30),state="disabled",
                                               height=2, width=8)
        self.thirty_sec_interval_button.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # Button zum Festlegen eines 60sek Intervalls
        self.sixty_sec_interval_button = tk.Button(self, text="60sek", command=lambda: trigger_empty_set_interval(60), state="disabled",
                                              height=2, width=8)
        self.sixty_sec_interval_button.grid(row=4, column=3, padx=115, pady=5, sticky="w")

    # Funktion zur erstellung des Bereiches, in dem die Liste der Atemzüge angezeigt werden soll
    def gui_list_area(self):
        self.column_headers = ["Nr", "Start (sek)", "Ende (sek)", "Status", "Kommentar"]
        # Erstellt ein Frame für die Liste und Scrollbar
        frame = ttk.Frame(self)
        frame.grid(row=5, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.breath_list_area = ttk.Treeview(frame, columns=("column_number", "column_start", "column_end", "column_is_breath", "column_comment"),
                                             height=15)

        self.invalid_breath_button = tk.Button(text="kein Atemzug", command=lambda: self.set_data_to_invalid(), state="disabled",
                                               height=2, width=12, wraplength=120)
        self.invalid_breath_button.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self.export_button = tk.Button(self, text="Liste als .csv exportieren", command=lambda: self.export_list(), state="disabled", height=2, width=12, wraplength=120)
        self.export_button.grid(row=6, column=4, padx=5, pady=5, sticky="w")

        self.breath_list_area.column("#0", width=0, stretch=tk.NO)  # Phantomspalte. Ist immer da, wird aber nicht benötigt
        self.breath_list_area.column("column_number", anchor="e", width=40, minwidth=40)
        self.breath_list_area.column("column_start", anchor="e", width=100, minwidth=100)
        self.breath_list_area.column("column_end", anchor="e", width=100, minwidth=100)
        self.breath_list_area.column("column_is_breath", anchor="e", width=70, minwidth=70)
        self.breath_list_area.column("column_comment", anchor="w", width=600, minwidth=600)

        # self.breath_list_area.heading("#0", text="Test", anchor="w")
        self.breath_list_area.heading("column_number", text=self.column_headers[0], anchor="w")
        self.breath_list_area.heading("column_start", text=self.column_headers[1], anchor="w")
        self.breath_list_area.heading("column_end", text=self.column_headers[2], anchor="w")
        self.breath_list_area.heading("column_is_breath", text=self.column_headers[3], anchor="w")
        self.breath_list_area.heading("column_comment", text=self.column_headers[4], anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.breath_list_area.yview)
        self.breath_list_area.configure(yscrollcommand=scrollbar.set)

        self.breath_list_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # beim Auswählen eines Atemzuges in der Liste wird die Funktion on_breath_selection ausgeführt
        self.breath_list_area.bind("<<TreeviewSelect>>", self.on_breath_selection)
        # ermöglicht einen Doppelklick in der Liste
        # führt beim Doppelklick die Funktion on_breath_double_click aus
        self.breath_list_area.bind("<Double-1>", self.on_breath_double_click)

    # Funktion aktualisiert die Information für validen Druckbereich und Dauer
    def list_info_text(self):
        limit_info_label = tk.Label(self, text="Valider Druckbereich:\nValide Dauer:", justify="left")
        limit_info_label.grid(row=6, column=1, columnspan=10, padx=5, pady=5, sticky="w")

        values_label = tk.Label(self, text=f"min {self.breath.min_pressure:.2f}mbar - max {self.breath.max_pressure:.2f}mbar\n"
                                           f"min {self.breath.min_duration:.2f}sek - max {self.breath.max_duration:.2f}sek", justify="left")
        values_label.grid(row=6, column=1, columnspan=10, padx=150, pady=5, sticky="w")

    # Funktion kopiert nur valide Daten in neue Liste
    def get_valid_data(self):
        breath_list_valid = []
        for i in self.breath.breath_list:
            if i[3] == 1 or i[3] == 2:
                breath_list_valid.append(i)

        return breath_list_valid

    # Funktion kopiert nur invalide Daten in neue Liste
    def get_invalid_data(self):
        breath_list_invalid = []
        for i in self.breath.breath_list:
            if i[3] == 0:
                breath_list_invalid.append(i)

        return breath_list_invalid

    # Funktion kopiert nur kommentierte Daten in neue Liste
    def get_commented_data(self):
        breath_list_commented = []
        for i in self.breath.breath_list:
            if i[3] == 2:
                breath_list_commented.append(i)

        return breath_list_commented

    # Funktion erstellt CSV Datei
    def export_to_csv(self, filename, data):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(self.column_headers)
            for row in data:
                writer.writerow(list(row))

    # Funktion exportiert übergebene Listen in CSV Dateien
    def export_list(self):
        self.breath.breath_list_valid_data = self.get_valid_data()
        self.breath.breath_list_invalid_data = self.get_invalid_data()
        self.breath.breath_list_commented_data = self.get_commented_data()

        # öffnet Dialogfenster, wo man den Speicherort auswählen kann
        folder_path = filedialog.askdirectory(
            title="Speicherort auswählen"
        )

        # wenn Speicherort ausgewählt wurde, werden alle Dateien dort abgelegt
        if folder_path:
            file_name = "full_data.csv"
            full_path = os.path.join(folder_path, file_name)
            self.export_to_csv(full_path, self.breath.breath_list)

            file_name = "valid_data.csv"
            full_path = os.path.join(folder_path, file_name)
            self.export_to_csv(full_path, self.breath.breath_list_valid_data)

            file_name = "invalid_data.csv"
            full_path = os.path.join(folder_path, file_name)
            self.export_to_csv(full_path, self.breath.breath_list_invalid_data)

            file_name = "commented_data.csv"
            full_path = os.path.join(folder_path, file_name)
            self.export_to_csv(full_path, self.breath.breath_list_commented_data)


    # Funktion, welche beim Auswählen eines Datensatzes ausgeführt werden soll
    def on_breath_selection(self, event):
        try:
            # selected_data bekommt die Liste mit der ID des Datensatzes
            selected_data = self.breath_list_area.selection()

            # wenn selected_data nicht leer ist, dann
            if selected_data:
                # ID wird ausgelesen
                selected_data_id = selected_data[0]  # Erster ausgewählter Eintrag
                # Übergibt die Werte aus der Liste mit der ausgewählten ID
                selected_data_values = self.breath_list_area.item(selected_data_id, "values")

                # Wenn sich der Benutzer in einem Intervall befindet, dann sollen Start und Ende des ausgewählten Atemzuges übergeben werden,
                # damit dieser im Plot markiert werden kann
                if self.interval_is_showen is True:
                    self.breath_start = selected_data_values[1]
                    self.breath_end = selected_data_values[2]
                    self.logic.use_multiple_funcs(self.starting_point, self.starting_point, self.forward, self.backward, self.fast_backward,
                                                  self.fast_forward, self.breath_start, self.breath_end)
                    self.breath_start = None
                    self.breath_end = None

                # Ermittlung des Index des ausgewählten Datensatzes
                breath_number = selected_data_values[0]
                self.selected_breath_index = int(breath_number) - 1

        except Exception as error_code:
            print(f"\033[93mFehler bei Auswahl eines Datensatzes: {error_code}\033[0m")

    # Funktion welche beim Doppelklick auf die Spalte "Kommentar" ausgeführt wird
    def on_breath_double_click(self, event):
        selected_item = self.breath_list_area.selection()[0]
        affected_column = self.breath_list_area.identify_column(event.x)
        if affected_column == "#5":
            # Koordinaten der ausgewählten Spalte werden ermittelt
            x, y, width, height = self.breath_list_area.bbox(selected_item, affected_column)
            comment_value = self.breath_list_area.item(selected_item, "values")[4]

            breath_number = self.breath_list_area.item(selected_item, "values")[0]
            selected_index = int(breath_number) - 1

            self.entry = tk.Entry(self.breath_list_area)
            self.entry.place(x=x, y=y, width=width, height=height)
            self.entry.insert(0, comment_value)
            self.entry.focus()

            # Funktion speichert neuen wert im Feld und entfernt Fokus von Liste
            def on_entry_confirm(event):
                # neuen kommentar auslesen
                new_comment_value = self.entry.get()

                # Funktion speichert Textwert in Spalte "Kommentar" und passt entsprechen Status des Datensatzes an
                def get_new_data(data, text_value):
                    first_5_min_text = "Atemzug befindet sich innerhalb der ersten 5 Minuten!"
                    last_5_min_text = "Atemzug befindet sich innerhalb der letzten 5 Minuten!"

                    if text_value.startswith("kein Atemzug!") or text_value == first_5_min_text or text_value == last_5_min_text:
                        data[3] = 0
                        data[4] = text_value
                    elif text_value != "-" and text_value != "":
                        data[3] = 2
                        data[4] = text_value
                    else:
                        data[3] = 1
                        data[4] = text_value

                    return data

                # zeigt neuen statt alten Kommentar nach Speicherung in Liste an
                selected_data = list(self.breath_list_area.item(selected_item, "values"))
                new_data = get_new_data(selected_data, new_comment_value)
                self.breath_list_area.item(selected_item, values=new_data)

                # ändert und speichert Kommentar in Atemzugliste (breath_list)
                # ausgewähltes Tupel in breath_list wird zur Liste konvertiert
                selected_tuple = list(self.breath.breath_list[selected_index])
                new_tuple = get_new_data(selected_tuple, new_comment_value)
                # Datensatz wird zurück zum Tupel konvertiert und in breath_list gespeichert
                self.breath.breath_list[selected_index] = tuple(new_tuple)

                self.entry.destroy()

            # Ereignis binden, wenn die Eingabe bestätigt wird
            self.entry.bind("<Return>", on_entry_confirm)
            self.entry.bind("<FocusOut>", lambda event: self.entry.destroy())

    # Funktion zum Befüllen der list_area
    def fill_list_area(self):
        self.list_info_text()

        for i in self.breath.breath_list:
            # Die Zeitpunkte werden auf zwei Nachkommastellen formatiert
            value_start = f"{i[1]:.2f}"
            value_end = f"{i[2]:.2f}"

            self.breath_list_area.insert("", "end", values=(i[0], value_start, value_end, i[3], i[4]))

    # Funktion zum Leeren der list_area
    def clear_list_area(self):
        for item in self.breath_list_area.get_children():
            self.breath_list_area.delete(item)

    def set_data_to_invalid(self):
        selected_item = self.breath_list_area.selection()[0]
        actual_temp_data = list(self.breath_list_area.item(selected_item, "values"))
        actual_temp_data[3] = 0
        actual_temp_data[4] = "kein Atemzug!"
        self.breath_list_area.item(selected_item, values=actual_temp_data)

        actual_data = list(self.breath.breath_list[self.selected_breath_index])
        actual_data[3] = 0
        actual_data[4] = "kein Atemzug!"
        new_data = tuple(actual_data)
        self.breath.breath_list[self.selected_breath_index] = new_data

    # Funktion um den Startpunkt des Intervalls in einer Variable abzuspeichern
    # Zusätzlich werden die Buttons backwards_button & forwards_button freigegeben
    def set_starting_point(self):
        self.interval_is_showen = True
        self.backwards_button.config(state="normal")
        self.forwards_button.config(state="normal")
        self.fast_backwards_button.config(state="normal")
        self.fast_forwards_button.config(state="normal")
        self.starting_point = self.starting_point_entry.get()
        self.logic.use_multiple_funcs(self.starting_point_entry.get(), self.starting_point, self.forward, self.backward, self.fast_backward,
                                      self.fast_forward, self.breath_start, self.breath_end)
        self.determine_breaths_in_interval(self.starting_point, self.logic.interval)

    # Funktion zum vor- und rückwärts Navigieren
    def backwards_forwards_navigation(self):
        focus = self.focus_get()
        # Navigation soll nicht möglich sein, wenn Fokus noch auf Eingabefeld in Kommentarspalte liegt
        if str(focus).startswith(".!frame.!treeview.!entry") is not True:
            self.logic.use_multiple_funcs(self.starting_point_entry.get(), self.starting_point, self.backward, self.forward, self.fast_backward,
                                          self.fast_forward, self.breath_start, self.breath_end)
            self.starting_point = self.logic.starting_point
            self.determine_breaths_in_interval(self.starting_point, self.logic.interval)

    def fast_validation_backwards_forwards(self):
        starting_point = float(self.starting_point)
        interval = float(self.logic.interval)
        breath_list = self.breath.breath_list
        first_data = None
        last_data = None
        index = 0

        try:
            # ermittelt den ersten Datensatz in der dargestellten Liste
            for data in breath_list:
                if float(breath_list[index][1]) >= starting_point:
                    first_data = data
                    index = 0
                    break
                index += 1

            # ermittelt den letzten Datensatz in der dargestellten Liste
            for data in breath_list:
                if float(breath_list[index][2]) <= starting_point + interval and float(breath_list[index + 1][2]) >= starting_point + interval:
                    last_data = data
                    index = 0
                    break
                index += 1

            # wird ausgeführt, wenn self.fast_forward == True ist
            if self.fast_forward:
                index = last_data[0]
                # sucht die nächste Anomalie und ermittelt die Dauer bis zu dieser
                for data in breath_list[index:]:
                    if data[4].startswith("ANOMALIE"):
                        self.logic.duration_to_next_anomaly = int(data[1] - starting_point)
                        self.backwards_forwards_navigation()
                        # wenn Button gesperrt ist, dann soll dieser entsperrt werden
                        if self.fast_backwards_button.cget("state") == "disabled":
                            self.fast_backwards_button.config(state="normal")
                        break
                    # wenn es keine weitere Anomalie gibt, dann soll Button gesperrt werden
                    elif data[4] == "Atemzug befindet sich innerhalb der letzten 5 Minuten!":
                        print("In dieser Richtung gibt es keine weiteren Anomalien!")
                        self.fast_forwards_button.config(state="disabled")
                        break

            # wird ausgeführt, wenn self.fast_forward == True ist
            if self.fast_backward:
                index = first_data[0] - 1
                # sucht die vorherige Anomalie und ermittelt die Dauer bis zu dieser
                for data in reversed(breath_list[:index]):
                    if data[4].startswith("ANOMALIE"):
                        self.logic.duration_to_previous_anomaly = int(starting_point - data[1] + 1)
                        self.backwards_forwards_navigation()
                        # wenn Button gesperrt ist, dann soll dieser entsperrt werden
                        if self.fast_forwards_button.cget("state") == "disabled":
                            self.fast_forwards_button.config(state="normal")
                        break
                    # wenn es keine weitere Anomalie gibt, dann soll Button gesperrt werden
                    elif data[4] == "Atemzug befindet sich innerhalb der ersten 5 Minuten!":
                        print("In dieser Richtung gibt es keine weiteren Anomalien!")
                        self.fast_backwards_button.config(state="disabled")
                        break

        except Exception as error_code:
            print(f"\033[93mFehler bei Fast-Validation: {error_code}\033[0m")

    # Funktion um im Plot rückwärts zu navigieren
    def go_backwards(self):
        self.backward = True
        self.backwards_forwards_navigation()
        self.backward = False

    # Funktion um im Plot vorwärts zu navigieren
    def go_forwards(self):
        self.forward = True
        self.backwards_forwards_navigation()
        self.forward = False

    # Funktion um direkt zur nächsten Anomalie zu springen
    def go_fast_backwards(self):
        self.fast_backward = True
        self.fast_validation_backwards_forwards()
        self.fast_backward = False

    # Funktion um direkt zur vorherigen Anomalie zu springen
    def go_fast_forwards(self):
        self.fast_forward = True
        self.fast_validation_backwards_forwards()
        self.fast_forward = False

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
        self.logic.pressure_median = self.breath.pressure_median

        # Entsperrt Buttons
        self.interval_button.config(state="normal")
        self.save_interval_button.config(state="normal")
        self.full_graph_button.config(state="normal")
        self.starting_point_entry.config(state="normal")
        self.interval_entry.config(state="normal")
        self.thirty_sec_interval_button.config(state="normal")
        self.sixty_sec_interval_button.config(state="normal")
        self.invalid_breath_button.config(state="normal")
        self.export_button.config(state="normal")

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
                value_start = f"{i[1]:.2f}"
                value_end = f"{i[2]:.2f}"

                self.breath_list_area.insert("", "end", values=(i[0], value_start, value_end, i[3], i[4]))
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
                self.fast_backwards_button.config(state="disabled")
                self.fast_forwards_button.config(state="disabled")

                # Leert die Eingabefelder
                self.starting_point_entry.delete(0, tk.END)
                self.interval_entry.delete(0, tk.END)

        except Exception as error_code:
            print(f"\033[93mFehler beim laden der EDF-Dateien: {error_code}\033[0m")

    def plot_back_edf_file(self, mask_edf_file_path, device_edf_file_path):
        try:
            self.interval_is_showen = False

            self.logic.read_edf_file(mask_edf_file_path, device_edf_file_path)
            self.update_canvas()

            # Leert und befüllt die Liste wieder mit allen Atemzügen
            self.clear_list_area()
            self.fill_list_area()

            # Sperrt beide buttons
            self.backwards_button.config(state="disabled")
            self.forwards_button.config(state="disabled")
            self.fast_backwards_button.config(state="disabled")
            self.fast_forwards_button.config(state="disabled")

            # Leert die Eingabefelder
            self.starting_point_entry.delete(0, tk.END)
            self.interval_entry.delete(0, tk.END)

            # Setzt den Startpunkt des Intervalls auf None
            self.starting_point = None

        except Exception as error_code:
            print(f"\033[93mFehler beim Darstellen des EDF-Graphen: {error_code}\033[0m")
