#!/usr/bin/env python3
"""Package existing XBuilder project files without regenerating any source/art."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
output=root.parent/'StarRailRunner.xbp'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in ['builder-meta.json','builder-thumbnail.png']:
  p=root/name
  if p.exists():z.write(p,name)
 for p in sorted(root.glob('*.spx')):z.write(p,p.name)
 for p in sorted((root/'assets').rglob('*')):
  if p.is_file():z.write(p,p.relative_to(root).as_posix())
print(output)
