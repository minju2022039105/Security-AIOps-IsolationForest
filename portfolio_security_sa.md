# AWS 3-Layer Security AIOps Platform

> 상세 내용 및 전체 코드: [GitHub README](https://github.com/minju2022039105/Security-AIOps-IsolationForest) · [Velog 시리즈](https://velog.io/@yapp/series/AIOps-%EB%B3%B4%EC%95%88-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8)

> 이커머스 환경의 실전 보안 위협을 막기 위해 설계한 AWS 네이티브 기반 예측적 보안 자동화 시스템  
> 6인 팀 | 보안 파트 단독 담당 | 클라우드웨이브 7기 부트캠프 (2026.02)

---

## 1. Project Overview

| 역할 | 구성 |
| :--- | :--- |
| **사전 차단** | CloudFront Origin Cloaking + AWS WAF v2 (Priority 5단계) |
| **이상 탐지** | Isolation Forest 비지도 학습 — 60초 선행 탐지 |
| **자동 대응** | GuardDuty → EventBridge → Lambda SOAR (WAF IPSet 자동 갱신) |
| **운영 관제** | S3 → Athena → Grafana (LGP Stack) |

---

## 2. Design Decisions

### 왜 이 구조를 설계했는가

두 가지 현실적 제약이 보안 아키텍처 설계를 결정했습니다.

- **예산 제약**: 부트캠프 크레딧 $1,200 안에서 EKS를 운영해야 했고, 악성 트래픽이 클러스터 내부까지 유입되면 컴퓨팅 비용이 증가하는 구조였습니다.
- **운영 현실**: 24/7 수동 모니터링 없이도 위협을 탐지하고 차단까지 이어지는 자율 방어 체계가 필요했습니다.

### 핵심 설계 결정

**Why Edge-First?**
WAF가 공격을 차단하면 요청은 EKS까지 도달하지 않습니다. EKS는 Node 수에 비례해 시간당 과금되므로, 악성 트래픽이 오토스케일링을 유발하기 전에 엣지에서 제거하는 것이 비용과 가용성을 동시에 지키는 핵심 전략이었습니다.

**Why CloudFront + WAF 이중 방어?**
CloudFront의 Origin Cloaking으로 EKS 실제 IP를 외부에 노출하지 않고, ALB 직접 접근 경로를 Security Group으로 차단했습니다. CloudFront를 우회해 ALB에 직접 접근하는 경로를 원천 차단하는 이중 구조입니다.

**Why Serverless SOAR?**
운영 부담 없이 이벤트 기반 자동 대응 구조를 구현하기 위해. Lambda 월 100만 호출 무료 티어를 활용해 상시 EC2 운영 없이 탐지부터 차단까지 자동화했습니다.

**Why LGP Stack (not OpenSearch)?**
OpenSearch는 전용 클러스터 운영 비용이 높습니다. Grafana 하나로 CloudWatch 메트릭 + Athena 로그 + ML 스코어를 단일 화면에 통합해 운영 비용을 80% 이상 절감했습니다.

---

## 3. Key Achievements

- WAF + Isolation Forest 2-Layer 방어로 정적 룰 사각지대 보완
- GuardDuty → Lambda 자동 차단 구조로 **탐지~차단 46ms** 달성
- SQLi, Log4j, 해외 IP 차단 검증 완료 — **유효 차단 로그 8건** 확보
- OpenSearch 대비 인프라 운영 비용 **80% 이상 절감** (LGP Stack)
- Security Group + CloudFront + WAF 3중 방어선으로 공격 표면 최소화

---

## 4. Architecture

![전체 아키텍처](assets/architecture.png)

전체 보안 파이프라인은 **차단 → 탐지 → 대응 → 시각화**의 폐루프 구조입니다. 각 계층은 독립적으로 작동하면서 S3 데이터 레이크를 공유 인터페이스로 연결됩니다.

---

## 5. 보안 아키텍처 설계

### 다층 방어 구조

```
[L4] Security Group — ALB 포트 외 전체 폐쇄 (무료)
[L7] CloudFront — Origin Cloaking, DDoS 흡수
[L7] WAF v2 — 5단계 Priority 룰 체인
[AI] Isolation Forest — 정적 룰 사각지대 탐지
[자동화] Lambda SOAR — 탐지 결과 WAF IPSet 자동 반영
```

### WAF 우선순위 설계

| Priority | 규칙 | 설계 근거 |
| :---: | :--- | :--- |
| 0 | Allow-Only-Korea | 해외 트래픽 입구 차단 → 이후 룰 검사 비용 절감 |
| 1 | AWSManagedRulesCommonRuleSet | OWASP Top 10 방어 |
| 2 | AWSManagedRulesSQLiRuleSet | SQL Injection 특화 차단 |
| 3 | AWSManagedRulesKnownBadInputsRuleSet | Log4j, JNDI 등 알려진 악성 입력 차단 |
| 4 | IP Reputation List (동적) | Lambda가 실시간 갱신하는 AI 기반 블랙리스트 |

P0에서 해외 IP를 걸러낸 뒤, 국내 발신 공격은 P1~P3 Managed Rule이 탐지합니다. AI가 식별한 공격 IP는 P4에 자동 반영되어 이후 요청을 즉시 차단합니다.

![WAF Rules](assets/waf-rules.png)

![403 Block](assets/403-block.png)

---

## 6. AI 기반 보안 보완 — Isolation Forest

WAF 정적 룰이 허용한 트래픽 중 변칙 패턴을 비지도 학습으로 추가 탐지합니다. 공격자의 사전 정찰 단계에서 발생하는 미세한 이상 패턴을 감지해 실제 공격 도달 **약 60초 전에 대응 시간을 확보**합니다.

![AIOps Dashboard](assets/aiops-dashboard.png)

![Grafana Table](assets/grafana-table.png)

---

## 7. SOAR 자동 대응

```
GuardDuty (위협 탐지)
    ↓
EventBridge → SNS (Slack·Email·Lambda 동시 전달)
    ↓
Analyzer Lambda → Athena 조회 → 공격 IP·ML 위험도 종합 판단
    ↓
Preventer Lambda → WAF IPSet 업데이트 (탐지~차단 46ms)
```

![Analyzer Query](assets/analyzer-query.png)

---

## 8. 검증 결과

| 시나리오 | 결과 |
| :--- | :---: |
| SQL Injection 페이로드 | **403 Forbidden** |
| Log4j / JNDI Injection | **403 Forbidden** |
| 해외 IP 접근 (네덜란드·미국) | **403 Forbidden** |
| GuardDuty 탐지 → Lambda 자동 차단 | **WAF IPSet 자동 갱신** |

![Grafana Gauge](assets/grafana-gauge.png)

---

## 9. 주요 트러블슈팅

**WAF 차단 미작동 — 근본 원인 3가지 규명**
트래픽 흐름·우회 경로·룰 우선순위 차원에서 분석해 구조적 원인 3가지를 각각 규명·해결. ALB 보안 그룹을 CloudFront Prefix List 전용으로 제한해 WAF 우회 경로 원천 차단.

**WAF IPSet 생성 실패 (ValidationException)**
AWS API 특정 필드에 한글 문자열 포함 시 거부. `Description` 필드 영문 변경으로 해결.

---

## 10. Tech Stack

| 분류 | 기술 |
| :--- | :--- |
| **보안 아키텍처** | AWS WAF v2, CloudFront, GuardDuty, Security Group |
| **SOAR / 자동화** | EventBridge, AWS Lambda (Python), SNS |
| **AI/ML** | Isolation Forest (Scikit-learn) |
| **모니터링** | S3, Athena, Grafana Cloud, CloudWatch |
| **컨테이너** | EKS, ALB |

---

**프로젝트 기간**: 2026.02 (3주)  
**역할**: 보안 파트 단독 담당 (6인 팀)
