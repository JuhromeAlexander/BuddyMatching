import math
import numpy as np
import os
import pandas as pd
import random
from scipy.optimize import linear_sum_assignment

class Matcher:

    def __init__(self, file_names, exchanger_data, exchanger_prefs, buddy_data, 
                 buddy_prefs, matching_prefs, matching_pts):
        self.file_names = file_names
        self.exchanger_data = exchanger_data
        self.exchanger_prefs = exchanger_prefs
        self.buddy_data = buddy_data
        self.buddy_prefs = buddy_prefs
        self.matching_prefs = matching_prefs
        self.matching_pts = matching_pts

        # Validation checks
        if len(self.matching_pts) < 3: raise Exception("Please fill up compulsory fields for Matching Points")
        if len(self.file_names) < 3: raise Exception("Please fill up compulsory fields for File Names")
        if len(self.matching_prefs) < 2: raise Exception("Please fill up compulsory fields for Matching Preference")
        if len(self.exchanger_prefs) < 5: raise Exception("Please fill up compulsory fields for Exchanger Preference")
        if len(self.buddy_prefs) < 5: raise Exception("Please fill up compulsory fields for Buddy Preference")

    class Exchanger:
        def __init__(self, info, gender, match_gender, faculty, match_faculty, 
                     interests, match_pts):
            self.info = info
            self.gender = gender
            self.match_gender = match_gender
            self.faculty = faculty
            self.match_faculty = match_faculty
            self.interests = interests
            self.match_pts = match_pts

        def pure_match_score(self, buddy):
            score = 0

            # Gender Prefs - Highest Priority
            if self.match_gender and buddy.match_gender:
                if self.gender == buddy.gender:
                    score += self.match_pts[1] * 1.0
                else:
                    score -= self.match_pts[1]
            elif self.match_gender and not buddy.match_gender:
                if self.gender == buddy.gender:
                    score += self.match_pts[1] * 0.8
                else:
                    score -= self.match_pts[1]
            elif not self.match_gender and buddy.match_gender:
                if self.gender == buddy.gender:
                    score += self.match_pts[1] * 0.6
                else:
                    score -= self.match_pts[1] * 0.5
            else:
                if self.gender == buddy.gender:
                    score += self.match_pts[2] / 2
                else:
                    score += 0

            # Faculty Prefs 
            if self.match_faculty or buddy.match_faculty:
                matched = any(fac in self.faculty for fac in buddy.faculty)
                if matched:
                    score += self.match_pts[0]
                else:
                    score -= self.match_pts[0]
            else:
                score += self.match_pts[0] / 5

            # Interests Prefs
            for interest in self.interests:
                if interest in buddy.interests:
                    score += self.match_pts[2]

            return score


    class Buddy:
        def __init__(self, info, gender, match_gender, faculty, match_faculty, 
                     interests, matching_prefs):
            self.info = info
            self.faculty = faculty
            self.match_faculty = match_faculty
            self.gender = gender
            self.match_gender = match_gender
            self.interests = interests
            self.odds = random.randint(0, 9)
            self.exchangers = []

            self.max_num_exchangers = matching_prefs[0]
            self.percentage_buddies_with_max = math.ceil(matching_prefs[1] / 10)
        
        def get_capacity(self):
            capacity = self.max_num_exchangers
            if self.odds < 10 - self.percentage_buddies_with_max:
                capacity = max(1, capacity - 1)
            return capacity
        
        def add_exchanger(self, exchanger):
            self.exchangers.append(exchanger)

