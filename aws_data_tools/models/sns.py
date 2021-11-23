from dataclasses import dataclass
import logging
from typing import Optional

from .base import ModelBase
from ..utils.validators import is_valid_json

logging.getLogger(__name__).addHandler(logging.NullHandler())


@dataclass
class SnsMessageData(ModelBase):
    """Represents the data from an SNS message that is under the "Sns" field"""

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


@dataclass
class SnsMessage(ModelBase):
    """Schema for an SNS message"""

    message: str
    message_id: str
    subject: str
    timestamp: str
    topic_arn: str
    type: str
    unsubscribe_url: str

    signature: Optional[str]
    signature_version: Optional[str]
    signing_cert_url: Optional[str]

    # TODO: Unsure if there are additional attributes if the message comes from an SNS
    # FIFO topic

    @property
    def is_body_json(self) -> bool:
        """Check if the message body is a JSON string"""
        return is_valid_json(self.message)


@dataclass
class LambdaSnsMessage(ModelBase):
    """Represents the SNS message format when using Lambda subscriptions"""

    event_source: str
    event_version: str
    event_subscription_arn: str
    sns: SnsMessage
