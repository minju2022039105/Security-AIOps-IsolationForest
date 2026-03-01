# 🛡️ Security AIOps: Predictive Anomaly Detection & Response
**CloudWave 7기 4조 | 핵심 엔진 및 인프라 설계 전담**

본 저장소는 클라우드웨이브 7기 4조 프로젝트의 핵심인 **AI 이상 탐지 엔진**과 **서버리스 자동 대응(SOAR) 파이프라인**을 독립적으로 구성한 결과물입니다.

단순 모니터링을 넘어, AI의 예측 신호를 클라우드 인프라와 실시간 연동하여 위협을 선제적으로 차단하는 '지능형 보안 시스템' 구축에 집중했습니다.

---

## 👨‍💻 Key Contributions (Minju Kim)
- **AI Modeling**: Isolation Forest 알고리즘 기반 비지도 학습 이상 탐지 로직 설계
- **Cloud Engineering**: Terraform(IaC)을 활용한 AWS 보안 인프라(WAF, Lambda, S3) 자동화 구축
- **Pipeline Integration**: AI 예측 데이터(`pred_risk`)와 서버리스 아키텍처를 결합한 실시간 대응 워크플로우 구현

---

## 🚀 Core Engineering Features

### 1. 지능형 탐지 엔진 (`monitor.py`)
* **Risk Scoring**: `decision_function` 점수를 0~100 위험도로 변환하여 탐지 정밀도를 확보했습니다.
* **Pre-mitigation Logic**: 실제 공격 유입 전 트래픽 징후를 감지하여 `premit_on` 트리거를 발생시키는 선제 방어 로직을 설계했습니다.

### 2. AWS Serverless 기반 자동 대응 (SOAR)
* **Analytical Automation**: `SecurityAnalyzer` Lambda가 Athena를 통해 실시간 로그를 쿼리하고 위협 유형을 분석합니다.
* **Real-time Mitigation**: 분석 결과에 따라 `SecurityPreventer`가 WAF 규칙을 업데이트하고 방어 상태를 Grafana에 즉시 반영합니다.

---

## 🏗 Architecture Workflow
1. **Detection**: `monitor.py` (AI Model) -> S3 (JSON Data 적재)
2. **Analysis**: Amazon Athena -> SecurityAnalyzer (Lambda 분석)
3. **Response**: SecurityPreventer (Lambda) -> AWS WAF 차단 및 Grafana 시각화

---

## 📂 Repository Components
* `monitor.py`: 핵심 AI 탐지 및 데이터 익스포트 로직
* `final_preprocessed_waf_data.csv`: 모델 학습 및 시뮬레이션용 데이터셋
* `cw-infra/`: Terraform 기반 인프라 설계 코드 (인프라 지분 증빙)

---

## 📺 Technical Demo
AI 모델의 위험도 예측부터 Lambda의 자동 대응까지의 전 과정 시연 영상입니다.

## 🎥 Full Simulation Video

AI 모델의 위험도 예측부터 Lambda의 자동 대응까지의 전 과정 시연 영상입니다.

AI-based risk prediction → Lambda automated response pipeline demonstration.

[Watch the Demo](https://www.youtube.com/watch?v=VNAqdCOsqVg)

---
*© 2026 Minju Kim. 본 프로젝트의 아키텍처 설계와 핵심 로직 구현은 본인에게 소유권이 있습니다.*