def match(self):
        def load_data(filepath):
            # Check the file extension
            _, ext = os.path.splitext(filepath)
            ext = ext.lower()

            if ext == '.csv':
                try:
                    return pd.read_csv(filepath, encoding='utf-8', encoding_errors='replace')
                except UnicodeDecodeError:
                    return pd.read_csv(filepath, encoding='cp1252', encoding_errors='replace')
            elif ext in ['.xlsx', '.xls']:
                # openpyxl handles the background decoding for Excel files
                return pd.read_excel(filepath)
            else:
                raise Exception(f"Unsupported file type: {ext}. Please use .csv or .xlsx")
            
        exchangers_data = load_data(self.file_names[0])
        buddies_data = load_data(self.file_names[1])

        # Simple Automated Pre-Processing
        exchanger_faculty, exchanger_match_faculty, exchanger_gender, exchanger_match_gender, exchanger_interests = self.exchanger_prefs
        buddy_faculty, buddy_match_faculty, buddy_gender, buddy_match_gender, buddy_interests = self.buddy_prefs

        exchagers_data = exchangers_data.drop_duplicates()
        buddies_data = buddies_data.drop_duplicates()

        exchangers_data = exchangers_data.sort_values(
            by=[exchanger_match_faculty, exchanger_match_gender], ascending=[False, False]
        )

        buddies_data = buddies_data.sort_values(
            by=[buddy_match_faculty, buddy_match_gender], ascending=[False, False]
        )

        exchangers = []
        buddies = []

        # Parse Exchangers
        for _, data in exchagers_data.iterrows():
            info = [data[col] for col in self.exchanger_data]
            faculty = str(data[exchanger_faculty]).split(';')[:-1]
            match_faculty = data[exchanger_match_faculty] == 'Yes'
            gender = data[exchanger_gender]
            match_gender = data[exchanger_match_gender] == 'Yes'
            interests = str(data[exchanger_interests]).split(';')[:-1]

            exchangers.append(self.Exchanger(info, gender, match_gender, faculty, match_faculty, interests, self.matching_pts))

        # Parse Buddies
        for _, data in buddies_data.iterrows():
            info = [data[col] for col in self.buddy_data]
            faculty = str(data[buddy_faculty]).split(';')[:-1]
            match_faculty = data[buddy_match_faculty] == 'Yes'
            gender = data[buddy_gender]
            match_gender = data[buddy_match_gender] == 'Yes'
            interests = str(data[buddy_interests]).split(';')[:-1]

            buddies.append(self.Buddy(info, gender, match_gender, faculty, match_faculty, interests, self.matching_prefs))

        buddy_slots = []
        for buddy in buddies:
            for slot_ndx in range(buddy.get_capacity()):
                buddy_slots.append((buddy, slot_ndx))
        
        if len(exchangers) > len(buddy_slots):
            raise Exception("Not enough buddy slots for exchangers. Please adjust the matching preferences or add more buddies.")
        
        # Create Cost Matrix
        num_exchangers = len(exchangers)
        num_buddy_slots = len(buddy_slots)
        cost_matrix = np.zeros((num_exchangers, num_buddy_slots))

        for i, exchanger in enumerate(exchangers):
            for j, (buddy, slot_ndx) in enumerate(buddy_slots):
                score = exchanger.pure_match_score(buddy)

                if slot_ndx > 0:
                    score -= 100 * slot_ndx
                cost_matrix[i][j] = -score
        
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Assign Matches
        matchings = []
        for i, j in zip(row_ind, col_ind):
            assigned_exchanger = exchangers[i]
            assigned_buddy, _ = buddy_slots[j]
            assigned_buddy.add_exchanger(assigned_exchanger)

            if assigned_buddy not in matchings:
                matchings.append(assigned_buddy)
        
        for buddy in buddies:
            if buddy not in matchings:
                matchings.append(buddy)
        
        # Exporting to CSV
        results = []
        for buddy in matchings:
            if not buddy.exchangers:
                buddy.exchangers = [None]
            
            for exchanger in buddy.exchangers:
                result = {f"Buddy_{self.buddy_data[i]}": buddy.info[i] for i in range(len(self.buddy_data))}
                result.update({
                    f"Buddy_{buddy_faculty}": ';'.join(buddy.faculty),
                    f"Buddy_{buddy_match_faculty}": 'Yes' if buddy.match_faculty else 'No preference',
                    f"Buddy_{buddy_gender}": buddy.gender,
                    f"Buddy_{buddy_match_gender}": 'Yes' if buddy.match_gender else 'No preference',
                    f"Buddy_{buddy_interests}": ';'.join(buddy.interests)
                })

                if exchanger:
                    result.update({f"Exchanger_{self.exchanger_data[i]}": exchanger.info[i] for i in range(len(self.exchanger_data))})
                    result.update({
                        f"Exchanger_{exchanger_faculty}": ';'.join(exchanger.faculty),
                        f"Exchanger_{exchanger_match_faculty}": 'Yes' if exchanger.match_faculty else 'No preference',
                        f"Exchanger_{exchanger_gender}": exchanger.gender,
                        f"Exchanger_{exchanger_match_gender}": 'Yes' if exchanger.match_gender else 'No preference',
                        f"Exchanger_{exchanger_interests}": ';'.join(exchanger.interests),
                    })
                else:
                    # Fill Exchanger columns with blanks
                    result.update({f"Exchanger_{col}": "" for col in self.exchanger_data})
                    result.update({
                        f"Exchanger_{exchanger_faculty}": "", f"Exchanger_{exchanger_match_faculty}": "",
                        f"Exchanger_{exchanger_gender}": "", f"Exchanger_{exchanger_match_gender}": "",
                        f"Exchanger_{exchanger_interests}": ""
                    })

                results.append(result)

        matchings_data = pd.DataFrame(results)
        matchings_data.to_csv(self.file_names[2], index=False, encoding='utf-8-sig')

# Testing for CLI, no app yet
if __name__ == "__main__":
    files = ["Exchangers.xlsx", "Buddies.xlsx", "Final_Matchings.csv"]
    exchanger_info_cols = [
        "Full Name in English (as on your Passport):",
        "NUS Email Address (exxxxxxx@u.nus.edu):",
        "Personal Email Address:",
        "Telegram Handle (do not include the @):",
        "Home Country:",
        "Home University (in English):",
        "Major of study (if any):",
        "Faculty of study at NUS:",
        "Year of Study at Home University (at Jan 2026):",
        "(Optional) If you have any other comments or preferences regarding the matching, please let us know below!"
    ]

    buddy_info_cols = [
        "Full Name (as on your matric card):",
        "NUS Email Address (exxxxxxx@u.nus.edu):",
        "Personal Email Address:",
        "Telegram Handle (do not include the @):",
        "Major:",
        "Year and semester of study (as of AY25/26 Sem 2):",
        "Faculty:",
        "(Optional) If you have any other comments or preferences regarding the matching, please let us know below!"
    ]

    #Preferences
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
        "Share with us your interests! (Top 3)"
    ]

    matching_prefs = [3, 30] # Max Exchangers per Buddy, Percentage of Buddies with Max Exchangers
    matching_pts = [2, 10, 5] # Faculty Match, Gender Match, Interest Match

    print("Running Matcher...")
    try:
        matcher = Matcher(
            file_names=files,
            exchanger_data=exchanger_info_cols,
            exchanger_prefs=exchanger_prefs,
            buddy_data=buddy_info_cols,
            buddy_prefs=buddy_prefs,
            matching_prefs=matching_prefs,
            matching_pts=matching_pts
        )

        print("Matching in progress...")
        matcher.match()
        print("Matching completed successfully! Check Final_Matchings.csv for results.")
    except Exception as e:
        print(f"Error: {e}")