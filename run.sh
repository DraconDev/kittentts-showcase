#!/usr/bin/env bash
# Run KittenTTS with proper NixOS library paths
cd "$(dirname "$0")"
nix-shell --run "python $@"
