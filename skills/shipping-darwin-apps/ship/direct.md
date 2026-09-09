# Ship: Direct macOS (Developer ID, notarize, DMG)

For macOS desktop apps distributed outside the Mac App Store, especially when a CI builds a `.app`, packages a `.dmg`, signs with Developer ID, notarizes with Apple, and verifies Gatekeeper acceptance.

## Inputs

Collect these without exposing secrets:

- Apple Developer Team ID.
- Developer ID Application identity or exported `.p12` with matching private key.
- Notarization auth: App Store Connect API key, or Apple ID app-specific password.
- Bundle identifier, app display name, and hardened runtime or entitlement needs.
- Artifact target: `.app`, `.zip`, `.dmg`, or a combination.
- Release mode: branch artifact, draft release, tag release, or manual upload.

## Certificate prep

Inspect local signing identities:

```bash
security find-identity -v -p codesigning
```

Confirm the expected identity is `Developer ID Application: ...` and has a matching private key in Keychain Access. Export a password-protected `.p12`, then base64 encode it for CI:

```bash
base64 -i DeveloperIDApplication.p12 | pbcopy
```

Use a strong random export password and store it separately from the encoded certificate. **If the matching private key is missing, stop.** A downloaded Developer ID certificate alone cannot produce a usable signing identity.

## GitHub Secrets

Use consistent secret names in app repositories and reusable workflows:

- `APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_P12_BASE64`
- `APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_PASSWORD`
- `APPLE_TEAM_ID`
- `APPLE_BUNDLE_ID`
- `APPLE_ID` and `APPLE_APP_SPECIFIC_PASSWORD`, if using Apple ID auth.
- `APPLE_API_KEY_ID`, `APPLE_API_ISSUER_ID`, and `APPLE_API_PRIVATE_KEY`, if using App Store Connect API auth.

Prefer App Store Connect API keys for automation when the workflow supports them.

## CI keychain pattern

Create a temporary keychain, import the `.p12`, unlock it, restrict key access, and clean it up at the end of the job.

```bash
CERT_PATH="$RUNNER_TEMP/developer-id.p12"
KEYCHAIN_PATH="$RUNNER_TEMP/app-signing.keychain-db"

echo "$APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_P12_BASE64" | base64 --decode > "$CERT_PATH"
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security import "$CERT_PATH" -P "$APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_PASSWORD" -A -t cert -f pkcs12 -k "$KEYCHAIN_PATH"
security list-keychain -d user -s "$KEYCHAIN_PATH"
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security find-identity -v -p codesigning "$KEYCHAIN_PATH"
```

## Signing checks

After building the app bundle:

```bash
codesign --force --deep --options runtime --timestamp \
  --sign "Developer ID Application: Example Team (TEAMID1234)" \
  path/to/App.app

codesign --verify --deep --strict --verbose=2 path/to/App.app
spctl --assess --type execute --verbose=4 path/to/App.app
```

Sign nested helpers, frameworks, login items, and extensions according to the app's packaging tool requirements. Do not rely on `--deep` as a substitute for fixing an incorrect bundle signing order.

## Notarization

Use `xcrun notarytool`, not legacy `altool`:

```bash
xcrun notarytool submit path/to/App.dmg \
  --apple-id "$APPLE_ID" \
  --team-id "$APPLE_TEAM_ID" \
  --password "$APPLE_APP_SPECIFIC_PASSWORD" \
  --wait

xcrun stapler staple path/to/App.dmg
xcrun stapler validate path/to/App.dmg
```

For API key auth, use the repository's supported `notarytool` API key flags or a stored notarytool profile.

## Gatekeeper verification

Assess the app bundle:

```bash
spctl --assess --type execute --verbose=4 path/to/App.app
```

For signed DMGs, verify the primary signature context instead of treating `--type install` failures as definitive:

```bash
spctl --assess --type open --context context:primary-signature --verbose=4 path/to/App.dmg
```

When practical, test the user path: mount the DMG, copy the app to `/Applications`, and assess or launch the copied app on a clean macOS environment.

## GitHub Actions notes

