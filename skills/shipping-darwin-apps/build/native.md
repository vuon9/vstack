# Build: Native (Xcode / Swift / ObjC)

Native iOS and macOS apps are built with `xcodebuild` from an `.xcodeproj`, `.xcworkspace`, `project.yml` (XcodeGen), or a Swift Package (`Package.swift`).

## Detect

- `.xcodeproj` / `.xcworkspace` / `project.yml` / `Package.swift`.

## Reason about it first

- The scheme is the build entry point. Confirm the shared scheme exists before archiving.
- `xcodebuild` requires a selected full Xcode; if `xcode-select` points at CommandLineTools, `xcodebuild`/`xcrun` fail from PATH even when Xcode is installed.
- Version and build come from `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION` (or the `Info.plist`). Bump `CURRENT_PROJECT_VERSION` above the last uploaded build to avoid a duplicate-build rejection.
- iOS and macOS have separate `-destination` values; a generic device build ("generic/platform=iOS") is what archives for distribution.

## Build for simulator / local test

```bash
xcrun simctl list devices available
xcodebuild test -project App.xcodeproj -scheme App \
  -destination "platform=iOS Simulator,name=<available simulator>"
```

## Archive for distribution

```bash
xcodebuild archive -project App.xcodeproj -scheme App \
  -configuration Release -destination "generic/platform=iOS" \
  -archivePath build/App.xcarchive
```

For macOS, use `-destination "generic/platform=macOS"` (or `platform=macOS`).

Then `xcodebuild -exportArchive` (or the workflow) exports the `.ipa`/`.app` for upload. For signing, `CODE_SIGN_STYLE`/`DEVELOPMENT_TEAM` are set in the build settings or passed on the command line.

## Gotchas

- Duplicate build number: bump `CURRENT_PROJECT_VERSION` above the latest uploaded build.
- Missing simulator: change the destination or install a matching runtime.
- SDK rejection on upload: the selected Xcode may lack the SDK Apple requires; use a newer Xcode/macOS runner.
- Missing signing identity: create/download the certificate, or use automatic signing on a capable runner.
- `xcodebuild` does not follow a tarred/embedded `Info.plist`; the archive is the artifact to hand to the ship path.
- After archiving, hand the `.ipa`/`.app` to the ship docs: [ship/appstore.md](../ship/appstore.md) (iOS) or [ship/direct.md](../ship/direct.md) (macOS out of store).
