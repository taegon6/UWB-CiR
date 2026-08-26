function selfcheck_vehicle_gt_pipeline_verified
% Synthetic regression check for the verified trajectory/evaluation path.
outDir=tempname; mkdir(outDir);
t=(0:0.05:4)';
x=0.1*sin(t); y=2-0.4*t; yaw=2*sin(0.5*t);
valid=ones(size(t)); valid(t>=1.5 & t<=1.9)=0;
gt=table(t,valid,x,y,yaw, ...
    'VariableNames',{'time_s','valid','x_gt_m','y_gt_m','yaw_gt_deg'});
writetable(gt,fullfile(outDir,'gt.csv'));

uwb=table(t,x+0.03,y-0.04,yaw+1,repmat("SS",size(t)), ...
    'VariableNames',{'time_s','x_uwb_m','y_uwb_m','yaw_uwb_deg','mode'});
uwb.mode(t>=1.3)="DS";
uwb.mode(t>=2.8)="PHASE";
writetable(uwb,fullfile(outDir,'uwb.csv'));

here=fileparts(mfilename('fullpath'));
cfg=fullfile(here,'..','config','vehicle_gt_config.json');
r=run_vehicle_gt_pipeline_verified( ...
    fullfile(outDir,'gt.csv'),fullfile(outDir,'uwb.csv'),cfg);

assert(abs(r.position_rmse_m-0.05)<1e-10,'Expected 5 cm synthetic position RMSE.');
assert(abs(r.yaw_rmse_deg-1)<1e-10,'Expected 1 deg synthetic yaw RMSE.');
assert(r.gt_valid_rate<1,'Synthetic GT dropout was not preserved.');
assert(~any(r.aligned.time>=1.5 & r.aligned.time<=1.9), ...
    'Long invalid ChArUco gap was incorrectly interpolated.');
disp('selfcheck_vehicle_gt_pipeline_verified: PASS');
