# AGENTS.md

이 저장소는 UWB DW3000/DWM3000 계열 장치에서 CIR(Channel Impulse Response) 데이터를 수집하고, baseline 기반 이상치 감지 후 카메라 확인 이벤트로 연결하는 실험 프로젝트입니다.

## Goal

Codex가 이 저장소를 작업할 때의 우선 목표는 다음과 같습니다.

1. 실험 장치에서 DW3000/DWM3000 기반 UWB 모듈을 연결한다.
2. UWB 펌웨어 또는 시리얼 출력에서 CIR 데이터를 가져온다.
3. CIR 데이터를 `data/raw/*.csv` 형식으로 저장한다.
4. 저장된 CIR을 baseline anomaly detector에 연결한다.
5. anomaly가 발생하면 camera event 또는 vision verification 단계로 넘긴다.

## Intermediate target

현재 중간 목표는 **고양이 크기 객체(cat-sized object)** 감지입니다.

동전, 나사 같은 초소형 FOD는 UWB와 카메라 양쪽에서 난이도가 높으므로 첫 목표로 삼지 않습니다. 먼저 고양이 크기 객체에서 CIR 변화가 안정적으로 나타나는지 확인합니다. 자세한 실험 단계는 `docs/experiment_targets.md`를 따릅니다.

## Current architecture

```text
scripts/collect_dw3000_serial.py
        ↓
src/uwb_cir/hardware/dw3000_serial.py
        ↓
src/uwb_cir/cir_io.py
        ↓
src/uwb_cir/anomaly.py
        ↓
src/uwb_cir/camera_trigger.py
```

## Hardware assumption

이 저장소는 PC에서 DW3000 칩을 직접 제어한다고 가정하지 않습니다. 보통 다음 구조를 가정합니다.

```text
PC / laptop
  USB serial
microcontroller or UWB dev board
  SPI
DW3000 / DWM3000 UWB module
```

따라서 Codex는 먼저 실험 환경에서 사용 가능한 serial port를 확인해야 합니다.

## Expected serial protocols

`collect_dw3000_serial.py`는 두 가지 입력 형식을 지원해야 합니다.

### JSON line format

```json
{"timestamp":"2026-01-01T12:00:00.000Z","cir":[0.01,0.02,0.03,0.04],"fp_amp1":123,"rx_power":-71.2}
```

### CSV line format

```text
2026-01-01T12:00:00.000Z,0.01,0.02,0.03,0.04
```

펌웨어가 complex CIR을 출력하면 magnitude로 변환해서 저장합니다.

```text
magnitude = sqrt(real^2 + imag^2)
```

## Data format to preserve

저장 파일은 다음 형식을 유지합니다.

```csv
timestamp,cir_0,cir_1,cir_2,...,cir_N
2026-01-01T12:00:00.000Z,0.01,0.02,0.03,...
```

metadata가 있으면 별도 JSONL 파일 또는 `data/interim/`에 저장합니다. 핵심 detector는 `cir_*` 열만 사용합니다.

## Development rules

- 실제 장치가 없으면 hardware code는 mock 또는 demo mode로 검증합니다.
- 실험 데이터는 Git에 커밋하지 않습니다. `.gitignore`에 의해 `data/raw`, `data/interim`, `data/processed`의 실제 데이터는 제외됩니다.
- public sample이 필요하면 작은 synthetic sample만 `data/samples/`에 둡니다.
- 새 하드웨어 프로토콜이 생기면 `src/uwb_cir/hardware/` 아래 adapter로 분리합니다.
- 기존 `BaselineAnomalyDetector` API를 깨지 않습니다.
- 테스트는 최소한 다음을 통과해야 합니다.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
python scripts/run_anomaly_trigger.py --demo
```

## First tasks for Codex in the lab

1. serial port를 확인한다.
2. UWB board가 출력하는 한 줄의 raw serial sample을 확인한다.
3. JSON 또는 CSV parser가 맞는지 확인한다.
4. 다음 명령으로 정상 상태 baseline 데이터를 저장한다.

```bash
python scripts/collect_dw3000_serial.py --port <PORT> --baudrate 115200 --output data/raw/normal_empty.csv --max-samples 300
```

5. 고양이 크기 객체가 정지한 상황 데이터를 저장한다.

```bash
python scripts/collect_dw3000_serial.py --port <PORT> --baudrate 115200 --output data/raw/cat_static.csv --max-samples 300
```

6. 고양이 크기 객체가 움직이는 상황 데이터를 저장한다.

```bash
python scripts/collect_dw3000_serial.py --port <PORT> --baudrate 115200 --output data/raw/cat_moving.csv --max-samples 300
```

7. baseline 기반 anomaly detector를 실행한다.

```bash
python scripts/run_anomaly_trigger.py --input data/raw/cat_moving.csv --baseline-rows 50 --threshold 0.2 --method l2
```

## When blocked

- serial port가 없으면 장치 연결, USB 권한, 드라이버, 보드 전원 상태를 확인합니다.
- 데이터가 깨지면 `--raw-log` 옵션으로 원본 라인을 저장하고 parser를 수정합니다.
- CIR 길이가 매번 다르면 가장 흔한 길이를 기준으로 padding/truncation 정책을 명시적으로 구현합니다.
- threshold가 너무 민감하면 `method=cosine` 또는 `method=energy`도 비교합니다.
- 고양이 크기 객체에서 변화가 약하면 UWB 송수신기 위치를 낮추고, 객체가 링크 근처를 지나가도록 실험 배치를 조정합니다.
