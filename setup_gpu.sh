#!/bin/bash
# MinerU GPU 加速安装脚本

echo "🚀 开始安装 MinerU GPU 版本..."

# 检查 CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "✓ 检测到 NVIDIA GPU"
    nvidia-smi --query-gpu=name --format=csv,noheader
else
    echo "⚠ 未检测到 NVIDIA GPU，将安装 CPU 版本"
    pip install mineru
    exit 0
fi

# 安装 PyTorch GPU 版本
echo "📦 安装 PyTorch (CUDA)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 安装 MinerU GPU 版本
echo "📦 安装 MinerU (GPU)..."
pip install mineru[gpu]

# 验证安装
echo "🔍 验证安装..."
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')

try:
    from mineru.backend.pipeline.pipeline_analyze import pdf_parse_main
    print('✓ MinerU 安装成功')
except ImportError as e:
    print(f'✗ MinerU 安装失败: {e}')
"

echo "✓ 安装完成！"
