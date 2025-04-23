OAUTH2_JWT_ENABLED = True

OAUTH2_JWT_ISS = "https://authlib.org"
# OAUTH2_JWT_KEY = "35c49bcb53c6b99bb5247f4f44d0dcc8b22386d17c6fda2770a12812b67efdb2"
OAUTH2_JWT_ALG = "ES256"
# OAUTH2_JWT_KEY = """
# -----BEGIN EC PRIVATE KEY-----
# MHQCAQEEIBJfWc3TeNJ3MCg5lioZViJaRRerVszFwlzO4oII1H6qoAcGBSuBBAAK
# oUQDQgAEwQkH3EaW+9O5+povn9yF/HAvIusy8+PcSfguJGRaHET3foaZGqGn0Qiz
# BRc9lXbHUE2bEfebJRCp57zf9G5zjg==
# -----END EC PRIVATE KEY-----
# """.strip()
OAUTH2_JWT_KEY = {
    "crv": "P-256",
    "d": "p9Bbmkr0mrqE3HuYqR4hdblH85BO3jiaKI3DQo_YjeY",
    "kid": "example",
    "kty": "EC",
    "x": "Kp9RBOl7QILm9KSbgSaCQbj1OSFLFE7Euvk3hnDlTqo",
    "y": "TOH8T09IfxObId_g0IlKOPXU-9jiDPylXV5iKsNSedI",
}
