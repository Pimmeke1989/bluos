# BluOS Integration - Join/Unjoin Implementation Details

## How It Works

### Architecture Overview

The join/unjoin functionality uses the BluOS API's `AddSlave` and `RemoveSlave` endpoints to create multi-room audio groups.

### Join Implementation

When you call `bluos.join`:

1. **Service Call**: `bluos.join` service is called with:
   - `entity_id`: The player to join (slave)
   - `master`: The entity_id of the master player

2. **Entity Lookup**: The integration finds the master player's coordinator by:
   - First trying to match the entry_id in the entity_id
   - If that fails, matching by IP address from attributes

3. **API Call**: Calls `AddSlave` on the **master** player with these parameters:
   ```python
   {
       "slave": "10.10.10.23",      # IP of slave player
       "port": "11000",              # Port number
       "channelMode": "0",           # 0=stereo, 1=left, 2=right
       "group": "Group"              # Name of the group
   }
   ```

4. **Refresh**: Both master and slave coordinators refresh their status

### Unjoin Implementation

When you call `bluos.unjoin`:

1. **Check Status**: Determines if the player is a slave or master by checking `sync_status`

2. **If Slave**:
   - Finds the master's coordinator
   - Calls `RemoveSlave` on the master with the slave's IP
   - Refreshes both coordinators

3. **If Master/Standalone**:
   - Calls `RemoveSlave` without parameters to ungroup all slaves
   - Refreshes the coordinator

## Testing Your Setup

### Enable Debug Logging

Add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.bluos: debug
```

Then restart Home Assistant.

### Test Join Command

Try joining your Flex Player to the Woonkamer NAD:

```yaml
service: bluos.join
target:
  entity_id: media_player.flex_player  # Adjust to your actual entity_id
data:
  master: media_player.woonkamer_nad   # Adjust to your actual entity_id
```

### Check the Logs

Go to Settings → System → Logs and look for entries like:

```
custom_components.bluos.media_player: Attempting to join media_player.flex_player to master media_player.woonkamer_nad
custom_components.bluos.media_player: Found master coordinator by entry_id: abc123 (IP: 10.10.10.31)
custom_components.bluos.media_player: Calling AddSlave on master 10.10.10.31 to add slave 10.10.10.23
custom_components.bluos.bluos_api: Adding slave 10.10.10.23 to master 10.10.10.31 with params: {'slave': '10.10.10.23', 'port': '11000', 'channelMode': '0', 'group': 'Group'}
custom_components.bluos.bluos_api: AddSlave response: <xml response>
custom_components.bluos.media_player: Successfully joined 10.10.10.23 to 10.10.10.31
```

## Common Issues and Solutions

### Issue 1: "Master player not found"

**Symptom**: Error in logs: `Master player entity media_player.xxx not found in Home Assistant`

**Solution**: 
- Verify the exact entity_id of your master player
- Go to Developer Tools → States
- Search for your BluOS players
- Use the exact entity_id shown

### Issue 2: "Could not find coordinator for master player"

**Symptom**: Error in logs: `Could not find coordinator for master player`

**Solution**:
- Ensure both players are added as separate integrations
- Check that both players show up in Settings → Devices & Services → BluOS
- Restart Home Assistant if you just added a player

### Issue 3: "AddSlave command failed"

**Symptom**: Error in logs: `AddSlave command failed` or `AddSlave response: None`

**Possible Causes**:
1. **Network connectivity**: Master can't reach slave
2. **Firmware incompatibility**: Different BluOS versions
3. **Already grouped**: Player is already in another group
4. **Firewall**: Port 11000 is blocked

**Solutions**:
- Verify both players can ping each other
- Check firmware versions (should be similar)
- Unjoin the player first if it's already grouped
- Check firewall rules

### Issue 4: Group status not updating

**Symptom**: Players are grouped but `blueos_group` attribute doesn't show it

**Solution**:
- Wait 5-10 seconds for the next poll
- Manually refresh: Developer Tools → States → Click refresh icon
- Check the `/SyncStatus` endpoint directly: `http://10.10.10.31:11000/SyncStatus`

## Manual API Testing

You can test the BluOS API directly to verify it's working:

### Check Player Status
```
http://10.10.10.31:11000/Status
```

### Check Sync Status
```
http://10.10.10.31:11000/SyncStatus
```

### Manually Join Players
```
http://10.10.10.31:11000/AddSlave?slave=10.10.10.23&port=11000&channelMode=0&group=TestGroup
```

### Manually Unjoin
```
http://10.10.10.31:11000/RemoveSlave?slave=10.10.10.23
```

Or from the slave:
```
http://10.10.10.23:11000/RemoveSlave
```

## What Changed in v1.0.1

### Improvements to `add_slave`:
- Added `channelMode` parameter (required by BluOS API)
- Added `group` parameter for group naming
- Converted port to string (API expects string)
- Added debug logging

### Improvements to `async_join_player`:
- Better entity lookup (tries entry_id first, then IP matching)
- Comprehensive error handling
- Detailed debug logging at each step
- Better error messages

### Improvements to `async_unjoin_player`:
- Fallback to direct unjoin if master coordinator not found
- Better error handling
- Detailed debug logging

## Expected Behavior

### When Join Succeeds:
1. Slave player stops its current playback
2. Slave player joins the master's group
3. Slave player starts playing the same content as master
4. `blueos_group` attribute on both players shows all group members
5. Volume can be controlled independently or as a group

### When Unjoin Succeeds:
1. Player leaves the group
2. Player stops playback
3. Player becomes independent
4. `blueos_group` attribute becomes empty or shows only itself

## Debugging Checklist

- [ ] Both players are added to Home Assistant
- [ ] Both players show up in Settings → Devices & Services → BluOS
- [ ] Debug logging is enabled
- [ ] Entity IDs are correct (check Developer Tools → States)
- [ ] Players can ping each other on the network
- [ ] Port 11000 is accessible on both players
- [ ] Firmware versions are compatible
- [ ] Players are not already in conflicting groups
- [ ] Home Assistant can reach both players

## Getting Help

If you're still having issues:

1. **Collect logs**: Enable debug logging and try the join operation
2. **Test API directly**: Try the manual API URLs above
3. **Check network**: Verify connectivity between players
4. **Report issue**: https://github.com/Pimmeke1989/bluos/issues

Include in your report:
- Home Assistant version
- BluOS integration version
- BluOS firmware versions
- Player models
- Complete debug logs
- Results of manual API testing
