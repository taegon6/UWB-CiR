# Data directory

이 폴더는 UWB CIR 실험 데이터를 저장하는 공간입니다.

## Recommended layout

```text
data/
├── raw/        # UWB 모듈에서 바로 export한 원본 CSV
├── interim/    # 전처리 중간 산출물
└── processed/  # baseline, feature table, model input 등
```

## CSV format

```csv
timestamp,cir_0,cir_1,cir_2,...,cir_N
2026-01-01T12:00:00.000,0.01,0.02,0.03,...
```

처음 실험은 다음 순서로 진행합니다.

1. 아무 객체도 없는 상태에서 정상 CIR 수집
2. 고양이/사람/물체가 지나가는 상황에서 CIR 수집
3. baseline과 현재 CIR의 차이로 anomaly score 계산
4. score가 threshold를 넘으면 카메라 확인 이벤트 발생
