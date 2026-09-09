# Build: Wails (Go → macOS)

Wails compiles a Go backend with a web frontend into a native macOS `.app`. The Go code embeds the built frontend, so a production build needs the frontend built and embedded before the app is assembled.

## Detect

- `wails.json` (v2/v3) or a Wails dependency in `go.mod`.

## Reason about it first

- Wails needs its bindings generated and the frontend built into the embed target before `go build`.
- A macOS `.app` is assembled from a binary plus `Contents/MacOS` and `Contents/Info.plist` (and optional `icons.icns`, `*.car` assets). Packaging tools do this assembly; a plain `go build` only produces the binary.
- Version fields (`CFBundleShortVersionString`, `CFBundleVersion`) come from the build tool or from a git tag, so a prerelease tag can embed a stable base version.
- A universal binary is built by compiling `amd64` + `arm64` and joining them with `lipo -create`.

## Build

Prefer the repo's own task/scripts. Typical shape (Wails v3):

```bash
wails3 generate bindings -clean=true     # regenerate Go↔TS bindings
wails3 build                             # dev-ish build
task package                             # production package for current OS
```

On mac, `task package:<os>` or a repo script does the universal build:

```bash
GOOS=darwin CGO_ENABLED=1 GOARCH=amd64 go build -o bin/<app>-amd64 .
GOOS=darwin CGO_ENABLED=1 GOARCH=arm64 go build -o bin/<app>-arm64 .
lipo -create bin/<app>-amd64 bin/<app>-arm64 -output bin/<app>
```

Then assemble `bin/<app>.app` with the `Info.plist` and `icons.icns` from `build/<os>/`.

## Gotchas

- The build script usually hard-requires `build/<os>/Info.plist` and `build/<os>/icons.icns` to exist. If they are deleted, the package step fails even though the code compiles.
- The frontend needs to be built into `frontend/dist` (embed source) before the Go binary is compiled, or the app launches with a blank/old UI.
- `wails3` may not be installed on a bare machine; if the release path uses a custom script instead of `task`, the Wails CLI is not needed for CI.
- Production builds set `PRODUCTION=true` for the frontend build; dev mode uses a dev server URL instead of embedded assets.
- After building, hand the `.app` (usually as a `.tar.gz`) to the sign/notarize path in [ship/direct.md](../ship/direct.md).
