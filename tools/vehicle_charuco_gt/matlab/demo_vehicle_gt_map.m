function demo_vehicle_gt_map
% Synthetic demonstration of the vehicle trajectory plotting pipeline.
outDir = tempname; mkdir(outDir);
t = (0:0.05:8)'; y=2.0-0.25*t; x=0.15*sin(0.7*t); yaw=4*sin(0.4*t);
gt=table(t,ones(size(t)),x,y,yaw,'VariableNames',{'time_s','valid','x_gt_m','y_gt_m','yaw_gt_deg'});
writetable(gt,fullfile(outDir,'gt.csv'));
uwb=table(t,x+0.025*sin(2*t),y+0.035*cos(1.5*t),yaw+0.8*sin(t),repmat("SS",size(t)), ...
    'VariableNames',{'time_s','x_uwb_m','y_uwb_m','yaw_uwb_deg','mode'});
uwb.mode(t>=3)="DS"; uwb.mode(t>=6)="PHASE"; writetable(uwb,fullfile(outDir,'uwb.csv'));
here=fileparts(mfilename('fullpath')); cfg=fullfile(here,'..','config','vehicle_gt_config.json');
run_vehicle_gt_pipeline(fullfile(outDir,'gt.csv'),fullfile(outDir,'uwb.csv'),cfg);
end
