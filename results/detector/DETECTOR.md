# On-device and network AI detector pilot

### A. Is an AI model running on this computer? (process signals)

| Workload (never seen in training) | AI? | Windows | Flagged as AI |
|---|---|---|---|
| ai_batch_bench | yes | 15 | 0% |
| ai_server | yes | 15 | 100% |
| compile_gcc | no | 15 | 0% |
| compress_xz | no | 15 | 0% |
| hash_sha | no | 15 | 0% |
| numpy_bigarray | no | 15 | 0% |
| numpy_matmul | no | 15 | 0% |
| sqlite_db | no | 15 | 0% |
| video_ffmpeg | no | 15 | 0% |

Average detection of unseen AI workloads: **50%** · average false alarm on unseen ordinary workloads: **0%**

Most telling signals: file_mb (1.00), rss_mb (0.00), sys_share (0.00), file_share (0.00), threads (0.00)

### B. Is an AI model split across devices? (network traffic only)

Not tested: no AI windows were captured in this run.

