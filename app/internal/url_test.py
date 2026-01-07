from .url import validate_and_cannonicalize_url, MAX_URL_LENGTH
import pytest


class TestURLValidation:
    def test_empty_url(self):
        with pytest.raises(ValueError):
            validate_and_cannonicalize_url("")

    def test_high_len_url(self):
        url = "http://www.example.com"
        padding_length = MAX_URL_LENGTH - len(url) + 1
        long_url = url + ("a" * padding_length)
        with pytest.raises(ValueError):
            validate_and_cannonicalize_url(long_url)

    def test_missing_hostname(self):
        url = "http://path"
        with pytest.raises(ValueError):
            validate_and_cannonicalize_url(url)

    def test_username_or_password(self):
        url = "http://username:pass@domain.com"
        with pytest.raises(ValueError):
            validate_and_cannonicalize_url(url)

    def test_private_ips(self):
        url = "http://127.0.0.1:8000"
        with pytest.raises(ValueError):
            validate_and_cannonicalize_url(url)

    def test_suspicious_port_443(self):
        url = "http://example.com:443"
        with pytest.raises(ValueError):
            validate_and_cannonicalize_url(url)

    def test_suspicious_port_80(self):
        url = "https://example.com:80"
        with pytest.raises(ValueError):
            validate_and_cannonicalize_url(url)

    def test_all_cap_url(self):
        url = "HTTP://WWW.EXAMPLE.COM"
        validated_url = validate_and_cannonicalize_url(url)
        assert validated_url == "http://www.example.com"

    def test_random_case_url(self):
        url = "HttP://WwW.ExamPlE.com"
        validated_url = validate_and_cannonicalize_url(url)
        assert validated_url == "http://www.example.com"

    def test_query_params(self):
        url = "http://www.example.com?utm_source=src&page=1"
        validated_url = validate_and_cannonicalize_url(url)

        assert validated_url == url
