import ipaddress
from urllib.parse import urlsplit, urlunsplit


MAX_URL_LENGTH = 2048


def validate_and_cannonicalize_url(url: str) -> str:
    if not url or len(url) > MAX_URL_LENGTH:
        raise ValueError("Invalid url length")

    if "://" not in url:
        url = "https://" + url

    parsed_url = urlsplit(url)

    scheme = parsed_url.scheme.lower()
    if not scheme:
        scheme = "https"
    elif scheme not in ("http", "https"):
        raise ValueError("Unsupported scheme")

    if not parsed_url.hostname:
        raise ValueError("Missing hostname")

    hostname = parsed_url.hostname

    if "." not in hostname and hostname != "localhost":
        raise ValueError("Invalid hostname")

    if parsed_url.username or parsed_url.password:
        raise ValueError("Credentials in url are not allowed")

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None

    if ip and (ip.is_private or ip.is_loopback):
        raise ValueError("Private IPs are not allowed")

    port = parsed_url.port

    if port:
        if scheme == "http" and port == 443:
            raise ValueError("Invalid port for http")
        if scheme == "https" and port == 80:
            raise ValueError("Invalid port for http")

    netloc = hostname
    if port and not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    ):
        netloc += f":{port}"

    return urlunsplit(
        (
            scheme,
            netloc,
            parsed_url.path or "",
            parsed_url.query or "",
            parsed_url.fragment or "",
        )
    )
