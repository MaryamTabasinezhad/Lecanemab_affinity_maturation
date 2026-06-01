# Agent Inbox System

Inter-agent messaging via git. Each agent has an inbox directory.

## Protocol
1. To send a message: write a `.md` file in `inbox/<recipient>/`.
2. Commit with a `[<sender>] msg: <subject>` prefix and push.
3. The recipient picks it up on the next `git pull`.
4. The recipient DELETES the file after reading and commits (delete on read, always).

## Filename
`YYYY-MM-DD_from-<sender>_<subject-slug>.md`

## Message template
```
# Message from <Sender>

**Date:** YYYY-MM-DD
**From:** <sender cluster>
**To:** <recipient cluster>
**Subject:** <one-line summary>

---

<body — be specific: exact command, thresholds, and output paths>
```
