import json, subprocess, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'pilot/approved/manifest.json').read_text())
assert manifest['technical_fixture'] is True
out=root/'pilot/output'; out.mkdir(parents=True,exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
for i,shot in enumerate(manifest['shots'],1):
    assert shot['approved'] and shot['duration_seconds']>0
    im=Image.new('RGB',(720,1280),(18+8*i,35+9*i,56+9*i)); d=ImageDraw.Draw(im)
    big=ImageFont.truetype(font,49); small=ImageFont.truetype(font,26)
    d.rounded_rectangle((65,410,655,840),radius=35,outline=(185,205,225),width=3)
    d.text((110,505),f'SHOT {i:02}',font=big,fill='white')
    d.text((110,610),shot['label'],font=small,fill='white')
    d.text((110,700),'TECHNICAL DEMO',font=small,fill=(180,205,220))
    im.save(out/f'frame-{i:02}.png')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','25','-i',str(out/f'frame-{i:02}.png'),'-t',str(shot['duration_seconds']),'-vf','format=yuv420p','-c:v','libx264','-r','25','-pix_fmt','yuv420p',str(out/f'clip-{i:02}.mp4')],check=True)
files=[out/f'clip-{i:02}.mp4' for i in range(1,len(manifest['shots'])+1)]
(out/'concat.txt').write_text(''.join(f"file '{p.name}'\n" for p in files))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(out/'concat.txt'),'-c','copy',str(out/'pilot.mp4')],check=True)
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=codec_name,width,height,r_frame_rate','-of','json',str(out/'pilot.mp4')]))
assert abs(float(meta['format']['duration'])-sum(s['duration_seconds'] for s in manifest['shots']))<0.2
assert meta['streams'][0]['width']==720 and meta['streams'][0]['height']==1280
meta['sha256']=hashlib.sha256((out/'pilot.mp4').read_bytes()).hexdigest()
meta['status']='PASS_TECHNICAL_ONLY'
(out/'qa.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
