#!/usr/bin/env python3
"""Test the exact pure gameplay methods from main.spx using Go's test runner.
No duplicate game implementation is used. Requires Go 1.22+.
"""
from pathlib import Path
import argparse, subprocess, tempfile, shutil
p=argparse.ArgumentParser();p.add_argument('--go',default=shutil.which('go') or 'go');args=p.parse_args()
root=Path(__file__).resolve().parents[1]
s=(root/'main.spx').read_text().split('// 所有输入')[0]
with tempfile.TemporaryDirectory(prefix='starrail-test-') as tmp:
 d=Path(tmp);(d/'go.mod').write_text('module starrailtest\n\ngo 1.22\n');(d/'core.go').write_text('package main\n'+s);shutil.copy(Path(__file__).with_name('core_test.go'),d/'core_test.go')
 result=subprocess.run([args.go,'test','-v','-count=1','.'],cwd=d)
 raise SystemExit(result.returncode)
