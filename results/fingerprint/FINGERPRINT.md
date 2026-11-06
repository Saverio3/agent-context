# Fingerprinting pilot — 4964 runs, 10 models (≥60 runs each)

Train/test split by task: the same task never appears in both.

## A. Which model is it?

| Evidence seen | Accuracy |
|---|---|
| Guessing the most common model (baseline) | 10.1% |
| First 3 steps only | 58.5% |
| First 25% of the run | 65.2% |
| First half of the run | 74.2% |
| Whole run | 85.2% |

| Model | Test runs | Correctly identified |
|---|---|---|
| claude-4-5-haiku-high | 126 | 79% |
| claude-4-5-opus-high | 126 | 97% |
| claude-4-5-sonnet-high | 126 | 86% |
| claude-4-6-opus | 126 | 98% |
| deepseek-3-2-high | 126 | 95% |
| kimi-k2-5-high | 126 | 73% |
| minimax-2-5-high | 126 | 86% |
| gemini-3-pro-high | 125 | 83% |
| gemini-3-flash-high | 124 | 85% |
| glm-5-high | 123 | 69% |

Strongest giveaways per model (top 6 habits):

- **claude-4-5-haiku-high**: o_i'll_help, f_heading, b_find_ls, o_perfect_let, o_perfect_the, a_wc
- **claude-4-5-opus-high**: o_i'll_start, o_let_me, o_i'll_analyze, o_the_patch, b_pip_pip, o_i_need
- **claude-4-5-sonnet-high**: o_i'll_help, l_1, b_ls_find, o_perfect_the, o_i'll_start, a_ls
- **claude-4-6-opus**: o_now_let, o_good_now, o_the_patch, o_the_fix, l_1, b_cat_echo
- **deepseek-3-2-high**: a_pwd, a_cp, b_pwd_find, b_pwd_grep, b_grep_pip, a_awk
- **gemini-3-flash-high**: b_cat_pip, b_grep_grep, a_pytest, b_pytest_python, b_git_echo, a_i
- **gemini-3-pro-high**: b_cat_echo, a_read_file, b_cat_python, a_ls, b_python_grep, b_python_cat
- **glm-5-high**: a_print, b_find_cat, b_echo_echo, a_default, b_head_echo, a_find
- **kimi-k2-5-high**: o_let_me, a_command, a_find, b_git_echo, b_find_cat, o_the_fix
- **minimax-2-5-high**: o_now_let's, o_i'll_analyze, o_now_i, o_i_need, o_thought_let, b_git_python

## B. Can we predict its next move? (second half of each test run)

| Predictor | Next command type correct |
|---|---|
| Generic (all models pooled) | 37.8% |
| Specialised to the model the fingerprint guessed | 38.2% |
| Specialised to the true model (upper bound) | 38.8% |

Predictions scored: 34,743. Command types: 363 distinct.
