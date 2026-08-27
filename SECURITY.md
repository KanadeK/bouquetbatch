# Security policy

## Supported versions

The latest GitHub Release is supported. Before a later release exists, v0.1.x is the supported line.

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/KanadeK/bouquetbatch/security/advisories/new). Do not include exploit details in a public issue. Include the affected version, a minimal input, observed impact, and reproduction command. Never include customer records or credentials.

## Security boundary

Planning JSON is untrusted. BouquetBatch performs no network requests or shell execution at runtime, rejects fields outside the versioned schema, escapes HTML, and neutralizes spreadsheet formula prefixes in CSV text. An existing output directory is never overwritten.
