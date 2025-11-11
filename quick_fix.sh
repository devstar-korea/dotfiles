#!/bin/bash
# 빠른 타임코드 보정 + SRT 생성 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 사용법 출력
usage() {
    echo -e "${BLUE}사용법:${NC}"
    echo "  $0 <대본파일> <오프셋초> [출력이름]"
    echo ""
    echo -e "${BLUE}예시:${NC}"
    echo "  $0 script.txt 2.4"
    echo "  $0 script.txt 2.4 final"
    echo "  $0 script.txt -1.5 test"
    echo ""
    echo -e "${BLUE}설명:${NC}"
    echo "  <대본파일>   : 타임코드가 있는 대본 파일"
    echo "  <오프셋초>   : 적용할 오프셋 (초 단위, 양수=늦춤, 음수=앞당김)"
    echo "  [출력이름]   : 출력 파일 이름 (선택, 기본값: output)"
    echo ""
    echo -e "${YELLOW}오프셋을 모른다면:${NC}"
    echo "  ./capcut_timecode_sync.py --interactive --video video.mp4"
    exit 1
}

# 인자 확인
if [ $# -lt 2 ]; then
    echo -e "${RED}오류: 필수 인자가 부족합니다${NC}\n"
    usage
fi

SCRIPT_FILE=$1
OFFSET=$2
OUTPUT_NAME=${3:-output}

# 파일 존재 확인
if [ ! -f "$SCRIPT_FILE" ]; then
    echo -e "${RED}오류: 파일을 찾을 수 없습니다: $SCRIPT_FILE${NC}"
    exit 1
fi

# 스크립트 경로 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMECODE_SYNC="$SCRIPT_DIR/capcut_timecode_sync.py"
SRT_CONVERT="$SCRIPT_DIR/convert_to_srt.py"

if [ ! -f "$TIMECODE_SYNC" ]; then
    echo -e "${RED}오류: capcut_timecode_sync.py를 찾을 수 없습니다${NC}"
    exit 1
fi

if [ ! -f "$SRT_CONVERT" ]; then
    echo -e "${RED}오류: convert_to_srt.py를 찾을 수 없습니다${NC}"
    exit 1
fi

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  캡컷 타임코드 빠른 보정 도구${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}설정:${NC}"
echo "  입력 파일: $SCRIPT_FILE"
echo "  오프셋:    ${OFFSET}초"
echo "  출력 이름: $OUTPUT_NAME"
echo ""

# 1단계: 타임코드 보정
echo -e "${YELLOW}[1/2] 타임코드 보정 중...${NC}"
CORRECTED_FILE="${OUTPUT_NAME}_corrected.txt"

"$TIMECODE_SYNC" --convert "$SCRIPT_FILE" --output "$CORRECTED_FILE" --offset-seconds "$OFFSET"

if [ $? -ne 0 ]; then
    echo -e "${RED}오류: 타임코드 보정 실패${NC}"
    exit 1
fi

echo ""

# 2단계: SRT 생성
echo -e "${YELLOW}[2/2] SRT 자막 파일 생성 중...${NC}"
SRT_FILE="${OUTPUT_NAME}_markers.srt"

"$SRT_CONVERT" "$CORRECTED_FILE" -o "$SRT_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}오류: SRT 생성 실패${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 완료!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}생성된 파일:${NC}"
echo "  📄 $CORRECTED_FILE (보정된 대본)"
echo "  🎬 $SRT_FILE (캡컷용 자막)"
echo ""
echo -e "${YELLOW}📺 캡컷에서 사용 방법:${NC}"
echo "  1. 캡컷 프로젝트 열기"
echo "  2. 영상을 타임라인에 추가"
echo "  3. '텍스트' → '자막' → '파일 불러오기'"
echo "  4. '$SRT_FILE' 선택"
echo "  5. 자막이 나타나는 위치 = 정확한 타임코드!"
echo "  6. 해당 위치에서 편집 (Ctrl+B 또는 Cmd+B로 컷)"
echo "  7. 편집 완료 후 자막 삭제"
echo ""
echo -e "${GREEN}Happy editing! 🎬✨${NC}"
