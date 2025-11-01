# Dotfiles for GitHub Codespaces

이 저장소는 모든 GitHub Codespaces에서 자동으로 개발 환경을 설정합니다.

## 포함된 내용

- **Claude Code CLI** - Anthropic의 AI 코딩 도구 자동 설치
- **유용한 alias** - git, ls 등의 단축 명령어
- **PATH 설정** - Claude Code와 기타 도구들을 위한 경로 설정

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

---

모든 Codespace에서 동일한 개발 환경을 사용하세요! 🚀
