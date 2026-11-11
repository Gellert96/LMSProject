from urllib.parse import urlparse

from rest_framework import serializers


def validate_youtube_url(value):
    """Разрешает ссылки только на YouTube."""

    parsed_url = urlparse(value)

    hostname = parsed_url.hostname

    allowed_domains = (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
    )

    if parsed_url.scheme not in ("http", "https"):
        raise serializers.ValidationError(
            "Ссылка должна начинаться с http:// или https://."
        )

    if hostname not in allowed_domains:
        raise serializers.ValidationError("Разрешены ссылки только на youtube.com.")

    return value
