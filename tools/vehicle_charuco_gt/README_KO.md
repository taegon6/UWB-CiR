# 차량 ChArUco GT + MATLAB 경로 맵

목적은 실시간 추정이 아니라 **스마트폰으로 촬영한 ChArUco 영상에서 오프라인으로 Ground Truth 경로를 얻고**, UWB 추정 결과와 MATLAB에서 한 맵에 비교하는 것입니다.

## 좌표계

- `A1 = (-1, 0) m`
- `A2 = (+1, 0) m`
- anchor baseline = `2.0 m`
- 원점 = A1-A2 중점
- `+X = A1 -> A2`
- `+Y = 패드에서 차량 시작 위치 방향`
- 차량 접근 방향 = `-Y`

ChArUco world registration은 보드 중심을 원점에 놓고 보드 +X를 A1->A2로 맞춘 상태에서 수행합니다. 이후 스마트폰/삼각대는 움직이지 않습니다.

## Ground Truth CSV

영상 후처리 결과는 최소 다음 형식이면 됩니다.

```csv
time_s,valid,x_gt_m,y_gt_m,yaw_gt_deg
0.000,1,0.02,1.98,-2.1
0.033,1,0.02,1.97,-2.0
```

## UWB CSV

```csv
time_s,x_uwb_m,y_uwb_m,yaw_uwb_deg,mode
0.000,0.03,2.01,-2.5,SS
0.050,0.03,1.97,-2.3,SS
```

`mode`는 `SS`, `DS`, `PHASE`를 권장합니다.

## MATLAB 실행

```matlab
cd tools/vehicle_charuco_gt/matlab
run_vehicle_gt_pipeline('../output/run01_gt.csv', '../output/run01_uwb.csv', '../config/vehicle_gt_config.json');
```

결과 그림에는 Anchor, ChArUco GT 경로, UWB 경로, 여러 시점의 차량 footprint, SS->DS/DS->PHASE 전환 위치가 표시됩니다. UWB가 있으면 위치 오차와 yaw 오차도 별도 figure로 계산합니다.

먼저 synthetic demo를 실행할 수 있습니다.

```matlab
demo_vehicle_gt_map
```
