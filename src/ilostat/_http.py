from importlib.metadata import version

USER_AGENT = f"PYilostat/{version('ilostat')}"

HTTP_HEADERS = {
    "User-Agent": USER_AGENT,
}