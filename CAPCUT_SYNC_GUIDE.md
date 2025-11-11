# 캡컷 타임코드 동기화 가이드

캡컷에서 타임코드 싱크가 안 맞는 문제를 해결하는 방법을 설명합니다.

## 문제 증상

- 25 FPS CFR 영상을 캡컷에 불러옴
- 캡컷 프로젝트도 25 FPS로 설정
- 대본의 타임코드로 컷하면 실제 내용과 싱크가 안 맞음

## 주요 원인

### 1. 시작 타임코드 오프셋
- 비디오 파일이 00:00:00:00이 아닌 다른 타임코드에서 시작
- 예: 01:00:00:00부터 시작하는 경우

### 2. 프레임 카운팅 차이
- 일부 소프트웨어는 프레임을 0부터 카운팅
- 다른 소프트웨어는 1부터 카운팅
- 1 프레임 차이 발생 가능

### 3. 타임코드 메타데이터 불일치
- 실제 FPS와 파일 메타데이터의 FPS가 다를 수 있음
- 예: 실제는 25 FPS인데 메타데이터는 24 FPS

### 4. 오디오 싱크 오프셋
- 비디오와 오디오가 살짝 어긋난 경우
- 보통 몇 프레임~몇 초 차이

## 사용 방법

### 설치

먼저 Python 3가 설치되어 있어야 합니다. FFmpeg도 설치하면 더 많은 기능을 사용할 수 있습니다:

```bash
# Ubuntu/Debian
sudo apt-get install python3 ffmpeg

# macOS
brew install python3 ffmpeg

# Windows (Chocolatey)
choco install python ffmpeg
```

### 1. 비디오 파일 분석

먼저 비디오 파일의 실제 정보를 확인합니다:

```bash
./capcut_timecode_sync.py --analyze video.mp4
```

출력 예시:
```
📹 비디오 분석: video.mp4
======================================================================
FPS: 25.000
해상도: 1920x1080
코덱: h264
길이: 3600.000초
시작 시간: 0.000초
총 프레임: 90000
시작 타임코드: 없음 (00:00:00:00으로 가정)
프레임당 시간: 40.000ms
```

### 2. 대화형 진단 모드

문제를 진단하려면:

```bash
./capcut_timecode_sync.py --interactive --video video.mp4
```

스크립트가 질문을 하면서 문제를 진단하고 해결 방법을 제안합니다.

### 3. 타임코드 리스트 변환

대본 파일의 타임코드를 오프셋을 적용하여 변환:

#### 초 단위 오프셋

```bash
# 3초 늦추기 (대본보다 3초 뒤에 나타남)
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 3.0

# 2.5초 앞당기기 (대본보다 2.5초 먼저 나타남)
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds -2.5
```

#### 프레임 단위 오프셋

```bash
# 5 프레임 늦추기
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --fps 25 --offset-frames 5

# 3 프레임 앞당기기
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --fps 25 --offset-frames -3
```

#### 복합 오프셋

```bash
# 3초 늦추고 5 프레임 앞당기기
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 3.0 --offset-frames -5
```

### 4. 단일 타임코드 변환

특정 타임코드를 빠르게 변환:

```bash
# 기본 변환
./capcut_timecode_sync.py --timecode 00:01:23:15 --fps 25

# 오프셋 적용
./capcut_timecode_sync.py --timecode 00:01:23:15 --fps 25 --offset-seconds 2.5
```

출력:
```
타임코드 변환 결과 (FPS: 25.0):
  타임코드: 00:01:26:02
  초: 86.080s
  프레임: 2152
  밀리초: 86080ms
  SRT 형식: 00:01:26,080
```

## 실전 해결 사례

### 사례 1: 일정한 오프셋

**증상**: 모든 타임코드가 2초씩 늦게 나타남

**해결**:
```bash
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds -2.0
```

### 사례 2: 시작 타임코드가 있는 영상

**증상**: 영상이 01:00:00:00에서 시작하지만 캡컷은 00:00:00:00부터 표시

**해결**:
```bash
# 비디오 분석으로 시작 타임코드 확인
./capcut_timecode_sync.py --analyze video.mp4

# 1시간(3600초) 오프셋 적용
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds -3600
```

### 사례 3: 프레임 하나 차이

**증상**: 타임코드가 정확히 1 프레임씩 어긋남

**해결**:
```bash
# 1 프레임 앞당기기
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --fps 25 --offset-frames -1
```

### 사례 4: FPS가 다른 경우

**증상**: 시간이 지날수록 싱크가 점점 더 안 맞음 (드리프트 현상)

