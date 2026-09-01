from abc import ABC, abstractmethod


class DocumentStorage(ABC):

    @abstractmethod
    def save(
        self,
        source_path: str,
        document_id: str,
        version_number: int,
        filename: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_local_path(
        self,
        storage_path: str,
    ) -> str:
        raise NotImplementedError