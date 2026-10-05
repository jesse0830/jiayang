# Hermes Memory Configuration

Covers all supported memory providers: built-in, Holographic, Honcho, Mem0, RetainDB.

## Quick Reference

```bash
# Check current memory status
hermes memory status

# Switch to a different provider — edit config.yaml:
#   memory.provider: holographic  (or honcho, mem0, retaindb, etc.)
# Then add the provider's config section (see below)
```

## Provider Overview

| Provider | Cost | Storage Type | API Key Needed | Sync Across Devices |
|----------|------|-------------|----------------|-------------------|
| Built-in | Free | In-memory + context | No | No (per-session only) |
| Holographic | Free | Local SQLite | No | Manual / cloud sync |
| Honcho | Paid | Cloud API | Yes | Built-in (cloud) |
| Mem0 | Paid | Cloud API | Yes | Built-in (cloud) |
| RetainDB | Free tier | Cloud/self-host | Yes | Built-in (cloud) |

## Holographic (Recommended for Free, Local Storage)

Holographic uses a local SQLite database (`memory_store.db`) for structured fact
storage with FTS5 search, trust scoring, and compositional retrieval. It requires
**no API key** and stores everything on your machine.

### Setup

1. **Edit `~/.hermes/config.yaml`:**

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  provider: holographic
  # memory_char_limit: 2200   # optional, default
  # user_char_limit: 1375     # optional, default

holographic:
  db_path: $HERMES_HOME/memory_store.db   # default, omit for auto
  auto_extract: false                       # auto-extract facts from conversation
  default_trust: 0.5                        # trust score for new facts (0-1)
  min_trust_threshold: 0.3                  # minimum trust for retrieval
  temporal_decay_half_life: 0               # 0 = no decay
```

2. **Verify:**

```bash
hermes memory status
# Expected output:
#   Provider:  holographic
#   Plugin:    installed ✓
#   Status:    available ✓
```

3. **Start a new session** (`/reset` or exit and re-enter) for the change to take effect.

### Config Options Explained

- `db_path`: Path to the SQLite database. Use `$HERMES_HOME` for profile-safe paths.
- `auto_extract`: If `true`, the agent automatically extracts and stores facts from conversation without explicit memory tool calls.
- `default_trust`: Default trust score for new facts (0.0-1.0). Higher = more authoritative.
- `min_trust_threshold`: Facts below this trust score are filtered from retrieval.
- `temporal_decay_half_life`: How many hours for a fact's trust to halve. `0` = no decay.

### Cross-Device Sync (Holographic)

Since Holographic stores data in a local file, sharing memory across devices requires
**file-level synchronization**:

**Option A: Cloud Drive (Recommended)**
1. Move `memory_store.db` to a cloud-synced folder (iCloud Drive, OneDrive, Dropbox, etc.)
2. Symlink or update `db_path` to point there:
   ```bash
   mv ~/.hermes/memory_store.db ~/Library/Mobile\ Documents/com~apple~CloudDocs/hermes/
   ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/hermes/memory_store.db ~/.hermes/memory_store.db
   ```
3. Do the same on the other device (point to the same cloud path)

**Option B: Periodic Manual Copy**
```bash
# On source device
cp ~/.hermes/memory_store.db /path/to/usb/or/share/
# On target device
cp /path/to/usb/or/share/memory_store.db ~/.hermes/memory_store.db
# Then /reset Hermes to pick up the new data
```

**Option C: Syncthing (Free, P2P)**
```bash
# Install Syncthing on both devices, share the ~/.hermes/memory_store.db folder
```

### Important Notes
- Only **one** Hermes instance should write to the DB at a time to avoid corruption.
- If both devices might run Hermes simultaneously, cloud sync with conflict resolution is safer than Syncthing.
- After replacing the DB file on a device, run `/reset` or restart Hermes to re-initialize.
- The built-in memory (`memory` tool → `memory`/`user` targets) is **always active** alongside Holographic.

## Honcho (Paid, Cloud)

Honcho provides cloud-synced memory across all your devices automatically.
Requires Honcho API key and account registration.

### Setup

1. Register at https://app.honcho.dev (requires Cloudflare verification — headless browser cannot bypass)
2. Get your API key from the Honcho dashboard
3. Set `HONCHO_API_KEY` in `~/.hermes/.env`
4. Configure `config.yaml`:

```yaml
memory:
  provider: honcho
honcho: {}
```

### Cross-Device Sync (Honcho)

See main SKILL.md → 跨设备记忆同步（Honcho）section for complete setup including:
- Cloudflare CAPTCHA registration obstacle
- Switching provider on both devices
- Conflict avoidance

## Troubleshooting

### `hermes memory status` shows wrong provider
- Check `config.yaml` has the correct `memory.provider` value
- Run `/reset` to load new config
- Verify the plugin exists: check `~/.hermes/hermes-agent/plugins/memory/<name>/`

### Holographic not saving facts
- Verify `memory.memory_enabled: true`
- Check write permissions on `memory_store.db`
- Try `auto_extract: true` in the holographic config

### Cross-device sync conflicts
- SQLite can handle simple overwrites, but simultaneous writes from two instances will corrupt the DB
- Recommendation: use cloud drive sync (iCloud/OneDrive) which provides basic conflict handling

### "Plugin not found" error
- Run `hermes plugins list` to confirm the plugin is installed
- If not, reinstall or check your Hermes version (plugins ship with the agent, not separately)
