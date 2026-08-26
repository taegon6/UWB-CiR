function results = run_vehicle_gt_pipeline_verified(gtCsv, uwbCsv, configJson)
% Verified offline ChArUco GT + UWB trajectory plot/evaluation pipeline.
% GT is plotted like a DGPS reference trajectory. Long ChArUco dropouts are
% never bridged by interpolation when computing UWB error metrics.
arguments
    gtCsv (1,1) string
    uwbCsv (1,1) string = ""
    configJson (1,1) string = "../config/vehicle_gt_config.json"
end

cfg = jsondecode(fileread(configJson));

%% Ground truth input
g0 = readtable(gtCsv, TextType="string");
gt = table( ...
    numcol(g0,["time_s","time"]), ...
    logical(numcoldef(g0,["valid"],ones(height(g0),1))), ...
    numcol(g0,["x_gt_m","x_gt","x"]), ...
    numcol(g0,["y_gt_m","y_gt","y"]), ...
    numcoldef(g0,["yaw_gt_deg","yaw_deg","theta_deg"],zeros(height(g0),1)), ...
    'VariableNames',{'time','valid','x','y','yaw'});

gt.valid = gt.valid & isfinite(gt.time) & isfinite(gt.x) & isfinite(gt.y);
if ~any(gt.valid)
    error('No valid GT samples.');
end

gtPlot = gt;
gtPlot.x(~gtPlot.valid) = nan;
gtPlot.y(~gtPlot.valid) = nan;
gtPlot.yaw(~gtPlot.valid) = nan;
gtValid = gt(gt.valid,:);

%% Optional UWB input
hasUwb = strlength(uwbCsv)>0 && isfile(uwbCsv);
if hasUwb
    u0 = readtable(uwbCsv, TextType="string");
    uwb = table( ...
        numcol(u0,["time_s","time"]), ...
        numcol(u0,["x_uwb_m","x_uwb","x"]), ...
        numcol(u0,["y_uwb_m","y_uwb","y"]), ...
        numcoldef(u0,["yaw_uwb_deg","yaw_deg","theta_deg"],nan(height(u0),1)), ...
        strcoldef(u0,["mode","ranging_mode"],repmat("",height(u0),1)), ...
        'VariableNames',{'time','x','y','yaw','mode'});
    uwb.time = uwb.time + cfg.sync.uwb_time_offset_s;
    uwb = uwb(isfinite(uwb.time) & isfinite(uwb.x) & isfinite(uwb.y),:);
else
    uwb = table();
end

%% Lee-paper-style trajectory map
anchors = [cfg.anchors.A1(:)'; cfg.anchors.A2(:)'];
figure('Color','w','Name','Vehicle trajectory');
hold on; grid on; axis equal; box on;
plot(anchors(:,1),anchors(:,2),'k^','MarkerFaceColor','k', ...
    'MarkerSize',8,'DisplayName','Anchor');
plot(gtPlot.x,gtPlot.y,'k-.','LineWidth',1.7, ...
    'DisplayName','Camera/ChArUco GT');
if hasUwb
    plot(uwb.x,uwb.y,'b-','LineWidth',1.4,'DisplayName','UWB estimate');
end

count = min(cfg.plot.vehicle_footprint_count,height(gtValid));
idx = unique(round(linspace(1,height(gtValid),count)));
cx = fielddef(cfg.vehicle,'reference_to_body_center_x_m',0.0);
cy = fielddef(cfg.vehicle,'reference_to_body_center_y_m',0.0);
for k = idx(:)'
    drawVehicleFromReference(gtValid.x(k),gtValid.y(k),gtValid.yaw(k), ...
        cfg.vehicle.length_m,cfg.vehicle.width_m,cx,cy);
end

if hasUwb && cfg.plot.show_mode_switches
    m = upper(strtrim(uwb.mode));
    sw = find(m(2:end)~=m(1:end-1))+1;
    for i = 1:numel(sw)
        k = sw(i);
        if strlength(m(k-1))==0 || strlength(m(k))==0
            continue;
        end
        plot(uwb.x(k),uwb.y(k),'ko','MarkerFaceColor','w', ...
            'HandleVisibility','off');
        text(uwb.x(k),uwb.y(k),"  "+m(k-1)+"->"+m(k),'FontSize',9);
    end
end

xlabel('x (m)'); ylabel('y (m)');
title('Vehicle trajectory: Camera GT vs UWB');
legend('Location','best');
allx = [gtValid.x; anchors(:,1)];
ally = [gtValid.y; anchors(:,2)];
if hasUwb
    allx = [allx; uwb.x];
    ally = [ally; uwb.y];
end
p = cfg.plot.axis_padding_m;
xlim([min(allx)-p max(allx)+p]);
ylim([min(ally)-p max(ally)+p]);

results = struct('gt',gt,'gtValid',gtValid,'uwb',uwb);
results.gt_valid_rate = mean(gt.valid);

%% UWB error against GT
if hasUwb
    t0 = max(min(gtValid.time),min(uwb.time));
    t1 = min(max(gtValid.time),max(uwb.time));
    a = uwb(uwb.time>=t0 & uwb.time<=t1,:);
    maxGap = fielddef(cfg.plot,'gt_max_interp_gap_s',0.20);
    a.x_gt = interpNoLongGap(gtValid.time,gtValid.x,a.time,maxGap);
    a.y_gt = interpNoLongGap(gtValid.time,gtValid.y,a.time,maxGap);
    yawUnwrapped = rad2deg(unwrap(deg2rad(gtValid.yaw)));
    a.yaw_gt = interpNoLongGap(gtValid.time,yawUnwrapped,a.time,maxGap);
    a.pos_err = hypot(a.x-a.x_gt,a.y-a.y_gt);
    a.yaw_err = mod(a.yaw-a.yaw_gt+180,360)-180;
    a = a(isfinite(a.pos_err),:);
    if isempty(a)
        error('No synchronized GT/UWB samples after applying GT gap guard.');
    end
    results.aligned = a;
    results.position_rmse_m = sqrt(mean(a.pos_err.^2,'omitnan'));
    results.position_p95_m = percentile95(a.pos_err);
    results.yaw_rmse_deg = sqrt(mean(a.yaw_err.^2,'omitnan'));
    results.yaw_p95_deg = percentile95(abs(a.yaw_err));

    figure('Color','w','Name','UWB error');
    tiledlayout(2,1);
    nexttile; plot(a.time,a.pos_err,'k-'); grid on; ylabel('position error (m)');
    nexttile; plot(a.time,a.yaw_err,'k-'); grid on; ylabel('yaw error (deg)'); xlabel('time (s)');
end
end

function drawVehicleFromReference(x,y,yawDeg,L,W,cx,cy)
body = [cx-W/2 cy-L/2; cx+W/2 cy-L/2; cx+W/2 cy+L/2; ...
    cx-W/2 cy+L/2; cx-W/2 cy-L/2];
a = deg2rad(yawDeg); R = [cos(a) -sin(a); sin(a) cos(a)];
q = (R*body')' + [x y];
plot(q(:,1),q(:,2),'-','Color',[0.35 0.35 0.35], ...
    'LineWidth',0.9,'HandleVisibility','off');
front = (R*[0;-0.6])' + [x y];
plot([x front(1)],[y front(2)],'-','Color',[0.35 0.35 0.35], ...
    'HandleVisibility','off');
end

function v = numcol(T,names)
for n = names
    if ismember(n,T.Properties.VariableNames), v=str2double(string(T.(n))); return; end
end
error('Missing required column: %s',strjoin(names,', '));
