# Thu 22 Oct 2026 · Wk 1 · HLD · API protocols + 4-step framework (~60 min)

**Goal:** know when to pick REST vs gRPC vs WebSockets (with a reason), and have a 45-min interview script (Xu 4-step) you can run on Sat.

## Block 1: Learn (25 min)
- [x] Alex Xu Vol 1 **Ch 3: A Framework for System Design Interviews** (the 4 steps + do/don't list) (10 min)
- [x] AlgoMaster HLD: `how-to-answer-a-system-design-interview-problem` (skim, 5 min, compare to Xu)
- [x] AlgoMaster HLD: `api-architectural-styles` + `rest-api-design` (10 min)
- [x] AlgoMaster HLD: `websockets` + `long-polling-vs-websockets` (use leftover time; if short, do these Fri morning)

## Block 2: Produce (25 min), from memory, no notes open
- [x] Table, 3 rows (REST / gRPC / WebSockets) x columns: transport (HTTP/1.1 vs HTTP/2), payload format, connection model (req-resp / streaming / persistent), who initiates, best for, worst for, one real example (e.g. chat, internal microservice call, public CRUD API)
- [x] 4-step framework cheat sheet: each step in 1 line + minutes for a 45-min round + 2 things to say in that step
- [x] Answer in 2 lines each: (a) chat app: which protocol and why? (b) service-to-service inside your DC: which and why? (c) why not WebSockets for everything?
- [x] Save as `week01/W01 22-Oct-26/thu-protocols-framework.md`

## Block 3: Recall check (10 min), answer before checking
1. A phone app polls the server every 2s for new messages; 1M users. What's the QPS, and what protocol change fixes it?
2. gRPC vs REST: name 2 reasons gRPC is faster, and 1 reason you still pick REST for a public API.
3. In the 4-step framework, what do you do in step 1 BEFORE drawing anything, and why does skipping it fail the round?

## Notes
- Back-of-envelope estimation (Xu Ch 2) slipped from Tue, now Sat 24 Oct before the light mock.
- DB internals / caching / MQ stay in Wk 2.
- Carried LLD items (`count_reports` with `ReadableSink`, Tic-Tac-Toe `play()`) are for Fri build.
