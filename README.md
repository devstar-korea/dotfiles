# Dotfiles

Windows 개발 환경 설정 동기화

## 포함 내용

- **SenseVoice**: 음성-텍스트 변환 (Whisper 대비 15배 빠름)
- **/talk 스킬**: Claude Code에서 음성 입력 활성화

## 설치

```powershell
git clone https://github.com/YOUR_USERNAME/dotfiles.git C:\Users\PC\dotfiles
cd C:\Users\PC\dotfiles
powershell -ExecutionPolicy Bypass -File setup.ps1
```

## 사용법

Claude Code에서:
```
/talk
```

어디서든 **백틱(`)** 키로 녹음 시작/중지. 인식된 텍스트가 커서 위치에 자동 입력됨.

## 파일 구조

```
dotfiles/
├── .claude/
│   └── skills/
│       └── talk/
│           └── SKILL.md      # /talk 스킬 정의
├── tools/
│   └── SenseVoice/
│       ├── sensevoice_cli.py # CLI 버전
│       └── sensevoice_bg.pyw # 백그라운드 버전
├── setup.ps1                 # 설치 스크립트
└── README.md
```
