# Portable setup

A complete workspace on any arm64 Android device, without root, in about 30
minutes. SSH for the operator, `GITHUB_TOKEN` for workflows; no personal access
tokens.

Reference build: Redmi `25062RN2DL`, Android 16, 6 GB RAM, 108 GB storage,
Alpine 3.24 in `proot-distro`, opencode v2.2.7.

## Minimum requirements

| Resource | Minimum | Comfortable | Why |
| --- | --- | --- | --- |
| CPU | arm64, 4 cores | 6 to 8 cores | proot adds overhead |
| RAM | 8 GB | 12 GB | video call, screen share, browser tabs |
| Storage | 128 GB | 256 GB | toolchain and repositories use under 5 GB |
| Android | 12 | 14 or newer | Termux background execution |
| Other | USB-C, 5000 mAh | tablet or kickstand | long review sessions |

No GPU, fan, or root is required. CI runs in GitHub Actions; the device is a
terminal and a review screen.

## Rootless path

Run `proot-distro` as the normal Termux user, never as root.

```bash
termux-wake-lock
pkg update
pkg install proot-distro
proot-distro install alpine
proot-distro login alpine
apk add git curl python3 bash jq github-cli openssh
```

Install opencode and register the API key:

```bash
# official installer, or: npm install -g opencode-ai
opencode auth login
```

## SSH key

```bash
ssh-keygen -t ed25519 -C "operator@<device>" -f ~/.ssh/id_ed25519_github
cat ~/.ssh/id_ed25519_github.pub
```

Add the public key under **Settings → SSH and GPG keys → New SSH key** in GitHub.
Then:

```bash
ssh -T git@github.com
```

Create `~/.ssh/config`:

```sshconfig
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```

## Workspace

```bash
mkdir -p ~/github/{contract,dashboard,database,game,package,workflow,meta}
git clone git@github.com:gardusi-gustavo/package-yml.git ~/github/meta/package-yml
```

Clone the rest with their SSH URLs; the list is in `workspace.json`. No further
credential setup is needed.

## Private repository

`gardusi-gustavo/private` can be cloned with the same SSH key, operator only. It
has no workflow and no automation access.

## Security

- the SSH key is the only credential on the device;
- protect it with device encryption and a lock screen;
- store a backup of the key and its passphrase offline;
- revoke the key per device if the device is lost;
- never place the private key in a repository or a workflow.

## Recovery drill

Once a month, prove a fresh device can rebuild the workspace: Termux, Alpine,
tools, SSH key, clone, run a local test. If it takes longer than 30 minutes, fix
the instructions.

## Related

- [Local workspace](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/local-workspace.md)
- [Operating model](https://github.com/gardusi-gustavo/contract-json/blob/main/docs/runbooks/operating-model.md)
