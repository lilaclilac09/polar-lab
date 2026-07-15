"""Shared helpers for Polar Lab."""

from .config import load_config

__all__ = ["load_config", "resolve_device", "resolve_dtype"]


def __getattr__(name: str):
    if name in {"resolve_device", "resolve_dtype"}:
        from . import device

        return getattr(device, name)
    raise AttributeError(name)
