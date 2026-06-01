from typing import Optional


class SemanticMatcher:
    @staticmethod
    def match(text: str, asset: dict) -> Optional[dict]:
        if not text or not asset:
            return None
        text_lower = text.lower().strip()

        name = asset.get("name", "")
        if name and name.lower() in text_lower:
            return {"mode": "semantic_name", "matched": name, "confidence": 0.6}

        aliases = asset.get("aliases", [])
        for alias in aliases:
            if isinstance(alias, str) and alias.lower() in text_lower:
                return {"mode": "semantic_alias", "matched": alias, "confidence": 0.7}

        description = asset.get("description", "")
        if description:
            keywords = [w.strip().lower() for w in description.replace(",", " ").split() if len(w.strip()) > 2]
            matched_keywords = [k for k in keywords if k in text_lower]
            if matched_keywords and len(matched_keywords) >= len(keywords) * 0.5:
                return {"mode": "semantic_description", "matched": matched_keywords, "confidence": 0.5}

        return None
