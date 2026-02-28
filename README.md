
⸻

🛡️ Security-AIOps-IsolationForest

CloudWave 7기 4조 프로젝트: AI 기반 선제 대응 보안 엔진

본 레포지토리는 클라우드웨이브 7기 4조 최종 프로젝트 중,
제가 전담 설계 및 구현한 AI 기반 이상 탐지 및 서버리스 자동 대응 파이프라인을 독립 구성한 포트폴리오입니다.

⸻

👤 Developer
	•	김민주 (Minju Kim) / 4조 리드 엔지니어
	•	Role
	•	Isolation Forest 기반 보안 모델 설계
	•	AWS Serverless SOAR 파이프라인 아키텍처 설계
	•	Lambda 분석/대응 로직 구현
	•	실시간 보안 시각화 구성

⸻

🚀 Core Architecture

1️⃣ AI Detection Engine (monitor.py)
	•	Unsupervised Learning
	•	라벨링 없이 비정상 트래픽 탐지를 위한 Isolation Forest 적용
	•	Predictive Risk Scoring
	•	score → risk_percent 변환 로직 구현
	•	공격 발생 전 pred_risk 기반 선제 경보 설계
	•	S3 Log Export
	•	분석 결과를 JSON 형태로 S3에 업로드
	•	Athena 분석을 위한 파티션 구조 자동 생성

⸻

2️⃣ Serverless Analysis & Mitigation Pipeline

🧠 SecurityAnalyzer (Lambda)
	•	EventBridge 5분 주기 실행
	•	Athena를 통해 최근 로그 집계
	•	Top rule_code 기반 공격 유형 판정
	•	SecurityPreventer Lambda 호출

🛡 SecurityPreventer (Lambda)
	•	공격 유형 매핑 (가/나/다/라)
	•	CloudWatch Metric 발행
	•	Grafana에서 실시간 알람 표시

⸻

3️⃣ Real-time Security Visualization
	•	CloudWatch Metric 기반 실시간 시각화
	•	Grafana 대시보드에서 공격 유형별 대응 상태 표시
	•	“나 유형 공격 방어 중”과 같은 이벤트 기반 알람 구현

⸻

🏗 System Flow

monitor.py
   ↓
S3 (AI 결과 저장)
   ↓
Athena (로그 집계 분석)
   ↓
SecurityAnalyzer Lambda
   ↓
SecurityPreventer Lambda
   ↓
CloudWatch Metric
   ↓
Grafana Dashboard


⸻

📺 Technical Demonstration

AI 모델이 공격을 예측하고,
Lambda가 자동 대응하며,
Grafana에 방어 상태가 실시간 반영되는 전체 시연 영상:

▶️ 시연 영상 보기￼

⸻

🎯 Engineering Impact
	•	✔ Unsupervised AI 기반 보안 이상 탐지 구현
	•	✔ Event-driven Serverless SOAR 파이프라인 설계
	•	✔ 모델 → 분석 → 대응 → 시각화까지 End-to-End 자동화
	•	✔ 실제 공격 시나리오 기반 선제 방어 입증

⸻

🔥 왜 이 버전이 더 좋냐

✔ 현재 코드 구조와 100% 일치
✔ Prometheus 언급 제거 → 구조 혼선 제거
✔ Serverless 아키텍처 강조 → 클라우드 역량 어필
✔ 면접에서 구조 설명이 명확

⸻

[▶️ 시연 영상 보기 (Security_AIOps_Demo_MinjuKim.mp4)](https://github.com/minju2022039105/Security-AIOps-IsolationForest/blob/main/Security_AIOps_Demo_MinjuKim.mp4)

---
*본 코드는 클라우드웨이브 7기 4조 프로젝트의 핵심 모듈로, 무단 도용을 금하며 인용 시 출처를 밝혀주시기 바랍니다.*

