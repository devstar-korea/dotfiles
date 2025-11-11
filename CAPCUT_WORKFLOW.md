# 캡컷 실전 편집 워크플로우

타임코드가 안 맞는 문제를 실제로 해결하고 캡컷에서 편집하는 방법을 단계별로 설명합니다.

## 시나리오

**상황:**
- 25 FPS 영상이 있음
- 대본에 타임코드가 적혀있음 (예: `00:01:23:15 - 중요 장면`)
- 캡컷에서 `00:01:23:15`로 가면 실제로는 다른 장면이 나옴
- 싱크가 맞지 않아 일일이 찾아야 함 😫

**목표:**
- 정확한 타임코드를 찾아서 빠르게 편집하기

---

## 방법 1: SRT 자막으로 마커 표시 (추천! ⭐)

캡컷은 SRT 자막 파일을 불러올 수 있습니다. 타임코드를 자막으로 변환하면 정확한 위치를 쉽게 확인할 수 있습니다.

### 1단계: 오프셋 찾기

먼저 얼마나 어긋났는지 확인합니다.

**방법 A: 대화형 진단 (간단)**
```bash
./capcut_timecode_sync.py --interactive --video video.mp4
```

스크립트가 질문하면서 오프셋을 찾아줍니다.

**방법 B: 수동으로 찾기**
1. 대본에서 쉽게 찾을 수 있는 장면의 타임코드 확인 (예: `00:01:00:00`)
2. 캡컷에서 그 장면 찾기 (예: 실제로는 `00:01:02:10`에 있음)
3. 차이 계산: `00:01:02:10 - 00:01:00:00 = 2.4초`

### 2단계: 타임코드 보정

```bash
# 오프셋을 적용하여 대본 변환
./capcut_timecode_sync.py --convert script.txt --output script_corrected.txt --offset-seconds 2.4

# 또는 프레임 단위로
./capcut_timecode_sync.py --convert script.txt --output script_corrected.txt --offset-frames 60
```

### 3단계: SRT 자막 생성

```bash
# 보정된 대본을 SRT 자막으로 변환
./convert_to_srt.py script_corrected.txt -o markers.srt

# 또는 한번에 (파이프 사용 없이 순차 실행)
./capcut_timecode_sync.py --convert script.txt --output script_corrected.txt --offset-seconds 2.4
./convert_to_srt.py script_corrected.txt -o markers.srt
```

### 4단계: 캡컷에서 자막 불러오기

1. **캡컷 프로젝트 열기**
2. **영상을 타임라인에 추가**
3. **자막 불러오기:**
   - 왼쪽 메뉴에서 **'텍스트'** 클릭
   - **'자막'** 선택
   - **'파일 불러오기'** 또는 **'SRT 불러오기'** 클릭
   - `markers.srt` 선택

4. **자막이 타임라인에 추가됨!**
   - 각 자막이 나타나는 위치 = 정확한 타임코드
   - 자막 텍스트 = 장면 설명

5. **편집하기:**
   - 자막을 참고하여 컷 편집
   - 필요없는 자막은 나중에 삭제

### 예시

**원본 대본 (script.txt):**
```
00:00:10:00 - 오프닝 시작
00:00:25:12 - 인터뷰 시작
00:01:30:05 - B-roll 시작
00:02:00:00 - 마무리
```

**캡컷에서 확인 결과:**
- 대본: `00:00:10:00` → 실제: `00:00:12:10` (2.4초 늦음)

**변환:**
```bash
# 1. 타임코드 보정 (2.4초 오프셋)
./capcut_timecode_sync.py --convert script.txt --output script_corrected.txt --offset-seconds 2.4

# 2. SRT 생성
./convert_to_srt.py script_corrected.txt -o markers.srt
```

**생성된 SRT (markers.srt):**
```
1
00:00:12:10 --> 00:00:15:10
오프닝 시작

2
00:00:27:22 --> 00:00:30:22
인터뷰 시작

3
00:01:32:17 --> 00:01:35:17
B-roll 시작

4
00:02:02:10 --> 00:02:05:10
마무리
```

**캡컷에서 사용:**
- 자막이 `00:00:12:10`에 나타남 = 여기가 정확한 오프닝 시작 지점!
- 해당 위치에서 컷 편집

---

## 방법 2: 보정된 타임코드로 수동 편집

SRT 자막을 사용하지 않고 직접 타임코드를 입력하는 방법입니다.

### 1단계: 타임코드 보정

```bash
./capcut_timecode_sync.py --convert script.txt --output script_corrected.txt --offset-seconds 2.4
```

### 2단계: 캡컷에서 타임코드로 이동

**캡컷은 `분:초.밀리초` 형식 사용!**

타임코드 변환:
```bash
# HH:MM:SS:FF를 캡컷 형식으로 변환
./capcut_timecode_sync.py --timecode 00:01:23:15 --fps 25

# 출력:
# 타임코드: 00:01:23:15
# 초: 83.600s
# 밀리초: 83600ms
# SRT 형식: 00:01:23,600
```

**캡컷에 입력:**
- 타임라인 상단의 시간 표시 클릭
- `01:23.600` 입력 (분:초.밀리초)
- 재생 헤드가 해당 위치로 이동
- `Ctrl+B` (Windows) 또는 `Cmd+B` (Mac)으로 컷

### 3단계: 반복

보정된 대본의 각 타임코드마다 위 과정 반복

---

## 방법 3: 빠른 오프셋 테스트

오프셋을 여러 번 시도해야 하는 경우:

### 1단계: 테스트 자막 생성

