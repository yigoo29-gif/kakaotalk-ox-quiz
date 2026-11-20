#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
index.html 안의 효과음 data URI를 실제 WAV 파일 내용으로 채워 넣는다.
  python3 make_sounds.py && python3 inline_sounds.py
- correct.wav / wrong.wav / finish.wav 를 base64로 바꿔
  `correct: "data:audio/wav;base64,..."` 세 줄을 갱신한다(여러 번 실행해도 안전).
"""
import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(HERE, 'index.html')

with open(html_path, encoding='utf-8') as f:
    html = f.read()

for name in ('correct', 'wrong', 'finish'):
    with open(os.path.join(HERE, name + '.wav'), 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    pattern = re.compile(r'(%s:\s*"data:audio/wav;base64,)[^"]*(")' % name)
    html, n = pattern.subn(lambda m: m.group(1) + b64 + m.group(2), html)
    print('%-8s %6d bytes wav → %6d bytes base64  (replaced %d)' % (name, os.path.getsize(os.path.join(HERE, name + '.wav')), len(b64), n))

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('index.html %d bytes' % os.path.getsize(html_path))
