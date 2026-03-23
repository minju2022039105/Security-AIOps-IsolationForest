import os
import json
import boto3
from datetime import datetime

cloudwatch = boto3.client("cloudwatch")

CW_NAMESPACE = "AIOps/Security"
CW_METRIC = "DefenseSignal"

# ⭐️ 한글(가,나,다) 대신 영어로 매핑하세요!
RULE_MAP = {
    "1": "SQL_Injection",
    "2": "Brute_Force",
    "999": "Anomaly_Traffic"
}

def handler(event, context):
    print(f"📥 Received: {json.dumps(event)}")
    
    # Analyzer가 준 데이터 혹은 기본값
    rule_code = str(event.get("rule_code", "0"))
    attack_ip = event.get("attack_ip", "unknown")
    
    # ⭐️ Dimension 값들을 모두 영어로 변경
    attack_type = RULE_MAP.get(rule_code, "General_Anomaly")

    cloudwatch.put_metric_data(
        Namespace=CW_NAMESPACE,
        MetricData=[{
            "MetricName": CW_METRIC,
            "Dimensions": [
                {"Name": "AttackType", "Value": attack_type}, # 👈 이제 영어라 통과됨!
                {"Name": "AttackIP", "Value": attack_ip}
            ],
            "Timestamp": datetime.utcnow(),
            "Value": 1.0,
            "Unit": "Count"
        }]
    )

    return {
        "status": "prevented",
        "attack_type": attack_type
    }