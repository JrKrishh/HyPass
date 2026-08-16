# Contributing to HyPass

## Running the tests

The test suite uses the Python standard library's `unittest`. From the repo root:

```bash
pip install -r requirements.txt   # Pillow, pikepdf
sudo apt-get install -y ffmpeg    # for the media stripper test (optional locally)
python -m unittest discover -s tests -v
```

Tests that need an optional dependency skip cleanly when it's absent (the image test skips without Pillow, the media test without ffmpeg), so a partial toolchain still runs green. CI installs everything and runs the full suite on every push and PR.

## Commit and PR style

Commits and PRs are authored by the account holder, in a plain human style — no AI attribution trailers or "Generated with" footers. See the `git-human-commits` skill for the full convention:

- Short imperative subjects (`Add X`, `Fix Y`), no emojis, no trailing period
- Bodies only when they add information, in a sentence or two

## Verified commits (optional)

To get the green **Verified** badge on your commits, sign them with an SSH key registered to your GitHub account. Generate the key **on your own machine** (the private key must never leave it):

```bash
ssh-keygen -t ed25519 -C "you@example.com" -f ~/.ssh/git-signing
cat ~/.ssh/git-signing.pub   # add this to GitHub as a *Signing Key*
```

GitHub → **Settings → SSH and GPG keys → New SSH key** → **Key type: Signing Key** → paste the public key. Then tell git to sign:

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/git-signing.pub
git config --global commit.gpgsign true
```

Signing is cosmetic — it attests authorship and does not affect the code or CI.
