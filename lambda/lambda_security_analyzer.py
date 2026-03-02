import os
import json
import boto3
import time

athena = boto3.client("athena")
lambda_client = boto3.client("lambda")

ATHENA_DB = os.getenv("ATHENA_DB", "monitoring_db")
ATHENA_TABLE = os.getenv("ATHENA_TABLE", "aiops_results")
ATHENA_OUTPUT = os.getenv("ATHENA_OUTPUT")  # s3://bucket/path/
WORKGROUP = os.getenv("WORKGROUP", "primary")

PREVENTER_FN = os.getenv("PREVENTER_FN")  # SecurityPreventer 이름

LOOKBACK_MIN = 5


def run_query(query):
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": ATHENA_DB},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
        WorkGroup=WORKGROUP,
    )

    qid = response["QueryExecutionId"]

    while True:
        status = athena.get_query_execution(QueryExecutionId=qid)
        state = status["QueryExecution"]["Status"]["State"]
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)

    if state != "SUCCEEDED":
        raise RuntimeError(f"Athena query failed: {state}")

    results = athena.get_query_results(QueryExecutionId=qid)
    return results


def handler(event, context):

    query = f"""
    SELECT rule_code, COUNT(*) AS cnt
    FROM {ATHENA_TABLE}
    WHERE date_parse(event_time, '%Y-%m-%d %H:%i:%s') 
          >= current_timestamp - INTERVAL '{LOOKBACK_MIN}' MINUTE
    GROUP BY rule_code
    ORDER BY cnt DESC
    LIMIT 1
    """

    results = run_query(query)

    rows = results["ResultSet"]["Rows"]
    if len(rows) < 2:
        return {"status": "no_data"}

    rule_code = rows[1]["Data"][0]["VarCharValue"]

    payload = {
        "rule_code": rule_code
    }

    lambda_client.invoke(
        FunctionName=PREVENTER_FN,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8")
    )

    return {"status": "analyzed", "rule_code": rule_code}
