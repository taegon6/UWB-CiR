# Project plan

## Title

UWB CIR 기반 이상치 감지를 이용한 이벤트 트리거 카메라 객체 확인 시스템

## Motivation

카메라를 항상 켜두면 전력 소모와 프라이버시 문제가 생길 수 있습니다. UWB CIR은 실내 공간의 반사, 차단, multipath 변화를 포함하므로, 평상시와 다른 공간 변화가 발생했는지 저전력으로 먼저 감지하는 센서로 사용할 수 있습니다.

## Hypothesis

고정된 UWB 송수신 링크에서 고양이, 사람, 물체가 링크 근처를 지나가면 CIR의 에너지, 피크, 지연 spread, baseline similarity가 변한다. 이 변화를 anomaly score로 계산하면 카메라 활성화 시점을 결정할 수 있다.

## System pipeline

```text
UWB CIR acquisition
        ↓
Baseline construction
        ↓
Feature extraction / anomaly score
        ↓
Event decision
        ↓
Camera verification
```

## Step 1: Baseline method

- 정상 상태 CIR 여러 개를 수집한다.
- 평균 CIR을 baseline으로 저장한다.
- 현재 CIR과 baseline의 L2 distance, cosine distance, energy change를 계산한다.
- threshold를 넘으면 anomaly로 판단한다.

## Step 2: ML method

- 정상 CIR만 사용해 One-Class SVM 또는 Isolation Forest를 학습한다.
- 정상/이상 CIR label을 만들 수 있으면 1D CNN classifier를 학습한다.
- 데이터가 충분하면 autoencoder 기반 reconstruction error를 사용한다.

## Step 3: Camera verification

- UWB anomaly가 발생했을 때만 카메라 이벤트를 만든다.
- 초기에는 단순 캡처 또는 로그 출력으로 구현한다.
- 이후 YOLO 계열 object detector로 고양이, 사람, 기타 물체를 확인한다.

## Evaluation metrics

- anomaly detection accuracy
- false positive rate
- false negative rate
- camera activation reduction ratio
- trigger latency

## Notes

처음부터 복잡한 SNN이나 CNN으로 시작하지 않는다. baseline difference와 threshold로 동작하는 최소 시스템을 먼저 만들고, 이후 AI 모델로 확장한다.
