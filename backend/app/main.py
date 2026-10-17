from __future__ import annotations

import os
from pathlib import Path
from tempfile import gettempdir
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .three_mf import create_box_3mf


ARTIFACT_DIR = Path(gettempdir()) / "3doodle-artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=3)


class DesignRequest(BaseModel):
    session_id: str = Field(min_length=1)
    description: str = Field(min_length=6)
    machine: str
    material: str


sessions: dict[str, list[ChatTurn]] = {}
artifacts: dict[str, Path] = {}

app = FastAPI(title="3doodle Foundry Agent Scaffold", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    history = sessions.setdefault(payload.session_id, [])
    history.append(ChatTurn(role="user", content=payload.message))

    response_text = (
        "Design intent captured. I can now refine geometry, tolerances, and support strategy. "
        "When ready, click Generate 3MF to produce a slicer-ready artifact."
    )
    history.append(ChatTurn(role="assistant", content=response_text))

    return {"reply": response_text}


@app.post("/api/design")
def create_design(payload: DesignRequest) -> dict[str, object]:
    history = sessions.setdefault(payload.session_id, [])
    history.append(ChatTurn(role="user", content=payload.description))

    # Placeholder sizing logic to keep scaffold deterministic before model wiring.
    base = max(20, min(80, len(payload.description) // 2))
    width = float(base)
    depth = float(max(18, base - 6))
    height = float(max(12, base // 2))

    file_id = str(uuid4())
    filename = f"3doodle-{file_id}.3mf"
    target = ARTIFACT_DIR / filename
    target.write_bytes(create_box_3mf(width=width, depth=depth, height=height))
    artifacts[file_id] = target

    assistant_text = (
        f"Generated a complete 3MF for machine '{payload.machine}' using material '{payload.material}'. "
        f"Dimensions are approximately {width:.0f}mm x {depth:.0f}mm x {height:.0f}mm."
    )
    history.append(ChatTurn(role="assistant", content=assistant_text))

    return {
        "reply": assistant_text,
        "artifact": {
            "id": file_id,
            "filename": filename,
            "downloadUrl": f"/api/artifacts/{file_id}",
            "preview": {"width": width, "depth": depth, "height": height},
            "status": "validated-structure",
        },
    }


@app.get("/api/artifacts/{artifact_id}")
def download_artifact(artifact_id: str) -> FileResponse:
    path = artifacts.get(artifact_id)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")

    return FileResponse(
        path,
        media_type="application/vnd.ms-package.3dmanufacturing-3dmodel+xml",
        filename=path.name,
    )


# TODO: replace deterministic reply and geometry logic with a Foundry model invocation.
# Example env vars expected by the future integration:
# - FOUNDRY_PROJECT_ENDPOINT
# - FOUNDRY_MODEL_DEPLOYMENT
# - FOUNDRY_API_KEY
