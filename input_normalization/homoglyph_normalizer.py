class HomoglyphNormalizer:
    HOMOGLYPH_MAP = {
        "0": "0", "O": "0", "o": "0",
        "1": "1", "l": "1", "I": "1", "|": "1",
        "2": "2", "Z": "2", "z": "2",
        "3": "3", "E": "3", "e": "3",
        "4": "4", "A": "4", "a": "4",
        "5": "5", "S": "5", "s": "5",
        "6": "6", "G": "6", "g": "6",
        "7": "7", "T": "7", "t": "7",
        "8": "8", "B": "8", "b": "8",
        "9": "9",
        "а": "a", "Ａ": "A",
        "е": "e", "Е": "E",
        "о": "o", "О": "O",
        "с": "c", "С": "C",
        "р": "p", "Р": "P",
        "х": "x", "Х": "X",
        "і": "i", "І": "I",
        "ѕ": "s",
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        result = []
        for c in text:
            result.append(cls.HOMOGLYPH_MAP.get(c, c))
        return "".join(result)

    @classmethod
    def detect_homoglyph(cls, text: str) -> list[dict]:
        found = []
        for i, c in enumerate(text):
            if c in cls.HOMOGLYPH_MAP and c != cls.HOMOGLYPH_MAP[c]:
                found.append({
                    "position": i,
                    "original": c,
                    "normalized": cls.HOMOGLYPH_MAP[c],
                })
        return found
