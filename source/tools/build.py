#!/usr/bin/env python3
"""Rebuild original art, spx sprite configs, sounds and importable .xbp.
Requires Python 3.10+ and Pillow. Run from anywhere: python tools/build.py
All art/audio are generated locally. No network assets.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math, json, random, wave, struct, zipfile, shutil, os
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
AS=ROOT/'assets'
S=2
# XBuilder ignores custom run dimensions and always uses a 480x360 viewport.
# Keep gameplay in 960x540 design coordinates; scale ALL rendered sizes/positions.
VIEW_SCALE=0.5
FONT_CANDIDATES=[os.environ.get('RUNNER_FONT',''),'/System/Library/Fonts/Supplemental/Arial Unicode.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/msyh.ttc']
FONT=next((x for x in FONT_CANDIDATES if x and Path(x).exists()),None)
BOLD=next((x for x in ['/System/Library/Fonts/Supplemental/Arial Bold.ttf',FONT] if x and Path(x).exists()),None)
MINT='#74f7d5'; WHITE='#f4f5ff'; MUTED='#a5b3ce'; ORANGE='#ffb36f'; NAVY='#111b35'
rng=random.Random(23)
def canvas(w,h): return Image.new('RGBA',(w*S,h*S))
def draw(im): return ImageDraw.Draw(im)
def box(im,xy,fill,r=0,outline=None,width=1):
 d=draw(im); xy=tuple(int(v*S) for v in xy)
 if r:d.rounded_rectangle(xy,int(r*S),fill,outline,width*S)
 else:d.rectangle(xy,fill,outline,width*S)
def ellipse(im,xy,fill,outline=None,width=1):draw(im).ellipse(tuple(int(v*S) for v in xy),fill,outline,width*S)
def line(im,xy,fill,width=1):draw(im).line(tuple(int(v*S) for v in xy),fill,width*S)
def poly(im,xy,fill): draw(im).polygon([(int(x*S),int(y*S)) for x,y in xy],fill)
def text(im,xy,t,size=18,fill=WHITE,bold=False,anchor=None):
 f=ImageFont.truetype(BOLD if bold and t.isascii() else FONT,int(size*S)) if FONT else ImageFont.load_default()
 draw(im).text((int(xy[0]*S),int(xy[1]*S)),t,font=f,fill=fill,anchor=anchor)
def save(im,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 im.resize((im.width//S,im.height//S),Image.Resampling.LANCZOS).save(path)
def glow(im,xy,color,width=5):
 g=Image.new('RGBA',im.size);line(g,xy,color,width);im.alpha_composite(g.filter(ImageFilter.GaussianBlur(9*S)));line(im,xy,color,2)
def pill(im,xy,t,color=MINT):
 x,y,w=xy;box(im,(x,y,x+w,y+28),'#1c3247',14,outline='#335269');text(im,(x+w/2,y+14),t,12,color,anchor='mm')
def sprite(name,ims,code='',x=0,y=0,visible=True,pivot=None):
 if not isinstance(ims,list):ims=[ims]
 base=AS/'sprites'/name; costumes=[]
 for i,im in enumerate(ims):
  path=base/f'{i}.png';save(im,path);w,h=im.width//S,im.height//S
  px,py=pivot or (w/2,h/2)
  costumes.append(dict(name=f'frame{i}',path=f'{i}.png',x=px,y=py,faceRight=0,bitmapResolution=1,imageWidth=w,imageHeight=h))
 cfg=dict(heading=90,x=x*VIEW_SCALE,y=y*VIEW_SCALE,size=VIEW_SCALE,rotationStyle='none',physicsMode='no',costumeIndex=0,visible=visible,isDraggable=False,collisionShapeType='none',costumes=costumes)
 (base/'index.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2))
 (ROOT/f'{name}.spx').write_text(code+'\n')
 return name
sprites=[]
def add(*args,**kw):
 n=sprite(*args,**kw);sprites.append(n);return n
# BACKDROP ------------------------------------------------------------------
bg=canvas(960,540)
for yy in range(540):
 t=yy/540;c=tuple(int(a*(1-t)+b*t) for a,b in zip((13,23,48),(56,51,84)))+(255,)
 line(bg,(0,yy,960,yy),c,1)
# distant stars, orbital rings and warm planet
for _ in range(75):
 x,y=rng.randrange(960),rng.randrange(12,320);r=rng.choice([.7,1,1.5]);ellipse(bg,(x-r,y-r,x+r,y+r),(169,196,230,rng.randrange(80,210)))
ellipse(bg,(600,70,806,276),'#f6aa92')
for yy in range(75,277,11):line(bg,(602,yy,805,yy),'#e8978e',2)
ellipse(bg,(573,53,832,303),None,'#847b9b',1)
# thin orange moon line and orbit
line(bg,(542,203,866,141),'#9b8a9e',2)
for i in range(26):
 x=i*40-8;h=rng.randint(30,130);base=355
 box(bg,(x,base-h,x+29,base),'#263650',3)
 if i%3==0:line(bg,(x+15,base-h,x+15,base-h-20),'#4d5776',2)
 for yy in range(base-h+10,base-8,17):
  for xx in range(x+6,x+25,9):box(bg,(xx,yy,xx+2,yy+4),'#657288')
text(bg,(38,199),'SECTOR 07',11,'#6e859d',True)
line(bg,(39,222,140,222),'#536b86')
# lower track base static
box(bg,(0,412,960,540),'#101b30')
for yy in range(445,540,22):line(bg,(0,yy,960,yy),'#1a2e43')
backdrop=canvas(960,720)
box(backdrop,(0,0,960,720),'#0d172e')
backdrop.alpha_composite(bg,(0,90*S))
save(backdrop,AS/'backdrops'/'orbit.png')
# PARALLAX CITY strips -------------------------------------------------------
city=canvas(960,215)
for i in range(16):
 x=i*62;h=rng.randint(45,166)
 box(city,(x,215-h,x+44,215),'#1a2942',3,outline='#30465e')
 box(city,(x+4,216-h,x+40,218-h),'#4a697c')
 for yy in range(226-h,208,17):
  for xx in range(x+8,x+40,12):box(city,(xx,yy,xx+4,yy+6),rng.choice(['#477084','#59758a','#3b4d68']))
 if i%5==0:
  box(city,(x-4,232-h,x+48,251-h),'#584d70',3);text(city,(x+22,242-h),'07 / X',9,MINT,anchor='mm')
for i in range(2):
 add(f'City{i}',city,f'''import "math"
onMsg "render", => {{
    setXYpos ({i*960} - math.Mod(Scroll*0.2,960))*0.5, -41.25
}}''',x=i*960,y=-82.5)
# Ground strip repeated, anchored to center y=-162
track=canvas(960,54)
box(track,(0,0,960,54),'#16283b');box(track,(0,0,960,7),'#a4fff0');box(track,(0,7,960,12),'#337b82');box(track,(0,12,960,17),'#163544')
for x in range(0,960,80):
 poly(track,[(x,19),(x+39,19),(x+24,30),(x-15,30)],'#334459')
 line(track,(x+3,43,x+59,43),'#546071',2)
glow(track,(0,3,960,3),'#79ffe0',5)
for i in range(2):
 add(f'Track{i}',track,f'''import "math"
onMsg "render", => {{
    setXYpos ({i*960} - math.Mod(Scroll,960))*0.5, -83.5
}}''',x=i*960,y=-167)
# Obstacles common costumes: crate / tower / hovering drone / pit -------------
crate=canvas(82,140);box(crate,(15,85,67,138),'#b26b62',7,outline='#ffcb9c',width=2)
box(crate,(20,91,62,131),'#764c58',4);poly(crate,[(24,121),(41,99),(58,121)],ORANGE);line(crate,(41,106,41,114),'#5c4058',3);ellipse(crate,(40,118,42,120),'#5c4058')
tower=canvas(82,140);box(tower,(14,35,68,138),'#655b94',7,outline='#c7b1fb',width=2)
for y in [46,74,102]:
 box(tower,(22,y,60,y+17),'#333b64',3);line(tower,(28,y+11,38,y+4,48,y+11,57,y+4),'#c4b1fe',2)
drone=canvas(82,140);ellipse(drone,(10,49,72,80),'#a285c5',outline='#ddc1fa',width=2);box(drone,(21,54,61,72),'#2a3555',8);ellipse(drone,(32,58,48,68),'#fb9d89');line(drone,(4,48,22,48),'#fee0ae',3);line(drone,(60,48,78,48),'#fee0ae',3);glow(drone,(23,81,59,81),'#fe8c9e',4)
# gap uses same 180x180 pivot adjusted independently later
pit=canvas(180,180);box(pit,(0,125,180,180),'#0b1326');poly(pit,[(0,125),(180,125),(154,180),(25,180)],'#080f20');line(pit,(0,125,0,175),'#ffb36f',5);line(pit,(179,125,179,175),'#ffb36f',5)
for x in range(15,180,28):poly(pit,[(x,125),(x+12,125),(x+4,136),(x-8,136)],'#ffb36f')
# pad all costumes to common canvas 180x180, feet baseline=125
obs=[]
for im in [crate,tower,drone]:
 p=canvas(180,180);p.alpha_composite(im,(49*S,-15*S));obs.append(p)
obs.append(pit)
for i in range(4):
 add(f'Obstacle{i}',obs,f'''onMsg "render", => {{
    if ObActive[{i}] && Mode != 0 {{
        show
        setXYpos ObX[{i}]*0.5, -70
        setCostume ObKind[{i}]
    }} else {{ hide }}
}}''',visible=False,pivot=(90,125))
# Coins --------------------------------------------------------------------
coin=canvas(30,30);ellipse(coin,(2,2,28,28),'#c8804e',outline='#ffe0a1',width=2);ellipse(coin,(7,6,23,23),'#f8bd69');poly(coin,[(15,8),(21,15),(15,22),(9,15)],'#fff0af');line(coin,(6,7,11,4),'#fff4c9',2)
for i in range(24):
 add(f'Coin{i:02}',coin,f'''onMsg "render", => {{
    if CoinActive[{i}] && Mode != 0 {{
        show
        setXYpos CoinX[{i}]*0.5, (CoinY[{i}]-140)*0.5
    }} else {{ hide }}
}}''',visible=False)
# Powerups -----------------------------------------------------------------
powers=[]
for kind in range(2):
 im=canvas(52,58);ellipse(im,(2,3,50,51),'#203e56',outline=MINT if kind==0 else '#c4a7fb',width=2)
 if kind==0:
  poly(im,[(26,12),(39,18),(36,33),(26,42),(16,33),(13,18)],MINT);line(im,(20,26,25,31,34,21),'#224556',3)
 else:
  draw(im).arc((13*S,12*S,39*S,40*S),0,180,fill='#d1b8ff',width=8*S);box(im,(13,13,20,27),'#d1b8ff',2);box(im,(32,13,39,27),'#d1b8ff',2);box(im,(13,13,20,19),WHITE);box(im,(32,13,39,19),WHITE)
 powers.append(im)
add('Power',powers,'''onMsg "render", => {
    if PowerActive && Mode != 0 { show; setXYpos PowerX*0.5, (PowerY-140)*0.5; setCostume PowerKind } else { hide }
}''',visible=False)
# Player: original little space courier with scarf and glass helmet ----------
def runner(frame):
 im=canvas(92,106)
 slide=frame==7
 if slide:
  ellipse(im,(9,84,84,103),(55,220,199,35));box(im,(25,71,70,91),'#d7e3e7',9);box(im,(10,84,48,94),'#ffb36f',4);box(im,(47,87,82,96),'#75ead1',4)
  ellipse(im,(55,51,88,84),'#daeefa',outline=MINT,width=2);ellipse(im,(60,55,85,77),'#253e5a');line(im,(67,60,78,60),WHITE,2);poly(im,[(51,66),(25,67),(10,56),(40,61)],'#ee8e9f')
  return im
 phase=frame%6;lift=math.sin(phase*math.pi/3)*3 if frame<6 else 0
 # exhaust trail and scarf
 poly(im,[(31,48+lift),(5,38+lift),(12,52+lift),(2,60+lift),(33,57+lift)],'#e58b9f')
 # legs alternate for running
 swing=math.sin(phase*math.pi/3)*12 if frame<6 else 11
 line(im,(43,75,35+swing,94),'#93bacb',10);line(im,(52,75,62-swing,94),'#e5edf0',10)
 box(im,(25+swing,91,43+swing,100),'#ffb36f',4);box(im,(55-swing,91,74-swing,100),MINT,4)
 box(im,(31,49+lift,62,81+lift),'#d7e3e7',12);box(im,(37,56+lift,56,70+lift),'#305469',5);ellipse(im,(43,59+lift,50,65+lift),MINT)
 # arms and backpack
 box(im,(24,55+lift,34,75+lift),'#6c809c',4);line(im,(58,59+lift,70,70+lift),'#e9f0ee',9);ellipse(im,(67,66+lift,76,75+lift),ORANGE)
 # fox ears tucked behind helmet
 poly(im,[(34,27+lift),(33,5+lift),(47,22+lift)],ORANGE);poly(im,[(56,21+lift),(68,7+lift),(67,31+lift)],ORANGE)
 ellipse(im,(28,17+lift,77,57+lift),'#c6ecee',outline='#85f3e0',width=2)
 ellipse(im,(34,22+lift,72,51+lift),'#28415c');poly(im,[(40,30+lift),(51,23+lift),(65,31+lift),(66,43+lift),(51,48+lift),(39,41+lift)],'#ffb36f')
 ellipse(im,(57,32+lift,61,36+lift),'#17273c');poly(im,[(64,39+lift),(70,40+lift),(65,43+lift)],'#17273c');line(im,(37,25+lift,49,22+lift),'#f4ffff',2)
 return im
frames=[runner(i) for i in range(8)]
# shadow sits below runner, visible unless in menu
shadow=canvas(86,18);ellipse(shadow,(1,1,85,17),(4,12,27,125));add('Shadow',shadow,'''onMsg "render", => { if Mode != 0 { show } else { hide } }''',x=-280,y=-145,visible=False)
add('Runner',frames,'''onMsg "render", => {
    if Mode != 0 {
        if Invincible > 0 && int(Clock*14)%2 == 0 && Mode == 1 { hide } else { show }
        setXYpos -140, (-140+Height)*0.5
        if SlideTime > 0 { setCostume 7 } else if Height > 3 { setCostume 6 } else { setCostume int(Clock*12)%6 }
    } else { hide }
}''',x=-280,y=-140,visible=False,pivot=(46,100))
aura=canvas(112,122);ellipse(aura,(7,6,105,117),None,MINT,2);ellipse(aura,(12,11,100,112),None,(116,247,213,65),4)
add('Aura',aura,'''onMsg "render", => {
    if ShieldTime > 0 && Mode != 0 { show; setXYpos -140, (-90+Height)*0.5 } else { hide }
}''',visible=False)
# HUD, custom digit atlases -------------------------------------------------
hud=canvas(960,100);box(hud,(22,16,938,89),(12,23,44,230),18,outline='#3b4d64')
text(hud,(42,30),'STAR / RUNNER',11,MINT,True);text(hud,(42,51),'星轨疾跑',21,WHITE)
line(hud,(204,32,204,72),'#36475f');text(hud,(227,27),'SCORE  /  得分',10,MUTED);text(hud,(426,27),'DISTANCE  /  米',10,MUTED);text(hud,(610,27),'COINS  /  金币',10,MUTED)
text(hud,(760,27),'ENERGY',10,MUTED)
add('Hud',hud,x=0,y=220)
digits=[]
for i in range(10):
 im=canvas(20,30);text(im,(10,15),str(i),26,WHITE,True,'mm');digits.append(im)
def digitgroup(prefix,expr,count,x,y,visible='Mode != 0'):
 for j in range(count):
  div=10**(count-1-j)
  add(f'{prefix}{j}',digits,f'''onMsg "render", => {{
    if {visible} {{ show; setCostume (({expr})/{div})%10 }} else {{ hide }}
}}''',x=x+j*20,y=y,visible=False)
digitgroup('ScoreDigit','Score',6,-243,205)
digitgroup('DistanceDigit','int(Distance)',5,-44,205)
digitgroup('CoinDigit','Coins',3,140,205)
hearts=[]
for n in range(4):
 im=canvas(100,30)
 for i in range(3):
  x=i*31+2;c='#fa9ca6' if i<n else '#39465e';poly(im,[(x,9),(x+5,4),(x+11,7),(x+17,4),(x+23,9),(x+22,16),(x+11,26),(x+1,16)],c)
 hearts.append(im)
add('Life',hearts,'''onMsg "render", => { setCostume Lives }''',x=330,y=205)
# status indicators with timer digits
for name,title,col,x,cond,expr in [('ShieldStatus','护盾',MINT,254,'ShieldTime > 0','int(ShieldTime)+1'),('MagnetStatus','磁力','#c5adfa',378,'MagnetTime > 0','int(MagnetTime)+1')]:
 im=canvas(112,36);box(im,(0,0,112,36),'#1a3548',12,outline=col);text(im,(13,18),title,15,col,anchor='lm');text(im,(98,18),'s',12,col,anchor='mm')
 add(name,im,f'''onMsg "render", => {{ if {cond} && Mode != 0 {{ show }} else {{ hide }} }}''',x=x,y=132,visible=False)
 digitgroup(name+'Digit',expr,2,x+9,132,f'{cond} && Mode != 0')
# Bottom controls -----------------------------------------------------------
footer=canvas(960,110);text(footer,(34,57),'07',30,'#506b81',True);text(footer,(92,46),'ORBITAL EXPRESS',10,MUTED,True);text(footer,(92,65),'跃过边界，奔向下一颗星。',12,MUTED)
text(footer,(479,82),'SPACE / ↑ 二段跳     ↓ 下滑     P 暂停     M 静音',11,'#778da4',anchor='mm')
add('Footer',footer,x=0,y=-215)
def button(w,h,title,subtitle='',accent=False):
 im=canvas(w,h);box(im,(1,1,w-1,h-1),MINT if accent else '#1c3048',14,outline='#b2ffe7' if accent else '#49627a')
 text(im,(w/2,h/2-(8 if subtitle else 0)),title,20 if accent else 17,'#133c40' if accent else WHITE,False,'mm')
 if subtitle:text(im,(w/2,h/2+17),subtitle,10,'#376258' if accent else MUTED,True,'mm')
 return im
add('JumpButton',button(120,70,'跳跃 ↑','SPACE · 连按二段跳',True),'''onClick => { JumpAction() }
onMsg "render", => { if Mode == 1 { show } else { hide } }''',x=370,y=-206,visible=False)
add('SlideButton',button(110,70,'下滑 ↓','DOWN · 躲避飞行器'),'''onClick => { SlideAction() }
onMsg "render", => { if Mode == 1 { show } else { hide } }''',x=240,y=-206,visible=False)
add('PauseButton',button(56,45,'Ⅱ'),'''onClick => { PauseAction() }
onMsg "render", => { if Mode == 1 { show } else { hide } }''',x=424,y=125,visible=False)
mutes=[button(86,32,t) for t in ['声音 ON','声音 OFF']]
add('SoundButton',mutes,'''onClick => { SoundOn = !SoundOn }
onMsg "render", => { if SoundOn { setCostume 0 } else { setCostume 1 } }''',x=-399,y=125)
# Full-screen overlays ------------------------------------------------------
menu=canvas(960,540);box(menu,(0,0,960,540),(8,16,33,180));box(menu,(112,106,848,423),'#15243c',26,outline='#52647b')
pill(menu,(148,127,150),'原创 · 横版无尽跑酷')
text(menu,(147,171),'星轨疾跑',58,WHITE);text(menu,(151,249),'STAR RAIL / RUNNER',18,MINT,True)
text(menu,(152,286),'穿越霓虹星港，收集沿途的每一道光。',17,'#bdc9dc')
text(menu,(152,310),'二段跳越过高墙 · 下滑躲避飞行器 · 留心断桥',14,MUTED)
# character hero larger
hero=frames[0].resize((184*S,212*S),Image.Resampling.LANCZOS);menu.alpha_composite(hero,(625*S,151*S))
line(menu,(609,372,804,372),MINT,3);text(menu,(151,393),'3 格能量   /   护盾与磁力道具   /   难度逐渐提升',12,MUTED)
add('MenuPanel',menu,'''onMsg "render", => { if Mode == 0 { show } else { hide } }''')
add('StartButton',button(212,48,'即刻出发  →','',True),'''onClick => { if Mode == 0 { StartRun() } }
onMsg "render", => { if Mode == 0 { show } else { hide } }''',x=-223,y=-88)
text(menu,(377,360),'ENTER 开始',12,MUTED) # final menu saved again with hint
save(menu,AS/'sprites'/'MenuPanel'/'0.png')
pause=canvas(960,540);box(pause,(0,0,960,540),(8,16,33,200));box(pause,(245,145,715,386),'#15243c',24,outline='#52647b');text(pause,(480,187),'航程暂停',34,WHITE,anchor='mm');text(pause,(480,235),'休息一下，星光会等你。',16,MUTED,anchor='mm');text(pause,(480,353),'P / ESC / ENTER 继续航程',12,MUTED,anchor='mm')
add('PausePanel',pause,'''onMsg "render", => { if Mode == 2 { show } else { hide } }''',visible=False)
add('ResumeButton',button(220,52,'继续奔跑  →','',True),'''onClick => { if Mode == 2 { PauseAction() } }
onMsg "render", => { if Mode == 2 { show } else { hide } }''',x=0,y=-17,visible=False)
end=canvas(960,540);box(end,(0,0,960,540),(8,16,33,207));box(end,(208,110,752,428),'#15243c',24,outline='#52647b');pill(end,(393,127,174),'MISSION COMPLETE')
text(end,(480,188),'每一次出发，都会更远',28,WHITE,anchor='mm');text(end,(480,225),'本次得分',13,MUTED,anchor='mm');line(end,(260,288,700,288),'#33485f');text(end,(300,311),'本次最远 / 米',12,MUTED,anchor='mm');text(end,(480,311),'收集金币',12,MUTED,anchor='mm');text(end,(660,311),'本次会话最佳',12,MUTED,anchor='mm')
add('EndPanel',end,'''onMsg "render", => { if Mode == 3 { show } else { hide } }''',visible=False)
digitgroup('EndScore','Score',6,-50,16,'Mode == 3');digitgroup('EndDist','int(Distance)',5,-220,-72,'Mode == 3');digitgroup('EndCoin','Coins',3,-20,-72,'Mode == 3');digitgroup('EndBest','Best',6,130,-72,'Mode == 3')
add('RetryButton',button(220,48,'再跑一次  ↻','',True),'''onClick => { if Mode == 3 { StartRun() } }
onMsg "render", => { if Mode == 3 { show } else { hide } }''',x=0,y=-125,visible=False)
# Sounds: synthesized, original sine envelopes -------------------------------
for name,notes in {'jump':[(520,.05),(780,.08)],'coin':[(1050,.035),(1450,.065)],'hit':[(190,.09),(100,.1)],'over':[(420,.12),(310,.12),(210,.2)],'power':[(660,.08),(880,.08),(1320,.13)]}.items():
 base=AS/'sounds'/name;base.mkdir(parents=True,exist_ok=True);samples=[]
 for freq,dur in notes:
  n=int(22050*dur)
  for i in range(n):
   env=min(1,i/120)*(1-i/n)**1.8
   samples.append(int(6500*math.sin(2*math.pi*freq*i/22050)*env))
 with wave.open(str(base/f'{name}.wav'),'w') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
 (base/'index.json').write_text(json.dumps(dict(name=name,path=f'{name}.wav',rate=22050,sampleCount=len(samples))))
# Config + metadata ---------------------------------------------------------
config=dict(backdrops=[dict(name='轨道星港',path='backdrops/orbit.png',bitmapResolution=2,x=480,y=360,imageWidth=960,imageHeight=720)],backdropIndex=0,map=dict(width=480,height=360,mode='actualSize'),run=dict(width=480,height=360),physics=False,maxFPS=60,zorder=sprites,camera=dict(on=''),audioAttenuation=-1)
(AS/'index.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))
meta=dict(type='game',displayName='星轨疾跑 · Star Rail Runner',description='原创横版无尽跑酷。二段跳、下滑、断桥、金币、护盾与磁力道具；键盘和画面按钮均可操作。',instructions='Enter 开始/重开；Space / ↑ / W 跳跃，空中再按二段跳；↓ / S 下滑，空中按可快速落地；P / Esc 暂停；M 静音。也可点击画面按钮。3 格生命，护盾及磁力持续 9 秒，速度随时间提高。最高分保留于本次运行会话。')
(ROOT/'builder-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
# Thumbnail / review image (draws the actual generated menu assets)
preview=bg.copy();preview.alpha_composite(menu);preview.alpha_composite(button(212,48,'即刻出发  →','',True),(151*S,334*S));native_preview=backdrop.copy();native_preview.alpha_composite(preview,(0,90*S));save(native_preview,ROOT/'builder-thumbnail.png');save(native_preview,OUT/'preview.png')
# Gameplay composition for visual review
play=bg.copy();play.alpha_composite(city,(0,245*S));play.alpha_composite(track,(0,410*S));play.alpha_composite(hud,(0,0));play.alpha_composite(frames[2],(154*S,310*S));play.alpha_composite(crate,(620*S,272*S));play.alpha_composite(drone,(822*S,272*S))
for xx in range(370,620,55):play.alpha_composite(coin,(xx*S,340*S))
play.alpha_composite(footer,(0,430*S));play.alpha_composite(button(120,70,'跳跃 ↑','SPACE · 连按二段跳',True),(790*S,441*S));play.alpha_composite(button(110,70,'下滑 ↓','DOWN · 躲避飞行器'),(665*S,441*S))
text(play,(237,65),'001280',26,WHITE,True,'lm');text(play,(436,65),'00058',26,WHITE,True,'lm');text(play,(620,65),'014',26,WHITE,True,'lm');play.alpha_composite(hearts[3],(760*S,50*S));native_play=backdrop.copy();native_play.alpha_composite(play,(0,90*S));save(native_play,OUT/'gameplay.png')
# Reproducible ZIP: .xbp has no enclosing source/ folder.
xbp=OUT/'StarRailRunner.xbp'
with zipfile.ZipFile(xbp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and p.suffix in ['.spx','.json','.png','.wav']:
   z.write(p,p.relative_to(ROOT).as_posix())
print(f'Generated {len(sprites)} sprites, 5 sounds; {xbp} ({xbp.stat().st_size:,} bytes)')
