import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from delivery_planner import (
    check_missing_columns,
    create_trips,
    export_trips_to_csv,
    filter_deliveries,
    get_filter_options,
    get_remaining_capacity,
    get_trip_weight,
    read_deliveries,
    validate_deliveries,
)


class DeliveryRoutePlannerGUI:

    def __init__(self, root):
        self.root = root

        self.root.title("Delivery Route Planner")
        self.root.geometry("1100x700")
        self.root.minsize(950, 600)

        self.bg_color = "#F4F5F7"
        self.primary = "#243447"
        self.secondary = "#5B6770"
        self.accent = "#3F6B8A"
        self.accent_dark = "#31566F"
        self.white = "#FFFFFF"
        self.border = "#D8DDE2"
        self.text = "#263238"
        self.muted = "#6B747C"
        self.table_header = "#E8EBEE"
        self.selected = "#DCE6ED"
        self.trip_one = "#FFFFFF"
        self.trip_two = "#F7F9FA"

        self.generated_trips = []
        self.valid_deliveries = []
        self.rejected_deliveries = []

        self.root.configure(bg=self.bg_color)

        self.create_styles()
        self.create_widgets()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview", background=self.white, foreground=self.text, fieldbackground=self.white, rowheight=32, font=("Arial", 10), borderwidth=0)

        style.configure("Treeview.Heading", background=self.table_header, foreground=self.primary, font=("Arial", 10, "bold"), padding=(8, 8), borderwidth=0)

        style.map("Treeview", background=[("selected", self.selected)], foreground=[("selected", self.text)])

        style.configure("Vertical.TScrollbar", background="#D1D6DA", troughcolor=self.bg_color, bordercolor=self.bg_color, arrowcolor=self.secondary)

        style.configure("Filter.TCombobox", fieldbackground=self.white, background=self.white, foreground=self.text, bordercolor=self.border, lightcolor=self.border, darkcolor=self.border, arrowcolor=self.secondary, padding=(8, 6), font=("Arial", 10))

        style.map("Filter.TCombobox", fieldbackground=[("readonly", self.white), ("active", self.white)], background=[("readonly", self.white), ("active", self.white)], foreground=[("readonly", self.text), ("active", self.text)], bordercolor=[("readonly", self.border), ("focus", self.accent), ("active", self.border)], lightcolor=[("focus", self.accent), ("active", self.border)], darkcolor=[("focus", self.accent), ("active", self.border)])

        self.root.option_add("*TCombobox*Listbox*Background", self.white)

        self.root.option_add("*TCombobox*Listbox*Foreground", self.text)

        self.root.option_add("*TCombobox*Listbox*selectBackground", self.selected)

        self.root.option_add("*TCombobox*Listbox*selectForeground", self.text)

        self.root.option_add("*TCombobox*Listbox*Font", "Arial 10")

    def create_widgets(self):

        main_frame = tk.Frame(self.root, bg=self.bg_color)

        main_frame.pack(fill="both", expand=True, padx=25, pady=20)

        header_frame = tk.Frame(main_frame, bg=self.bg_color)

        header_frame.pack(fill="x", pady=(0, 15))

        title = tk.Label(header_frame, text="Delivery Route Planner", font=("Arial", 24, "bold"), fg=self.primary, bg=self.bg_color, anchor="w")

        title.pack(anchor="w")

        subtitle = tk.Label(header_frame, text="Organize delivery requests into trips with a 10 kg capacity.", font=("Arial", 11), fg=self.secondary, bg=self.bg_color, anchor="w")

        subtitle.pack(anchor="w", pady=(3, 0))

        control_frame = tk.Frame(main_frame, bg=self.white, highlightbackground=self.border, highlightthickness=1)

        control_frame.pack(fill="x", pady=(0, 15))

        control_content = tk.Frame(control_frame, bg=self.white)

        control_content.pack(fill="x", padx=18, pady=15)

        file_section = tk.Frame(control_content, bg=self.white)

        file_section.pack(fill="x")

        file_title = tk.Label(file_section, text="Input File", font=("Arial", 10, "bold"), fg=self.primary, bg=self.white, anchor="w")

        file_title.pack(anchor="w")

        self.file_label = tk.Label(file_section, text="No CSV file selected", font=("Arial", 10), fg=self.muted, bg=self.white, anchor="w")

        self.file_label.pack(anchor="w", pady=(4, 10))

        self.selected_file = None

        button_frame = tk.Frame(control_content, bg=self.white)

        button_frame.pack(anchor="w")

        choose_button = tk.Button(button_frame, text="Choose CSV File", width=18, command=self.choose_file, bg=self.primary, fg=self.white, activebackground=self.secondary, activeforeground=self.white, font=("Arial", 10, "bold"), relief="flat", bd=0, padx=10, pady=8, cursor="hand2")

        choose_button.grid(row=0, column=0, padx=(0, 8))

        generate_button = tk.Button(button_frame, text="Generate Trips", width=18, command=self.generate_trips, bg=self.accent, fg=self.white, activebackground=self.accent_dark, activeforeground=self.white, font=("Arial", 10, "bold"), relief="flat", bd=0, padx=10, pady=8, cursor="hand2")

        generate_button.grid(row=0, column=1, padx=8)

        export_button = tk.Button(button_frame, text="Export Result", width=18, command=self.export_result, bg=self.accent, fg=self.white, activebackground=self.accent_dark, activeforeground=self.white, font=("Arial", 10, "bold"), relief="flat", bd=0, padx=10, pady=8, cursor="hand2")

        export_button.grid(row=0, column=2, padx=8)

        clear_button = tk.Button(button_frame, text="Clear", width=18, command=self.clear, bg=self.table_header, fg=self.primary, activebackground=self.border, activeforeground=self.primary, font=("Arial", 10, "bold"), relief="flat", bd=0, padx=10, pady=8, cursor="hand2")

        clear_button.grid(row=0, column=3, padx=(8, 0))

        search_frame = tk.Frame(main_frame, bg=self.white, highlightbackground=self.border, highlightthickness=1)

        search_frame.pack(fill="x", pady=(0, 15))

        search_content = tk.Frame(search_frame, bg=self.white)

        search_content.pack(fill="x", padx=18, pady=12)

        search_title = tk.Label(search_content, text="Search & Filter", font=("Arial", 10, "bold"), fg=self.primary, bg=self.white, anchor="w")

        search_title.pack(side="left", padx=(0, 12))

        search_hint = tk.Label(search_content, text="ID", font=("Arial", 9, "bold"), fg=self.muted, bg=self.white)

        search_hint.pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(search_content, width=18, font=("Arial", 10), relief="solid", bd=1)

        self.search_entry.pack(side="left", padx=(0, 10), ipady=5)

        self.search_entry.bind("<KeyRelease>", self.apply_filters)

        self.area_var = tk.StringVar(value="Area: All")

        self.area_combo = ttk.Combobox(search_content, textvariable=self.area_var, width=15, state="readonly", style="Filter.TCombobox")

        self.area_combo.pack(side="left", padx=5)

        self.area_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        self.priority_var = tk.StringVar(value="Priority: All")

        self.priority_combo = ttk.Combobox(search_content, textvariable=self.priority_var, width=15, state="readonly", style="Filter.TCombobox")

        self.priority_combo.pack(side="left", padx=5)

        self.priority_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        clear_search_button = tk.Button(search_content, text="Clear", width=9, command=self.clear_search, bg=self.table_header, fg=self.primary, activebackground=self.border, activeforeground=self.primary, font=("Arial", 10, "bold"), relief="flat", bd=0, padx=8, pady=7, cursor="hand2")

        clear_search_button.pack(side="left", padx=(10, 0))

        summary_frame = tk.Frame(main_frame, bg=self.bg_color)

        summary_frame.pack(fill="x", pady=(0, 10))

        summary_title = tk.Label(summary_frame, text="Results Summary", font=("Arial", 10, "bold"), fg=self.primary, bg=self.bg_color, anchor="w")

        summary_title.pack(anchor="w")

        self.summary_label = tk.Label(summary_frame, text="", font=("Arial", 10), fg=self.secondary, bg=self.bg_color, anchor="w")

        self.summary_label.pack(anchor="w", pady=(3, 0))

        results_frame = tk.Frame(main_frame, bg=self.bg_color)

        results_frame.pack(fill="both", expand=True)

        results_frame.grid_rowconfigure(0, weight=1)

        results_frame.grid_rowconfigure(1, weight=0)

        results_frame.grid_columnconfigure(0, weight=1)

        table_container = tk.Frame(results_frame, bg=self.white, highlightbackground=self.border, highlightthickness=1)

        table_container.grid(row=0, column=0, sticky="nsew", pady=(0, 12))

        table_frame = tk.Frame(table_container, bg=self.white)

        table_frame.pack(fill="both", expand=True, padx=1, pady=1)

        columns = ("trip", "delivery_id", "area", "priority", "weight", "trip_total", "remaining")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("trip", text="Trip")

        self.tree.heading("delivery_id", text="Delivery ID")

        self.tree.heading("area", text="Area")

        self.tree.heading("priority", text="Priority")

        self.tree.heading("weight", text="Package Weight")

        self.tree.heading("trip_total", text="Trip Total")

        self.tree.heading("remaining", text="Remaining Capacity")

        self.tree.column("trip", width=70, anchor="center")

        self.tree.column("delivery_id", width=105, anchor="center")

        self.tree.column("area", width=160, anchor="w")

        self.tree.column("priority", width=90, anchor="center")

        self.tree.column("weight", width=135, anchor="center")

        self.tree.column("trip_total", width=110, anchor="center")

        self.tree.column("remaining", width=160, anchor="center")

        self.tree.tag_configure("trip_even", background=self.trip_two)

        self.tree.tag_configure("trip_odd", background=self.trip_one)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar.pack(side="right", fill="y")

        rejected_frame = tk.Frame(results_frame, bg=self.white, highlightbackground=self.border, highlightthickness=1, height=105)

        rejected_frame.grid(row=1, column=0, sticky="ew")

        rejected_frame.grid_propagate(False)

        rejected_header = tk.Frame(rejected_frame, bg=self.white)

        rejected_header.pack(fill="x", padx=15, pady=(8, 3))

        rejected_title = tk.Label(rejected_header, text="Rejected Deliveries", font=("Arial", 10, "bold"), fg=self.primary, bg=self.white, anchor="w")

        rejected_title.pack(anchor="w")

        self.rejected_text = tk.Text(rejected_frame, height=3, state="disabled", font=("Arial", 9), fg=self.text, bg="#FAFBFC", relief="flat", bd=0, wrap="word")

        self.rejected_text.pack(fill="both", expand=True, padx=15, pady=(0, 8))

    def choose_file(self):
        filename = filedialog.askopenfilename(title="Select Delivery CSV File", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])

        if filename:
            self.selected_file = filename

            self.file_label.config(text=f"Selected: {filename}", fg=self.text)

    def update_filters(self):

        areas, priorities = get_filter_options(self.valid_deliveries)

        current_area = self.area_var.get()
        current_priority = self.priority_var.get()

        self.area_combo["values"] = ["Area: All"] + [f"Area: {area}" for area in areas]

        self.priority_combo["values"] = ["Priority: All"] + [f"Priority: {priority}" for priority in priorities]

        if current_area in self.area_combo["values"]:
            self.area_var.set(current_area)
        else:
            self.area_var.set("Area: All")

        if current_priority in self.priority_combo["values"]:
            self.priority_var.set(current_priority)
        else:
            self.priority_var.set("Priority: All")

    def generate_trips(self):

        if not self.selected_file:

            messagebox.showwarning("No File", "Please choose a CSV file first.")

            return

        try:

            missing_columns = check_missing_columns(self.selected_file)

            if missing_columns:

                self.generated_trips = []
                self.valid_deliveries = []
                self.rejected_deliveries = []

                for item in self.tree.get_children():
                    self.tree.delete(item)

                self.area_var.set("Area: All")

                self.priority_var.set("Priority: All")

                self.area_combo["values"] = ["Area: All"]

                self.priority_combo["values"] = ["Priority: All"]

                self.summary_label.config(text="No trips generated because the CSV is missing required columns.")

                self.rejected_text.config(state="normal")

                self.rejected_text.delete("1.0", tk.END)

                if len(missing_columns) == 1:

                    self.rejected_text.insert(tk.END, f"Missing column: {missing_columns[0]}")

                else:

                    self.rejected_text.insert(tk.END, "Missing columns: " + ", ".join(missing_columns))

                self.rejected_text.config(state="disabled")

                return

            deliveries = read_deliveries(self.selected_file)

            if not deliveries:

                self.generated_trips = []
                self.valid_deliveries = []
                self.rejected_deliveries = []

                for item in self.tree.get_children():
                    self.tree.delete(item)

                self.area_var.set("Area: All")

                self.priority_var.set("Priority: All")

                self.area_combo["values"] = ["Area: All"]

                self.priority_combo["values"] = ["Priority: All"]

                self.summary_label.config(text="No deliveries found.")

                self.rejected_text.config(state="normal")

                self.rejected_text.delete("1.0", tk.END)

                self.rejected_text.insert(tk.END, "No deliveries found in the selected CSV file.")

                self.rejected_text.config(state="disabled")

                return

            (valid_deliveries, rejected) = validate_deliveries(deliveries)

            self.valid_deliveries = (valid_deliveries)

            self.rejected_deliveries = (rejected)

            self.update_filters()

            if not valid_deliveries:

                self.generated_trips = []

                for item in self.tree.get_children():
                    self.tree.delete(item)

                self.summary_label.config(text=("No valid deliveries found. " f"Rejected: {len(rejected)}"))

                self.rejected_text.config(state="normal")

                self.rejected_text.delete("1.0", tk.END)

                for delivery, reason in rejected:

                    delivery_id = (delivery["id"] if delivery["id"] is not None else "Missing")

                    area = (delivery["area"] if delivery["area"] else "Missing")

                    priority = (delivery["priority"] if delivery["priority"] is not None else "Missing")

                    weight = (delivery["weight"] if delivery["weight"] is not None else "Missing")

                    self.rejected_text.insert(tk.END, f"ID: {delivery_id} | " f"Area: {area} | " f"Priority: {priority} | " f"Weight: {weight} | " f"Reason: {reason}\n")

                self.rejected_text.config(state="disabled")

                return

            trips = create_trips(valid_deliveries)

            self.generated_trips = trips

            self.search_entry.delete(0, tk.END)

            self.area_var.set("Area: All")

            self.priority_var.set("Priority: All")

            self.display_trips(trips, len(valid_deliveries), rejected)

        except Exception as error:

            messagebox.showerror("Error", str(error))

    def apply_filters(self, event=None):

        if not self.valid_deliveries:
            return

        search_term = (self.search_entry.get())

        selected_area = self.area_var.get()

        if selected_area.startswith("Area: "):
            selected_area = selected_area[len("Area: "):]

        selected_priority = self.priority_var.get()

        if selected_priority.startswith("Priority: "):
            selected_priority = selected_priority[len("Priority: "):]

        filtered_deliveries = (filter_deliveries(self.valid_deliveries, search_term, selected_area, selected_priority))

        self.display_trips(self.generated_trips, len(filtered_deliveries), self.rejected_deliveries, filtered_deliveries)

    def clear_search(self):

        self.search_entry.delete(0, tk.END)

        self.area_var.set("Area: All")

        self.priority_var.set("Priority: All")

        if self.generated_trips:

            self.display_trips(self.generated_trips, len(self.valid_deliveries), self.rejected_deliveries, self.valid_deliveries)

    def export_result(self):

        if (not self.generated_trips and not self.rejected_deliveries):

            messagebox.showwarning("No Data", "There are no generated trips to export.")

            return

        filename = filedialog.asksaveasfilename(title="Export Delivery Trips", defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])

        if filename:

            try:

                export_trips_to_csv(filename, self.generated_trips, self.rejected_deliveries)

                messagebox.showinfo("Success", f"Trips successfully exported to:\n{filename}")

            except Exception as error:

                messagebox.showerror("Export Error", str(error))

    def display_trips(self, trips, valid_count, rejected, deliveries_to_show=None):

        for item in self.tree.get_children():
            self.tree.delete(item)

        if deliveries_to_show is None:

            deliveries_to_show = [delivery for trip in trips for delivery in trip]

        delivery_ids = {delivery["id"] for delivery in deliveries_to_show}

        shown_count = 0

        for trip_number, trip in enumerate(trips, start=1):

            trip_deliveries = [delivery for delivery in trip if delivery["id"] in delivery_ids]

            if not trip_deliveries:
                continue

            trip_weight = get_trip_weight(trip)

            remaining_capacity = (get_remaining_capacity(trip))

            trip_tag = ("trip_even" if trip_number % 2 == 0 else "trip_odd")

            for delivery in trip_deliveries:

                shown_count += 1

                self.tree.insert("", "end", values=(trip_number, delivery["id"], delivery["area"], delivery["priority"], f"{delivery['weight']:.1f} kg", f"{trip_weight:.1f} kg", f"{remaining_capacity:.1f} kg"), tags=(trip_tag,))

        has_filters = (self.search_entry.get().strip() or self.area_var.get() != "Area: All" or self.priority_var.get() != "Priority: All")

        if has_filters:

            self.summary_label.config(text=(f"Showing {shown_count} of " f"{len(self.valid_deliveries)} " f"valid deliveries"))

        else:

            total_weight = sum(get_trip_weight(trip) for trip in trips)

            self.summary_label.config(text=(f"Valid Deliveries: {valid_count}    |    " f"Trips: {len(trips)}    |    " f"Total Weight: {total_weight:.1f} kg    |    " f"Rejected: {len(rejected)}"))

        self.rejected_text.config(state="normal")

        self.rejected_text.delete("1.0", tk.END)

        if rejected:

            for delivery, reason in rejected:

                delivery_id = (delivery["id"] if delivery["id"] is not None else "Missing")

                area = (delivery["area"] if delivery["area"] else "Missing")

                priority = (delivery["priority"] if delivery["priority"] is not None else "Missing")

                weight = (delivery["weight"] if delivery["weight"] is not None else "Missing")

                self.rejected_text.insert(tk.END, f"ID: {delivery_id} | " f"Area: {area} | " f"Priority: {priority} | " f"Weight: {weight} | " f"Reason: {reason}\n")

        else:

            self.rejected_text.insert(tk.END, "No rejected deliveries.")

        self.rejected_text.config(state="disabled")

    def clear(self):

        self.selected_file = None
        self.generated_trips = []
        self.valid_deliveries = []
        self.rejected_deliveries = []

        self.search_entry.delete(0, tk.END)

        self.area_var.set("Area: All")

        self.priority_var.set("Priority: All")

        self.area_combo["values"] = ["Area: All"]

        self.priority_combo["values"] = ["Priority: All"]

        self.file_label.config(text="No CSV file selected", fg=self.muted)

        self.summary_label.config(text="")

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.rejected_text.config(state="normal")

        self.rejected_text.delete("1.0", tk.END)

        self.rejected_text.config(state="disabled")


def main():
    root = tk.Tk()
    app = DeliveryRoutePlannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()