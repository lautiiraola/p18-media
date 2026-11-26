import sys, subprocess, numpy as np
f=sys.argv[1]; fps=10; W,H=108,192
p=subprocess.run(["ffmpeg","-v","error","-i",f,"-vf",f"fps={fps},scale={W}:{H},format=gray","-f","rawvideo","-"],capture_output=True).stdout
fr=np.frombuffer(p,np.uint8).reshape(-1,H,W).astype(float)
# sharpness on the lower-right area (no card text there): mean abs gradient
reg=fr[:,110:185,55:105]
sh=np.abs(np.diff(reg,axis=1)).mean((1,2))+np.abs(np.diff(reg,axis=2)).mean((1,2))
med=np.median(sh)
blur=sh<med*0.45
# runs
runs=[];i=0
while i<len(blur):
    if blur[i]:
        j=i
        while j<len(blur) and blur[j]: j+=1
        if j-i>=6: runs.append((i/fps,j/fps))
        i=j
    else: i+=1
print(f"dur={len(fr)/fps:.1f} med={med:.2f}")
for a,b in runs: print(f"placa {a:6.2f} -> {b:6.2f}")
