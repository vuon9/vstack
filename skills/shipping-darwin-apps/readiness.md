# Readiness

Run these checks before any build or release, especially if the environment is uncertain or this is a first release. Verify with local tools before claiming readiness.

## Environment checks

```bash
xcodebuild -version
xcode-select -p
xcrun simctl list runtimes
xcrun simctl list devices available
security find-identity -p codesigning -v
```

For App Store Connect uploads, verify the selected Xcode includes the SDK currently required by Apple. If upload fails with an SDK version rejection, move the workflow to a newer macOS/Xcode runner.

## Project checks

Inspect these before release work:

- Bundle ID and test bundle ID.
- `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION`.
- `DEVELOPMENT_TEAM`, signing style, entitlements, and capabilities.
- Shared scheme availability.
- Test destination exists on the current machine or runner.

Useful searches:

```bash
rg -n "PRODUCT_BUNDLE_IDENTIFIER|MARKETING_VERSION|CURRENT_PROJECT_VERSION|DEVELOPMENT_TEAM" .
find . -name "*.xcscheme" -maxdepth 5
```

## Verification

Use the project's existing commands when present. Otherwise prefer:

```bash
xcrun simctl list devices available
xcodebuild test -project App.xcodeproj -scheme App -destination "platform=iOS Simulator,name=<available iPhone simulator>"
xcodebuild archive -project App.xcodeproj -scheme App -configuration Release -destination "generic/platform=iOS" -archivePath build/App.xcarchive
```

Before reporting success, capture the exact command, exit code, and key output such as `TEST SUCCEEDED`, `ARCHIVE SUCCEEDED`, or the concrete failure message.

## Common failures

- Duplicate build number: bump `CURRENT_PROJECT_VERSION` above the latest uploaded build.
- Missing simulator: change destination or install a matching runtime.
- Missing signing identity: create/download the certificate or use automatic signing on a capable runner.
- SDK rejection: use Xcode with the required SDK, often by selecting a newer hosted runner.
- App Store Connect auth failure: verify repository secrets and issuer/key IDs without printing secret values.
- `xcode-select` points to CommandLineTools: select a full Xcode path so `xcodebuild`/`xcrun` work from PATH.
