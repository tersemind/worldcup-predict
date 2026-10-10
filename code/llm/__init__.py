# Copyright (C) TerseMind.
# Use of this source code is governed by a MIT license.

"""LLM 接入层（lingya OpenAI 兼容协议）"""
from .client import LLMClient, LLMUnavailable, get_default_client

__all__ = ["LLMClient", "LLMUnavailable", "get_default_client"]