- Prefer the shared workflow in `vuon9/gh-workflows`: `.github/workflows/macos-release.yml`.
- Keep app-specific build systems (Wails, Xcode, Electron, or custom scripts) in the caller repository. The reusable workflow should consume an uploaded `.app` archive, then handle Developer ID signing, notarization, DMG packaging, and release artifacts.
- Pin third-party actions and tools to stable versions.
- Separate branch artifact runs from tag release runs. A branch run can prove sign/notarize is green while release asset upload is skipped because there is no tag.
- Upload signed and notarized artifacts on manual branch runs so they can be inspected before tagging.
- Keep reusable workflow inputs small: app name, team id, app artifact name, app path, DMG name, artifact name, runner, and release mode.

## Reusable workflow

Use `vuon9/gh-workflows/.github/workflows/macos-release.yml` when the caller workflow can upload a `.tar.gz` archive containing the built `.app` bundle.

Caller wrapper shape:

```yaml
name: macOS Release

on:
  workflow_dispatch:
  push:
    tags:
      - "v*"

jobs:
  build:
    runs-on: macos-26
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-go@v6
        with:
          go-version-file: go.mod
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      - run: task package:macos
      - run: tar -czf "$RUNNER_TEMP/macos-app.tar.gz" -C build/bin DevToolbox.app
      - uses: actions/upload-artifact@v7.0.1
        with:
          name: devtoolbox-macos-app-${{ github.run_id }}
          path: ${{ runner.temp }}/macos-app.tar.gz

  release:
    needs: build
    uses: vuon9/gh-workflows/.github/workflows/macos-release.yml@v0.2.0
    with:
      app-name: DevToolbox
      team-id: ${{ vars.APPLE_TEAM_ID }}
      app-path: build/bin/DevToolbox.app
      app-artifact-name: devtoolbox-macos-app-${{ github.run_id }}
      dmg-name: DevToolbox-${{ github.ref_name }}.dmg
      artifact-name: devtoolbox-macos-release
    secrets:
      APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_P12_BASE64: ${{ secrets.APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_P12_BASE64 }}
      APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_DEVELOPER_ID_APPLICATION_CERTIFICATE_PASSWORD }}
      APP_STORE_CONNECT_API_KEY_P8: ${{ secrets.APP_STORE_CONNECT_API_KEY_P8 }}
      APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}
      APP_STORE_CONNECT_API_ISSUER_ID: ${{ secrets.APP_STORE_CONNECT_API_ISSUER_ID }}
      MACOS_CODESIGN_IDENTITY: ${{ secrets.MACOS_CODESIGN_IDENTITY }}
```

Before recommending it, verify the workflow contract still matches the app:

- Required inputs: `app-name`, `team-id`, `app-path`, `app-artifact-name`, and `dmg-name`.
- Optional inputs include `working-directory`, `app-archive-name`, `artifact-name`, `runner-label`, `upload-github-release`, and `github-release-prerelease`.
- Required secrets use App Store Connect API key notarization: `APP_STORE_CONNECT_API_KEY_P8`, `APP_STORE_CONNECT_API_KEY_ID`, and `APP_STORE_CONNECT_API_ISSUER_ID`.
- The workflow uploads a signed DMG artifact on all successful runs and uploads a GitHub Release asset only for tag refs when `upload-github-release` is true.
- Pin to a version tag when one exists. Use `@main` only for active testing or when the workflow repo has not published a stable tag yet.

## Troubleshooting

- `no identity found`: the `.p12` may not include the private key, or CI imported it into the wrong keychain.
- `User interaction is not allowed`: unlock the keychain and run `security set-key-partition-list`.
- `The specified item could not be found in the keychain`: confirm the signing command sees the same keychain used for import.
- Notarization rejected: fetch the notary log and inspect hardened runtime, unsigned nested code, entitlements, invalid bundle IDs, or embedded archives.
- DMG `spctl` mismatch: verify both the `.app` and DMG with the correct assessment type and context.
- Release upload skipped: check whether the workflow is running on a tag and whether publishing is gated by `github.ref_type == 'tag'`.

## Completion checklist

Before reporting the release pipeline ready:

1. GitHub Actions run completed successfully.
2. `codesign` verification passed for the app bundle.
3. Notarization completed and stapling validation passed.
4. DMG Gatekeeper assessment used `context:primary-signature` when applicable.
5. The artifact exists, with branch artifact versus tag release asset clearly stated.
6. The report includes the workflow run URL and artifact name without revealing secrets.

Reusable `workflow_call` design details live in the `gh-workflows` skill in the `vuon9/gh-workflows` repo.
