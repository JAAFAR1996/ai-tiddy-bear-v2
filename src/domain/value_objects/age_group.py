from enum import Enum


class AgeGroup(Enum):
    TODDLER = "toddler"
    PRESCHOOL = "preschool"
    SCHOOL_AGE = "school_age"
    PRE_TEEN = "pre_teen"
    TEEN = "teen"

    @staticmethod
    def from_age(age: int) -> "AgeGroup":
        if 0 <= age <= 2:
            return AgeGroup.TODDLER
        if 3 <= age <= 5:
            return AgeGroup.PRESCHOOL
        if 6 <= age <= 12:
            return AgeGroup.SCHOOL_AGE
        if 13 <= age <= 15:
            return AgeGroup.PRE_TEEN
        return AgeGroup.TEEN
