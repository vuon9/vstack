# Ship: App Store / TestFlight (iOS)

For iOS apps distributed via the App Store or internal TestFlight, using GitHub Actions and App Store Connect API keys. The goal is a repeatable upload with a small repo wrapper, private credentials, and evidence before any success claim.

## Preflight

Check the app repo:

```bash
git status --short --branch
rg -n "PRODUCT_BUNDLE_IDENTIFIER|MARKETING_VERSION|CURRENT_PROJECT_VERSION|DEVELOPMENT_TEAM" project.yml *.xcodeproj/project.pbxproj
find . -name "*.xcscheme" -maxdepth 5
```

Check local build health:

```bash
xcrun simctl list devices available
xcodebuild test -project App.xcodeproj -scheme App -destination "platform=iOS Simulator,name=<available iPhone simulator>"
```

If tests fail, stop and report the failure. Do not upload a release build unless the user explicitly accepts the risk.

## Secrets

The caller repository needs GitHub Actions secrets:

- `APP_STORE_CONNECT_API_KEY_P8`
- `APP_STORE_CONNECT_API_KEY_ID`
- `APP_STORE_CONNECT_API_ISSUER_ID`

Set or verify secrets without printing values:

```bash
gh secret list --repo owner/app
gh secret set APP_STORE_CONNECT_API_KEY_P8 --repo owner/app < AuthKey_EXAMPLE.p8
printf "%s" "$APP_STORE_CONNECT_API_KEY_ID" | gh secret set APP_STORE_CONNECT_API_KEY_ID --repo owner/app
printf "%s" "$APP_STORE_CONNECT_API_ISSUER_ID" | gh secret set APP_STORE_CONNECT_API_ISSUER_ID --repo owner/app
```

## Workflow wrapper

Prefer a thin wrapper that calls a reusable workflow. The public `vuon9/gh-workflows` repository can be reused directly for iOS TestFlight uploads, or forked if the project needs its own contract. Pin to the exact tested reusable workflow version:

```yaml
uses: vuon9/gh-workflows/.github/workflows/ios-testflight.yml@v0.1.8
```

Keep the caller wrapper small:

```yaml
name: TestFlight

on:
  workflow_dispatch:
    inputs:
      dry-run:
        type: boolean
        default: true
      skip-tests:
        type: boolean
        default: true
      skip-cert-check:
        type: boolean
        default: true

jobs:
  testflight:
    uses: vuon9/gh-workflows/.github/workflows/ios-testflight.yml@v0.1.8
    with:
      project-path: App.xcodeproj
      scheme: App
      team-id: TEAMID1234
      dry-run: ${{ inputs.dry-run }}
      skip-tests: ${{ inputs.skip-tests }}
      skip-cert-check: ${{ inputs.skip-cert-check }}
      runner-label: macos-26
    secrets: inherit
```

Use a runner with the SDK currently required by App Store Connect.

## Release flow

1. Create or update the wrapper.
2. Bump `CURRENT_PROJECT_VERSION` above the latest uploaded build.
3. Run local tests.
4. Run GitHub Actions dry-run.
5. Run real upload.
6. Inspect logs and report evidence.

Commands:

```bash
gh workflow run testflight.yml --repo owner/app --ref main -f dry-run=true -f skip-tests=true -f skip-cert-check=true
gh run watch RUN_ID --repo owner/app --exit-status

gh workflow run testflight.yml --repo owner/app --ref main -f dry-run=false -f skip-tests=true -f skip-cert-check=true
gh run watch RUN_ID --repo owner/app --exit-status
```

## Completion evidence

Report only after verification. Include:

- Local test command and result.
- Dry-run URL and conclusion.
- Real upload URL and conclusion.
- Runner image.
- Reusable workflow version.
- Log markers such as `ARCHIVE SUCCEEDED`, `Upload succeeded`, uploaded app name, and `EXPORT SUCCEEDED`.

## Troubleshooting

- Duplicate build number: bump `CURRENT_PROJECT_VERSION`.
- SDK version rejection: switch to a newer macOS/Xcode runner.
- Missing API credentials: set the three App Store Connect secrets.
- Missing signing identity preflight: either install a distribution identity or use an automatic-signing workflow that supports skipping local cert preflight.
- Reusable workflow checkout failure: ensure the workflow checks out tools using the called workflow repository and SHA, not the caller repository SHA.

Workflow `workflow_call` design details live in the `gh-workflows` skill in the `vuon9/gh-workflows` repo.
