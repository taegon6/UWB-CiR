# Lab Result

Date: 2026-06-23

## Target

Intermediate target is cat-sized object detection using DW3000/DWM3000 CIR anomaly detection. This pass focused on stabilizing the real CIR acquisition path before collecting cat-sized object datasets.

## Environment

- Python: 3.14.4
- Installed:
  - `requirements.txt`
  - `requirements-hardware.txt`
- Test command: `PYTHONPATH=src python -m pytest -q`
- Demo command: `python scripts/run_anomaly_trigger.py --demo`

## Board And Firmware Route

- Target MCU: `nRF52840_xxAA`
- Board marking: Nordic `nRF52840 DK`
- Debug interface detected by J-Link: `J-Link OB-nRF5340-NordicSemi`
- UWB route: nRF52840 DK with DW3000/DWM3000 UWB module/shield over SPI
- Receiver board J-Link serial: `001050280655`
- Initiator board J-Link serial: `001050265981`

Firmware route used:

- Receiver board `001050280655`: custom `DW3000_CIR_SERIAL_RX` firmware
- Initiator board `001050265981`: existing `DS_TWR_INITIATOR_FINAL` firmware
- Output route: USB CDC UART through the J-Link VCOM interface
- Serial port used for CIR collection: `COM27`
- Baudrate: `115200`

The custom receiver firmware prints one JSON CIR frame per received UWB packet. It reads DW3000 accumulator taps around the first path, converts complex samples to integer magnitudes, and emits a parseable JSON line.

Firmware source location used during this lab pass:

```text
C:\Users\User\Documents\학부연구생\research\uwb_followup\original_repos\UWB-Ranging-Optimization\API\Src\custom_code\dw3000_cir_serial_rx.c
```

## Serial Ports Checked

Detected J-Link CDC UART ports:

- `COM27`: JLink CDC UART Port, serial `001050280655`, interface `x.0`
- `COM28`: JLink CDC UART Port, serial `001050280655`, interface `x.2`
- `COM15`: JLink CDC UART Port, serial `001050265981`, interface `x.2`
- `COM16`: JLink CDC UART Port, serial `001050265981`, interface `x.0`

`COM27` is the working CIR serial output port for the receiver firmware.

## Raw Output Format

Actual parseable raw output example from `COM27` at `115200` baud:

```json
{"frame":5504,"fp_index":47248,"frame_len":12,"cir":[33,10,31,32,6,21,18,38,26,16,30,16,32,33,15,36,146,436,384,343,399,373,403,174,65,174,113,410,813,934,678,109]}
```

Boot/status lines may also appear after reset, for example:

```json
{"status":"dw3000_cir_serial_rx_start","baudrate":115200}
{"status":"rx_waiting"}
```

The collector skips status lines because they do not contain a `cir` field. Raw logs still keep them for debugging.

## Collector Verification

Probe command:

```powershell
python scripts\collect_dw3000_serial.py --port COM27 --baudrate 115200 --output data/raw/_probe.csv --max-samples 3 --timeout 0.2 --idle-timeout 5 --raw-log data/interim/com27_probe_raw.log
```

Result:

- Saved `3` real CIR frames to `data/raw/_probe.csv`
- Raw serial log saved to `data/interim/com27_probe_raw.log`
- Final CSV format preserved:

```csv
timestamp,cir_0,cir_1,...,cir_31
```

The collector can now load real DW3000 CIR frames into the existing anomaly pipeline.

## Dataset Collection

Requested datasets:

- `data/raw/normal_empty.csv`
- `data/raw/cat_static.csv`
- `data/raw/cat_moving.csv`

Samples collected so far:

- `normal_empty`: `0`
- `cat_static`: `0`
- `cat_moving`: `0`

Reason: the serial and firmware path is now working, but the three physical lab conditions have not been staged yet in this Codex run. No fake experimental data was generated.

## Anomaly Methods

Methods to compare after real datasets are collected:

- `l2`
- `cosine`
- `energy`

No best threshold is reported yet because `normal_empty` and `cat_moving` real datasets have not been collected. The synthetic demo confirms the baseline anomaly detector itself is functional.

Initial commands to run after data collection:

```powershell
python scripts\run_anomaly_trigger.py --input data/raw/cat_moving.csv --baseline-rows 50 --threshold 0.2 --method l2
python scripts\run_anomaly_trigger.py --input data/raw/cat_moving.csv --baseline-rows 50 --threshold 0.05 --method cosine
python scripts\run_anomaly_trigger.py --input data/raw/cat_moving.csv --baseline-rows 50 --threshold 0.15 --method energy
```

## Next Steps

1. Keep the receiver board on `DW3000_CIR_SERIAL_RX` and the initiator board on `DS_TWR_INITIATOR_FINAL`.
2. Collect `normal_empty.csv` with no object near the UWB link.
3. Collect `cat_static.csv` with a cat-sized object near or across the UWB link.
4. Collect `cat_moving.csv` while moving a cat-sized object through the UWB link.
5. Run `l2`, `cosine`, and `energy` anomaly checks and choose the method with the clearest separation.

Current blocker for the final anomaly report: real physical `normal_empty`, `cat_static`, and `cat_moving` datasets still need to be collected under controlled lab conditions.