```bash
# 2초 오프셋 테스트
./capcut_timecode_sync.py --convert script.txt --output test1.txt --offset-seconds 2.0
./convert_to_srt.py test1.txt -o test1.srt

# 2.5초 오프셋 테스트
./capcut_timecode_sync.py --convert script.txt --output test2.txt --offset-seconds 2.5
./convert_to_srt.py test2.txt -o test2.srt

# 3초 오프셋 테스트
./capcut_timecode_sync.py --convert script.txt --output test3.txt --offset-seconds 3.0
./convert_to_srt.py test3.txt -o test3.srt
```

### 2단계: 캡컷에서 빠르게 확인

1. `test1.srt` 불러오기 → 확인 → 안 맞으면 삭제
2. `test2.srt` 불러오기 → 확인 → 안 맞으면 삭제
3. `test3.srt` 불러오기 → 확인 → 맞으면 사용!

---

## 실전 팁

### 1. 자막 스타일 변경

캡컷에서 자막을 더 눈에 띄게 만들기:
- 자막 선택
- 스타일: 큰 글씨, 밝은 색상 (빨강, 노랑)
- 위치: 화면 상단으로 이동
- 이렇게 하면 마커처럼 사용 가능

### 2. 자막 표시 시간 조절

```bash
# 자막을 5초 동안 표시 (기본값: 3초)
./convert_to_srt.py script_corrected.txt -o markers.srt --duration 5.0

# 짧게 1초만 표시
./convert_to_srt.py script_corrected.txt -o markers.srt --duration 1.0
```

### 3. 여러 지점에서 확인

오프셋이 일정한지 확인:
- 시작 부분 (0~1분)
- 중간 부분 (전체의 50%)
- 끝 부분 (마지막 1분)

**세 곳이 모두 같은 오프셋이면** → 고정 오프셋, 한 번만 보정하면 됨
**세 곳의 오프셋이 점점 커지면** → FPS 불일치, FPS 재확인 필요

```bash
# 실제 FPS 확인
./capcut_timecode_sync.py --analyze video.mp4
```

### 4. 오프셋 미세 조정

첫 시도에서 거의 맞지만 약간 어긋나는 경우:

```bash
# 0.1초 단위로 조정
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 2.4
# 약간 늦다면
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 2.3
# 약간 빠르다면
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 2.5

# 프레임 단위로 조정 (25 FPS = 1 프레임 = 0.04초)
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 2.4 --offset-frames -2
```

### 5. 배치 스크립트

자주 사용한다면 배치 스크립트 만들기:

**fix_and_convert.sh:**
```bash
#!/bin/bash

# 사용법: ./fix_and_convert.sh script.txt 2.4 output

SCRIPT=$1
OFFSET=$2
OUTPUT_NAME=$3

echo "타임코드 보정 중..."
./capcut_timecode_sync.py --convert "$SCRIPT" --output "${OUTPUT_NAME}_corrected.txt" --offset-seconds "$OFFSET"

echo "SRT 생성 중..."
./convert_to_srt.py "${OUTPUT_NAME}_corrected.txt" -o "${OUTPUT_NAME}_markers.srt"

echo "완료!"
echo "파일: ${OUTPUT_NAME}_markers.srt"
echo "캡컷에서 불러오세요!"
```

사용:
```bash
chmod +x fix_and_convert.sh
./fix_and_convert.sh script.txt 2.4 final
# 결과: final_corrected.txt, final_markers.srt
```

---

## 문제 해결

### Q: 캡컷에서 SRT 불러오기 메뉴가 안 보여요

**A:** 캡컷 버전에 따라 위치가 다릅니다:
- **PC 버전:** 텍스트 → 자막 → 파일 불러오기 / SRT 불러오기
- **모바일 버전:** 텍스트 → 자동 자막 → 파일에서 불러오기
- 또는 SRT 파일을 타임라인에 직접 드래그

### Q: 자막이 너무 많아서 불편해요

**A:** 주요 지점만 선택:
```bash
# 예시 대본에서 필요한 줄만 남기고 나머지 주석 처리
# 00:00:10:00 - 오프닝 (필요없음)
00:00:25:12 - 인터뷰 시작 (중요!)
# 00:00:45:00 - 중간 (필요없음)
00:01:30:05 - B-roll 시작 (중요!)
```

### Q: 여전히 싱크가 안 맞아요

**A:** 드리프트 현상 가능성:
1. 시작 부분은 맞는데 갈수록 어긋남
2. FPS가 실제와 다름
3. 비디오의 실제 FPS 재확인:

```bash
./capcut_timecode_sync.py --analyze video.mp4
# 출력에서 "FPS: 24.997" 같은 값 확인
# 정확한 FPS로 다시 변환
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --fps 24.997 --offset-seconds 2.4
```

### Q: 영상에 시작 타임코드가 있어요 (예: 01:00:00:00부터 시작)

**A:** 시작 타임코드를 빼야 합니다:
```bash
# 1시간(3600초) 빼기
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds -3600
```

---

## 요약

### 가장 빠르고 편한 방법 (추천)

```bash
# 1. 오프셋 찾기
./capcut_timecode_sync.py --interactive --video video.mp4

# 2. 타임코드 보정 + SRT 생성
./capcut_timecode_sync.py --convert script.txt --output script_corrected.txt --offset-seconds [찾은_오프셋]
./convert_to_srt.py script_corrected.txt -o markers.srt

# 3. 캡컷에서 markers.srt 불러오기
# 4. 자막 위치 = 정확한 타임코드!
# 5. 편집 완료 후 자막 삭제 (또는 유지)
```

### 장점

- ✅ 타임코드를 일일이 입력할 필요 없음
- ✅ 시각적으로 위치 확인 가능
- ✅ 빠르게 여러 지점 찾을 수 있음
- ✅ 실수 방지

이제 캡컷에서 타임코드 싱크 문제 없이 빠르게 편집하세요! 🎬✨
