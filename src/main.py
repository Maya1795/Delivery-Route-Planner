import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from delivery_planner import (
    create_trips,
    export_trips_to_csv,
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
        self.rejected_deliveries = []
        self.root.configure(bg=self.bg_color)
        self.create_styles()
        self.create_widgets()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=self.white,
            foreground=self.text,
            fieldbackground=self.white,
            rowheight=32,
            font=("Arial", 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=self.table_header,
            foreground=self.primary,
            font=("Arial", 10, "bold"),
            padding=(8, 8),
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", self.selected)],
            foreground=[("selected", self.text)],
        )
        style.configure(
            "Vertical.TScrollbar",
            background="#D1D6DA",
            troughcolor=self.bg_color,
            bordercolor=self.bg_color,
            arrowcolor=self.secondary,
        )

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 15))
        title = tk.Label(
            header_frame,
            text="Delivery Route Planner",
            font=("Arial", 24, "bold"),
            fg=self.primary,
            bg=self.bg_color,
            anchor="w",
        )
        title.pack(anchor="w")
        subtitle = tk.Label(
            header_frame,
            text="Organize delivery requests into trips with a 10 kg capacity.",
            font=("Arial", 11),
            fg=self.secondary,
            bg=self.bg_color,
            anchor="w",
        )
        subtitle.pack(anchor="w", pady=(3, 0))
        control_frame = tk.Frame(
            main_frame,
            bg=self.white,
            highlightbackground=self.border,
            highlightthickness=1,
        )
        control_frame.pack(fill="x", pady=(0, 15))
        control_content = tk.Frame(control_frame, bg=self.white)
        control_content.pack(fill="x", padx=18, pady=15)
        file_section = tk.Frame(control_content, bg=self.white)
        file_section.pack(fill="x")
        file_title = tk.Label(
            file_section,
            text="Input File",
            font=("Arial", 10, "bold"),
            fg=self.primary,
            bg=self.white,
            anchor="w",
        )
        file_title.pack(anchor="w")
        self.file_label = tk.Label(
            file_section,
            text="No CSV file selected",
            font=("Arial", 10),
            fg=self.muted,
            bg=self.white,
            anchor="w",
        )
        self.file_label.pack(anchor="w", pady=(4, 10))
        self.selected_file = None
        button_frame = tk.Frame(control_content, bg=self.white)
        button_frame.pack(anchor="w")
        choose_button = tk.Button(
            button_frame,
            text="Choose CSV File",
            width=18,
            command=self.choose_file,
            bg=self.primary,
            fg=self.white,
            activebackground=self.secondary,
            activeforeground=self.white,
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
        )
        choose_button.grid(row=0, column=0, padx=(0, 8))
        generate_button = tk.Button(
            button_frame,
            text="Generate Trips",
            width=18,
            command=self.generate_trips,
            bg=self.accent,
            fg=self.white,
            activebackground=self.accent_dark,
            activeforeground=self.white,
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
        )
        generate_button.grid(row=0, column=1, padx=8)
        export_button = tk.Button(
            button_frame,
            text="Export Result",
            width=18,
            command=self.export_result,
            bg=self.accent,
            fg=self.white,
            activebackground=self.accent_dark,
            activeforeground=self.white,
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
        )
        export_button.grid(row=0, column=2, padx=8)
        clear_button = tk.Button(
            button_frame,
            text="Clear",
            width=18,
            command=self.clear,
            bg=self.table_header,
            fg=self.primary,
            activebackground=self.border,
            activeforeground=self.primary,
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
        )
        clear_button.grid(row=0, column=3, padx=(8, 0))
        summary_frame = tk.Frame(main_frame, bg=self.bg_color)
        summary_frame.pack(fill="x", pady=(0, 10))
        summary_title = tk.Label(
            summary_frame,
            text="Results Summary",
            font=("Arial", 10, "bold"),
            fg=self.primary,
            bg=self.bg_color,
            anchor="w",
        )
        summary_title.pack(anchor="w")
        self.summary_label = tk.Label(
            summary_frame,
            text="",
            font=("Arial", 10),
            fg=self.secondary,
            bg=self.bg_color,
            anchor="w",
        )
        self.summary_label.pack(anchor="w", pady=(3, 0))
        table_container = tk.Frame(
            main_frame,
            bg=self.white,
            highlightbackground=self.border,
            highlightthickness=1,
        )
        table_container.pack(fill="both", expand=True, pady=(0, 12))
        table_frame = tk.Frame(table_container, bg=self.white)
        table_frame.pack(fill="both", expand=True, padx=1, pady=1)
        columns = (
            "trip",
            "delivery_id",
            "area",
            "priority",
            "weight",
            "trip_total",
            "remaining",
        )
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings"
        )
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
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
            style="Vertical.TScrollbar",
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        rejected_frame = tk.Frame(
            main_frame,
            bg=self.white,
            highlightbackground=self.border,
            highlightthickness=1,
        )
        rejected_frame.pack(fill="x")
        rejected_header = tk.Frame(rejected_frame, bg=self.white)
        rejected_header.pack(fill="x", padx=15, pady=(10, 5))
        rejected_title = tk.Label(
            rejected_header,
            text="Rejected Deliveries",
            font=("Arial", 10, "bold"),
            fg=self.primary,
            bg=self.white,
            anchor="w",
        )
        rejected_title.pack(anchor="w")
        self.rejected_text = tk.Text(
            rejected_frame,
            height=4,
            state="disabled",
            font=("Arial", 9),
            fg=self.text,
            bg="#FAFBFC",
            relief="flat",
            bd=0,
            wrap="word",
        )
        self.rejected_text.pack(fill="x", padx=15, pady=(0, 12))

    def choose_file(self):
        filename = filedialog.askopenfilename(
            title="Select Delivery CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if filename:
            self.selected_file = filename
            self.file_label.config(
                text=f"Selected: {filename}", fg=self.text
            )

    def check_missing_columns(self):
        required_columns = {
            "id": "ID",
            "area": "Area",
            "priority": "Priority",
            "weight": "Weight",
        }
        with open(
            self.selected_file, "r", newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.reader(file)
            header = next(reader, None)
        if header is None:
            return list(required_columns.values())
        actual_columns = {column.strip().lower() for column in header}
        missing_columns = []
        for column, display_name in required_columns.items():
            if column not in actual_columns:
                missing_columns.append(display_name)
        return missing_columns

    def generate_trips(self):
        if not self.selected_file:
            messagebox.showwarning(
                "No File", "Please choose a CSV file first."
            )
            return
        try:
            missing_columns = self.check_missing_columns()
            if missing_columns:
                self.generated_trips = []
                self.rejected_deliveries = []
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.summary_label.config(
                    text="No trips generated because the CSV is missing required columns."
                )
                self.rejected_text.config(state="normal")
                self.rejected_text.delete("1.0", tk.END)
                if len(missing_columns) == 1:
                    self.rejected_text.insert(
                        tk.END, f"Missing column: {missing_columns[0]}"
                    )
                else:
                    self.rejected_text.insert(
                        tk.END,
                        "Missing columns: " + ", ".join(missing_columns),
                    )
                self.rejected_text.config(state="disabled")
                return
            deliveries = read_deliveries(self.selected_file)
            if not deliveries:
                self.generated_trips = []
                self.rejected_deliveries = []
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.summary_label.config(text="No deliveries found.")
                self.rejected_text.config(state="normal")
                self.rejected_text.delete("1.0", tk.END)
                self.rejected_text.insert(
                    tk.END, "No deliveries found in the selected CSV file."
                )
                self.rejected_text.config(state="disabled")
                return
            valid_deliveries, rejected = validate_deliveries(deliveries)
            self.rejected_deliveries = rejected
            if not valid_deliveries:
                self.generated_trips = []
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.summary_label.config(
                    text=f"No valid deliveries found. Rejected: {len(rejected)}"
                )
                self.rejected_text.config(state="normal")
                self.rejected_text.delete("1.0", tk.END)
                for delivery, reason in rejected:
                    delivery_id = (
                        delivery["id"]
                        if delivery["id"] is not None
                        else "Missing"
                    )
                    area = delivery["area"] if delivery["area"] else "Missing"
                    priority = (
                        delivery["priority"]
                        if delivery["priority"] is not None
                        else "Missing"
                    )
                    weight = (
                        delivery["weight"]
                        if delivery["weight"] is not None
                        else "Missing"
                    )
                    self.rejected_text.insert(
                        tk.END,
                        f"ID: {delivery_id} | Area: {area} | Priority: {priority} | Weight: {weight} | Reason: {reason}\n",
                    )
                self.rejected_text.config(state="disabled")
                return
            trips = create_trips(valid_deliveries)
            self.generated_trips = trips
            self.display_trips(trips, len(valid_deliveries), rejected)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def export_result(self):
        if not self.generated_trips and not self.rejected_deliveries:
            messagebox.showwarning(
                "No Data", "There are no generated trips to export."
            )
            return

        filename = filedialog.asksaveasfilename(
            title="Export Delivery Trips",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )

        if filename:
            try:
                export_trips_to_csv(filename, self.generated_trips, self.rejected_deliveries)
                messagebox.showinfo(
                    "Success", f"Trips successfully exported to:\n{filename}"
                )
            except Exception as error:
                messagebox.showerror("Export Error", str(error))

    def display_trips(self, trips, valid_count, rejected):
        for item in self.tree.get_children():
            self.tree.delete(item)
        total_weight = 0
        for trip_number, trip in enumerate(trips, start=1):
            trip_weight = get_trip_weight(trip)
            remaining_capacity = get_remaining_capacity(trip)
            total_weight += trip_weight
            trip_tag = "trip_even" if trip_number % 2 == 0 else "trip_odd"
            for delivery in trip:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        trip_number,
                        delivery["id"],
                        delivery["area"],
                        delivery["priority"],
                        f"{delivery['weight']:.1f} kg",
                        f"{trip_weight:.1f} kg",
                        f"{remaining_capacity:.1f} kg",
                    ),
                    tags=(trip_tag,),
                )
        self.summary_label.config(
            text=f"Valid Deliveries: {valid_count}    |    Trips: {len(trips)}    |    Total Weight: {total_weight:.1f} kg    |    Rejected: {len(rejected)}"
        )
        self.rejected_text.config(state="normal")
        self.rejected_text.delete("1.0", tk.END)
        if rejected:
            for delivery, reason in rejected:
                delivery_id = (
                    delivery["id"] if delivery["id"] is not None else "Missing"
                )
                area = delivery["area"] if delivery["area"] else "Missing"
                priority = (
                    delivery["priority"]
                    if delivery["priority"] is not None
                    else "Missing"
                )
                weight = (
                    delivery["weight"]
                    if delivery["weight"] is not None
                    else "Missing"
                )
                self.rejected_text.insert(
                    tk.END,
                    f"ID: {delivery_id} | Area: {area} | Priority: {priority} | Weight: {weight} | Reason: {reason}\n",
                )
        else:
            self.rejected_text.insert(tk.END, "No rejected deliveries.")
        self.rejected_text.config(state="disabled")

    def clear(self):
        self.selected_file = None
        self.generated_trips = []
        self.rejected_deliveries = []
        self.file_label.config(
            text="No CSV file selected", fg=self.muted
        )
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