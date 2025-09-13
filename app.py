from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import yaml
import argparse
import uvicorn
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory="templates")
CONFIG_FILE = Path("config.yaml")


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg, f)


@app.get("/")
def edit_config(request: Request):
    cfg = load_config()
    return templates.TemplateResponse(
        "edit.html", {"request": request, "config": cfg}
    )


@app.post("/save")
def save_config_route(
    request: Request,
    # flatten the form fields for each model
    **kwargs
):
    cfg = load_config()
    models = cfg.get("models", [])

    # Rebuild model entries from form data
    updated_models = []
    num_models = len(models)
    for i in range(num_models):
        updated_models.append({
            "name": kwargs.get(f"name_{i}", ""),
            "path": kwargs.get(f"path_{i}", ""),
            "gpu_layers": int(kwargs.get(f"gpu_layers_{i}", 0)),
            "context_size": int(kwargs.get(f"context_size_{i}", 0)),
            "batch_size": int(kwargs.get(f"batch_size_{i}", 0)),
            "flash_attention": kwargs.get(f"flash_attention_{i}", "off") == "on",
        })

    save_config({"models": updated_models})
    return RedirectResponse("/", status_code=303)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
