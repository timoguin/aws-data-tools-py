from dataclass import dataclass, field
from hashlib import md5

from .base import ModelBase
from ..utils import is_valid_json


@dataclass
class MessageAttributes(ModelBase):
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
class CustomMessageAttributeDefinition(ModelBase):
    """Type definition and value for a custom message attribute"""

    data_type: str
    string_value: str


@dataclass
class Message(ModelBase):
    """Schema for an SQS message"""

    message_id: str
    receipt_handle: str
    body: str
    attributes: MessageAttributes
    message_attributes: dict[str, CustomMessageAttributeDefinition]
    md5_of_body: str
    md5_of_message_attributes: str = field(default=None)
    event_source: str
    event_source_arn: str
    aws_region: str

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
        )  # noqa

    @property
    def is_md5_of_body_valid(self) -> bool:
        return md5(self.body.encode("utf-8")).hexdigest() == self.md5_of_body

    @property
    def is_body_json(self) -> bool:
        """Check if the message body is a JSON string"""
        return is_valid_json(self.body)
