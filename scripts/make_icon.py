"""Draw the app's geometric waveform mark; no generated artwork dependency."""
from pathlib import Path
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
target=root/'src-tauri'/'icons'
target.mkdir(exist_ok=True)
im=Image.new('RGBA',(512,512),(12,24,31,255))
draw=ImageDraw.Draw(im)
draw.rounded_rectangle((38,38,474,474),radius=110,fill=(20,43,48))
draw.line([(105,266),(167,266),(208,150),(258,363),(304,218),(342,266),(407,266)],
          fill=(115,231,204),width=29,joint='curve')
im.save(target/'icon.png')
im.save(target/'icon.ico',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
for size in [32,128]:
    im.resize((size,size),Image.Resampling.LANCZOS).save(target/f'{size}x{size}.png')
im.resize((256,256),Image.Resampling.LANCZOS).save(target/'128x128@2x.png')
