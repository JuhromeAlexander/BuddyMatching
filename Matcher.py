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
                     interests, preferred_capacity, matching_prefs):
            self.info = info
            self.faculty = faculty
            self.match_faculty = match_faculty
            self.gender = gender
            self.match_gender = match_gender
            self.interests = interests
            self.exchangers = []

            self.preferred_capacity_str = str(preferred_capacity).strip().lower()
            if self.preferred_capacity_str == "yes":
                self.requested_capacity = 2
            else:
                self.requested_capacity = 1

            self.odds = matching_prefs[1]
            self.roll = random.randint(1, 100)
            
        
        def get_capacity(self):
            if self.requested_capacity == 1:
                return 1
            
            if self.roll <= self.odds:
                return 2
            else:
                return 1
        
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
        buddy_faculty, buddy_match_faculty, buddy_gender, buddy_match_gender, buddy_interests, buddy_capacity_pref = self.buddy_prefs

        exchangers_data = exchangers_data.drop_duplicates()
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
        for _, data in exchangers_data.iterrows():
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
            preferred_cap = data[buddy_capacity_pref]

            buddies.append(self.Buddy(info, gender, match_gender, faculty, match_faculty, interests, preferred_cap, self.matching_prefs))

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
                    score -= 10000 * slot_ndx
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
        results_buddies = []
        results_exchangers = []
        max_exchangers_per_buddy = self.matching_prefs[0]

        for buddy in matchings:
            # Buddy Facing Export for MailMerge to Buddies
            buddy_row = {f"[BUDDY] {self.buddy_data[i]}": buddy.info[i] for i in range(len(self.buddy_data))}
            buddy_row.update({
                f"[BUDDY] {buddy_faculty}": ';'.join(buddy.faculty),
                f"[BUDDY] {buddy_match_faculty}": 'Yes' if buddy.match_faculty else 'No preference',
                f"[BUDDY] {buddy_gender}": buddy.gender,
                f"[BUDDY] {buddy_match_gender}": 'Yes' if buddy.match_gender else 'No preference',
                f"[BUDDY] {buddy_interests}": ';'.join(buddy.interests)
            })

            if not buddy.exchangers:
                buddy.exchangers = [None]

            for slot_num in range(max_exchangers_per_buddy):
                prefix = f"[EXCHANGER {slot_num + 1}] " 
                if slot_num < len(buddy.exchangers) and buddy.exchangers[slot_num] is not None:
                    exchanger = buddy.exchangers[slot_num]
                    buddy_row.update({f"{prefix}{self.exchanger_data[i]}": exchanger.info[i] for i in range(len(self.exchanger_data))})
                    buddy_row.update({
                        f"{prefix}{exchanger_faculty}": ';'.join(exchanger.faculty),
                        f"{prefix}{exchanger_match_faculty}": 'Yes' if exchanger.match_faculty else 'No preference',
                        f"{prefix}{exchanger_gender}": exchanger.gender,
                        f"{prefix}{exchanger_match_gender}": 'Yes' if exchanger.match_gender else 'No preference',
                        f"{prefix}{exchanger_interests}": ';'.join(exchanger.interests),
                    })
                else:
                    buddy_row.update({f"{prefix}{col}": "" for col in self.exchanger_data})
                    buddy_row.update({
                        f"{prefix}{exchanger_faculty}": "", f"{prefix}{exchanger_match_faculty}": "",
                        f"{prefix}{exchanger_gender}": "", f"{prefix}{exchanger_match_gender}": "",
                        f"{prefix}{exchanger_interests}": ""
                    })
            results_buddies.append(buddy_row)

            # Exchanger Facing Export for MailMerge to Exchangers
            for exchanger in buddy.exchangers:
                if exchanger is not None:
                    exch_row = {f"[MY INFO] {self.exchanger_data[i]}": exchanger.info[i] for i in range(len(self.exchanger_data))}
                    exch_row.update({
                        f"[MY INFO] {exchanger_faculty}": ';'.join(exchanger.faculty),
                        f"[MY INFO] {exchanger_match_faculty}": 'Yes' if exchanger.match_faculty else 'No preference',
                        f"[MY INFO] {exchanger_gender}": exchanger.gender,
                        f"[MY INFO] {exchanger_match_gender}": 'Yes' if exchanger.match_gender else 'No preference',
                        f"[MY INFO] {exchanger_interests}": ';'.join(exchanger.interests),
                    })
                    exch_row.update({f"[MY BUDDY] {self.buddy_data[i]}": buddy.info[i] for i in range(len(self.buddy_data))})
                    exch_row.update({
                        f"[MY BUDDY] {buddy_faculty}": ';'.join(buddy.faculty),
                        f"[MY BUDDY] {buddy_match_faculty}": 'Yes' if buddy.match_faculty else 'No preference',
                        f"[MY BUDDY] {buddy_gender}": buddy.gender,
                        f"[MY BUDDY] {buddy_match_gender}": 'Yes' if buddy.match_gender else 'No preference',
                        f"[MY BUDDY] {buddy_interests}": ';'.join(buddy.interests)
                    })
                    results_exchangers.append(exch_row)
                
        pd.DataFrame(results_buddies).to_csv(self.file_names[2], index=False, encoding='utf-8-sig')
        pd.DataFrame(results_exchangers).to_csv(self.file_names[3], index=False, encoding='utf-8-sig')
