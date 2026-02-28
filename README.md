# 🛡️ Security AIOps: Predictive Anomaly Detection & Response
**CloudWave 7기 4조 | 핵심 엔진 및 인프라 설계 전담**

본 저장소는 클라우드웨이브 7기 4조 프로젝트의 '두뇌' 역할을 하는 **AI 이상 탐지 엔진**과 **자동 대응(SOAR) 파이프라인**을 독립적으로 구성한 결과물입니다. 

단순 모니터링을 넘어, AI의 예측 신호를 클라우드 인프라와 실시간 연동하여 보안 위협을 선제적으로 차단하는 시스템을 구축하는 데 집중했습니다.

---

## 👨‍💻 Key Contributions (Minju Kim)
- **AI Modeling**: Isolation Forest 알고리즘을 활용한 비지도 학습 기반 이상 징후 탐지 로직 설계
- **Cloud Engineering**: Terraform(IaC)을 활용한 AWS 보안 인프라(WAF, Lambda, S3) 자동화 구축
- **Pipeline Integration**: AI 예측 데이터(`pred_risk`)와 서버리스 아키텍처를 결합한 실시간 대응 워크플로우 구현

---

## 🚀 Core Engineering Features

### 1. 지능형 탐지 엔진 (`monitor.py`)
* **Risk Scoring**: 단순 임계치 방식이 아닌 `decision_function` 기반의 위험도 점수화(0~100)를 통해 탐지 정밀도를 높였습니다.
* **Pre-mitigation Logic**: 실제 공격 유입 전, 트래픽의 미세한 징후를 감지하여 `premit_on` 트리거를 발생시키는 선제 방어 로직을 설계했습니다.

### 2. AWS Serverless 기반의 자동 대응(SOAR)
* **Analytical Automation**: `SecurityAnalyzer` Lambda가 Athena를 통해 실시간 로그를 쿼리하고 위협 유형을 정밀 분석합니다.
* **Real-time Mitigation**: 분석 결과에 따라 `SecurityPreventer`가 가동되어 WAF 규칙을 업데이트하고 방어 상태를 Grafana에 즉시 반영합니다.

---

## 🏗 Architecture Workflow
1. **Detection**: `monitor.py` (AI Model) -> S3 (JSON Data)
2. **Analysis**: Athena -> SecurityAnalyzer (Lambda)
3. **Response**: SecurityPreventer (Lambda) -> CloudWatch/Grafana

---

## 📂 Repository Components
* `monitor.py`: 핵심 AI 탐지 및 데이터 익스포트 로직
* `final_preprocessed_waf_data.csv`: 모델 학습 및 시뮬레이션용 데이터셋
* `cw-infra/`: Terraform 기반 인프라 설계 코드 (별도 관리)

---

## 📺 Technical Demo
AI 모델의 위험도 예측부터 Lambda의 자동 대응까지의 전 과정 시연 영상입니다.

👉 [**Full Simulation Video 보러가기**](https://github.com/minju2022039105/Security-AIOps-IsolationForest/blob/main/Security_AIOps_Demo_MinjuKim.mp4.mp4) 
*(※ 9MB 이상의 파일로 모바일 환경에 따라 재생이 원활하지 않을 수 있습니다.)*

---
*© 2026 Minju Kim. 본 프로젝트의 아키텍처 설계와 핵심 로직 구현은 본인에게 소유권이 있습니다.*
