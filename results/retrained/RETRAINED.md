# Does the fingerprint survive hacker modification?

Commands for 30 everyday admin tasks (x2). Trained on original models (llama, mistral, qwen) using half the tasks; tested on the other half. Random = 33%.

| Tested on | Answers | Named the right family |
|---|---|---|
| Original models (unseen tasks) | 90 | 52% |
| Llama-3.1-8B-abliterated (safety removed) | 30 | 60% |
| Qwen2.5-7B-uncensored-abl (safety removed) | 30 | 47% |

## Bait: original vs safety-removed

| Model | Ordinary result | Best lure | Average lure |
|---|---|---|---|
| Llama-3.1-8B-abliterated | 7% | 94% | 77% |
| Llama-3.1-8B | 9% | 84% | 69% |
| Mistral-7B | 13% | 86% | 60% |
| Qwen2.5-7B-uncensored-abl | 9% | 97% | 68% |
| Qwen2.5-7B | 9% | 94% | 69% |