**원인**: 실제 FPS와 설정한 FPS가 다름

**해결**:
```bash
# 먼저 실제 FPS 확인
./capcut_timecode_sync.py --analyze video.mp4

# 정확한 FPS로 변환
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --fps 25.000
# 또는
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --fps 23.976
```

## 대본 파일 형식

스크립트는 다양한 형식의 타임코드를 자동으로 인식합니다:

```
# 주석은 무시됩니다

# 표준 형식 (콜론)
00:00:10:00 - 첫 번째 장면
00:00:25:12 - 두 번째 장면
00:01:30:05 - 세 번째 장면

# 세미콜론 형식 (드롭 프레임 표기)
00:00:10;00 - 또 다른 장면
00:00:25;12 - 마지막 장면

# 일반 텍스트와 혼합
인터뷰 시작: 00:05:23:15
질문 1: 00:05:45:00 "당신의 이름은?"
답변: 00:05:47:10 "저는..."

# SRT 자막 형식
1
00:00:10:00 --> 00:00:15:00
자막 텍스트

2
00:00:15:05 --> 00:00:20:00
다음 자막
```

## 팁과 트릭

### 1. 오프셋 찾기

정확한 오프셋을 찾으려면:

1. 대본에서 쉽게 식별 가능한 시점의 타임코드를 찾습니다 (예: 강한 비트, 화면 전환)
2. 캡컷에서 실제 그 시점의 타임코드를 확인합니다
3. 두 타임코드의 차이를 계산합니다

예시:
- 대본: 00:01:23:15
- 실제: 00:01:25:20
- 차이: +2초 5프레임 = +2.2초

```bash
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 2.2
```

### 2. 여러 지점에서 확인

- 영상 시작 부분 (0~1분)
- 중간 부분 (전체 길이의 50%)
- 끝 부분 (마지막 1분)

세 지점에서 모두 오프셋이 같으면 → 고정 오프셋 문제
세 지점에서 오프셋이 점점 커지면 → FPS 불일치 문제

### 3. 백업 만들기

변환 전에 항상 원본을 백업하세요:

```bash
cp script.txt script_backup.txt
./capcut_timecode_sync.py --convert script.txt --output script_corrected.txt
```

### 4. 정밀한 오프셋 계산

두 타임코드의 정확한 차이를 계산:

```bash
# 대본 타임코드
./capcut_timecode_sync.py --timecode 00:01:23:15 --fps 25
# 출력: 초: 83.600s

# 실제 타임코드
./capcut_timecode_sync.py --timecode 00:01:25:20 --fps 25
# 출력: 초: 85.800s

# 차이 = 85.800 - 83.600 = 2.200초
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 2.2
```

## 25 FPS 관련 참고사항

- 25 FPS는 PAL 표준 (유럽, 호주, 중국 등)
- 1 프레임 = 정확히 40ms (0.04초)
- Non-drop frame 타임코드 사용
- 타임코드 형식: HH:MM:SS:FF (FF는 00~24)

다른 일반적인 FPS:
- 24 FPS: 영화 (1 프레임 = 41.667ms)
- 23.976 FPS: NTSC 영화 (드롭 프레임, 1 프레임 = 41.708ms)
- 29.97 FPS: NTSC 비디오 (드롭 프레임)
- 30 FPS: 웹 비디오 (1 프레임 = 33.333ms)
- 60 FPS: 게임, 고속 촬영 (1 프레임 = 16.667ms)

## 문제 해결

### FFmpeg 없음

```
⚠️ 경고: FFmpeg가 설치되어 있지 않습니다.
```

**해결**: FFmpeg를 설치하세요 (위 설치 섹션 참고)

없어도 타임코드 변환 기능은 사용 가능합니다.

### 타임코드 형식 오류

```
❌ 잘못된 타임코드 형식: 1:23:45. HH:MM:SS:FF 형식이어야 합니다.
```

**해결**: 타임코드를 `00:01:23:15` 형식으로 입력하세요 (HH:MM:SS:FF)

### 파일을 찾을 수 없음

```
❌ 파일을 찾을 수 없습니다: script.txt
```

**해결**: 파일 경로가 올바른지 확인하거나 절대 경로를 사용하세요

```bash
./capcut_timecode_sync.py --convert /full/path/to/script.txt --output corrected.txt
```

## 추가 도움

더 자세한 도움이 필요하면:

```bash
./capcut_timecode_sync.py --help
```

대화형 진단 도구를 사용하면 단계별로 문제를 진단할 수 있습니다:

```bash
./capcut_timecode_sync.py --interactive --video your_video.mp4
```
