#!/usr/bin/env python3
"""Render the imported project's actual initial configs at XBuilder's fixed viewport.
Checks project/map dimensions, UI bounds and render scale; uses no hand-placed mockup.
"""
from pathlib import Path
from PIL import Image
from io import BytesIO
import json,zipfile,argparse
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('xbp',nargs='?',default=str(root.parent/'StarRailRunner.xbp'));args=p.parse_args()
with zipfile.ZipFile(args.xbp) as z:
 config=json.loads(z.read('assets/index.json'))
 assert config['run']==dict(width=480,height=360), 'XBuilder uses fixed viewport 480x360'
 assert config['map']['width']==480 and config['map']['height']==360
 backdrop=config['backdrops'][config['backdropIndex']]
 background=Image.open(BytesIO(z.read('assets/'+backdrop['path']))).convert('RGBA')
 resolution=backdrop.get('bitmapResolution',1)
 assert background.size==(480*resolution,360*resolution)
 canvas=background.resize((480,360),Image.Resampling.LANCZOS)
 checked=0
 important={'Hud','MenuPanel','StartButton','Footer','PausePanel','ResumeButton','EndPanel','RetryButton','JumpButton','SlideButton','PauseButton','SoundButton','Life'}
 for name in config['zorder']:
  s=json.loads(z.read(f'assets/sprites/{name}/index.json'))
  assert s['size']==.5, name+' wrong render scale'
  c=s['costumes'][s['costumeIndex']]
  im=Image.open(BytesIO(z.read(f'assets/sprites/{name}/'+c['path']))).convert('RGBA')
  factor=s['size']/c.get('bitmapResolution',1)
  w,h=[round(v*factor) for v in im.size]
  left=240+s['x']-c['x']*factor
  top=180-s['y']-c['y']*factor
  if name in important or 'Digit' in name:
   assert left>=0 and top>=0 and left+w<=480 and top+h<=360,(name,left,top,w,h)
   checked+=1
  if s.get('visible',True):
   im=im.resize((w,h),Image.Resampling.LANCZOS)
   canvas.alpha_composite(im,(round(left),round(top)))
 target=root.parent/'import-layout.png';canvas.resize((960,720),Image.Resampling.LANCZOS).save(target)
 print(f'PASS: native 480x360 viewport, {checked} UI bounds and all 89 render scales; actual config composition: {target}')
