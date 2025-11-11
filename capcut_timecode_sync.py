#!/usr/bin/env python3
"""
CapCut Timecode Synchronization Tool
캡컷 타임코드 동기화 도구

이 스크립트는 캡컷에서 타임코드 싱크 문제를 진단하고 해결합니다.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, List, Dict


class Timecode:
    """타임코드 처리 클래스 (HH:MM:SS:FF 형식)"""

    def __init__(self, hours: int = 0, minutes: int = 0, seconds: int = 0, frames: int = 0, fps: float = 25.0):
        self.fps = fps
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.frames = frames
        self._normalize()

    def _normalize(self):
        """프레임을 초, 분, 시간으로 변환하여 정규화"""
        frames_per_second = int(self.fps)

        if self.frames >= frames_per_second:
            extra_seconds = self.frames // frames_per_second
            self.frames = self.frames % frames_per_second
            self.seconds += extra_seconds

        if self.seconds >= 60:
            self.minutes += self.seconds // 60
            self.seconds = self.seconds % 60

        if self.minutes >= 60:
            self.hours += self.minutes // 60
            self.minutes = self.minutes % 60

    @classmethod
    def from_string(cls, tc_string: str, fps: float = 25.0) -> 'Timecode':
        """문자열에서 타임코드 생성 (HH:MM:SS:FF 또는 HH:MM:SS;FF)"""
        # 구분자를 : 또는 ;로 처리
        parts = re.split(r'[:;]', tc_string)
        if len(parts) != 4:
            raise ValueError(f"잘못된 타임코드 형식: {tc_string}. HH:MM:SS:FF 형식이어야 합니다.")

        hours, minutes, seconds, frames = map(int, parts)
        return cls(hours, minutes, seconds, frames, fps)

    @classmethod
    def from_seconds(cls, total_seconds: float, fps: float = 25.0) -> 'Timecode':
        """초 단위 시간을 타임코드로 변환"""
        hours = int(total_seconds // 3600)
        remaining = total_seconds % 3600
        minutes = int(remaining // 60)
        remaining = remaining % 60
        seconds = int(remaining)
        frames = int((remaining - seconds) * fps)

        return cls(hours, minutes, seconds, frames, fps)

    @classmethod
    def from_frames(cls, total_frames: int, fps: float = 25.0) -> 'Timecode':
        """총 프레임 수를 타임코드로 변환"""
        frames_per_second = int(fps)

        hours = total_frames // (frames_per_second * 3600)
        remaining = total_frames % (frames_per_second * 3600)

        minutes = remaining // (frames_per_second * 60)
        remaining = remaining % (frames_per_second * 60)

        seconds = remaining // frames_per_second
        frames = remaining % frames_per_second

        return cls(hours, minutes, seconds, frames, fps)

    def to_seconds(self) -> float:
        """타임코드를 초 단위로 변환"""
        total_seconds = (self.hours * 3600 +
                        self.minutes * 60 +
                        self.seconds +
                        self.frames / self.fps)
        return total_seconds

    def to_frames(self) -> int:
        """타임코드를 총 프레임 수로 변환"""
        frames_per_second = int(self.fps)
        total_frames = (self.hours * 3600 * frames_per_second +
                       self.minutes * 60 * frames_per_second +
                       self.seconds * frames_per_second +
                       self.frames)
        return total_frames

    def to_milliseconds(self) -> int:
        """타임코드를 밀리초로 변환"""
        return int(self.to_seconds() * 1000)

    def add_offset(self, offset_seconds: float) -> 'Timecode':
        """오프셋을 추가한 새 타임코드 반환"""
        new_seconds = self.to_seconds() + offset_seconds
        return Timecode.from_seconds(max(0, new_seconds), self.fps)

    def add_frames(self, frame_offset: int) -> 'Timecode':
        """프레임 오프셋을 추가한 새 타임코드 반환"""
        new_frames = self.to_frames() + frame_offset
        return Timecode.from_frames(max(0, new_frames), self.fps)

    def __str__(self) -> str:
        """타임코드를 HH:MM:SS:FF 형식으로 반환"""
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}:{self.frames:02d}"

    def to_srt_format(self) -> str:
        """SRT 자막 형식으로 변환 (HH:MM:SS,mmm)"""
        milliseconds = int((self.frames / self.fps) * 1000)
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d},{milliseconds:03d}"

    def __repr__(self) -> str:
        return f"Timecode({self})"


def check_ffmpeg() -> bool:
    """FFmpeg 설치 확인"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def analyze_video(video_path: str) -> Dict:
    """FFprobe를 사용하여 비디오 정보 분석"""
    if not check_ffmpeg():
        print("⚠️  경고: FFmpeg가 설치되어 있지 않습니다. 비디오 분석 기능이 제한됩니다.")
        print("   설치: sudo apt-get install ffmpeg (Linux) 또는 brew install ffmpeg (Mac)")
        return {}

    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        # 비디오 스트림 찾기
        video_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break

        if not video_stream:
            print("❌ 비디오 스트림을 찾을 수 없습니다.")
            return {}

        # FPS 계산
        fps_str = video_stream.get('r_frame_rate', '25/1')
        num, denom = map(int, fps_str.split('/'))
        fps = num / denom if denom != 0 else 25.0

        # 타임코드 정보
        start_time = float(video_stream.get('start_time', 0))
        duration = float(video_stream.get('duration', 0))

        info = {
            'fps': fps,
            'width': video_stream.get('width'),
            'height': video_stream.get('height'),
            'codec': video_stream.get('codec_name'),
            'duration': duration,
            'start_time': start_time,
            'total_frames': int(duration * fps) if duration else None,
            'timecode_start': video_stream.get('tags', {}).get('timecode'),
        }

        return info

    except subprocess.CalledProcessError as e:
        print(f"❌ FFprobe 실행 오류: {e}")
        return {}
    except Exception as e:
        print(f"❌ 비디오 분석 오류: {e}")
        return {}


