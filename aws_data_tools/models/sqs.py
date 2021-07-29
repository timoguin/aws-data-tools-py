from dataclasses import dataclass, field
from hashlib import md5
import logging
from typing import Optional

from .base import ModelBase
from ..utils.validators import is_valid_json

logging.getLogger(__name__).addHandler(logging.NullHandler())


@dataclass
class SqsMessageAttributes(ModelBase):
    """Attributes attached to an SQS message"""

    # TODO: Unsure if some of these string will need to be cast to int or other types
    approximate_receive_count: str
    approximate_first_receive_timestamp: str
    sender_id: str
    sent_timestamp: str

    # Optional attributes added when using FIFO queues
    aws_trace_header: str = field(default=None)
    message_deduplication_id: str = field(default=None)
    message_group_id: str = field(default=None)
    sequence_number: str = field(default=None)

    _FIFO_ATTRIBUTES = [
        "message_deduplication_id",
        "message_group_id",
        "sequence_number",
    ]

    @property
    def is_fifo(self) -> bool:
        """Check if there are FIFO-specific attributes"""
        for attr in self._FIFO_ATTRIBUTES:
            if getattr(self, attr) is None:
                return False
        return True


@dataclass
class SqsCustomMessageAttributeDefinition(ModelBase):
    """Type definition and value for a custom message attribute"""

    data_type: str
    string_value: str


@dataclass
class SqsMessage(ModelBase):
    """Schema for an SQS message"""

    body: str
    md5_of_body: str
    message_id: str
    receipt_handle: str

    attributes: Optional[SqsMessageAttributes]
    message_attributes: Optional[dict[str, SqsCustomMessageAttributeDefinition]]
    event_source: Optional[str]
    event_source_arn: Optional[str]
    aws_region: Optional[str]

    # Optional
    md5_of_message_attributes: Optional[str] = field(default=None)

    @property
    def is_fifo(self) -> bool:
        """Check if a message came from a FIFO queue"""
        return self.attributes.is_fifo()

    @property
    def calculated_md5_of_message_attributes(self) -> str:
        """Calculate the MD5 checksum of the message attributes"""
        # TODO: Figure out the algorithm to build a digest of the message attributes.
        # View the following documentation for details:
        # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-metadata.html#sqs-attributes-md5-message-digest-calculation  # noqa
        raise NotImplementedError

    @property
    def is_md5_of_message_attributes_valid(self) -> bool:
        return (
            self.md5_of_message_attributes == self.calculated_md5_of_message_attributes
        )

    @property
    def is_md5_of_body_valid(self) -> bool:
        return md5(self.body.encode("utf-8")).hexdigest() == self.md5_of_body

    @property
    def is_body_json(self) -> bool:
        """Check if the message body is a JSON string"""
        return is_valid_json(self.body)
