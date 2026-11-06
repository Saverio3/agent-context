# eBird for agents: how many sensors are needed?

Time until the network has 5 sightings of a new AI-agent campaign (enough to name the model ~99% of the time by majority vote; 1 sighting: 85%, 3: 96%, 9: 100%).

| Installed sensors | stealthy (1,000 probes/h) | moderate (100,000/h) | aggressive (10 million/h) |
|---|---|---|---|
| 100 | 21.1 years | 0.2 years | 18 h |
| 1,000 | 2.1 years | 8 days | 2 h |
| 10,000 | 0.2 years | 18 h | 11 min |
| 100,000 | 8 days | 2 h | 1 min |
| 1,000,000 | 18 h | 11 min | 0 min |

Caveat: the vote assumes each sighting's error is independent; in reality errors on one campaign are correlated, so treat the naming figures as optimistic.

Reading: a home/office app reaching 100k installs would spot even a moderate campaign within hours; stealthy campaigns need either huge installs or sensors placed where the campaign is looking (e.g. on the device types it targets).