def print_video_analysis(video_path: str):
    """비디오 분석 결과 출력"""
    print(f"\n📹 비디오 분석: {video_path}")
    print("=" * 70)

    if not Path(video_path).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {video_path}")
        return None

    info = analyze_video(video_path)

    if not info:
        return None

    print(f"FPS: {info['fps']:.3f}")
    print(f"해상도: {info['width']}x{info['height']}")
    print(f"코덱: {info['codec']}")
    print(f"길이: {info['duration']:.3f}초")
    print(f"시작 시간: {info['start_time']:.3f}초")

    if info['total_frames']:
        print(f"총 프레임: {info['total_frames']}")

    if info['timecode_start']:
        print(f"시작 타임코드: {info['timecode_start']}")
    else:
        print("시작 타임코드: 없음 (00:00:00:00으로 가정)")

    # 프레임 시간 계산
    if info['fps']:
        frame_duration_ms = (1 / info['fps']) * 1000
        print(f"프레임당 시간: {frame_duration_ms:.3f}ms")

    return info


def convert_timecode_list(input_file: str, output_file: str, fps: float,
                         offset_seconds: float = 0, offset_frames: int = 0):
    """타임코드 리스트를 변환하여 오프셋 적용"""
    print(f"\n🔄 타임코드 변환 중...")
    print(f"입력: {input_file}")
    print(f"출력: {output_file}")
    print(f"FPS: {fps}")

    if offset_seconds != 0:
        print(f"초 오프셋: {offset_seconds:+.3f}초")
    if offset_frames != 0:
        print(f"프레임 오프셋: {offset_frames:+d} 프레임")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        converted_lines = []
        conversion_count = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                converted_lines.append(line)
                continue

            # 타임코드 패턴 찾기 (HH:MM:SS:FF 또는 HH:MM:SS;FF)
            tc_pattern = r'\b(\d{2}):(\d{2}):(\d{2})[:;](\d{2})\b'

            def replace_timecode(match):
                nonlocal conversion_count
                tc_str = match.group(0)
                try:
                    tc = Timecode.from_string(tc_str, fps)

                    # 오프셋 적용
                    if offset_seconds != 0:
                        tc = tc.add_offset(offset_seconds)
                    if offset_frames != 0:
                        tc = tc.add_frames(offset_frames)

                    conversion_count += 1
                    return str(tc)
                except Exception as e:
                    print(f"⚠️  타임코드 변환 오류 ({tc_str}): {e}")
                    return tc_str

            converted_line = re.sub(tc_pattern, replace_timecode, line)
            converted_lines.append(converted_line)

        # 결과 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(converted_lines))

        print(f"✅ 변환 완료: {conversion_count}개의 타임코드 변환됨")
        print(f"   저장됨: {output_file}")

    except Exception as e:
        print(f"❌ 변환 오류: {e}")
        sys.exit(1)


