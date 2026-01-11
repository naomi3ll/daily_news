#!/bin/bash

# GitHub Pages 部署配置脚本
# 此脚本帮助配置本地测试环境

set -e

echo "🚀 daily_news GitHub Actions 配置助手"
echo "════════════════════════════════════════════════════════════"
echo ""

# 检查 Git 仓库
if [ ! -d .git ]; then
    echo "❌ 错误：不在 Git 仓库目录中"
    exit 1
fi

echo "✅ 检测到 Git 仓库"
echo ""

# 检查必要文件
echo "📋 检查必要文件..."
required_files=(
    "requirements.txt"
    "scripts/generate_news_page.py"
    ".github/workflows/deploy.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ 缺失：$file"
        exit 1
    fi
done

echo ""
echo "✅ 所有必要文件已存在"
echo ""

# 检查 Python 环境
echo "🐍 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  ✅ Python $python_version"

# 检查依赖
echo ""
echo "📦 检查依赖..."
if [ ! -d "venv" ]; then
    echo "  创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "  安装依赖..."
pip install -q -r requirements.txt

echo "  ✅ 依赖已安装"

# 测试生成
echo ""
echo "🧪 测试生成新闻页面..."
python scripts/generate_news_page.py

if [ -f "docs/index.html" ]; then
    echo "  ✅ 页面生成成功"
    file_size=$(du -h docs/index.html | cut -f1)
    article_count=$(grep -o "data-source=" docs/index.html | wc -l)
    echo "  📄 文件大小：$file_size"
    echo "  📰 文章数量：$article_count 条"
else
    echo "  ❌ 页面生成失败"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ 配置完成！"
echo ""
echo "📖 后续步骤："
echo ""
echo "1️⃣  推送到 GitHub"
echo "   git add -A"
echo "   git commit -m 'feat: add GitHub Actions deployment'"
echo "   git push origin main"
echo ""
echo "2️⃣  启用 GitHub Pages"
echo "   Settings → Pages → Source → GitHub Actions"
echo ""
echo "3️⃣  (可选) 启用定时任务"
echo "   Actions 标签页会自动显示 workflow 状态"
echo "   定时任务每天 UTC 8:00 自动运行"
echo ""
echo "4️⃣  验证部署"
echo "   访问 https://username.github.io/daily_news"
echo ""
echo "📚 更多信息请查看 .github/GITHUB_ACTIONS_GUIDE.md"
echo ""
