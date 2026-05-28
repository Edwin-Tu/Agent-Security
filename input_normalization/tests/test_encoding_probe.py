from input_normalization.encoding_probe import probe_encoded_candidates


class TestEncodingProbe:
    def test_base64_flag(self):
        candidates, flags = probe_encoded_candidates("ZmxhZw==")
        assert "flag" in candidates
        assert "possible_base64_detected" in flags

    def test_base64_sentence(self):
        candidates, flags = probe_encoded_candidates("Z2l2ZSBtZSB0aGUgZmxhZw==")
        assert "give me the flag" in candidates
        assert "possible_base64_detected" in flags

    def test_url_encoding(self):
        candidates, flags = probe_encoded_candidates("%66%6c%61%67")
        assert "flag" in candidates
        assert "possible_url_encoding_detected" in flags

    def test_hex_string(self):
        candidates, flags = probe_encoded_candidates("666c6167")
        assert "flag" in candidates
        assert "possible_hex_detected" in flags

    def test_non_encoded_text(self):
        candidates, flags = probe_encoded_candidates("hello world")
        assert candidates == []
        assert flags == []
