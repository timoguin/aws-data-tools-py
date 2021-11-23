"""
Classes and utilities for working with notification from AWS Config. This is a work
in progress.

See the documentation for the structure of various notifications:
https://docs.aws.amazon.com/config/latest/developerguide/notifications-for-AWS-Config.html  # noqa
"""

from dataclasses import dataclass, field
import logging
from typing import Any, Optional, Union

from .base import ModelBase

logging.getLogger(__name__).addHandler(logging.NullHandler())


@dataclass
class SnapshotDeliveryStartedNotification(ModelBase):
    """Notification sent when a config snapshot delivery is started"""

    message_type: str  # Should be "ConfigurationSnapshotDeliveryStarted"
    notification_creation_time: str
    record_version: str

    config_snapshot_id: Optional[str]


@dataclass
class SnapshotDeliveryCompletedNotification(ModelBase):
    """Notification sent when a config snapshot delivery is completed"""

    message_type: str  # Should be "ConfigurationSnapshotDeliveryCompleted"
    notification_creation_time: str
    record_version: str
    s3_bucket: str
    s3_object_key: str

    config_snapshot_id: Optional[str]


@dataclass
class HistoryDeliveryStartedNotification(ModelBase):
    """Notification sent when config history delivery is started"""

    message_type: str  # Should be "ConfigurationHistoryDeliveryStarted"
    notification_creation_time: str
    record_version: str

    config_snapshot_id: Optional[str]


@dataclass
class HistoryDeliveryCompletedNotification(ModelBase):
    """Notification sent when config history delivery is completed"""

    message_type: str  # Should be "ConfigurationHistoryDeliveryCompleted"
    notification_creation_time: str
    record_version: str
    s3_bucket: str
    s3_object_key: str

    config_snapshot_id: Optional[str]


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

    arn: str
    availability_zone: str
    aws_account_id: str
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
    tags: dict[str, str]

    # TODO: Some examples don't show this field
    configuration_state_md5_hash: str = field(default=None)

    # TODO: Some examples don't show this field. Unsure if type is consistent.
    # Real-life item change events have a dict of dicts.
    supplementary_configuration: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigurationItemDiffChangedProperty(ModelBase):
    """Represents a changed property of a configuration item"""

    change_type: str
    previous_value: Optional[Union[int, str, dict[str, Any]]] = field(default=None)
    updated_value: Optional[Union[int, str, dict[str, Any]]] = field(default=None)


@dataclass
class ConfigurationItemDiff(ModelBase):
    """Configuration state and relationships for a resource"""

    change_type: str
    changed_properties: dict[str, ConfigurationItemDiffChangedProperty]


@dataclass
class ItemChangeNotification(ModelBase):
    """Notification sent when configuration has changed for a resource"""

    configuration_item: dict[str, Any]
    message_type: str  # Should be "ConfigurationItemChangeNotification"

    configuration_item_diff: Optional[ConfigurationItemDiff]
    notification_creation_time: Optional[str]
    record_version: Optional[str]

    # # TODO: Some examples in the docs say "ConfigurationItem" and others say
    # # "ConfigurationItems". For now we'll add both options and mark them as optional.
    # configuration_items: list[dict[str, Any]] = field(default_factory=list)
    # configuration_item: dict[str, Any] = field(default_factory=dict)
    #
    # Real-life item change events show "configuration_item"


@dataclass
class ComplianceEvaluationResultQualifier(ModelBase):
    """Unique qualifiers for an evaluated resource and the name of the rule"""

    config_rule_name: str
    resource_type: str
    resource_id: str


@dataclass
class ComplianceEvaluationResultIdentifier(ModelBase):
    """
    Details about a compliance rule evaluatation against a resource, including an
    ordering timestamp
    """

    evaluation_result_qualifier: ComplianceEvaluationResultQualifier
    ordering_timestamp: str


@dataclass
class ComplianceEvaluationResult(ModelBase):
    """The result of a rule compliance evaluation"""

    evaluation_result_identifier: ComplianceEvaluationResultIdentifier
    compliance_type: str
    result_recorded_time: str
    config_rule_invoked_time: str

    # Don't know the expected type of either of these. The examples only show "null"
    # for the values. Going to mark annotation as Any type and result_token as string.
    # TODO: Verify the types when not null.
    annotation: Optional[Any] = field(default=None)
    result_token: Optional[str] = field(default=None)


