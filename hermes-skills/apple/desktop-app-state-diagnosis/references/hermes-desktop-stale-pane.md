# Stale pane in a client/server chat app (Hermes desktop ↔ local gateway)

Report shape: "why isn't the content you just generated in the last line of the client — the client still
shows what I was doing yesterday". Prompts still submit; turns still finish. Nothing is actually lost.

## Mechanism

1. The app's WebSocket to the gateway drops. The close is **client-side**
   (`reason=client_disconnect(code=1005)`, `detached_sessions=1`) — typical of the app being backgrounded or
   throttled, and it repeats on a rough timer while the user is away.
2. Each drop makes the gateway reap that run's runtime and broadcast
   `session.reclaimed` with `"reason": "ws_orphan_reap"` and `stored_session_id` = the durable session id.
3. The client heals by resuming → a **new** runtime id. The log therefore shows a parade of runtime ids, all
   for the same `stored_session_id`.
4. Healing is capped **per app run** (`MAX_CONSECUTIVE_HEALS` in
   `apps/desktop/src/store/runtime-gone.ts`). Once spent, the pane stays bound to the dead runtime and keeps
   repainting its cached transcript until the app restarts.
5. Prompts still work because the composer submits over the HTTP side and the turn runs server-side — which
   is exactly why the reply exists everywhere except in the pane.

Contributing factors: an app left running for days accumulates dead-runtime records that never clear; a very
large session makes every heal re-load a big transcript.

## Evidence to collect (read-only, keep every print to ~1 short line)

```bash
# 1. connection churn + the reap loop
grep -c 'ws accepted' ~/.hermes/logs/dashboard.log
grep -c 'ws closed'   ~/.hermes/logs/dashboard.log      # expect: client_disconnect(code=1005), detached_sessions=1
grep -o '"type": "session.reclaimed".*' ~/.hermes/logs/dashboard.log | cut -c1-400 | tail -5
#    → ws_orphan_reap + a stored_session_id matching the user's session = root cause

# 2. is the backend healthy? (app-side log)
grep -E 'prompt|status=complete' ~/.hermes/logs/gui.log | tail -20

# 3. who owns the sockets, and how long the app has been up
lsof -nP -iTCP:8787
ps -o lstart= -p <pid>
#    → the renderer helper process (not the main app pid) holds the app's socket; the gateway host holds the
#      other side. Multi-day uptime means the heal latch has had time to stick.

# 4. the transcript is intact (backend session store)
sqlite3 -readonly ~/.hermes/state.db ".tables"          # then the sessions/messages tables
```

Pitfall: in a long session a large printed probe is compressed to a single line and the detail is
unrecoverable — print one short line per probe, and prefer several small probes over one big dump.

## Fix, in order

1. Switch to another session and back / close and reopen the pane → fresh resume + transcript refresh.
2. Quit and reopen the app (⌘Q) → clears warm cache, dead-runtime records and the heal counter; on boot it
   resumes the stored session and re-pulls the transcript. Nothing is lost.
3. Prevention: `/new` when the current session has grown huge; update the app when it is old.

Report the answer even if the user may not see it: name the alternate surfaces (CLI session view, the local
dashboard URL), and ask any "may I restart it?" question in plain reply text as well as any UI prompt,
since the UI that would show the prompt may be the frozen one. Restarting is destructive to an unsent
composer draft — always ask first.
