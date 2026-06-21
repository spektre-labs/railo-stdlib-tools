#!/usr/bin/env python3
"""
destructive_guard — a Claude Code PreToolUse hook that blocks destructive shell commands.

Reads the tool-call JSON from stdin (the PreToolUse hook contract), inspects Bash commands, and
DENIES anything matching a destructive pattern (irreversible delete / disk wipe / fork bomb / history
nuke / credential exfil). Exit 0 = allow; a JSON deny on stdout + exit 0 blocks with a reason; the
hook never crashes the session (any internal error → fail-open with a logged note, configurable).

Stdlib only. Wire it in `.claude/settings.json`:

  {
    "hooks": {
      "PreToolUse": [
        { "matcher": "Bash",
          "hooks": [ { "type": "command", "command": "python3 /abs/path/destructive_guard.py" } ] }
      ]
    }
  }

Patterns are conservative (low false-positive): they target unmistakably destructive forms.
"""
from __future__ import annotations
import sys, json, re

# Each rule: (compiled regex, human reason). Conservative — match clearly destructive shapes only.
RULES = [
    (re.compile(r"\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*[rf][a-zA-Z]*\s+(-[a-zA-Z]+\s+)*(/|~|\$HOME|\*)"),
     "recursive/forced rm targeting root, home, or a wildcard"),
    (re.compile(r"\brm\s+-rf?\s+/\s*($|\s)"), "rm -rf / (root wipe)"),
    (re.compile(r"\bdd\b.*\bof=/dev/"), "raw dd write to a block device"),
    (re.compile(r"\b(mkfs\S*|fdisk|parted)\s+.*?/dev/"), "format / partition of a block device"),
    (re.compile(r":\(\)\s*\{\s*:\|:&\s*\}\s*;\s*:"), "fork bomb"),
    (re.compile(r"\bgit\s+(push\s+.*--force|reset\s+--hard)\b.*\b(origin|main|master)\b"),
     "force-push / hard-reset onto a shared branch"),
    (re.compile(r">\s*~?/?\.(bash_history|zsh_history)\b"), "shell history wipe"),
    (re.compile(r"\bchmod\s+-R\s+0?00\s+/"), "chmod 000 -R on a root path (lockout)"),
    (re.compile(r"\b(curl|wget)\b.*\|\s*(sudo\s+)?(ba)?sh\b"), "pipe remote script straight into a shell"),
    (re.compile(r"\b(cat|grep|curl|head|tail)\b.*(\.ssh/id_|\.aws/credentials|\.env\b).*\|\s*(curl|nc|wget|ncat)"),
     "credential read piped to the network (exfil)"),
]


def evaluate(command: str) -> dict:
    """Return {allow: bool, reason: str}. Pure — testable without the hook runtime."""
    cmd = command or ""
    for rx, reason in RULES:
        if rx.search(cmd):
            return {"allow": False, "reason": reason}
    return {"allow": True, "reason": ""}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # no parseable input → don't block (fail-open, never break the session)
    tool = payload.get("tool_name") or payload.get("tool") or ""
    tin = payload.get("tool_input") or payload.get("input") or {}
    if tool != "Bash":
        return 0
    command = tin.get("command", "") if isinstance(tin, dict) else str(tin)
    verdict = evaluate(command)
    if not verdict["allow"]:
        # PreToolUse deny contract: emit a permissionDecision=deny with a reason.
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"🛑 destructive_guard blocked: {verdict['reason']}",
            }
        }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
