"""Hugging Face Hub load helpers — retry + local-cache fallback."""

from __future__ import annotations

import os
import time
from typing import Any


def _is_hub_network_error(exc: BaseException) -> bool:
    name = type(exc).__name__
    msg = str(exc).lower()
    needles = (
        "timeout",
        "timed out",
        "connection",
        "network",
        "temporary failure",
        "name or service not known",
        "max retries",
        "503",
        "504",
        "429",
    )
    if any(n in msg for n in needles):
        return True
    return name in {
        "ConnectTimeout",
        "ReadTimeout",
        "ConnectError",
        "ProxyError",
        "RemoteProtocolError",
    }


def load_tokenizer(model_name: str, *, trust_remote_code: bool = True, retries: int = 3):
    """Load tokenizer; on Hub timeouts fall back to local HF cache."""
    from transformers import AutoTokenizer

    kwargs: dict[str, Any] = {"trust_remote_code": trust_remote_code}
    last: BaseException | None = None

    # Prefer offline if user already set it
    if os.environ.get("HF_HUB_OFFLINE") == "1" or os.environ.get("TRANSFORMERS_OFFLINE") == "1":
        return AutoTokenizer.from_pretrained(model_name, local_files_only=True, **kwargs)

    for attempt in range(1, retries + 1):
        try:
            return AutoTokenizer.from_pretrained(model_name, **kwargs)
        except Exception as exc:  # noqa: BLE001 — Hub stack raises many types
            last = exc
            if not _is_hub_network_error(exc) or attempt == retries:
                break
            wait = 2 ** (attempt - 1)
            print(
                f"[hub] tokenizer download failed ({type(exc).__name__}); retry in {wait}s "
                f"({attempt}/{retries})",
                flush=True,
            )
            time.sleep(wait)

    print("[hub] falling back to local HF cache (local_files_only=True)", flush=True)
    try:
        return AutoTokenizer.from_pretrained(model_name, local_files_only=True, **kwargs)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Could not load tokenizer for {model_name!r} from Hub or local cache.\n"
            f"Last Hub error: {last!r}\n"
            f"Cache error: {exc!r}\n"
            "Fix: check network to huggingface.co, or set HF_TOKEN, or retry with:\n"
            "  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1\n"
            "  ./run_next.sh"
        ) from exc


def load_causal_lm(
    model_name: str,
    *,
    dtype: Any,
    trust_remote_code: bool = True,
    retries: int = 3,
    dtype_kw: str = "dtype",
):
    """Load CausalLM; on Hub timeouts fall back to local HF cache.

    dtype_kw: transformers 5 prefers `dtype`; older code used `torch_dtype`.
    """
    from transformers import AutoModelForCausalLM

    kwargs: dict[str, Any] = {
        dtype_kw: dtype,
        "trust_remote_code": trust_remote_code,
    }
    last: BaseException | None = None

    if os.environ.get("HF_HUB_OFFLINE") == "1" or os.environ.get("TRANSFORMERS_OFFLINE") == "1":
        return AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True, **kwargs)

    for attempt in range(1, retries + 1):
        try:
            return AutoModelForCausalLM.from_pretrained(model_name, **kwargs)
        except TypeError:
            # Older transformers: torch_dtype instead of dtype
            if dtype_kw == "dtype":
                return load_causal_lm(
                    model_name,
                    dtype=dtype,
                    trust_remote_code=trust_remote_code,
                    retries=retries,
                    dtype_kw="torch_dtype",
                )
            raise
        except Exception as exc:  # noqa: BLE001
            last = exc
            if not _is_hub_network_error(exc) or attempt == retries:
                break
            wait = 2 ** (attempt - 1)
            print(
                f"[hub] model download failed ({type(exc).__name__}); retry in {wait}s "
                f"({attempt}/{retries})",
                flush=True,
            )
            time.sleep(wait)

    print("[hub] falling back to local HF cache (local_files_only=True)", flush=True)
    try:
        return AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True, **kwargs)
    except TypeError:
        kwargs.pop(dtype_kw, None)
        kwargs["torch_dtype"] = dtype
        return AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True, **kwargs)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Could not load model {model_name!r} from Hub or local cache.\n"
            f"Last Hub error: {last!r}\n"
            f"Cache error: {exc!r}\n"
            "Fix: check network to huggingface.co, or set HF_TOKEN, or retry with:\n"
            "  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1\n"
            "  ./run_next.sh"
        ) from exc
