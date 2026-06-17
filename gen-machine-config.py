#!/usr/bin/env python3
"""Generate machine.json for the Jitsi multi-container Fly Machine.

Fly's `machine_config` containers do NOT inherit machine-level `env` or app
secrets, so every container needs its own complete `env`. We apply one shared
env superset to all four containers (each Jitsi image ignores vars it doesn't
use). Component passwords are the source of truth here and live in the gitignored
`.secrets.env`; this script generates them on first run.
"""
import json
import os
import secrets
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS_FILE = os.path.join(HERE, ".secrets.env")
OUT = os.path.join(HERE, "machine.json")

IMAGE_VERSION = "stable-11031"
ADVERTISE_IP = "213.188.199.193"  # app's dedicated Fly IPv4 (JVB media)

# Secret env vars (generated once, persisted to .secrets.env).
SECRET_KEYS = [
    "JICOFO_AUTH_PASSWORD",
    "JVB_AUTH_PASSWORD",
    "JICOFO_COMPONENT_SECRET",
    "JIGASI_XMPP_PASSWORD",
    "JIGASI_TRANSCRIBER_PASSWORD",
    "JIBRI_RECORDER_PASSWORD",
    "JIBRI_XMPP_PASSWORD",
]


def load_or_make_secrets():
    vals = {}
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    vals[k] = v
    changed = False
    for k in SECRET_KEYS:
        if not vals.get(k):
            vals[k] = secrets.token_hex(16)
            changed = True
    if changed:
        with open(SECRETS_FILE, "w") as f:
            f.write("# Jitsi component passwords (gitignored). Source of truth.\n")
            for k in SECRET_KEYS:
                f.write(f"{k}={vals[k]}\n")
        os.chmod(SECRETS_FILE, 0o600)
    return {k: vals[k] for k in SECRET_KEYS}


def shared_env(sec):
    env = {
        "TZ": "UTC",
        "PUBLIC_URL": "https://meet.anuna.io",
        # All components reach prosody on localhost (shared netns in the Machine).
        "XMPP_SERVER": "127.0.0.1",
        "XMPP_BOSH_URL_BASE": "http://127.0.0.1:5280",
        "XMPP_DOMAIN": "meet.jitsi",
        "XMPP_AUTH_DOMAIN": "auth.meet.jitsi",
        "XMPP_MUC_DOMAIN": "muc.meet.jitsi",
        "XMPP_INTERNAL_MUC_DOMAIN": "internal-muc.meet.jitsi",
        "XMPP_GUEST_DOMAIN": "guest.meet.jitsi",
        "XMPP_RECORDER_DOMAIN": "recorder.meet.jitsi",
        "XMPP_HIDDEN_DOMAIN": "hidden.meet.jitsi",
        "JVB_BREWERY_MUC": "jvbbrewery",
        "JVB_AUTH_USER": "jvb",
        "JICOFO_COMPONENT_SECRET": sec["JICOFO_COMPONENT_SECRET"],
        # TLS terminates at the Fly edge; web serves plain HTTP on :80.
        "DISABLE_HTTPS": "1",
        "ENABLE_HTTP_REDIRECT": "0",
        "ENABLE_LETSENCRYPT": "0",
        "ENABLE_HSTS": "0",
        # Open meeting (no login) for the first working deploy.
        "ENABLE_AUTH": "0",
        "ENABLE_GUESTS": "1",
        "ENABLE_XMPP_WEBSOCKET": "1",
        "ENABLE_COLIBRI_WEBSOCKET": "1",
        # Media: advertise the app's dedicated IPv4 (UDP/10000).
        "JVB_PORT": "10000",
        "JVB_ADVERTISE_IPS": ADVERTISE_IP,
        "DOCKER_HOST_ADDRESS": ADVERTISE_IP,
    }
    # Component passwords
    env["JICOFO_AUTH_PASSWORD"] = sec["JICOFO_AUTH_PASSWORD"]
    env["JVB_AUTH_PASSWORD"] = sec["JVB_AUTH_PASSWORD"]
    env["JIGASI_XMPP_PASSWORD"] = sec["JIGASI_XMPP_PASSWORD"]
    env["JIGASI_TRANSCRIBER_PASSWORD"] = sec["JIGASI_TRANSCRIBER_PASSWORD"]
    env["JIBRI_RECORDER_PASSWORD"] = sec["JIBRI_RECORDER_PASSWORD"]
    env["JIBRI_XMPP_PASSWORD"] = sec["JIBRI_XMPP_PASSWORD"]
    return env


def main():
    sec = load_or_make_secrets()
    env = shared_env(sec)

    import base64
    # jicofo/jvb images run `tpl /defaults/x.conf > /config/x.conf` but Fly's
    # container runtime doesn't materialise the image's `VOLUME /config`
    # mountpoint, so /config is missing and the redirect fails. Placing a file
    # there makes Fly create the directory before the entrypoint runs.
    keep_file = {
        "guest_path": "/config/.fly-keep",
        "raw_value": base64.b64encode(b"keep\n").decode(),
    }

    def container(name, image, deps=True, files=None):
        c = {"name": name, "image": f"jitsi/{image}:{IMAGE_VERSION}", "env": dict(env)}
        if deps and name != "prosody":
            c["depends_on"] = [{"name": "prosody", "condition": "started"}]
        if files:
            c["files"] = files
        return c

    config = {
        "containers": [
            container("web", "web"),
            container("prosody", "prosody"),
            container("jicofo", "jicofo", files=[keep_file]),
            container("jvb", "jvb", files=[keep_file]),
        ]
    }
    with open(OUT, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    print(f"Wrote {OUT} with {len(config['containers'])} containers, "
          f"{len(env)} env vars each.")


if __name__ == "__main__":
    main()