def interactive_sync_helper(video_path: Optional[str] = None, fps: float = 25.0):
    """대화형 동기화 도우미"""
    print("\n🎬 캡컷 타임코드 동기화 도우미")
    print("=" * 70)

    # 비디오 분석
    if video_path:
        info = analyze_video(video_path)
        if info and info.get('fps'):
            fps = info['fps']
            print(f"\n✅ 비디오에서 FPS 감지됨: {fps:.3f}")

    print(f"\n현재 FPS 설정: {fps}")
    print("\n문제 진단을 시작합니다...")

    # 1. 오프셋 확인
    print("\n❓ 질문 1: 대본의 첫 타임코드와 캡컷에서 실제 나타나는 시간이 다른가요?")
    print("   예: 대본에 00:00:10:00이라고 적혀있는데 캡컷에서는 00:00:09:15에 나타남")

    response = input("   다릅니까? (y/n): ").strip().lower()

    if response == 'y':
        print("\n이것은 시작 오프셋 문제입니다.")

        print("\n대본의 타임코드를 입력하세요 (HH:MM:SS:FF): ", end='')
        script_tc_str = input().strip()

        print("캡컷에서 실제 나타나는 시간을 입력하세요 (HH:MM:SS:FF): ", end='')
        actual_tc_str = input().strip()

        try:
            script_tc = Timecode.from_string(script_tc_str, fps)
            actual_tc = Timecode.from_string(actual_tc_str, fps)

            diff_seconds = actual_tc.to_seconds() - script_tc.to_seconds()
            diff_frames = actual_tc.to_frames() - script_tc.to_frames()

            print(f"\n📊 분석 결과:")
            print(f"   시간 차이: {diff_seconds:+.3f}초")
            print(f"   프레임 차이: {diff_frames:+d} 프레임")

            print(f"\n💡 해결 방법:")
            print(f"   타임코드 변환 시 다음 오프셋을 적용하세요:")
            print(f"   --offset-seconds {diff_seconds:.3f}")
            print(f"   또는")
            print(f"   --offset-frames {diff_frames}")

        except Exception as e:
            print(f"❌ 타임코드 파싱 오류: {e}")

    # 2. 프레임 카운팅 확인
    print("\n❓ 질문 2: 영상 시작 부분에서 이미 오프셋이 있나요?")
    print("   (예: 영상이 00:00:00:00이 아닌 01:00:00:00에서 시작)")

    response = input("   있습니까? (y/n): ").strip().lower()

    if response == 'y':
        print("\n영상의 시작 타임코드를 입력하세요 (HH:MM:SS:FF): ", end='')
        start_tc_str = input().strip()

        try:
            start_tc = Timecode.from_string(start_tc_str, fps)
            offset_seconds = -start_tc.to_seconds()  # 음수 오프셋

            print(f"\n💡 해결 방법:")
            print(f"   타임코드를 0부터 시작하도록 조정하세요:")
            print(f"   --offset-seconds {offset_seconds:.3f}")

        except Exception as e:
            print(f"❌ 타임코드 파싱 오류: {e}")

    # 3. FPS 재확인
    print("\n❓ 질문 3: 영상의 FPS가 정확히 25.000인지 확인하셨나요?")
    print(f"   현재 설정: {fps}")

    response = input("   다른 FPS를 시도해보시겠습니까? (y/n): ").strip().lower()

    if response == 'y':
        print("\n시도할 FPS를 입력하세요 (예: 25, 23.976, 29.97, 30): ", end='')
        try:
            new_fps = float(input().strip())
            print(f"\n다음 명령어로 FPS {new_fps}로 재시도하세요:")
            print(f"   --fps {new_fps}")
        except:
            print("❌ 잘못된 FPS 값입니다.")

    print("\n" + "=" * 70)
    print("진단이 완료되었습니다. 위의 제안을 시도해보세요!")


