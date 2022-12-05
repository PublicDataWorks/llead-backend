from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from tqdm import tqdm

from data.constants import MAP_IMAGES_SUB_DIR
from departments.models import Department
from utils.google_cloud import GoogleCloudService
from utils.image_generator import generate_map_thumbnail


class Command(BaseCommand):
    def handle(self, *args, **options):
        gs = GoogleCloudService()
        deps = Department.objects.filter(location_map_url__isnull=True)
        for dep in tqdm(deps):
            location = dep.location
            if location:
                try:
                    image = generate_map_thumbnail(location[0], location[1])
                    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                    upload_location = (
                        f"{MAP_IMAGES_SUB_DIR}/{current_time}-{dep.slug}.png"
                    )
                    gs.upload_file_from_string(upload_location, image, "image/png")
                    dep.location_map_url = f"{settings.GC_PATH}{upload_location}"
                except ValueError as ex:
                    print(
                        f"Error when update department map, at department {dep.id},"
                        f" {dep.slug}: {str(ex)}"
                    )

        Department.objects.bulk_update(deps, ["location_map_url"])
