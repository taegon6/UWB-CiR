function results = run_vehicle_gt_pipeline(gtCsv, uwbCsv, configJson)
% Plot offline ChArUco ground truth and optional UWB trajectory.
arguments
    gtCsv (1,1) string
    uwbCsv (1,1) string = ""
    configJson (1,1) string = "../config/vehicle_gt_config.json"
end
cfg = jsondecode(fileread(configJson));
gt0 = readtable(gtCsv, TextType="string");
gt = table(numcol(gt0,["time_s","time"]), logical(numcoldef(gt0,["valid"],ones(height(gt0),1))), ...
    numcol(gt0,["x_gt_m","x_gt","x"]), numcol(gt0,["y_gt_m","y_gt","y"]), ...
    numcoldef(gt0,["yaw_gt_deg","yaw_deg","theta_deg"],zeros(height(gt0),1)), ...
    'VariableNames',{'time','valid','x','y','yaw'});
gt = gt(gt.valid & isfinite(gt.x) & isfinite(gt.y),:);
if isempty(gt), error('No valid GT samples.'); end
hasUwb = strlength(uwbCsv)>0 && isfile(uwbCsv);
if hasUwb
    u0 = readtable(uwbCsv, TextType="string");
    uwb = table(numcol(u0,["time_s","time"]), numcol(u0,["x_uwb_m","x_uwb","x"]), ...
        numcol(u0,["y_uwb_m","y_uwb","y"]), numcoldef(u0,["yaw_uwb_deg","yaw_deg","theta_deg"],nan(height(u0),1)), ...
        strcoldef(u0,["mode","ranging_mode"],repmat("",height(u0),1)), ...
        'VariableNames',{'time','x','y','yaw','mode'});
    uwb.time = uwb.time + cfg.sync.uwb_time_offset_s;
    uwb = uwb(isfinite(uwb.time)&isfinite(uwb.x)&isfinite(uwb.y),:);
else
    uwb = table();
end
anchors = [cfg.anchors.A1(:)'; cfg.anchors.A2(:)'];
figure('Color','w','Name','Vehicle trajectory'); hold on; grid on; axis equal; box on;
plot(anchors(:,1),anchors(:,2),'k^','MarkerFaceColor','k','MarkerSize',8,'DisplayName','Anchor');
plot(gt.x,gt.y,'k-.','LineWidth',1.7,'DisplayName','Camera/ChArUco GT');
if hasUwb, plot(uwb.x,uwb.y,'b-','LineWidth',1.3,'DisplayName','UWB SS/DS/Phase'); end
idx = unique(round(linspace(1,height(gt),min(cfg.plot.vehicle_footprint_count,height(gt)))));
for k = idx(:)'
    drawVehicle(gt.x(k),gt.y(k),gt.yaw(k),cfg.vehicle.length_m,cfg.vehicle.width_m);
end
if hasUwb && cfg.plot.show_mode_switches
    m = upper(strtrim(uwb.mode));
    sw = find(m(2:end)~=m(1:end-1))+1;
    for i=1:numel(sw)
        k=sw(i); plot(uwb.x(k),uwb.y(k),'ko','MarkerFaceColor','w','HandleVisibility','off');
        text(uwb.x(k),uwb.y(k),"  "+m(k-1)+"->"+m(k),'FontSize',9);
    end
end
xlabel('x (m)'); ylabel('y (m)'); title('Vehicle trajectory: Camera/ChArUco GT vs UWB'); legend('Location','best');
allx=[gt.x;anchors(:,1)]; ally=[gt.y;anchors(:,2)];
if hasUwb, allx=[allx;uwb.x]; ally=[ally;uwb.y]; end
p=cfg.plot.axis_padding_m; xlim([min(allx)-p max(allx)+p]); ylim([min(ally)-p max(ally)+p]);
results=struct('gt',gt,'uwb',uwb);
if hasUwb
    t0=max(min(gt.time),min(uwb.time)); t1=min(max(gt.time),max(uwb.time));
    a=uwb(uwb.time>=t0 & uwb.time<=t1,:);
    a.x_gt=interp1(gt.time,gt.x,a.time,'linear',nan); a.y_gt=interp1(gt.time,gt.y,a.time,'linear',nan);
    a.yaw_gt=rad2deg(interp1(gt.time,unwrap(deg2rad(gt.yaw)),a.time,'linear',nan));
    a.pos_err=hypot(a.x-a.x_gt,a.y-a.y_gt); a.yaw_err=mod(a.yaw-a.yaw_gt+180,360)-180;
    a=a(isfinite(a.pos_err),:); results.aligned=a;
    results.position_rmse_m=sqrt(mean(a.pos_err.^2,'omitnan'));
    results.position_p95_m=prctile(a.pos_err,95);
    results.yaw_rmse_deg=sqrt(mean(a.yaw_err.^2,'omitnan'));
    results.yaw_p95_deg=prctile(abs(a.yaw_err),95);
    figure('Color','w','Name','UWB error'); tiledlayout(2,1);
    nexttile; plot(a.time,a.pos_err,'k-'); grid on; ylabel('position error (m)');
    nexttile; plot(a.time,a.yaw_err,'k-'); grid on; ylabel('yaw error (deg)'); xlabel('time (s)');
end
end

function drawVehicle(x,y,yawDeg,L,W)
body=[-W/2 -L/2; W/2 -L/2; W/2 L/2; -W/2 L/2; -W/2 -L/2];
a=deg2rad(yawDeg); R=[cos(a) -sin(a); sin(a) cos(a)]; p=(R*body')'+[x y];
plot(p(:,1),p(:,2),'-','Color',[0.2 0.45 1.0],'LineWidth',0.9,'HandleVisibility','off');
front=(R*[0;-L/2])'+[x y]; plot([x front(1)],[y front(2)],'-','Color',[0.2 0.45 1.0],'HandleVisibility','off');
end
function v=numcol(T,names)
for n=names, if ismember(n,T.Properties.VariableNames), v=str2double(string(T.(n))); return; end, end
error('Missing required column: %s',strjoin(names,', '));
end
function v=numcoldef(T,names,d)
for n=names, if ismember(n,T.Properties.VariableNames), v=str2double(string(T.(n))); return; end, end, v=d;
end
function v=strcoldef(T,names,d)
for n=names, if ismember(n,T.Properties.VariableNames), v=string(T.(n)); return; end, end, v=d;
end
