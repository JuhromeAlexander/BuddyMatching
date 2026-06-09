import customtkinter as ctk
from tkinter import filedialog, messagebox
from Matcher import Matcher
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NUS Buddy Matching - Matcher App")
        self.geometry("600x600")
        
        # File Paths
        self.exchanger_file = ctk.StringVar()
        self.buddy_file = ctk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self, text="NUS Buddy Matching - Matcher App", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20, padx=10)

        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=10, padx=20, fill="x")

        #Exchanger File
        ctk.CTkLabel(file_frame, text="1. Select Exchangers File (.xlsx)").pack(pady=(10, 0))
        exch_btn = ctk.CTkButton(file_frame, text="Browse...", command=self.browse_exchanger)
        exch_btn.pack(pady=5)
        ctk.CTkLabel(file_frame, textvariable=self.exchanger_file, text_color="gray").pack(pady=(0, 10))

        # Buddy File Picker
        ctk.CTkLabel(file_frame, text="2. Select Buddies File (.xlsx)").pack(pady=(10, 0))
        buddy_btn = ctk.CTkButton(file_frame, text="Browse...", command=self.browse_buddy)
        buddy_btn.pack(pady=5)
        ctk.CTkLabel(file_frame, textvariable=self.buddy_file, text_color="gray").pack(pady=(0, 10))

        # Settings
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(settings_frame, text="3. Lottery Settings", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        
        self.lottery_slider = ctk.CTkSlider(settings_frame, from_=0, to=100, number_of_steps=10)
        self.lottery_slider.set(40) # Default to 40%
        self.lottery_slider.pack(pady=5)
        
        self.lottery_label = ctk.CTkLabel(settings_frame, text="Lottery Win Chance: 40%")
        self.lottery_label.pack(pady=(0, 10))
        self.lottery_slider.configure(command=self.update_slider_label)

        # 4. Run Button
        self.run_btn = ctk.CTkButton(self, text="RUN MATCHING ALGORITHM", fg_color="green", hover_color="darkgreen", height=50, command=self.run_matching)
        self.run_btn.pack(pady=20, padx=20, fill="x")
        
        # 5. Status Console
        self.console = ctk.CTkTextbox(self, height=100)
        self.console.pack(pady=10, padx=20, fill="x")
        self.console.insert("0.0", "System Ready. Please select your Excel files.\n")
        self.console.configure(state="disabled")

    # --- Helper Functions ---
    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")
        self.update() # Force UI to update

    def update_slider_label(self, value):
        self.lottery_label.configure(text=f"Lottery Win Chance: {int(value)}%")

    def browse_exchanger(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if filename: self.exchanger_file.set(filename)

    def browse_buddy(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if filename: self.buddy_file.set(filename)
    
    def run_matching(self):
        exch_path = self.exchanger_file.get()
        buddy_path = self.buddy_file.get()

        if not exch_path or not buddy_path:
            messagebox.showwarning("Missing Files", "Please select both the Exchangers and Buddies files!")
            return

        self.log("\nStarting matching process...")
        self.run_btn.configure(state="disabled", text="MATCHING...")

        try:
            # Generate output filenames in the same folder as the Buddy file
            output_dir = os.path.dirname(buddy_path)
            buddy_out = os.path.join(output_dir, "Final_Matchings_Buddy.csv")
            exch_out = os.path.join(output_dir, "Final_Matchings_Exchanger.csv")
            files = [exch_path, buddy_path, buddy_out, exch_out]

            exchanger_info_cols = ["Full Name in English (as on your Passport):", "NUS Email Address (exxxxxxx@u.nus.edu):", "Personal Email Address:", "Telegram Handle (do not include the @):", "Home Country:", "Home University (in English):", "Major of study (if any):", "Faculty of study at NUS:", "Year of Study at Home University (at Jan 2026):", "(Optional) If you have any other comments or preferences regarding the matching, please let us know below!"]
            buddy_info_cols = ["Full Name (as on your matric card):", "NUS Email Address (exxxxxxx@u.nus.edu):", "Personal Email Address:", "Telegram Handle (do not include the @):", "Major:", "Year and semester of study (as of AY25/26 Sem 2):", "Faculty:", "(Optional) If you have any other comments or preferences regarding the matching, please let us know below!"]
            exchanger_prefs = [
                "Faculty of study at NUS:",
                "Would you want to be matched with a buddy from the same faculty?",
                "Gender:",
                "Would you want to be matched with a buddy of the same gender?",
                "Share with us your interests! (Top 3)"
            ]

            buddy_prefs = [
                "Faculty:",
                "Would you like to be matched with exchangers from the same faculty?",
                "Gender:",
                "Would you like to be matched with exchangers of the same gender? ",
                "Share with us your interests! (Top 3)",
                "Capacity"
            ]

            matching_prefs = [2, int(self.lottery_slider.get())]
            matching_pts = [2, 10, 5]

            # Initialize and run your engine
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