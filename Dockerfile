# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建非root用户
RUN addgroup --system app && adduser --system --group app

# 为日志目录设置权限
RUN mkdir -p /app/logs && chown -R app:app /app

# 复制应用代码
COPY . .
RUN chown -R app:app /app

# 切换到非root用户
USER app

# 暴露API端口
EXPOSE 8000

# 创建健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 运行API服务
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 