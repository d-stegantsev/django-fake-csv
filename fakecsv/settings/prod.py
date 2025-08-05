from fakecsv.settings.base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ["fakecsv.herokuapp.com"]

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
}

STATIC_ROOT = BASE_DIR / "staticfiles"

# Whitenoise
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
