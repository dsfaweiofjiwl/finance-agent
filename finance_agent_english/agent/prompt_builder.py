#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt Builder - Load layered configuration files and build prompts
Layered design:
- IDENTITY.md: Who are you? (Identity positioning)
- SOUL.md: What do you believe in? (Core principles)
- Finance.md: Data source specifications
"""

import os
from typing import List


class PromptBuilder:
    """Build layered prompts"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir

    def _read_file(self, filename: str) -> str:
        """Read configuration file"""
        path = os.path.join(self.config_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def build_system_prompts(self) -> List[str]:
        """Build system prompts for data collection/analysis phases (with tools)"""
        prompts = []
        prompts.append(self._read_file("IDENTITY.md"))
        prompts.append(self._read_file("SOUL.md"))
        prompts.append(self._read_file("Finance.md"))
        return prompts

    def build_compile_system_prompts(self) -> List[str]:
        """Build system prompts for the final compilation phase (no tools).

        Only IDENTITY is needed — no tool-use instructions, no data source specs.
        """
        return [self._read_file("IDENTITY.md")]
