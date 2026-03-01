# Security-AIOps-IsolationForest

AI 기반 이상 탐지 모델(**Isolation Forest**)과 **AWS Serverless** 아키텍처를 결합하여, 실시간 보안 위협 탐지부터 자동 대응까지 수행하는 통합 보안 엔진입니다.

---

## Developer
**김민주** (CloudWave 7기 4조)

---

## Architecture Flow
데이터 수집~ 시각화 파이프라인:

1. **Inference**: `monitor.py` (Isolation Forest 기반 실시간 탐지)
2. **Storage**: **Amazon S3** (분석 결과 적재)
3. **Analysis**: **Amazon Athena** (로그 구조화 및 쿼리 분석)
4. **Action**: **AWS Lambda** (SecurityAnalyzer → SecurityPreventer 자동 대응)
5. **Dashboard**: **Amazon CloudWatch** & **Grafana** (실시간 관제)

---

## Key Features
- **Unsupervised Learning**: Isolation Forest를 통한 미확인 위협(Zero-day) 탐지
- **Predictive Response**: 예측 위험도(`pred_risk`) 기반의 선제적 IP 차단 설계
- **Scalable Pipeline**: Athena + Lambda 연동을 통한 서버리스 자동 분석 체계
- **Visual Analytics**: Grafana를 통한 실시간 탐지 및 대응 현황 시각화

---

## Core Files
- `monitor.py`: AI 탐지 엔진 및 데이터 전송 스크립트
- `lambda_security_analyzer.py`: 위험 수치 분석 및 판단 로직
- `lambda_security_preventer.py`: 실제 방어 및 대응 수행

## Data & Resources
- 'final_preprocessed_waf_data.csv': 'monitor.py'를 위해 정제된 학습용 데이터셋
- 'enriched_waf_data.json': `lambda_security_analyzer.py` 과정에서 식별된 공격 패턴 및 부가 정보가 결합된 최종 가공 데이터
---

## 🎬 Demo Video

https://youtu.be/VNAqdCOsqVg?si=ni_6LffDZZVUGLG8

---
*© 2026 Minju Kim. 본 프로젝트의 아키텍처 설계와 핵심 로직 구현은 본인에게 소유권이 있습니다.*

