# Build: Electron (JS → macOS)

Electron is packaged for macOS with `electron-builder`. Signing and notarization are configured in `package.json` `build.mac` or passed via env vars.

## Detect

- `package.json` with `electron` and/or `electron-builder` in devDependencies.

## Reason about it first

- `electron-builder` does the signing, notarization, and DMG packaging during the build, so most of the delivery is inside the build step. Configure `build.mac` first.
- `hardenedRuntime: true` and an entitlements file are expected for notarizable distribution outside the App Store. Without entitlements, notarization can be rejected.
- `appId` and `productName` drive the bundle identity; they must be stable and match what you registered.
- Tauri/Wails need manual signing; Electron often automates it, but that automation depends on the signing identity being present in the keychain (or on `CSC_NAME`).

## Configure `build.mac`

```json
"mac": {
  "target": ["dmg"],
  "category": "public.app-category.productivity",
  "hardenedRuntime": true,
  "gatekeeperAssess": false,
  "entitlements": "build/entitlements.mac.plist",
  "entitlementsInherit": "build/entitlements.mac.plist"
}
```

Standard Electron entitlements (`build/entitlements.mac.plist`) usually allow `allow-jit`, `allow-unsigned-executable-memory`, `allow-dyld-environment-variables`, and `disable-library-validation`.

## Build

```bash
npm install
CSC_NAME="Developer ID Application: <Name> (<TEAMID>)" npx electron-builder --mac
```

Output lands in `dist/` with the `.app` and the DMG.

## Sign + notarize

Electron can notarize during the build if `build.mac.notarize` is enabled and the App Store Connect API key env vars are set. Otherwise build unsigned, then notarize the `.app`/DMG manually:

```bash
xcrun notarytool submit "dist/<App>-<version>-<arch>.dmg" \
  --key ~/.appstoreconnect/private_keys/AuthKey_<KEYID>.p8 \
  --key-id <KEYID> --issuer "$APP_STORE_CONNECT_API_ISSUER_ID" --wait
xcrun stapler staple "dist/<App>-<version>-<arch>.dmg"
xcrun stapler validate "dist/<App>-<version>-<arch>.dmg"
```

## Gotchas

- Without an entitlements file, `hardenedRuntime` alone may not satisfy notarization signature verification.
- The signing identity must be in the keychain with its private key, or `CSC_NAME`/keychain import must supply it. Otherwise electron-builder falls back to ad-hoc signing, which fails Gatekeeper.
- `gatekeeperAssess: false` is normal during build; do the real `spctl` assessment after stapling (see [ship/direct.md](../ship/direct.md)).
- The version in `package.json` and the app display name must match the identity you registered.
- For CI, wire this build into the reusable workflow (see the `gh-workflows` skill in the `vuon9/gh-workflows` repo).
