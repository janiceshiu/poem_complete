class Word:

    def __init__(self, spelling:str, stress_pattern:str) -> None:
        self.spelling = spelling
        self.stress_pattern = stress_pattern

    # how you represent the thing
    def __repr__(self) -> str:
        return f"{self.spelling}: {self.stress_pattern}"

    def __eq__(self, other) -> bool:
        return self.spelling == other.spelling and self.stress_pattern == other.stress_pattern
