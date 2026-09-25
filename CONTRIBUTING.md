# Contributing

Thanks for your interest in gitlab-version.

## Issues

Bug reports, questions and ideas are welcome as issues. Please describe what you ran, what you expected and what happened instead.

## Support

This is a personal project maintained in spare time. There is no guaranteed support, response time or roadmap. Pull requests may be declined if they do not fit the scope of the project.

## Developer Certificate of Origin

Every commit must be signed off to certify that you wrote the change or otherwise have the right to submit it under the project's MIT license, as described in the [Developer Certificate of Origin](https://developercertificate.org).

Sign off by committing with `-s`:

```bash
git commit -s -m "Describe your change"
```

This adds a `Signed-off-by: Your Name <you@example.com>` line to the commit message. Commits without it cannot be merged.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m unittest discover -s tests -v
```

The test suite mocks all GitLab API calls and needs no token.
