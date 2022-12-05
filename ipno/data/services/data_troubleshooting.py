from django.conf import settings

from tqdm import tqdm
from wrgl import Repository

from appeals.models import Appeal
from complaints.models import Complaint
from data.constants import WRGL_USER
from data.models import WrglRepo
from documents.models import Document
from officers.models import Event, Officer
from people.models import Person
from use_of_forces.models import UseOfForce, UseOfForceCitizen, UseOfForceOfficer


class DataTroubleshooting:
    new_commit = None
    column_mappings = {}
    model_mappings = {
        "Officer": Officer,
        "Event": Event,
        "Complaint": Complaint,
        "UseOfForce": UseOfForce,
        "UseOfForceOfficer": UseOfForceOfficer,
        "UseOfForceCitizen": UseOfForceCitizen,
        "Document": Document,
        "Person": Person,
        "Appeal": Appeal,
    }

    def __init__(self, data_model="Officer", updated_fields=("sex",), table_id="uid"):
        self.data_model = data_model
        self.updated_fields = updated_fields
        self.table_id = table_id
        self.model = self.model_mappings[data_model]

    def retrieve_wrgl_data(self, branch):
        self.repo = Repository(
            f"https://hub.wrgl.co/api/users/{WRGL_USER}/repos/data/",
            settings.WRGL_API_KEY,
        )

        self.new_commit = self.repo.get_branch(branch)

        columns = self.new_commit.table.columns
        self.column_mappings = {column: columns.index(column) for column in columns}

    def process(self):
        wrgl_repo = WrglRepo.objects.filter(data_model=self.data_model).first()

        self.retrieve_wrgl_data(wrgl_repo.repo_name)

        all_rows = list(
            self.repo.get_blocks(
                f"heads/{wrgl_repo.repo_name}", with_column_names=False
            )
        )

        updated_objects = []

        for row in tqdm(all_rows, desc="Update fields"):
            table_id = row[self.column_mappings[self.table_id]]

            kwargs = {self.table_id: table_id}
            updated_object = self.model.objects.get(**kwargs)

            for field in self.updated_fields:
                setattr(updated_object, field, row[self.column_mappings[field]])

            updated_objects.append(updated_object)

        self.model.objects.bulk_update(
            updated_objects, self.updated_fields, batch_size=1000
        )
