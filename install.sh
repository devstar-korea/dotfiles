#!/bin/bash

echo "=========================================="
echo "  Setting up development environment..."
echo "=========================================="

# Install Claude Code
echo ""
echo "📦 Installing Claude Code CLI..."
if command -v claude &> /dev/null; then
    echo "✅ Claude Code is already installed"
    claude --version
else
    curl -fsSL https://claude.ai/install.sh | bash

    # Update PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    if command -v claude &> /dev/null; then
        echo "✅ Claude Code installed successfully!"
        claude --version
    else
        echo "⚠️  Claude Code installed but needs shell restart"
        echo "Run: source ~/.bashrc"
    fi
fi

echo ""
echo "=========================================="
echo "  ✅ Setup complete!"
echo "=========================================="
