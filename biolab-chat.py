#!/usr/bin/env python3
"""
Script principal para execução da CLI do BioLab.Ai em modo interativo (chat)
"""

import sys
from ai_principal.cli.interactive import interactive_mode

if __name__ == "__main__":
    interactive_mode()