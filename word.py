class Word:
    def __init__(self, spelling, stress_pattern):
        self.spelling = spelling
        self.stress_pattern = stress_pattern

    # how you represent the thing
    def __repr__(self):
        return f"{self.spelling}: {self.stress_pattern}"

    def __eq__(self, other):
        return self.spelling == other.spelling and self.stress_pattern == other.stress_pattern