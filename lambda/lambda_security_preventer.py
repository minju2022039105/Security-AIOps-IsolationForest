import os
import json
import boto3
from datetime import datetime

cloudwatch = boto3.client("cloudwatch")

CW_NAMESPACE = "AIOps/Security"
CW_METRIC = "DefenseSignal"

RULE_MAP = {
    "1": "가",
    "2": "나",
    "999": "라"
}


def handler(event, context):

    rule_code = str(event.get("rule_code", "0"))
    attack_type = RULE_MAP.get(rule_code, "다")

    # CloudWatch Metric 발행 → Grafana에서 표시
    cloudwatch.put_metric_data(
        Namespace=CW_NAMESPACE,
        MetricData=[{
            "MetricName": CW_METRIC,
            "Dimensions": [
                {"Name": "AttackType", "Value": attack_type}
            ],
            "Timestamp": datetime.utcnow(),
            "Value": 1.0,
            "Unit": "Count"
        }]
    )

    # 여기서 실제 차단 로직 추가 가능 (WAF, SG 등)

    return {
        "status": "prevented",
        "attack_type": attack_type
    }
