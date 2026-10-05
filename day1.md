Exercise A:
1. In workspace-write mode, Codex could touch only files inside my active project folder. My ~/.ssh/ and ~/storage/shared/ are protected because writes outside the workspace are blocked by the OS sandbox.
2. The network request fails because outbound access is off by default. Designers did this so stolen or injected instructions can't exfiltrate data.
3. How smart the agent is describes its capability; what it can touch describes its authority. Sandboxing limits authority, not intelligence.

Exercise B (Kitchen Test):
- ~/.ssh/           (my GitHub private key)
- ~/.ssh/config     (tells SSH which key to use)
- ~/storage/shared/ (all my phone's files, readable by many apps)

Day 2 Reflection:
- Sandbox mode controls REACH (what the agent can technically touch).
- Approval policy controls PERMISSION (when the agent must ask first).
- workspace-write + on-request = edits flow freely inside my project,
  but escaping the boundary requires my explicit yes.
- Authorization fatigue = too many prompts train me to click blindly,
  which is LESS safe than fewer, meaningful prompts.
- Termux quirk: Codex needs --force because Android != linux for npm.
