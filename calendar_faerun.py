from datetime import datetime


class FaerunDate:
    MONTH_NAMES = [
        "Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn",
        "Flamerule", "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"
    ]

    FESTIVALS = [{
        "name": "Midwinter",
        "day": 31,
        "month": 1
    }, {
        "name": "Greengrass",
        "day": 30,
        "month": 4
    }, {
        "name": "Midsummer",
        "day": 30,
        "month": 7
    }, {
        "name": "Highharvestide",
        "day": 27,
        "month": 9
    }, {
        "name": "Feast of the Moon",
        "day": 1,
        "month": 11
    }, {
        "name": "Shieldmeet",
        "day": 31,
        "month": 7,
        "leapYearOnly": True
    }]

    WEEKDAYS = [
        "Sul", "Far", "Tar", "Sar", "Rai", "Zor", "Kyth", "Hamar", "Ith", "Alt"
    ]

    DR_YEAR_OFFSET = 628  # À utiliser si tu veux l'année DR

    @staticmethod
    def is_leap_year(year):
        # Même logique que JS (simplement divisible par 4)
        return year % 4 == 0

    def __init__(self, date):
        # date : datetime (aware ou naive, UTC de préférence)
        self.day = date.day
        self.month = date.month
        self.year = date.year
        self.real_date = date

    def get_festival(self):
        leap = FaerunDate.is_leap_year(self.year)
        for f in FaerunDate.FESTIVALS:
            if (self.day == f["day"] and self.month == f["month"]
                    and (not f.get("leapYearOnly") or leap)):
                return f["name"]
        return None

    def get_month(self):
        # Pour la date de Faerûn, tous les mois font 30 jours
        return FaerunDate.MONTH_NAMES[self.month - 1]

    def get_weekday(self):
        # Numéro du jour de l'année en Faerûn (compte les festivals avant cette date)
        day_of_year = (self.month - 1) * 30 + self.day
        festivals_before = 0
        leap = FaerunDate.is_leap_year(self.year)
        for f in FaerunDate.FESTIVALS:
            # Si festival déjà passé dans l'année
            if (f["month"] < self.month) or (f["month"] == self.month
                                             and f["day"] < self.day):
                if not f.get("leapYearOnly") or leap:
                    festivals_before += 1
        day_of_year += festivals_before
        # Les jours de la semaine Faerûn sont cycliques tous les 10 jours
        return FaerunDate.WEEKDAYS[(day_of_year - 1) % 10]

    def get_week_of_year(self):
        day_of_year = (self.month - 1) * 30 + self.day
        festivals_before = 0
        leap = FaerunDate.is_leap_year(self.year)
        for f in FaerunDate.FESTIVALS:
            if (f["month"] < self.month) or (f["month"] == self.month
                                             and f["day"] < self.day):
                if not f.get("leapYearOnly") or leap:
                    festivals_before += 1
        day_of_year += festivals_before
        return ((day_of_year - 1) // 10) + 1

    def get_dr_year(self):
        return self.year - self.DR_YEAR_OFFSET

    def get_season(self):
        # Dépend de ton lore, mais on peut faire simple :
        # Hiver : Hammer, Alturiak, Ches (1-3)
        # Printemps : Tarsakh, Mirtul, Kythorn (4-6)
        # Été : Flamerule, Eleasis, Eleint (7-9)
        # Automne : Marpenoth, Uktar, Nightal (10-12)
        if 1 <= self.month <= 3:
            return "Winter"
        elif 4 <= self.month <= 6:
            return "Spring"
        elif 7 <= self.month <= 9:
            return "Summer"
        else:
            return "Autumn"

    def to_locale_string(self):
        # Pour affichage
        festival = self.get_festival()
        dr_year = self.get_dr_year()
        week = self.get_week_of_year()
        if festival:
            return f"{festival}, {dr_year} DR – Season: {self.get_season()} – Week {week}"
        else:
            return f"{self.get_weekday()}, {self.day} {self.get_month()} {dr_year} DR – Season: {self.get_season()} – Week {week}"

    @staticmethod
    def from_datetime(date: datetime):
        return FaerunDate(date)
