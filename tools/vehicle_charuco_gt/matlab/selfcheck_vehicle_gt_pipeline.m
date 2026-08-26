function selfcheck_vehicle_gt_pipeline
% Synthetic check that the DGPS-style Camera GT map pipeline works.
outDir=tempname; mkdir(outDir);
t=(0:0.05:4)';
x=0.08*sin(t); y=2-0.4*t; yaw=2*sin(0.5*t);
gt=table(t,ones(size(t)),x,y,yaw, ...
    'VariableNames',{'time_s','valid','x_gt_m','y_gt_m','yaw_gt_deg'});
writetable(gt,fullfile(outDir,'gt.csv'));
uwb=table(t,x+0.03,y-0.04,yaw+1,repmat("SS",size(t)), ...
    'VariableNames',{'time_s','x_uwb_m','y_uwb_m','yaw_uwb_deg','mode'});
uwb.mode(t>=1.3)="DS";
uwb.mode(t>=2.8)="PHASE";
writetable(uwb,fullfile(outDir,'uwb.csv'));
here=fileparts(mfilename('fullpath'));
cfg=fullfile(here,'..','config','vehicle_gt_config.json');
r=run_vehicle_gt_pipeline(fullfile(outDir,'gt.csv'),fullfile(outDir,'uwb.csv'),cfg);
assert(abs(r.position_rmse_m-0.05)<1e-10,'Expected 5 cm synthetic position RMSE.');
assert(abs(r.yaw_rmse_deg-1)<1e-10,'Expected 1 deg synthetic yaw RMSE.');
assert(height(r.aligned)==height(uwb),'Expected all synthetic UWB samples to align.');
disp('selfcheck_vehicle_gt_pipeline: PASS');
end
