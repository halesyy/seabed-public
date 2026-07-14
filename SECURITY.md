# Security

## API keys

Never commit, log, print, or paste a Seabed API key into an issue, pull request, prompt, or agent handoff document. The CLI reads the key from the environment variable named by `token_env` (default: `SEABED_TOKEN`). Use the secret-management feature of your agent or automation runtime where available.

If a key is exposed, revoke it immediately at <https://seabed.jackhalestesting.xyz/connect> and create a replacement.

## Reports

Please report suspected vulnerabilities privately through GitHub's security advisory feature for this repository. Do not include a live key, private Seabed content, or personal data in the report.
