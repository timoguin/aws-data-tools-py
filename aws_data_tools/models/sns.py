from dataclasses import dataclass

from .base import ModelBase
from ..utils.validators import is_valid_json


@dataclass
class SnsMessage(ModelBase):
    """Schema for an SNS message"""

    message: str
    message_id: str
    signature: str
    signature_version: str
    signing_cert_url: str
    subject: str
    timestamp: str
    topic_arn: str
    type: str
    unsubscribe_url: str

    # TODO: Unsure if there are additional attributes if the message comes from an SNS
    # FIFO topic

    @property
    def is_body_json(self) -> bool:
        """Check if the message body is a JSON string"""
        return is_valid_json(self.body)
