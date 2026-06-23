# Codex handoff guide

이 문서는 실험 환경에서 Codex가 DW3000/DWM3000 계열 UWB 장치를 연결하고 CIR 데이터를 저장하기 위한 작업 지침입니다.

## Project objective

본 프로젝트의 목표는 다음과 같습니다.

```text
DW3000 CIR acquisition
        ↓
CSV logging
        ↓
Baseline anomaly detection
        ↓
Camera event / vision verification
```

핵심은 UWB CIR로 먼저 이상 변화를 감지하고, 그때만 카메라 확인 단계로 넘기는 것입니다.

## Lab checklist

### 1. Environment setup

```bash
git clone https://github.com/taegon6/UWB-CiR.git
cd UWB-CiR
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

Windows PowerShell:

```powershell
git clone https://github.com/taegon6/UWB-CiR.git
cd UWB-CiR
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH="src"
pytest -q
```

### 2. Find the serial port

```bash
python scripts/list_serial_ports.py
```

Typical port examples:

```text
/dev/ttyUSB0
/dev/ttyACM0
COM3
COM4
```

### 3. Inspect raw output

Run a short capture and save raw lines for debugging.

```bash
python scripts/collect_dw3000_serial.py --port /dev/ttyUSB0 --baudrate 115200 --output data/raw/test.csv --max-samples 10 --raw-log data/interim/test_raw.log
```

If the parser fails, inspect `data/interim/test_raw.log` and update `src/uwb_cir/hardware/dw3000_serial.py`.

### 4. Collect baseline data

No object, no human, no cat near the UWB link.

```bash
python scripts/collect_dw3000_serial.py --port /dev/ttyUSB0 --baudrate 115200 --output data/raw/baseline_empty.csv --max-samples 300
```

### 5. Collect event data

Place a cat/person/object near the link or let it pass through the link.

```bash
python scripts/collect_dw3000_serial.py --port /dev/ttyUSB0 --baudrate 115200 --output data/raw/object_event.csv --max-samples 300
```

### 6. Run anomaly detection

```bash
python scripts/run_anomaly_trigger.py --input data/raw/object_event.csv --baseline-rows 50 --threshold 0.2 --method l2
```

Compare methods:

```bash
python scripts/run_anomaly_trigger.py --input data/raw/object_event.csv --baseline-rows 50 --threshold 0.05 --method cosine
python scripts/run_anomaly_trigger.py --input data/raw/object_event.csv --baseline-rows 50 --threshold 0.15 --method energy
```

## Firmware output requirement

The easiest firmware-side protocol is one JSON object per line.

```json
{"timestamp":"2026-01-01T12:00:00.000Z","cir":[0.01,0.02,0.03,0.04]}
```

CSV line is also accepted.

```text
2026-01-01T12:00:00.000Z,0.01,0.02,0.03,0.04
```

## What Codex should implement next

1. Match parser with actual firmware output.
2. Add metadata extraction if the firmware exposes first path amplitude, RX power, or NLOS diagnostic values.
3. Add live anomaly detection mode:

```bash
python scripts/live_anomaly_monitor.py --port /dev/ttyUSB0 --baseline data/processed/baseline.csv
```

4. Add camera capture after camera event.
5. Add experiment summary notebook.

## Notes

This repository intentionally starts with a simple baseline detector. Do not jump directly to SNN/CNN until the data pipeline is stable.
