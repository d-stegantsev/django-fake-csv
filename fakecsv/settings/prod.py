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

# Celery
CELERY_BROKER_URL = os.environ.get("REDIS_URL")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL")

# Cloudinary
INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
    "RESOURCE_TYPE": "raw",
}
MEDIA_URL = "https://res.cloudinary.com/%s/" % os.environ.get("CLOUDINARY_CLOUD_NAME")