def main():
    parser = argparse.ArgumentParser(
        description='캡컷 타임코드 동기화 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 비디오 파일 분석
  %(prog)s --analyze video.mp4

  # 타임코드 리스트 변환 (3초 오프셋)
  %(prog)s --convert script.txt --output corrected.txt --offset-seconds 3.0

  # 타임코드 리스트 변환 (5 프레임 오프셋)
  %(prog)s --convert script.txt --output corrected.txt --offset-frames 5

  # 대화형 동기화 도우미
  %(prog)s --interactive --video video.mp4

  # 타임코드 변환 (문자열)
  %(prog)s --timecode 00:01:23:15 --fps 25
        """
    )

    parser.add_argument('--analyze', '-a', metavar='VIDEO',
                       help='비디오 파일 분석')

    parser.add_argument('--convert', '-c', metavar='INPUT',
                       help='타임코드 리스트 파일 변환')

    parser.add_argument('--output', '-o', metavar='OUTPUT',
                       help='변환된 타임코드 저장 파일')

    parser.add_argument('--fps', '-f', type=float, default=25.0,
                       help='프레임 레이트 (기본값: 25)')

    parser.add_argument('--offset-seconds', type=float, default=0,
                       help='초 단위 오프셋 (양수 = 늦춤, 음수 = 앞당김)')

    parser.add_argument('--offset-frames', type=int, default=0,
                       help='프레임 단위 오프셋 (양수 = 늦춤, 음수 = 앞당김)')

    parser.add_argument('--interactive', '-i', action='store_true',
                       help='대화형 동기화 도우미 실행')

    parser.add_argument('--video', '-v', metavar='VIDEO',
                       help='대화형 모드에서 분석할 비디오 파일')

    parser.add_argument('--timecode', '-t', metavar='TIMECODE',
                       help='타임코드 변환 (HH:MM:SS:FF)')

    args = parser.parse_args()

    # 인자가 없으면 도움말 표시
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # 비디오 분석
    if args.analyze:
        print_video_analysis(args.analyze)

    # 타임코드 변환
    elif args.convert:
        if not args.output:
            print("❌ 오류: --output 옵션이 필요합니다.")
            sys.exit(1)

        convert_timecode_list(args.convert, args.output, args.fps,
                            args.offset_seconds, args.offset_frames)

    # 대화형 모드
    elif args.interactive:
        interactive_sync_helper(args.video, args.fps)

    # 단일 타임코드 변환
    elif args.timecode:
        try:
            tc = Timecode.from_string(args.timecode, args.fps)

            if args.offset_seconds != 0:
                tc = tc.add_offset(args.offset_seconds)
            if args.offset_frames != 0:
                tc = tc.add_frames(args.offset_frames)

            print(f"\n타임코드 변환 결과 (FPS: {args.fps}):")
            print(f"  타임코드: {tc}")
            print(f"  초: {tc.to_seconds():.3f}s")
            print(f"  프레임: {tc.to_frames()}")
            print(f"  밀리초: {tc.to_milliseconds()}ms")
            print(f"  SRT 형식: {tc.to_srt_format()}")
        except Exception as e:
            print(f"❌ 오류: {e}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
