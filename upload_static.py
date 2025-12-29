# core/management/commands/upload_static.py
import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path

class Command(BaseCommand):
    help = 'Upload all static files to Cloudinary'

    def handle(self, *args, **kwargs):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        STATIC_DIR = BASE_DIR / 'core/static'  # adjust to your core app
        for root, dirs, files in os.walk(STATIC_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, STATIC_DIR)
                with open(file_path, 'rb') as f:
                    default_storage.save(relative_path, ContentFile(f.read()))
                self.stdout.write(self.style.SUCCESS(f'Uploaded {relative_path}'))
