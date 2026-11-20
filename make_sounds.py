# -*- coding: utf-8 -*-
"""
카카오톡 OX 퀴즈 효과음 3종 생성기 (실제 16-bit PCM WAV)

  correct.wav : 맑은 '딩동댕' 3음 상승 벨  (G5 → B5 → D6)
  wrong.wav   : 부드러운 '땡' 2음 하강      (F4 → C4)
  finish.wav  : 결과 화면 마무리 화음        (C5-E5-G5 → C6)

- 표준 라이브러리(wave, math, array)만 사용. 외부 패키지 불필요.
- 모노 / 16,000 Hz / 16-bit PCM, 피크 진폭 0.70~0.74 (충분히 크고 찌그러지지 않음)
- 날카롭지 않도록 어택을 8~22ms로 두고 지수 감쇠, 끝은 6ms 페이드아웃(클릭 방지)
- 사용법: python3 make_sounds.py   → 같은 폴더에 correct.wav, wrong.wav, finish.wav
"""
import math
import os
import wave
from array import array

SR = 16000          # 샘플레이트
PEAK = 0.72         # 최종 정규화 피크
HERE = os.path.dirname(os.path.abspath(__file__))


def silence(sec):
    return [0.0] * int(SR * sec)


def bell(buf, freq, at, dur, amp, attack=0.008, tau=0.26, partials=((1.0, 1.0), (2.0, 0.18), (3.0, 0.06))):
    """종소리 한 음: 사인파 + 옅은 배음, 어택 후 지수 감쇠."""
    start = int(SR * at)
    n = int(SR * dur)
    a = max(1, int(SR * attack))
    for i in range(n):
        if start + i >= len(buf):
            break
        t = i / SR
        env = (i / a) if i < a else math.exp(-(t - attack) / tau)      # 리니어 어택 → 지수 감쇠
        env *= 1.0 - (i / n) ** 6                                       # 꼬리 페이드
        v = 0.0
        for mult, pamp in partials:
            f = freq * mult
            if f >= SR / 2:                                            # 나이퀴스트 위는 생략
                continue
            v += pamp * math.sin(2 * math.pi * f * t) * math.exp(-t / (tau * 0.75))
        buf[start + i] += amp * env * v


def warm(buf, freq, at, dur, amp, attack=0.020, tau=0.22):
    """둥근 저음: 사인 + 낮은 2·3배음, 느린 어택(날카롭지 않게)."""
    start = int(SR * at)
    n = int(SR * dur)
    a = max(1, int(SR * attack))
    for i in range(n):
        if start + i >= len(buf):
            break
        t = i / SR
        env = (i / a) if i < a else math.exp(-(t - attack) / tau)
        env *= 1.0 - (i / n) ** 6
        v = (1.00 * math.sin(2 * math.pi * freq * t)
             + 0.16 * math.sin(2 * math.pi * freq * 2 * t)
             + 0.05 * math.sin(2 * math.pi * freq * 3 * t))
        buf[start + i] += amp * env * v


def normalize(buf, peak=PEAK, fade_out=0.006):
    m = max(abs(v) for v in buf) or 1.0
    g = peak / m
    out = [v * g for v in buf]
    n = min(len(out), max(1, int(SR * fade_out)))
    for i in range(n):                                                  # 끝 페이드아웃
        out[len(out) - n + i] *= (n - i) / n
    return out


def write_wav(name, buf):
    data = array('h')
    for v in buf:
        s = int(round(max(-1.0, min(1.0, v)) * 32767))
        data.append(s)
    path = os.path.join(HERE, name)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    dur = len(buf) / SR
    print('%-12s %5.2fs  %6d bytes  peak %.2f' % (name, dur, os.path.getsize(path),
                                                  max(abs(v) for v in buf)))
    return path


# ── correct : 딩(G5) - 동(B5) - 댕(D6) ──────────────────────────────
c = silence(1.15)
bell(c, 783.99, 0.000, 0.55, 0.95)
bell(c, 987.77, 0.105, 0.60, 0.92)
bell(c, 1174.66, 0.210, 0.90, 0.90)
write_wav('correct.wav', normalize(c))

# ── wrong : 띠(F4) - 용(C4) ────────────────────────────────────────
w = silence(0.80)
warm(w, 349.23, 0.000, 0.34, 1.00)
warm(w, 261.63, 0.170, 0.60, 1.00)
write_wav('wrong.wav', normalize(w))

# ── finish : C-E-G 화음 → C6 마무리 ────────────────────────────────
f = silence(1.55)
bell(f, 523.25, 0.000, 0.75, 0.72, tau=0.34)
bell(f, 659.25, 0.018, 0.75, 0.68, tau=0.34)
bell(f, 783.99, 0.036, 0.78, 0.66, tau=0.34)
bell(f, 1046.50, 0.300, 1.20, 0.95, tau=0.30)
write_wav('finish.wav', normalize(f))
