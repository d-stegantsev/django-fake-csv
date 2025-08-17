from fakecsv.settings.base import *

DEBUG = True

ALLOWED_HOSTS = []

# SQLite for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
