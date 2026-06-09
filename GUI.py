import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from Matcher import Matcher

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NUS Buddy Matching - Matcher App")
        self.geometry("750x800")
        
        # File Paths
        self.exchanger_file = ctk.StringVar()
        self.buddy_file = ctk.StringVar()

        # Dictionaries to store our dynamic UI variables
        self.exch_info_vars = {}   # Checkboxes
        self.buddy_info_vars = {}  # Checkboxes
        self.exch_pref_vars = {}   # Dropdowns
        self.buddy_pref_vars = {}  # Dropdowns

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self, text="NUS Buddy Matching Engine", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=10, padx=10)

        # Tab View for better organization
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tabs.add("1. Files & Settings")
        self.tabs.add("2. Exchanger Map")
        self.tabs.add("3. Buddy Map")

        self.build_files_tab()
        self.build_mapping_tabs()

        # Run Button & Console
        self.run_btn = ctk.CTkButton(self, text="RUN MATCHING ALGORITHM", fg_color="green", hover_color="darkgreen", height=50, command=self.run_matching)
        self.run_btn.pack(pady=10, padx=20, fill="x")
        
        self.console = ctk.CTkTextbox(self, height=100)
        self.console.pack(pady=(0, 20), padx=20, fill="x")
        self.console.insert("0.0", "System Ready. Please select your Excel files.\n")
        self.console.configure(state="disabled")

    def build_files_tab(self):
        tab = self.tabs.tab("1. Files & Settings")

        # Exchanger File
        ctk.CTkLabel(tab, text="Select Exchangers File (.xlsx)", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        ctk.CTkButton(tab, text="Browse...", command=self.browse_exchanger).pack(pady=5)
        ctk.CTkLabel(tab, textvariable=self.exchanger_file, text_color="gray").pack(pady=(0, 10))

        # Buddy File
        ctk.CTkLabel(tab, text="Select Buddies File (.xlsx)", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        ctk.CTkButton(tab, text="Browse...", command=self.browse_buddy).pack(pady=5)
        ctk.CTkLabel(tab, textvariable=self.buddy_file, text_color="gray").pack(pady=(0, 10))

        # Settings Frame
        settings_frame = ctk.CTkFrame(tab, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=10)

        # Lottery Settings (Left Side)
        lottery_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        lottery_frame.pack(side="left", expand=True)
        ctk.CTkLabel(lottery_frame, text="Lottery Settings", font=ctk.CTkFont(weight="bold")).pack(pady=(0, 5))
        self.lottery_slider = ctk.CTkSlider(lottery_frame, from_=0, to=100, number_of_steps=10, command=self.update_slider_label)
        self.lottery_slider.set(40)
        self.lottery_slider.pack(pady=5)
        self.lottery_label = ctk.CTkLabel(lottery_frame, text="Lottery Win Chance: 40%")
        self.lottery_label.pack()

        # Algorithm Points Settings (Right Side)
        pts_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        pts_frame.pack(side="right", expand=True)
        ctk.CTkLabel(pts_frame, text="Algorithm Point Weights", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5))

        self.fac_pts = ctk.StringVar(value="5")
        self.gen_pts = ctk.StringVar(value="10")
        self.int_pts = ctk.StringVar(value="2")

        ctk.CTkLabel(pts_frame, text="Faculty Match:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ctk.CTkEntry(pts_frame, textvariable=self.fac_pts, width=40).grid(row=1, column=1, sticky="w", pady=2)

        ctk.CTkLabel(pts_frame, text="Gender Match:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ctk.CTkEntry(pts_frame, textvariable=self.gen_pts, width=40).grid(row=2, column=1, sticky="w", pady=2)

        ctk.CTkLabel(pts_frame, text="Interest Match:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        ctk.CTkEntry(pts_frame, textvariable=self.int_pts, width=40).grid(row=3, column=1, sticky="w", pady=2)

    def build_mapping_tabs(self):
        self.exch_scroll = ctk.CTkScrollableFrame(self.tabs.tab("2. Exchanger Map"))
        self.exch_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.exch_scroll, text="Waiting for Exchanger file...", text_color="gray").pack(pady=20)

        self.buddy_scroll = ctk.CTkScrollableFrame(self.tabs.tab("3. Buddy Map"))
        self.buddy_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.buddy_scroll, text="Waiting for Buddy file...", text_color="gray").pack(pady=20)

    # Dynamic Loading + File Browsing
    def browse_exchanger(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if filename: 
            self.exchanger_file.set(filename)
            self.load_columns(filename, "exchanger")

    def browse_buddy(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if filename: 
            self.buddy_file.set(filename)
            self.load_columns(filename, "buddy")

    def load_columns(self, filename, target):
        try:
            # Instantly read just the headers
            df = pd.read_excel(filename, nrows=0) if filename.endswith(('.xlsx', '.xls')) else pd.read_csv(filename, nrows=0)
            columns = df.columns.tolist()

            if target == "exchanger":
                self.populate_mapping_ui(self.exch_scroll, columns, self.exch_info_vars, self.exch_pref_vars, target)
                self.log("Exchanger columns loaded dynamically.")
            else:
                self.populate_mapping_ui(self.buddy_scroll, columns, self.buddy_info_vars, self.buddy_pref_vars, target)
                self.log("Buddy columns loaded dynamically.")

        except Exception as e:
            messagebox.showerror("Error Reading File", f"Could not read columns from file:\n{str(e)}")

    def populate_mapping_ui(self, parent_frame, columns, info_vars_dict, pref_vars_dict, target):
        # Clear existing widgets
        for widget in parent_frame.winfo_children():
            widget.destroy()
        info_vars_dict.clear()
        pref_vars_dict.clear()

        # Checkboxes - Output Information
        ctk.CTkLabel(parent_frame, text="1. Select Output Information", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(10, 5), anchor="w")
        ctk.CTkLabel(parent_frame, text="Check the boxes you want included in the final CSV, not everything needs to be selected!:", text_color="gray").pack(anchor="w", pady=(0,10))

        for col in columns:
            var = ctk.BooleanVar(value=True) # Default to checked
            cb = ctk.CTkCheckBox(parent_frame, text=col, variable=var)
            cb.pack(anchor="w", pady=2)
            info_vars_dict[col] = var

        # Dropdowns - Algo Preferences 
        ctk.CTkLabel(parent_frame, text="\n2. Map Algorithm Preferences", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 5), anchor="w")
        ctk.CTkLabel(parent_frame, text="Match the exact column to the required algorithm data:", text_color="gray").pack(anchor="w", pady=(0,10))

        pref_labels = [
            "Faculty Column:", 
            "Same Faculty Preference Column:", 
            "Gender Column:", 
            "Same Gender Preference Column:", 
            "Interests (Top 3) Column:"
        ]
        
        # Keywords to help the Auto-Guesser
        keywords = [
            ["faculty"],
            ["same faculty"],
            ["gender", "sex"],
            ["same gender"],
            ["interest", "hobby", "share"]
        ]

        if target == "buddy":
            pref_labels.append("Capacity Column:")
            keywords.append(["capacity", "how many", "number"])

        options = ["-- Select Column --"] + columns

        for i, label in enumerate(pref_labels):
            ctk.CTkLabel(parent_frame, text=label).pack(anchor="w", pady=(5,0))
            dropdown = ctk.CTkComboBox(parent_frame, values=options, width=400)
            
            # The Auto-Guesser Logic
            best_guess = "-- Select Column --"
            for col in columns:
                if any(kw in col.lower() for kw in keywords[i]):
                    best_guess = col
                    break
            
            dropdown.set(best_guess)
            dropdown.pack(anchor="w", pady=(0, 5))
            pref_vars_dict[i] = dropdown

    # --- Utilities & Execution ---
    def update_slider_label(self, value):
        self.lottery_label.configure(text=f"Lottery Win Chance: {int(value)}%")

    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")
        self.update()

    def run_matching(self):
        exch_path = self.exchanger_file.get()
        buddy_path = self.buddy_file.get()

        if not exch_path or not buddy_path:
            messagebox.showwarning("Missing Files", "Please select both the Exchangers and Buddies files on Tab 1!")
            return

        # Gather dynamic Checkbox data
        exchanger_info_cols = [col for col, var in self.exch_info_vars.items() if var.get()]
        buddy_info_cols = [col for col, var in self.buddy_info_vars.items() if var.get()]

        # Gather dynamic Dropdown data safely using the length of the dictionaries
        exchanger_prefs = [self.exch_pref_vars[i].get() for i in range(len(self.exch_pref_vars))]
        buddy_prefs = [self.buddy_pref_vars[i].get() for i in range(len(self.buddy_pref_vars))]

        # Validate that no dropdowns were left unselected
        if "-- Select Column --" in exchanger_prefs or "-- Select Column --" in buddy_prefs:
            messagebox.showwarning("Incomplete Mapping", "Please ensure all Algorithm Preferences are selected in Tabs 2 and 3!")
            return

        self.log("\nStarting matching process...")
        self.run_btn.configure(state="disabled", text="MATCHING...")

        try:
            output_dir = os.path.dirname(buddy_path)
            buddy_out = os.path.join(output_dir, "Final_Matchings_Buddy.csv")
            exch_out = os.path.join(output_dir, "Final_Matchings_Exchanger.csv")
            files = [exch_path, buddy_path, buddy_out, exch_out]

            matching_prefs = [2, int(self.lottery_slider.get())]

            # Pull points from UI
            try:
                f_pts = int(self.fac_pts.get())
                g_pts = int(self.gen_pts.get())
                i_pts = int(self.int_pts.get())
                matching_pts = [f_pts, g_pts, i_pts]
            except ValueError:
                self.run_btn.configure(state="normal", text="RUN MATCHING ALGORITHM")
                messagebox.showerror("Invalid Input", "Matching point weights must be whole numbers!")
                return

            # Pass to Engine
            my_matcher = Matcher(files, exchanger_info_cols, exchanger_prefs, buddy_info_cols, buddy_prefs, matching_prefs, matching_pts)
            my_matcher.match()

            self.log(f"SUCCESS! Files saved to:\n- {buddy_out}\n- {exch_out}")
            messagebox.showinfo("Success", "Matching complete! Check the folder where your Buddies Excel file is located.")

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            self.run_btn.configure(state="normal", text="RUN MATCHING ALGORITHM")

if __name__ == "__main__":
    app = MatcherApp()
    app.mainloop()