import unicodedata


class UnicodeNormalizer:
    @staticmethod
    def normalize(text: str, form: str = "NFKC") -> str:
        return unicodedata.normalize(form, text)

    @staticmethod
    def strip_control_characters(text: str) -> str:
        return "".join(c for c in text if unicodedata.category(c)[0] != "C" or c in "\n\r\t")

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        result = ""
        for c in text:
            if c in ("\u00A0", "\u2000", "\u2001", "\u2002", "\u2003",
                     "\u2004", "\u2005", "\u2006", "\u2007", "\u2008",
                     "\u2009", "\u200A", "\u200B", "\u202F", "\u205F", "\u3000"):
                result += " "
            else:
                result += c
        return result

    @staticmethod
    def full_width_to_half_width(text: str) -> str:
        result = []
        for c in text:
            code = ord(c)
            if 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            elif code == 0x3000:
                result.append(" ")
            else:
                result.append(c)
        return "".join(result)

    def normalize_all(self, text: str) -> str:
        text = self.normalize_whitespace(text)
        text = self.full_width_to_half_width(text)
        text = self.normalize(text, "NFKC")
        text = self.strip_control_characters(text)
        return text.strip()
