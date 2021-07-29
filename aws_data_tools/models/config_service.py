# Classes and utilities for working with notification from AWS Config. This is a work
# in progress.
#
# See the documentation for the structure of various notifications:
# https://docs.aws.amazon.com/config/latest/developerguide/notifications-for-AWS-Config.html  # noqa

from dataclass import dataclass, field
from typing import Any, Union

from .base import ModelBase


@dataclass
class SnapshotDeliveryStartedNotification(ModelBase):
    """Notification sent when a config snapshot delivery is started"""

    config_snapshot_id: str
    message_type: str  # Should be "ConfigurationSnapshotDeliveryStarted"
    notification_creation_time: str
    record_version: str


@dataclass
class SnapshotDeliveryCompletedNotification(ModelBase):
    """Notification sent when a config snapshot delivery is completed"""

    config_snapshot_id: str
    message_type: str  # Should be "ConfigurationSnapshotDeliveryCompleted"
    notification_creation_time: str
    record_version: str
    s3_bucket: str
    s3_object_key: str


@dataclass
class HistoryDeliveryStartedNotification(ModelBase):
    """Notification sent when config history delivery is started"""

    config_snapshot_id: str
    message_type: str  # Should be "ConfigurationHistoryDeliveryStarted"
    notification_creation_time: str
    record_version: str


@dataclass
class HistoryDeliveryCompletedNotification(ModelBase):
    """Notification sent when config history delivery is completed"""

    config_snapshot_id: str
    message_type: str  # Should be "ConfigurationHistoryDeliveryCompleted"
    notification_creation_time: str
    record_version: str
    s3_bucket: str
    s3_object_key: str


@dataclass
class ConfigurationItemRelationshipItem(ModelBase):
    """Represents a resource that can be related to a configuration item"""

    name: str
    resource_id: str
    resource_type: str
    resource_name: str


@dataclass
class ConfigurationItem(ModelBase):
    """Configuration state and relationships for a resource"""

    account_id: str
    arn: str
    availability_zone: str
    configuration: dict[str, Any]
    configuration_item_capture_time: str
    configuration_item_status: str
    configuration_item_version: str
    configuration_state_id: str
    related_events: list[Any]
    relationships: list[ConfigurationItemRelationshipItem]
    resource_creation_time: str
    resource_id: str
    resource_type: str
    tags: dict[str, Any]

    # TODO: Some examples say "account_id" and others say "aws_account_id"
    aws_account_id: str
    # TODO: Some examples docs show this field
    configuration_state_md5_hash: str
    # TODO: Some examples docs show this field
    supplementary_configuration: dict[str, Any]


@dataclass
class ConfigurationItemDiffChangedProperty(ModelBase):
    """Represents a changed property of a configuration item"""

    change_type: str
    previous_value: Union[str, dict[str, Any]] = field(default=None)
    updated_value: Union[str, dict[str, Any]] = field(default=None)


@dataclass
class ConfigurationItemDiff(ModelBase):
    """Configuration state and relationships for a resource"""

    change_type: str
    changed_properties: dict[str, ConfigurationItemDiffChangedProperty]


@dataclass
class ItemChangeNotification(ModelBase):
    """Notification sent when configuration has changed for a resource"""

    message_type: str  # Should be "ConfigurationItemChangeNotification"

    # TODO: Check if docs are correct about using "notification_create_time" instead of
    # "notification_creation_time" like other notification types. Also check if
    # "message_version" should be "record_version" like the others.
    message_version: str
    notification_create_time: str

    # TODO: Create dataclasses for these attributes
    # TODO: Some examples in the docs say "ConfigurationItem" and others say
    # "ConfigurationItems"
    configuration_items: list[dict[str, Any]]
    configuration_item_diff: dict[str, ConfigurationItemDiff]


@dataclass
class ComplianceChangeNotification(ModelBase):
    """Notification sent when the compliance status for a resource has changed"""

    pass


@dataclass
class ConfigRulesEvaluationStartedNotification(ModelBase):
    """Notification sent when a rule evaluation has started"""

    pass


@dataclass
class OversizedConfigurationItemChangeNotification(ModelBase):
    """Notification sent when the a configuration change is too large for SNS"""

    pass


@dataclass
class DeliveryFailedNotification(ModelBase):
    """
    Notification sent when a config snapshot or oversized config item change can't be
    delivered to S3
    """

    pass
