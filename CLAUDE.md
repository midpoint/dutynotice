# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains a setup script (`m25.sh`) that configures environment variables and launches Claude Code with a specific permission mode.

## Usage

Run the setup script to start Claude Code with the configured settings:

```bash
./m25.sh
```

## Configuration

The script sets up:
- `ANTHROPIC_BASE_URL` - API endpoint for MiniMax
- `ANTHROPIC_AUTH_TOKEN` - Authentication token (do not share)
- `ANTHROPIC_MODEL` - Default model (MiniMax-M2.7)
- `API_TIMEOUT_MS` - API timeout (3000000ms)
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` - Disables non-essential traffic
- Model fallbacks for Opus, Sonnet, and Haiku families

## Permission Mode

The script runs Claude Code with `--permission-mode acceptEdits`, which allows accepting edits without additional prompts.
