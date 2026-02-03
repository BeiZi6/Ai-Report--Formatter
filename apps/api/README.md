# API (FastAPI)

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

> 开发模式下，`requirements.txt` 已包含 `-e ../formatter`，确保本地 formatter 可作为可编辑包被 FastAPI 导入。

## Endpoints

- `POST /api/preview`
- `POST /api/generate`
