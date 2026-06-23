# Experiment targets

## Current intermediate target

우선 중간 목표는 **고양이 크기 객체(cat-sized object)** 감지로 잡는다.

이 프로젝트의 1차 목적은 UWB CIR만으로 객체 종류를 정확히 분류하는 것이 아니라, 평상시와 다른 공간 변화가 생겼는지를 먼저 감지하는 것이다. 이후 카메라 기반 모델이 실제 객체를 확인한다.

## Why cat-sized target first?

동전, 나사, 작은 금속 조각 같은 초소형 FOD는 카메라와 UWB 모두에서 난이도가 높다. 반면 고양이 크기 객체는 다음 이유로 중간 목표에 적합하다.

- 사람보다 작아서 단순 인체 감지보다 도전적이다.
- 동전보다 크기와 움직임이 커서 UWB CIR 변화가 관찰될 가능성이 높다.
- 카메라 기반 객체 확인도 비교적 가능하다.
- 실내 생활 환경의 실제 문제와 연결된다.

## Target stages

### Stage 0: Empty room baseline

- 아무 물체도 링크 주변에 두지 않는다.
- 정상 상태 CIR을 수집한다.
- baseline CIR을 만든다.

### Stage 1: Large object sanity check

- 사람, 가방, 박스 같은 큰 객체를 링크 근처에 둔다.
- CIR 변화가 baseline 대비 충분히 나타나는지 확인한다.

### Stage 2: Cat-sized object

- 실제 고양이 또는 고양이 크기 대체 물체를 사용한다.
- 예: 인형, 작은 박스, 쿠션, 움직이는 장난감
- 목표는 cat-sized object가 들어왔을 때 anomaly score가 상승하는지 확인하는 것이다.

### Stage 3: Moving cat-sized object

- 정적인 물체가 아니라 이동하는 고양이 크기 객체를 사용한다.
- CIR snapshot 하나가 아니라 CIR 시계열 변화도 확인한다.

### Stage 4: Small FOD exploration

- 금속 캔, 열쇠, 동전, 나사 등 작은 물체로 확장한다.
- 이 단계는 추가 실험 목표이며, 중간 목표는 아니다.

## Success criteria for the intermediate target

고양이 크기 객체 기준의 중간 성공 조건은 다음과 같다.

1. empty baseline과 cat-sized object 상황에서 anomaly score 분포가 구분된다.
2. threshold 기반 detector가 cat-sized object 상황에서 반복적으로 event를 발생시킨다.
3. 사람이 지나가는 큰 변화와 고양이 크기 객체의 중간 크기 변화가 구분 가능하다.
4. 카메라 확인 단계에서 cat/person/object 중 하나로 후속 판별이 가능하다.

## Recommended labels

데이터를 모을 때는 다음 label을 사용한다.

```text
normal_empty
large_person
large_box
cat_static
cat_moving
small_metal
unknown_motion
```

## Experiment command examples

Baseline:

```bash
python scripts/collect_dw3000_serial.py --port PORT_NAME --baudrate 115200 --output data/raw/normal_empty.csv --max-samples 300
```

Cat-sized static object:

```bash
python scripts/collect_dw3000_serial.py --port PORT_NAME --baudrate 115200 --output data/raw/cat_static.csv --max-samples 300
```

Cat-sized moving object:

```bash
python scripts/collect_dw3000_serial.py --port PORT_NAME --baudrate 115200 --output data/raw/cat_moving.csv --max-samples 300
```

Initial anomaly check:

```bash
python scripts/run_anomaly_trigger.py --input data/raw/cat_moving.csv --baseline-rows 50 --threshold 0.2 --method l2
```

## Notes for Codex

- Do not optimize for coin-sized FOD first.
- First make the data pipeline stable for cat-sized objects.
- If cat-sized object detection is unstable, improve UWB link placement and baseline collection before adding a complex ML model.
- After enough labeled sequences are collected, add Autoencoder or CNN-LSTM models.
