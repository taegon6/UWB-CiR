# UWB-CiR

UWB CIR(Channel Impulse Response)를 이용해 실내 공간의 이상 변화를 감지하고, 이상 상황에서만 카메라를 활성화하는 프로젝트입니다.

## Project idea

```text
UWB CIR baseline measurement
        ↓
Current CIR measurement
        ↓
Anomaly score calculation
        ↓
Camera trigger
        ↓
Vision-based verification
```

핵심 목표는 카메라를 항상 켜두지 않고, UWB 신호 변화가 발생했을 때만 카메라를 켜서 고양이, 사람, 기타 물체를 확인하는 저전력·프라이버시 친화형 감시 구조를 만드는 것입니다.

## Initial scope

1. 정상 상태의 UWB CIR baseline 수집
2. 현재 CIR과 baseline CIR 비교
3. CIR feature 기반 anomaly score 계산
4. threshold 초과 시 camera trigger 이벤트 발생
5. 이후 vision 모델 또는 카메라 캡처로 객체 확인

## Repository structure

```text
UWB-CiR/
├── data/
│   └── README.md
├── docs/
│   └── project_plan.md
├── scripts/
│   ├── collect_baseline.py
│   ├── plot_cir.py
│   └── run_anomaly_trigger.py
├── src/uwb_cir/
│   ├── __init__.py
│   ├── anomaly.py
│   ├── camera_trigger.py
│   ├── cir_io.py
│   └── features.py
├── tests/
│   └── test_features.py
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=src pytest -q
python scripts/run_anomaly_trigger.py --demo
```

## CIR CSV format

현재 스크립트는 한 행에 하나의 CIR snapshot이 들어간다고 가정합니다.

```csv
timestamp,cir_0,cir_1,cir_2,...,cir_N
2026-01-01T12:00:00.000,0.01,0.02,0.03,...
```

UWB 모듈에서 complex CIR을 제공하면 magnitude로 변환해서 사용합니다.

```text
magnitude = sqrt(real^2 + imag^2)
```

## Baseline anomaly methods

초기 구현 목표:

- L2 difference from baseline
- cosine similarity / correlation-style score
- total energy change
- simple threshold trigger

추후 확장:

- One-Class SVM
- Isolation Forest
- Autoencoder-based anomaly detection
- 1D CNN-based CIR classifier

## Hardware notes

DW1000/DWM1000, DWM3000 계열 UWB 장치에서 CIR array를 CSV로 export할 수 있으면 연결할 수 있도록 설계합니다.
