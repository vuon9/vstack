# Build: Go / Rust (plain `.app` / `.dmg`)

A plain Go or Rust program can be turned into a distributable macOS app, but a bare binary is not an app bundle. You must assemble the `.app` structure (and optionally a DMG) yourself, then sign and notarize.

## Detect

- `go.mod` or `Cargo.toml`, no Wails/Tauri/Electron, and the goal is a macOS GUI/distributable `.app`/`.dmg`.

## Reason about it first

- A `.app` is a directory: `App.app/Contents/MacOS/<binary>` plus `App.app/Contents/Info.plist`. Code signing and notarization apply to that bundle, not to a bare binary.
- Cross-compiling stops at a Mach-O binary; you still have to lay out the bundle and set `CFBundleIdentifier`, `CFBundleName`, `CFBundleVersion`, `CFBundleExecutable`.
- Some GUI toolkits (e.g. `fyne`, `egui`/`iced`) provide their own macOS packaging; that can save you layout work. Check the toolkit's packaging route first.

## Build the binary for darwin

```bash
# Go
GOOS=darwin GOARCH=arm64 go build -o App.app/Contents/MacOS/App ./cmd/app
# or universal via lipo, like the Wails path
```

For Rust, `cargo build --release --target aarch64-apple-darwin` places a binary under `target/<triple>/release/`.

## Assemble the bundle

```bash
mkdir -p App.app/Contents/MacOS
cp <binary> App.app/Contents/MacOS/App
cp Info.plist App.app/Contents/Info.plist
```

The `Info.plist` must set `CFBundleExecutable`, `CFBundleIdentifier`, `CFBundleName`, `CFBundleShortVersionString`, and `CFBundlePackageType` (`APPL`).

## Distribute

For a DMG, create the disk image from the `.app`, then hand it to the sign/notarize/staple path in [ship/direct.md](../ship/direct.md).

## Gotchas

- `codesign` on a bare Mach-O binary is not the same as signing the `.app` bundle; sign the bundle (with `--deep` only as a last resort, not as a substitute for correct order).
- Gatekeeper and notarization require a valid bundle structure; a bare binary `spctl`-assess fails.
- Set `CFBundleIdentifier` before signing; changing it afterward invalidates the signature.
- If the toolkit provides packaging, prefer it over hand-rolling the bundle layout.
