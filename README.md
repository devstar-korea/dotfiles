# Dotfiles for GitHub Codespaces

이 저장소는 모든 GitHub Codespaces에서 자동으로 개발 환경을 설정합니다.

## 포함된 내용

- **Claude Code CLI** - Anthropic의 AI 코딩 도구 자동 설치
- **유용한 alias** - git, ls 등의 단축 명령어
- **PATH 설정** - Claude Code와 기타 도구들을 위한 경로 설정
- **캡컷 타임코드 동기화 도구** - 비디오 편집 시 타임코드 싱크 문제 해결

## 설정 방법

### 1. 이 저장소를 GitHub에 업로드

```bash
cd dotfiles
git init
git add .
git commit -m "Initial dotfiles setup"
git remote add origin https://github.com/YOUR_USERNAME/dotfiles.git
git push -u origin main
```

### 2. GitHub Codespaces 설정

1. GitHub 계정 설정으로 이동: https://github.com/settings/codespaces
2. **Dotfiles** 섹션 찾기
3. ✅ **Automatically install dotfiles** 체크
4. 저장소 선택: `YOUR_USERNAME/dotfiles`
5. Install command: `bash install.sh` (기본값)

### 3. 완료!

이제 **어떤 저장소**에서든 Codespace를 만들면:
- Claude Code가 자동으로 설치됩니다
- 유용한 alias와 설정이 적용됩니다
- 개발 환경이 즉시 준비됩니다

## 포함된 파일

- `install.sh` - Codespace 생성 시 실행되는 설치 스크립트
- `.bashrc` - Bash 셸 설정 (PATH, alias 등)

## 커스터마이징

원하는 도구나 설정을 `install.sh`에 추가하세요:

```bash
# 예: Node.js 글로벌 패키지 설치
npm install -g typescript tsx

# 예: 기타 CLI 도구 설치
pip install --user black flake8
```

## 문제 해결

### Claude가 설치되지 않는 경우

Codespace 터미널에서 수동으로 실행:
```bash
bash ~/install.sh
source ~/.bashrc
```

### PATH 문제

```bash
echo $PATH
# ~/.local/bin이 포함되어 있는지 확인
```

## 캡컷 타임코드 동기화 도구

비디오 편집 시 타임코드가 대본과 맞지 않는 문제를 해결하는 Python 스크립트입니다.

### 주요 기능

- 비디오 파일의 FPS 및 타임코드 메타데이터 분석
- 타임코드 리스트 파일에 오프셋 적용
- 대화형 진단 모드로 문제 원인 파악
- 다양한 타임코드 형식 지원 (HH:MM:SS:FF, SRT 등)

### 빠른 시작

```bash
# 비디오 파일 분석
./capcut_timecode_sync.py --analyze video.mp4

# 대화형 진단 (권장)
./capcut_timecode_sync.py --interactive --video video.mp4

# 타임코드 리스트 변환 (3초 오프셋)
./capcut_timecode_sync.py --convert script.txt --output corrected.txt --offset-seconds 3.0

# 도움말
./capcut_timecode_sync.py --help
```

자세한 사용법은 [캡컷 동기화 가이드](CAPCUT_SYNC_GUIDE.md)를 참고하세요.

### 필요한 도구

- Python 3 (필수)
- FFmpeg (선택, 비디오 분석 기능용)

```bash
# Ubuntu/Debian
sudo apt-get install python3 ffmpeg

# macOS
brew install python3 ffmpeg
```

---

모든 Codespace에서 동일한 개발 환경을 사용하세요! 🚀
