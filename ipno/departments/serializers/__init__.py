from .department_coordinates_serializer import DepartmentCoordinateSerializer
from .department_details_serializer import DepartmentDetailsSerializer
from .department_news_articles_serializer import DepartmentNewsArticleSerializer
from .department_officers_serializer import DepartmentOfficerSerializer
from .department_documents_serializer import DepartmentDocumentSerializer
from .migratory_event_serializer import MigratoryEventSerializer
from .wrgl_serializer import WrglFileSerializer

__all__ = [
    'DepartmentCoordinateSerializer',
    'DepartmentDetailsSerializer',
    'DepartmentDocumentSerializer',
    'DepartmentNewsArticleSerializer',
    'DepartmentOfficerSerializer',
    'MigratoryEventSerializer',
    'WrglFileSerializer',
]
