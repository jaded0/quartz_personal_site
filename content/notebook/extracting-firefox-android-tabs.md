---
title: Extracting all Firefox Android tabs via ADB
publish: true
description: Firefox Android hides 'inactive' tabs from share-all, sync, and remote
  debugging. Here is what doesn't work, and the ADB route that finally got every URL
  out.
---

# Extracting All Firefox Android Tabs (Including Inactive) via ADB

## Problem
Firefox Android has "inactive" tabs that don't show up through normal means (share all tabs, sync, remote debugging tab list). Need to get ALL tab URLs into a text file.

## What Doesn't Work
- **"Share all tabs"** in Firefox Android — only shares active tabs
- **Firefox Sync** — only syncs a subset of tabs
- **Remote debugging tab list** (`listTabs` via RDP) — only returns actively loaded tabs (GeckoView doesn't load inactive ones)
- **`adb backup`** — Firefox opts out; produces a ~47 byte empty backup
- **`adb shell run-as org.mozilla.firefox`** — not debuggable on release builds
- **Content providers** — Firefox Fenix doesn't expose tab data via content providers
- **`/sdcard/Android/data/org.mozilla.firefox/`** — only has a Download folder
- **Browser extensions** (e.g. "Copy All Tab Urls") — only see active tabs

## What Works: Remote Debugger + Privileged JS to Read Session File

### Setup
```bash
sudo apt install adb
# Enable Developer Options + USB Debugging on phone
# Enable Remote debugging via USB in Firefox Android (Settings > Advanced)
adb devices  # should show "device"
adb forward tcp:6000 localabstract:org.mozilla.firefox/firefox-debugger-socket
```

### Key Insight
Firefox Fenix stores ALL tab data (including inactive) in:
```
/data/user/0/org.mozilla.firefox/files/mozilla_components_session_storage_gecko.json
```

This file is ~13MB and contains a `sessionStateTuples` array with every tab. Each tuple has:
```json
{
  "session": {
    "url": "https://...",
    "title": "...",
    "lastAccess": 1743312222013,
    ...
  },
  "engineSession": { ... }
}
```

### How to Access It
Connect to Firefox's remote debugger protocol (port 6000), get the **parent process target**, and use its **console actor** to evaluate privileged JavaScript that reads the file using `nsIFile` / `nsIFileInputStream` APIs.

The remote debugger's parent process console runs in a chrome-privileged context, so it can read internal app files that are otherwise inaccessible without root.

### Extraction Script

```python
import socket, json, re, time

def send_rdp(s, msg):
    raw = json.dumps(msg)
    packet = f'{len(raw)}:{raw}'
    s.sendall(packet.encode())

def recv_all(s, timeout=30):
    s.settimeout(timeout)
    data = b''
    while True:
        try:
            chunk = s.recv(65536)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    return data

def parse_rdp(data):
    text = data.decode('utf-8', errors='replace')
    results = []
    pos = 0
    while pos < len(text):
        match = re.match(r'(\d+):', text[pos:])
        if not match:
            break
        length = int(match.group(1))
        start = pos + match.end()
        if start + length > len(text):
            break
        payload = text[start:start+length]
        try:
            results.append(json.loads(payload))
        except:
            results.append(payload)
        pos = start + length
    return results

def recv_until(s, check_fn, timeout=30):
    s.settimeout(3)
    data = b''
    start = time.time()
    while time.time() - start < timeout:
        try:
            chunk = s.recv(65536)
            if not chunk:
                break
            data += chunk
            if check_fn(data):
                return data
        except socket.timeout:
            continue
    return data

import subprocess
subprocess.run(['adb', 'forward', '--remove-all'], capture_output=True)
subprocess.run(['adb', 'forward', 'tcp:6000',
    'localabstract:org.mozilla.firefox/firefox-debugger-socket'], capture_output=True)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect(('localhost', 6000))
recv_until(s, lambda d: b'applicationType' in d, timeout=5)

# Get parent process
send_rdp(s, {'to': 'root', 'type': 'getProcess', 'id': 0})
resp = parse_rdp(recv_until(s, lambda d: b'processDescriptor' in d, timeout=5))
proc_actor = resp[0]['processDescriptor']['actor']

# Get parent process target (has privileged console)
send_rdp(s, {'to': proc_actor, 'type': 'getTarget'})
resp = parse_rdp(recv_until(s, lambda d: b'consoleActor' in d, timeout=5))
console_actor = resp[0]['process']['consoleActor']

# Extract URLs in chunks (RDP returns LongString for large results)
all_urls = []
chunk_size = 200

for chunk_start in range(0, 3000, chunk_size):
    js = f"""
    (() => {{
        let file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
        file.initWithPath("/data/user/0/org.mozilla.firefox/files/mozilla_components_session_storage_gecko.json");
        let stream = Cc["@mozilla.org/network/file-input-stream;1"].createInstance(Ci.nsIFileInputStream);
        stream.init(file, 0x01, 0, 0);
        let converter = Cc["@mozilla.org/intl/converter-input-stream;1"].createInstance(Ci.nsIConverterInputStream);
        converter.init(stream, "UTF-8", 0, 0);
        let data = "";
        let str = {{}};
        while (converter.readString(65536, str) != 0) {{ data += str.value; }}
        converter.close();
        let parsed = JSON.parse(data);
        let urls = parsed.sessionStateTuples.slice({chunk_start}, {chunk_start + chunk_size}).map(t => t.session.url || "about:blank");
        return urls.join("\\n");
    }})()
    """
    send_rdp(s, {'to': console_actor, 'type': 'evaluateJSAsync', 'text': js})
    data = recv_until(s, lambda d: b'evaluationResult' in d, timeout=30)
    resp = parse_rdp(data)

    for r in resp:
        if isinstance(r, dict) and 'result' in r:
            result = r['result']
            if isinstance(result, str) and result:
                urls = result.split('\n')
                all_urls.extend(urls)
            elif isinstance(result, dict) and result.get('type') == 'longString':
                # Fetch the full string from the LongString actor
                send_rdp(s, {'to': result['actor'], 'type': 'substring',
                             'start': 0, 'end': result['length']})
                data2 = recv_until(s, lambda d: b'substring' in d, timeout=15)
                resp2 = parse_rdp(data2)
                for r2 in resp2:
                    if isinstance(r2, dict) and 'substring' in r2:
                        all_urls.extend(r2['substring'].split('\n'))

    if len(all_urls) > 0 and (len(all_urls) % chunk_size != 0 or chunk_start > 2500):
        break

s.close()

with open('firefox_tabs.txt', 'w') as f:
    f.write('\n'.join(all_urls) + '\n')
print(f"Saved {len(all_urls)} URLs")
```

### ADB/udev Troubleshooting (Ubuntu)
If `adb devices` shows "no permissions":
```bash
lsusb  # find vendor ID (e.g. 18d1 for Google/Pixel)
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/51-android.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
adb kill-server
adb devices  # accept authorization on phone
```

### Notes
- Profile path can be found via: `Services.dirsvc.get("ProfD", Ci.nsIFile).path`
- Gecko profile is at e.g. `/data/user/0/org.mozilla.firefox/files/mozilla/2kne90x4.default/`
- But tabs are NOT in the Gecko profile — they're managed by Android Components at the app level
- The session JSON path: `/data/user/0/org.mozilla.firefox/files/mozilla_components_session_storage_gecko.json`
- `tabs.sqlite` in the same directory is for Firefox Sync, not local tabs
