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

    arn: str
    availability_zone: str = field(default=None)
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

    # TODO: Some examples say "account_id" and others say "aws_account_id"
    account_id: str = field(default=None)
    aws_account_id: str = field(default=None)

    # TODO: Some examples don't show this field
    configuration_state_md5_hash: str = field(default=None)

    # TODO: Some examples don't show this field. Unsure of the type.
    supplementary_configuration: dict[str, Any] = field(default_factory=dict)


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
    # "message_version" should be "record_version" like the others. For now, we're
    # including the alternate names and marking them all as optional.
    message_version: str = field(default=None)
    record_version: str = field(default=None)
    notification_create_time: str = field(default=None)
    notification_creation_time: str = field(default=None)

    # TODO: Some examples in the docs say "ConfigurationItem" and others say
    # "ConfigurationItems". For now we'll add both options and mark them as optional.
    configuration_items: list[dict[str, Any]] = field(default_factory=list)
    configuration_item: dict[str, Any] = field(default_factory=dict)
    configuration_item_diff: dict[str, ConfigurationItemDiff]


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
    annotation: Any = field(default=None)
    result_token: str = field(default=None)


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
    availability_zone: str = field(default=None)
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
    resource_name: str = field(default=None)
    resource_type: str


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
