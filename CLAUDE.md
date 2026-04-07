# Global Claude Code Rules

## Commit Authorship

**Commit author is ONLY the user.** Never add `Co-Authored-By`, `Co-authored-by`, or any Claude/AI attribution to commit messages. Not in the message body, not in trailers, nowhere. The user writes or approves every commit — Claude's role is invisible.

## Never Commit Claude Files

**Never commit `.claude/` folders or files to git.** This includes `.claude/`, `CLAUDE.md` files inside `.claude/`, memory files, session files, or anything else under a `.claude/` directory. If `.claude/` is not already in `.gitignore`, add it before committing.
