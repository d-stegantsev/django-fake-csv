import os
from fakecsv.settings.base import *
import dj_database_url

DEBUG = os.environ.get("DEBUG", "0") == "1"

ALLOWED_HOSTS = ["fakecsv-64edd7b944b1.herokuapp.com"]

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
}

STATIC_ROOT = BASE_DIR / "staticfiles"

# Whitenoise
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
