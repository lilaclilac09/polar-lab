from __future__ import annotations

from typing import Any


def resolve_device(preference: str = "auto") -> str:
    import torch

    pref = (preference or "auto").lower()
    if pref == "auto":
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"
    if pref in {"mps", "cuda", "cpu"}:
        if pref == "mps" and not (
            getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
        ):
            raise RuntimeError("MPS requested but not available")
        if pref == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but not available")
        return pref
    raise ValueError(f"unknown device preference: {preference}")


def resolve_dtype(preference: str = "auto", device: str = "cpu") -> Any:
    import torch

    pref = (preference or "auto").lower()
    if pref == "float32":
        return torch.float32
    if pref == "float16":
        return torch.float16
    if pref == "bfloat16":
        return torch.bfloat16
    if pref != "auto":
        raise ValueError(f"unknown dtype preference: {preference}")
    if device == "mps":
        return torch.float16
    if device == "cuda":
        return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return torch.float32