@dataclass
class ComplianceChangeNotification(ModelBase):
    """Notification sent when the compliance status for a resource has changed"""

    aws_account_id: str
    config_rule_name: str
    config_rule_arn: str
    resource_type: str
    resource_id: str
    aws_region: str
    new_evaluation_result: ComplianceEvaluationResult
    old_evaluation_result: ComplianceEvaluationResult
    notification_creation_time: str
    message_type: str  # ComplianceChangeNotification
    record_version: str

    # m.new_evaluation_result.compliance_type will equal COMPLIANT or NON_CONPLIANT


# TODO: It seems there is a "ScheduledEvaluation" event that is created when Config
# triggers a scheduled rule evaluation (periodic). It is sent to the Lambda during
# invocation.
#
# https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_example-events.html#periodic-example-event


@dataclass
class ConfigRulesEvaluationStartedNotification(ModelBase):
    """Notification sent when a rule evaluation has started"""

    # TODO: Are there evaluation finished notifications?

    aws_account_id: str
    aws_region: str
    config_rule_names: list[str]
    notification_creation_time: str
    message_type: str  # ConfigRulesEvaluationStarted
    record_version: str


@dataclass
class OversizedConfigurationItemSummary(ModelBase):
    """
    The subset of configuration details provided by an oversized change notification
    for a resource
    """

    arn: str
    aws_account_id: str
    aws_region: str
    change_type: str
    configuration_item_capture_time: str
    configuration_item_status: str
    configuration_item_version: str
    configuration_state_id: int
    configuration_state_md5_hash: str
    resource_creation_time: str
    resource_id: str
    resource_type: str

    availability_zone: str = field(default=None)
    resource_name: str = field(default=None)


@dataclass
class OversizedConfigurationItemChangeS3DeliverySummary(ModelBase):
    """Details about where an oversized configuration change were delivered in S3"""

    # The bucket location is null if there was a delivery error
    s3_bucket_location: str = field(default=None)
    error_code: str = field(default=None)
    error_message: str = field(default=None)


@dataclass
class OversizedConfigurationItemChangeNotification(ModelBase):
    """Notification sent when the a configuration change is too large for SNS"""

    change_summary: OversizedConfigurationItemSummary
    s3_delivery_summary: OversizedConfigurationItemChangeS3DeliverySummary


@dataclass
class DeliveryFailedNotification(ModelBase):
    """
    Notification sent when a config snapshot or oversized config item change can't be
    delivered to S3

    https://docs.aws.amazon.com/config/latest/developerguide/notification-delivery-failed.html  # noqa
    """

    # TODO: There is only one documented example that shows a failed delivery for an
    # oversized configuration item change. It is the same as the oversized changed
    # notfication, except the S3 delivery summary has the error code and message fields
    # populated, with a null value for the S3 bucket location.
    #
    # I'm unsure what the notification would look like for a snapshot delivery failure.
    pass


# Maps the value for the "messageType" field to the corresponding model
MESSAGE_TYPE_MAP = {
    "ConfigurationSnapshotDeliveryStarted": SnapshotDeliveryStartedNotification,
    "ConfigurationSnapshotDeliveryCompleted": SnapshotDeliveryCompletedNotification,
    "ConfigurationHistoryDeliveryStarted": HistoryDeliveryStartedNotification,
    "ConfigurationHistoryDeliveryCompleted": HistoryDeliveryCompletedNotification,
    "ConfigurationItemChangeNotification": ItemChangeNotification,
    "ComplianceChangeNotification": ComplianceChangeNotification,
    "ConfigRulesEvaluationStarted": ConfigRulesEvaluationStartedNotification,
    "OversizedConfigurationItemChangeNotification": OversizedConfigurationItemChangeNotification,  # noqa
    "DeliveryFailedNotification": DeliveryFailedNotification,
}


def get_model(message_type: str) -> Any:
    """
    Takes a message type string and returns the model class based on the above
    mapping
    """
    model = MESSAGE_TYPE_MAP.get(message_type)
    if model is None:
        raise Exception(f"Model not found for message type {message_type}")
    return model
