# Build: Tauri (Rust → macOS)

Tauri compiles a Rust backend with a web frontend into a macOS `.app` and bundles a DMG. The build is driven by `@tauri-apps/cli` and `tauri.conf.json`.

## Detect

- `tauri.conf.json` (in `src-tauri/`, or `.tauri/`.)

## Reason about it first

- The frontend must be built to `frontendDist` (config `build.frontendDist`, usually `../dist`) before Tauri bundles, via `beforeBuildCommand` (`build.beforeBuildCommand`, usually `npm run build`).
- Tauri needs an icon set at `src-tauri/icons/` before it can bundle.
- `bundle.targets` controls what is produced; `["dmg", "app"]` gives a DMG and a `.app`. `macOS.minimumSystemVersion` pins the floor.
- Signing is either automated (env vars that the CLI reads) or manual after build. If `bundle.macOS.signingIdentity` is empty, the CLI does not sign.

## Build

```bash
npm install                    # installs @tauri-apps/cli and the frontend deps
npm run build                  # must emit to build.frontendDist (creates ../dist)
npm run tauri build            # or: cargo tauri build
```

Equivalent: `cargo tauri build` in `src-tauri/`. Output lands under `src-tauri/target/release/bundle/macos/`.

## Build + sign in one pass (env vars)

```bash
APPLE_SIGNING_IDENTITY="Developer ID Application: <Name> (<TEAMID>)" \
APPLE_API_KEY="$HOME/.appstoreconnect/private_keys/AuthKey_<KEYID>.p8" \
APPLE_API_KEY_ID="<KEYID>" \
APPLE_API_ISSUER="<ISSUER_ID>" \
APPLE_TEAM_ID="<TEAMID>" \
npm run tauri build
```

Otherwise build unsigned, then sign + notarize manually (see [ship/direct.md](../ship/direct.md)).

## Gotchas

- If `frontendDist` or the icon set is missing, `tauri build` fails with a config/asset error even though the Rust code compiles.
- If `package.json` has no `build` script (`beforeBuildCommand`), the CLI cannot produce the frontend and exits with "could not determine executable to run". Either add the script or drop `beforeBuildCommand`.
- Do not rely on `codesign --deep` for Tauri output; sign nested bundles in order and use `spctl --assess --type open --context context:primary-signature` for the DMG.
- Tauri can require Rust tooling (`rustc`/`cargo`) that is not installed on a bare machine; bootstrapping Rust alone is not the same as producing a signed release.
- After building, hand the `.app`/`.dmg` to the sign/notarize path in [ship/direct.md](../ship/direct.md).
