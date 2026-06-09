When writing skills or orchestrating automated routines inside **Claude Code**, managing the context window isn't just about saving money—it's about **latency, execution accuracy, and preventing state corruption**.
Claude Code executes local CLI commands and reads files natively. If a skill blindly dumps full file contents or raw terminal outputs into the context window, it triggers **Token Bloat**. This causes Claude to lose track of the original instruction and slows down local execution loops.
The most practical token-reduction techniques for Claude Code skills focus on **Local Pre-Processing**—using lean, native scripts to compress information *before* Claude ever sees it.
## 1. Structural Tree Shaking for Code Base Navigation
When a skill needs to understand a codebase's layout to find where a bug might be, developers often run a recursive directory list or pass entire files. This consumes massive amounts of tokens.
 * **The Skill Idea:** /map-symbols
 * **Token-Reduction Mechanism:** Use local Language Server Protocol (LSP) tools or lightweight abstract syntax tree (AST) parsers (like Python’s native ast module or Node's typescript compiler API) to strip out all implementation details.
```markdown
# Instead of reading 10 full files (50,000 tokens):
# The skill runs a local script that extracts ONLY the declarations.

## Before (Raw Code):
function calculateTax(user) {
  // 300 lines of complex calculations, logging, and error handling
}

## After (What Claude Receives - 95% Token Reduction):
interface User { id: string; tier: 'premium' | 'standard'; }
function calculateTax(user: User): number;

```
## 2. Dynamic Git Diff Chunking & Line Anchoring
When building a git automation or code-review skill, passing a raw git diff of a large feature branch can easily devour 20,000+ tokens, much of which contains irrelevant context lines or massive auto-generated dependency lockfiles.
 * **The Skill Idea:** /lean-review
 * **Token-Reduction Mechanism:** A pre-processing bash/python wrapper that filters out noise using strict file extensions and chunking strategies before sending data to Claude.
| Step | Operation | Token-Saving Impact |
|---|---|---|
| **1. Ignore Lockfiles** | Automatically appends flags to drop package-lock.json, poetry.lock, or pnpm-lock.yaml. | Eliminates thousands of lines of raw JSON diffs. |
| **2. Chunking** | Splits the diff file-by-file. Instead of passing the whole diff, it passes only the file names and sizes first, letting Claude call for specific file chunks as needed. | Keeps the active context window lean and tightly focused. |
| **3. Summary Diffing** | Uses git diff --stat to give Claude a high-level overview before it explicitly requests a deep diff of a specific module. | Prevents reading unchanged boilerplate code. |
## 3. Log Stream "Squashing" & RegEx Sifting
If you create an error-triage skill (like the /parse-trace or /ci-triage tools discussed earlier), feeding an uncompressed server log file into Claude will quickly exhaust its context window with repetitive boilerplate text.
 * **The Skill Idea:** /compress-logs
 * **Token-Reduction Mechanism:** Use a local stream filter (like grep, awk, or a custom regex script) to squash repetitive lines into a singular counter.
> **Token Bloat Output (Avoid This):**
> [2026-06-09 06:00:01] INFO Connection pool heartbeat successful.  *(repeated 4,000 times)*
> [2026-06-09 06:45:12] ERROR Database connection timeout at line 42.
> **Squashed Output (What Claude Actually Sees):**
> [2026-06-09 06:00:01 to 06:45:00] INFO Connection pool heartbeat successful. (Skipped 4,211 duplicate entries)
> [2026-06-09 06:45:12] ERROR Database connection timeout at line 42.
> 
## 4. Database Schema Compression (Token-Efficient Reflection)
If you build a skill that interfaces with a local database to generate types or optimize queries, passing a full database dump (pg_dump) is incredibly token-heavy.
 * **The Skill Idea:** /compact-schema
 * **Token-Reduction Mechanism:** Write a script that queries the database's metadata table (information_schema) and converts it into an ultra-compact custom shorthand notation instead of verbose SQL scripts.
```text
-- Avoid sending raw DDL SQL (High Token Cost):
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Send custom compact representation instead (Low Token Cost):
users: id(int,pk), email(str,uniq), created_at(time)

```
## 5. Sliding-Window Self-Correction Loop
When Claude Code is placed in an autonomous code-and-execute verification loop (e.g., trying to fix a failing test suite), every single execution iteration adds the new terminal output to the chat history. By iteration 4, the history contains duplicate copies of the source file and multiple historical terminal dumps.
 * **The Skill Idea:** /iterative-heal
 * **Token-Reduction Mechanism:** Enforce a strict state-clearing command inside your skill configuration. Instead of carrying the entire conversational log forward, the skill instructions force Claude to use a stateless, single-turn execution pattern.
 1. Execute Tool
   Step 1
   Claude executes a command and writes a temporary state file locally (.claude_state.json) containing its current architectural assumptions.
 2. Wipe History
   Step 2
   The skill triggers an internal reset or instructs Claude to clear its current session conversation tokens.
 3. Hydrate State
   Step 3
   Claude reads the tiny local .claude_state.json file to pick up exactly where it left off, cleanly shedding thousands of tokens of old terminal history.
### Implementing Token Controls
