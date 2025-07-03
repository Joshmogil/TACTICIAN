from pydantic import BaseModel
from typing import List, Literal
from enum import Enum
import math
import numpy as np

DAYS_IN_WEEK=7

class Gender(Enum):
    FEMALE = "female"
    MALE = "male"

class Stress(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class User(BaseModel):
    name: str
    week_sleep_hours: List[float] #TODO must only contain 7 numbers
    week_stress: List[Stress] #TODO must only contain 7 numbers
    resting_hr: int

    age: int
    body_fat_estimate: float

    gender: Gender

    def _sleep_need(self) -> float:
        """
        Approximate normative daily sleep requirement (hours) as a function of
        chronological age and gender/sex.
        
        Parameters
        ----------
        age : float
            Age in years.
        gender : str
            'male', 'female', or any other identifier (case-insensitive).  Non-binary
            or unspecified values default to no gender correction.
        
        Returns
        -------
        float
            Recommended hours of sleep per 24-hour period.
        """
        # -------- baseline by age (piecewise) --------
        age = self.age
        
        if age < 3:
            base = 14.0                         # infants / toddlers
        elif age < 6:
            base = 12.0                         # preschool
        elif age < 13:
            base = 10.0                         # school-age
        elif age < 18:
            base = 9.0                          # adolescents
        elif age < 26:
            base = 8.0                          # emerging adults
        elif age < 65:
            base = 7.5                          # typical adults
        else:
            base = 7.0                          # older adults

        # -------- gender/sex adjustment --------
        g = self.gender.value
        if g == "female":
            adj = 0.3 if 13 <= age <= 45 else 0.1
        elif g == "male":
            adj = -0.1 if 13 <= age <= 25 else 0.0
        else:
            adj = 0.0                           # default / non-binary
        return base + adj


    # ---------------- 2. IDEAL RESTING HEART-RATE -------------
    def _ideal_resting_hr(self) -> float:
        """
        Estimate an 'ideal' Resting Heart Rate (RHR) in beats per minute (bpm),
        adjusted for age & sex.  The model fits the midpoint of the
        “good”/“excellent” band in large cohort tables. :contentReference[oaicite:1]{index=1}

        Formula
        -------
            RHR_male   = 57 + 0.30 × (age − 20)  for 20 ≤ age ≤ 75
            RHR_female = 60 + 0.30 × (age − 20)
        Outside that span the lines are clipped (min 55, max 80).

        Returns
        -------
        float – Target resting pulse in bpm.
        """

        age = self.age
        gender = self.gender
        # linear drift ≈ +0.30 bpm per year after age-20
        if gender == "female":
            rhr = 60 + 0.30 * max(0, age - 20)
        elif gender == "male":
            rhr = 57 + 0.30 * max(0, age - 20)
        else:                     # non-binary / unspecified – average
            rhr = 58.5 + 0.30 * max(0, age - 20)

        # physiological hard bounds
        return float(min(max(rhr, 55.0), 80.0))

    def _ideal_bodyfat(self) -> float:
        """
        Return the ideal body fat percentage based on age and gender.
        
        Uses age-stratified midpoints from large population studies and
        fitness orgs (ACSM, WHO, etc).

        Parameters:
        -----------
        age : int
            Age in years.
        gender : str
            'male' or 'female' (case-insensitive)

        Returns:
        --------
        float – Ideal body fat percentage as a float (e.g. 18.5)
        """
        age=self.age
        gender = self.gender.value


        # --- Ideal BF% midpoints by age/gender bands ---
        if gender == "male":
            if age < 20:   return 14.0
            if age < 30:   return 16.0
            if age < 40:   return 18.0
            if age < 50:   return 20.0
            if age < 60:   return 21.0
            if age < 70:   return 22.0
            return 23.0

        if gender == "female":
            if age < 20:   return 22.0
            if age < 30:   return 24.0
            if age < 40:   return 26.0
            if age < 50:   return 28.0
            if age < 60:   return 30.0
            if age < 70:   return 31.0
            return 32.0
        print(gender, age)



    def vitality_score(self) -> float:
        """
        Biological 'vitality' / anabolic-recovery potential, scaled 0-1.

        * puberty ramp  ..........  10-18 yr
        * prime plateau ..........  18-27 yr
        * exponential decline ....  >27 yr  (gender-specific rate)

        Returns
        -------
        float  --  vitality in [0, 1]
        """
        age    = self.age
        gender = self.gender.value.lower()

        # ------------- CONFIGURABLE PARAMETERS ------------------------------
        if gender == "male":
            peak         = 1.00            # plateau height
            puberty_on   = 11              # yrs
            decay_rate   = 0.045           # faster post-27 decline
        elif gender == "female":
            peak         = 0.70            # slightly lower peak, but...
            puberty_on   = 10              # earlier onset
            decay_rate   = 0.035           # slower decline
        else:                               # non-binary / unspecified
            peak         = 0.95
            puberty_on   = 10.5
            decay_rate   = 0.040

        plateau_start = 18
        plateau_end   = 27
        childhood_val = 0.30 * peak        # baseline vitality below puberty

        # ------------- PIECEWISE MODEL --------------------------------------
        if age < puberty_on:
            # linear lift from ~0.3→~0.8 of peak during childhood
            vitality = childhood_val + (0.8 * peak - childhood_val) * (age / puberty_on)

        elif age < plateau_start:
            # rapid (nearly linear) climb from 0.8→1.0 of peak
            vitality = 0.8 * peak + (peak - 0.8 * peak) * (
                (age - puberty_on) / (plateau_start - puberty_on)
            )

        elif age <= plateau_end:
            # prime years – sustain full peak
            vitality = peak

        else:
            # exponential decay after prime plateau
            vitality = peak * math.exp(-decay_rate * (age - plateau_end))

        # clamp to [0, 1] for safety
        return float(max(0.0, min(1.0, vitality)))
    
    def anabolic_factor(self, term: Literal["short", "long"]) -> float:
        a = np.array(self.week_sleep_hours)
        w = np.linspace(0.5, 2, len(a))**1.2

        weighted_sleep_hours = (a @ w / w.sum())
        # 2. normalise:  ratio of actual / required, then clamp to [0,1]
        need = self._sleep_need()                   # hours per night required
        sleep_score = np.clip(weighted_sleep_hours / need, 0.0, 1.0)


        a = np.array([s.value for s in self.week_stress], dtype=float)

        # recency-biased weights: 0.5 → 2.0, then a mild power curve
        w = np.linspace(0.5, 2.0, len(a)) ** 1.9

        weighted_stress = (a @ w) / w.sum()          # daily weighted mean

        ideal = Stress.LOW.value                     # 1
        worst = Stress.HIGH.value                    # 3  (adjust if enum differs)

        # distance from ideal, expressed as a fraction of worst-case distance
        stress_score = 1.0 - np.clip(
            (weighted_stress - ideal) / (worst - ideal),
            0.0, 1.0
        )

        ideal_bf = self._ideal_bodyfat()        # % body-fat that’s “perfect”
        ideal_hr = self._ideal_resting_hr()     # bpm that’s “perfect”

        # --- BODY-FAT -----------------------------------------------------------
        # 1 when you’re at or below ideal, linearly → 0 when you hit 2× ideal.
        bodyfat_score = np.clip(2.0 - (self.body_fat_estimate / ideal_bf), 0.0, 1.0)

        # --- RESTING HEART-RATE -------------------------------------------------
        # 1 when at/below ideal, linearly → 0 when you hit 2× ideal.
        heartrate_score = np.clip(2.0 - (self.resting_hr / ideal_hr), 0.0, 1.0)

        vitality_score = self.vitality_score()

        print(sleep_score,stress_score, bodyfat_score, heartrate_score, vitality_score)
    
        
        scores = {
            "sleep": sleep_score,
            "stress": stress_score,
            "bodyfat": bodyfat_score,
            "heartrate": heartrate_score,
            "vitality": vitality_score
        }

        # assign weights (they do not need to sum to 1; we'll normalize)
        if term == "short":
            weights = {
                "sleep":    2,    # maybe more important
                "stress":   2,
                "bodyfat":  1.0,
                "heartrate":1.0,
                "vitality": 1.5     # underlying potential
            }
        
        if term == "long":
            weights = {
                "sleep":    .5,    # maybe more important
                "stress":   .5,
                "bodyfat":  1.0,
                "heartrate":1.0,
                "vitality": 2     # underlying potential
            }


        # weighted average: sum(score × weight) / sum(weights)
        numerator   = sum(scores[k] * weights[k] for k in scores)
        denominator = sum(weights.values())
        anabolic_score = numerator / denominator
        return anabolic_score
        
if __name__ == "__main__":
    josh = User(
        name="Josh",
        week_sleep_hours=[7.5,7.5,7.5,7.5,7.5,7.5,2],
        week_stress=[1,1,1,1,1,1,1],
        age=26,
        resting_hr=75,
        body_fat_estimate=60,
        gender="male"
    )
    print(josh.anabolic_factor("short"))
    print(josh.anabolic_factor("long"))