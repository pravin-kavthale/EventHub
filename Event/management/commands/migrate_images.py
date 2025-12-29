from django.core.management.base import BaseCommand
from django.conf import settings
from Event.models import Event
import cloudinary.uploaderz 
import os

class Command(BaseCommand):
    help = "Migrate local images to Cloudinary"

    def handle(self, *args, **kwargs):
        count = 0

        for event in Event.objects.exclude(image=""):
            local_path = os.path.join(settings.MEDIA_ROOT, event.image.name)

            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(f"Missing: {local_path}"))
                continue

            result = cloudinary.uploader.upload(
                local_path,
                folder="event_images"
            )

            event.image = result["public_id"]
            event.save(update_fields=["image"])
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Migrated {count} images"))
from django.core.management.base import BaseCommand
from django.conf import settings
from Event.models import Event
import cloudinary.uploader
import os

class Command(BaseCommand):
    help = "Migrate local images to Cloudinary"

    def handle(self, *args, **kwargs):
        count = 0

        for event in Event.objects.exclude(image=""):
            local_path = os.path.join(settings.MEDIA_ROOT, event.image.name)

            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(f"Missing: {local_path}"))
                continue

            result = cloudinary.uploader.upload(
                local_path,
                folder="event_images"
            )

            event.image = result["public_id"]
            event.save(update_fields=["image"])
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Migrated {count} images"))
