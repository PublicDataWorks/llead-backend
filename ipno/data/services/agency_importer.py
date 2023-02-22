import ast
from datetime import datetime

from django.conf import settings

import structlog
from tqdm import tqdm

from data.constants import AGENCY_MODEL_NAME, MAP_IMAGES_SUB_DIR
from data.services import BaseImporter
from departments.models import Department
from utils.google_cloud import GoogleCloudService
from utils.image_generator import generate_map_thumbnail

logger = structlog.get_logger("IPNO")


class AgencyImporter(BaseImporter):
    data_model = AGENCY_MODEL_NAME

    ATTRIBUTES = list(
        {field.name for field in Department._meta.fields}
        - Department.BASE_FIELDS
        - Department.CUSTOM_FIELDS
    )
    UPDATE_ATTRIBUTES = ATTRIBUTES + ["location_map_url"]

    def __init__(self):
        self.gs = GoogleCloudService()
        self.new_agency_attrs = []
        self.new_agency_slugs = []
        self.update_agency_attrs = []
        self.delete_agency_ids = []
        self.agency_mappings = {
            agency.agency_slug: agency
            for agency in Department.objects.only(
                "id", "agency_slug", "location", "location_map_url"
            )
        }

    def upload_file(self, upload_location, file_blob):
        try:
            self.gs.upload_file_from_string(upload_location, file_blob, "image/png")

            department_image_url = f"{settings.GC_PATH}{upload_location}"

            return department_image_url
        except Exception:
            pass

    def handle_record_data(self, row):
        agency_data = self.parse_row_data(row, self.column_mappings)
        agency_slug = agency_data["agency_slug"]
        agency_name = agency_data["agency_name"]
        location = (
            ast.literal_eval(agency_data["location"])
            if agency_data["location"]
            else None
        )
        location = location[::-1] if location else None

        department = self.agency_mappings.get(agency_slug)

        should_update_location = False
        location_map_url = None

        if location:
            if not department or location != department.location:
                should_update_location = True
            elif department.location_map_url:
                location_map_url = department.location_map_url

        if should_update_location:
            try:
                image = generate_map_thumbnail(location[0], location[1])
                current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                upload_location = (
                    f"{MAP_IMAGES_SUB_DIR}/{current_time}-{agency_slug}.png"
                )
                location_map_url = self.upload_file(upload_location, image)
            except ValueError as ex:
                logger.error(f"Error when import department {agency_slug}: {str(ex)}")

        department_data = {
            "agency_name": agency_name,
            "agency_slug": agency_slug,
            "location": location,
            "location_map_url": location_map_url,
        }

        if department:
            department_data["id"] = department.id
            self.update_agency_attrs.append(department_data)
        elif agency_slug not in self.new_agency_slugs:
            self.new_agency_slugs.append(agency_slug)
            self.new_agency_attrs.append(department_data)

    def import_data(self, data):
        for row in tqdm(data.get("added_rows"), desc="Create departments"):
            self.handle_record_data(row)

        for row in tqdm(data.get("deleted_rows"), desc="Delete departments"):
            agency_slug = row[self.column_mappings["agency_slug"]]
            agency = self.agency_mappings.get(agency_slug)
            if agency:
                self.delete_agency_ids.append(agency.id)

        for row in tqdm(data.get("updated_rows"), desc="Update departments"):
            self.handle_record_data(row)

        return self.bulk_import(
            Department,
            self.new_agency_attrs,
            self.update_agency_attrs,
            self.delete_agency_ids,
        )
