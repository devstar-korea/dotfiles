#!/usr/bin/env python3
"""
타임코드 리스트를 SRT 자막 파일로 변환
캡컷에 불러와서 정확한 위치 확인 가능
"""

import argparse
import re
import sys
from pathlib import Path


def timecode_to_srt(hours, minutes, seconds, frames, fps=25.0):
    """타임코드를 SRT 형식으로 변환 (HH:MM:SS,mmm)"""
    milliseconds = int((frames / fps) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def parse_timecode(tc_string, fps=25.0):
    """타임코드 파싱 (HH:MM:SS:FF)"""
    parts = re.split(r'[:;]', tc_string)
    if len(parts) != 4:
        return None

    try:
        hours, minutes, seconds, frames = map(int, parts)
        return timecode_to_srt(hours, minutes, seconds, frames, fps)
    except:
        return None


def convert_script_to_srt(input_file, output_file, fps=25.0, duration=3.0):
    """대본 파일을 SRT 자막으로 변환"""

    print(f"📄 대본을 SRT 자막으로 변환 중...")
    print(f"입력: {input_file}")
    print(f"출력: {output_file}")
    print(f"FPS: {fps}")
    print(f"자막 표시 시간: {duration}초")
    print()

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        subtitles = []
        tc_pattern = r'\b(\d{2}):(\d{2}):(\d{2})[:;](\d{2})\b'

        for line in lines:
            line = line.strip()

            # 빈 줄이나 주석은 건너뛰기
            if not line or line.startswith('#'):
                continue

            # 타임코드 찾기
            match = re.search(tc_pattern, line)
            if not match:
                continue

            tc_str = match.group(0)

            # 타임코드를 제외한 나머지를 자막 텍스트로 사용
            text = re.sub(tc_pattern, '', line).strip()
            # 앞뒤 구분자 제거
            text = text.lstrip('-').lstrip(':').strip()

            if not text:
                text = f"[{tc_str}]"

            # 시작 시간
            start_srt = parse_timecode(tc_str, fps)
            if not start_srt:
                continue

            # 종료 시간 계산 (duration초 후)
            hours, minutes, seconds, frames = map(int, re.split(r'[:;]', tc_str))
            total_seconds = hours * 3600 + minutes * 60 + seconds + frames / fps
            end_seconds = total_seconds + duration

            end_hours = int(end_seconds // 3600)
            end_minutes = int((end_seconds % 3600) // 60)
            end_secs = int(end_seconds % 60)
            end_ms = int((end_seconds % 1) * 1000)

            end_srt = f"{end_hours:02d}:{end_minutes:02d}:{end_secs:02d},{end_ms:03d}"

            subtitles.append({
                'start': start_srt,
                'end': end_srt,
                'text': text
            })

        # SRT 파일 작성
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                f.write(f"{i}\n")
                f.write(f"{sub['start']} --> {sub['end']}\n")
                f.write(f"{sub['text']}\n")
                f.write("\n")

        print(f"✅ 변환 완료!")
        print(f"   {len(subtitles)}개의 자막 생성됨")
        print(f"   저장됨: {output_file}")
        print()
        print("📺 캡컷에서 사용 방법:")
        print("   1. 캡컷 프로젝트 열기")
        print("   2. '텍스트' → '자막' → '파일 불러오기'")
        print(f"   3. {output_file} 선택")
        print("   4. 자막이 나타나는 위치가 정확한 타임코드!")

    except Exception as e:
        print(f"❌ 오류: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='타임코드 리스트를 SRT 자막 파일로 변환 (캡컷용)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 기본 변환 (각 자막 3초 표시)
  %(prog)s script.txt -o markers.srt

  # 자막 표시 시간 조절
  %(prog)s script.txt -o markers.srt --duration 5.0

  # FPS 지정
  %(prog)s script.txt -o markers.srt --fps 29.97

캡컷에서 사용:
  1. 캡컷 프로젝트 열기
  2. '텍스트' → '자막' → '파일 불러오기' 클릭
  3. 생성된 SRT 파일 선택
  4. 자막이 나타나는 위치 = 정확한 타임코드!
        """
    )

    parser.add_argument('input', help='입력 대본 파일')
    parser.add_argument('-o', '--output', required=True, help='출력 SRT 파일')
    parser.add_argument('--fps', type=float, default=25.0, help='FPS (기본값: 25)')
    parser.add_argument('--duration', type=float, default=3.0,
                       help='각 자막 표시 시간 (초, 기본값: 3.0)')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {args.input}")
        sys.exit(1)

    convert_script_to_srt(args.input, args.output, args.fps, args.duration)


if __name__ == '__main__':
    main()
