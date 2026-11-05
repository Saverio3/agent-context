# Need-to-know lab — 55 ChatDev multi-agent runs, 2340 messages, 1,958,110 tokens sent today

| Method | Tokens sent | Saved vs plain | Median per run | Miss rate |
|---|---|---|---|---|
| Plain text (today) | 1,958,110 | 0.0% | 0.0% | 0.0% |
| JSON envelope (A2A-style) | 2,085,185 | -6.5% | -5.8% | 0.0% |
| Refs + diffs (Pilot 2) | 1,314,224 | 32.9% | 28.3% | 0.0% |
| Refs + diffs + repeated-paragraph refs | 839,049 | 57.2% | 49.4% | 0.0% |
| Need-to-know: menu + pull | 948,136 | 51.6% | 43.7% | 0.0% |
| Need-to-know tree (fractal): file → function | 1,365,793 | 30.2% | 27.5% | 1.2% |
| Low-pass skeleton (epicycloid) + pull | 1,358,197 | 30.6% | 27.2% | 1.1% |

Tokens ≈ characters/4. Role system prompts are excluded (they are cacheable instructions, not messages). Pull methods assume the receiver asks for what its next reply mentions; requests cost 15 tokens each. Miss rate = receiver references to earlier content it could not see.

## Methods

- **Plain text (today)**: Every message sent in full, including full copies of every code file each time.
- **JSON envelope (A2A-style)**: Same content wrapped in a JSON message object, as agent-to-agent standards do.
- **Refs + diffs (Pilot 2)**: A file sent before unchanged becomes a short reference; a changed file is sent as only its changes.
- **Refs + diffs + repeated-paragraph refs**: Also: any paragraph already sent earlier (task text, requirements, instructions) becomes a reference.
- **Need-to-know: menu + pull**: Code is never pushed. The sender lists a menu line per file (name, size, what it defines). The receiver pulls a file only when it needs it; it gets just the changes if it has an older copy.
- **Need-to-know tree (fractal): file → function**: Two zoom levels. The menu shows file names and function names; the receiver pulls single functions it mentions, not whole files (whole file only if it names the file itself).
- **Low-pass skeleton (epicycloid) + pull**: Send the 'shape' of each file: imports, class and function signature lines, first docstring line. Function bodies (the fast-changing detail) are pulled only when mentioned.
