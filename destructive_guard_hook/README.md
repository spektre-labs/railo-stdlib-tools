# destructive_guard — Claude Code PreToolUse safety hook

Blocks **irreversible / destructive shell commands** before they run. Stdlib only, zero deps,
fail-open (never breaks the session), low false-positive.

## What it blocks
- `rm -rf` targeting `/`, `~`, `$HOME`, or a wildcard
- raw disk write/format: `dd of=/dev/…`, `mkfs…`, `fdisk`, `parted … /dev/…`
- fork bomb `:(){ :|:& };:`
- force-push / hard-reset onto `main`/`master`/`origin`
- shell-history wipe, `chmod -R 000 /`
- `curl … | sh` (pipe remote script into a shell)
- credential read piped to the network (`cat ~/.ssh/id_rsa | nc …`)

Ordinary commands (`rm -rf ./build`, `git push origin feature`, `dd if=a of=b`) pass untouched.

## Install
`.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [ { "type": "command", "command": "python3 /abs/path/destructive_guard.py" } ] }
    ]
  }
}
```

## Test
```bash
python3 -m pytest test_destructive_guard.py -q   # 23 cases (block + allow + hook contract)
```

## Design
- `evaluate(command) -> {allow, reason}` is pure → unit-testable without the hook runtime.
- On a block: emits the PreToolUse `permissionDecision: "deny"` JSON with a human reason.
- On unparseable input or any internal error: exit 0, no block (fail-open — safety hook must never
  brick the session). Flip to fail-closed by returning a deny in the `except`.
- Patterns match unmistakably destructive *shapes*; a destructive string inside a commit message or
  a relative-path `rm -rf ./dir` is intentionally allowed.
