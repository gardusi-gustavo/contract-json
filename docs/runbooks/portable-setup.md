# Portable setup

A complete workspace on any arm64 Android device, without root, in about 30 minutes.

Reference build: Redmi `25062RN2DL`, Android 16, 6 GB RAM, 108 GB storage,
Alpine 3.24 in `proot-distro`, opencode v2.2.7, 43 repositories at 34 MB.

## Minimum requirements

| Resource | Minimum | Comfortable | Why |
| --- | --- | --- | --- |
| CPU | arm64, 4 cores | 6 to 8 cores | proot adds 5 to 15 percent overhead |
| RAM | 8 GB | 12 GB | video call, screen share, and browser tabs |
| Storage | 128 GB | 256 GB | Alpine, opencode, and repositories use under 3 GB |
| Android | 12 | 14 or newer | Termux and background execution |
| Other | USB-C, 5000 mAh | tablet or kickstand | long review sessions |

No GPU, fan, or root is required. CI and the agent run in GitHub Actions; the
device is a terminal and a review screen.

A phone around R$1,000 is enough. A tablet with a larger screen and battery is
better for review and meetings, and the keyboard can stay optional.

## Rootless path (recommended)

Run everything as the normal Termux user. Never run `proot-distro` as root.

1. Install Termux from F-Droid, then keep it alive:

   ```bash
   termux-wake-lock
   ```

   Disable battery optimisation for Termux in Android settings.

2. Install the Alpine container:

   ```bash
   pkg update
   pkg install proot-distro
   proot-distro install alpine
   proot-distro login alpine
   ```

3. Install the tools inside Alpine:

   ```bash
   apk add git curl python3 bash jq github-cli
   ```

4. Install opencode and register the API key:

   ```bash
   # official installer, or: npm install -g opencode-ai
   opencode auth login
   ```

5. Prepare the workspace:

   ```bash
   mkdir -p ~/github/{contract,dashboard,database,game,package,workflow,meta}
   git clone https://github.com/gardusi-gustavo/contract-json ~/github/contract/contract-json
   cd ~/github/contract/contract-json
   python3 scripts/workspace.py init --root ~/github --expires <date>
   ```

6. Register the seven tokens and clone:

   ```bash
   python3 scripts/workspace.py add contracts  --token-file ~/.gh-token-contracts
   python3 scripts/workspace.py add dashboards --token-file ~/.gh-token-dashboards
   python3 scripts/workspace.py add databases  --token-file ~/.gh-token-databases
   python3 scripts/workspace.py add games      --token-file ~/.gh-token-games
   python3 scripts/workspace.py add packages   --token-file ~/.gh-token-packages
   python3 scripts/workspace.py add workflows  --token-file ~/.gh-token-workflows
   python3 scripts/workspace.py add github     --token-file ~/.gh-token-github
   python3 scripts/workspace.py clone
   ```

7. Verify:

   ```bash
   python3 scripts/workspace.py verify --workflows
   python3 scripts/workspace.py check
   ```

The token files can be deleted after registration; credentials live in
`~/.config/gh/domains/<domain>/hosts.yml`.

## Rooted appendix (optional)

A rooted device can run Alpine through `chroot` instead of proot, removing the
5 to 15 percent CPU overhead. Root is not a security boundary for tokens and it
breaks Play Integrity, so use it only if the device is dedicated to this work.

Rooting, Magisk modules, and kernel choices are out of scope for this runbook.
The rest of the setup is identical.

## Device matrix

| Device | Setup | Review | Meetings | Cost | Verdict |
| --- | --- | --- | --- | --- | --- |
| Phone, 8 GB | 30 min | cramped for large diffs | workable | lowest | daily carry |
| Tablet, 8 to 12 GB | 30 min | best | best | moderate | primary if review-heavy |
| Laptop | 1 to 2 h | best | best | highest | unnecessary |
| iPad | not supported | good | good | high | review-only, no Termux |

Avoid iPad as the setup device: it cannot run Termux or a Linux container.

## Security

- proot is not a sandbox; `~/.config/gh` holds plaintext tokens;
- rely on device encryption and a strong lock screen;
- exclude `~/.config/gh` from Google backup;
- revoke tokens immediately if the device is lost;
- keep the seven token values in a password manager for recovery.

## Recovery drill

Once a month, prove that a fresh device can rebuild the workspace: new Termux,
Alpine, opencode, seven tokens, `init`, `add`, `clone`, `verify`. If it takes
longer than 30 minutes, fix the instructions rather than the device.

## Related

- [Local workspace](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/local-workspace.md)
- [Operating model](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/operating-model.md)
