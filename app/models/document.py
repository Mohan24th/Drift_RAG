from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    document_id: str
    name: str
    created_at: datetime


@dataclass
class DocumentVersion:
    version_id: str
    document_id: str
    version_number: int
    file_path: str
    created_at: datetime