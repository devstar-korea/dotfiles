# Claude Code CLI
export PATH="$HOME/.local/bin:$PATH"

# Aliases
alias cls='clear'
alias ll='ls -lah'
alias gs='git status'
alias gp='git pull'
alias gc='git commit'

# Welcome message
echo "🚀 Development environment ready!"
if command -v claude &> /dev/null; then
    echo "✅ Claude Code: $(claude --version 2>&1 | head -n 1)"
fi
