IsolationForest
# 🛡️ Security-AIOps-IsolationForest
**CloudWave 7기 4조 프로젝트: 지능형 선제 방어 시스템 (Core Engine Part)**

본 레포지토리는 클라우드웨이브 7기 4조 최종 프로젝트 중, 제가 전담하여 설계 및 구현한 **'AI 기반 이상 징후 탐지 및 자동 대응 엔진'** 파트를 독립적으로 구성한 포트폴리오입니다.

## 👤 Developer
- **김민주 (Min ju Kim)** / 4조 리드 엔지니어
- **Role**: AI 보안 모델링, 서버리스 대응 파이프라인 아키텍처 설계 및 Full-stack 개발

## 🚀 Key Engineering Focus
### 1. Isolation Forest 기반 이상 탐지 모델 (`monitor.py`)
- **Unsupervised Learning**: 보안 데이터의 비대칭성을 고려해 별도의 라벨링 없이도 정밀한 탐지가 가능한 `Isolation Forest` 모델 채택
- **Predictive Scoring**: 트래픽 패턴의 미세한 변화를 감지하여 실제 공격 유입 전 `pred_risk` 지수를 산출하는 선제적 탐지 로직 구현

### 2. AWS Serverless SOAR 파이프라인
- **Event-Driven Mitigation**: AI의 예측 신호(`premit_on`)에 따라 Lambda가 가동되어 WAF IPSet을 실시간 업데이트하는 자동 방어 시스템 구축
- **Threat Classification**: Athena 연동을 통해 유입된 공격을 `Rule 0 (XSS/Scanner)`, `Rule 1 (SQLi/Brute Force)` 등으로 정밀 분류

### 3. Real-time Monitoring Dashboard
- **Metric Exporting**: Prometheus를 통해 AI 모델의 추론 결과와 시스템 상태 지표를 실시간 익스포트
- **Visual Evidence**: 실제 공격 시 `obs_risk`가 억제되는 방어 성공 지표를 시각적으로 입증

---
*본 코드는 클라우드웨이브 7기 4조 프로젝트의 핵심 모듈로, 무단 도용을 금하며 인용 시 출처를 밝혀주시기 바랍니다.*

