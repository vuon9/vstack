# shipping-darwin-apps

Build and ship apps that target iOS or macOS, regardless of source language:
native Xcode (Swift/ObjC), Wails (Go), Tauri (Rust), Electron (JS/TS), or plain
Go/Rust `.app` targets.

This is a routing hub. `SKILL.md` detects the framework and distribution target
from the repo and points the agent at the right reference doc:

- `readiness.md` — environment and project checks before any build or ship
- `build/native.md`, `build/wails.md`, `build/tauri.md`, `build/electron.md`, `build/go-rust.md`
- `ship/appstore.md` — App Store / TestFlight (iOS)
- `ship/direct.md` — Developer ID signing, notarization, DMG (macOS out of store)

It replaces the separate `apple-platform-readiness`, `ios-testflight-release`,
and `macos-release` skills.

See `SKILL.md` for the routing table and guardrails.

## Model requirement

Skill auto-discovery is unreliable on small "flash" models. Use
`deepseek/deepseek-v4-pro`, or invoke the skill explicitly with
`/skill:shipping-darwin-apps`.
