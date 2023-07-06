import uuid
from typing import Any

from pynamodb.attributes import Attribute
from pynamodb.constants import STRING


class UUIDAttribute(Attribute[uuid.UUID]):
    """
    PynamoDB attribute to for UUIDs. These are backed by DynamoDB unicode (`S`) types.
    """

    attr_type = STRING

    def __init__(self, remove_dashes: bool = False, **kwargs: Any) -> None:
        """
        Initializes a UUIDAttribute object.
        :param remove_dashes: if set, the string serialization will be without dashes.
        Defaults to False.
        """
        super().__init__(**kwargs)
        self._remove_dashes = remove_dashes

    def serialize(self, value: uuid.UUID) -> str:
        result = str(value)

        if self._remove_dashes:
            result = result.replace("-", "")

        return result

    def deserialize(self, value: str) -> uuid.UUID:
        return uuid.UUID(value)
