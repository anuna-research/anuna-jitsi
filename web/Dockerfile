# Anuna-branded Jitsi web image. Thin layer over the official jitsi/web that
# bakes in the Anuna palette, fonts, logo and app name. Built by `fly deploy`
# and injected into the `web` container (see fly.toml [experimental] container).
FROM jitsi/web:stable-11031

# Anuna mark — used as the in-call watermark and welcome-page logo.
COPY web/branding/anuna-logo.png /usr/share/jitsi-meet/images/anuna-logo.png

# Brand CSS overlay, appended so it overrides the bundled stylesheet.
COPY web/branding/anuna.css /tmp/anuna.css
RUN cat /tmp/anuna.css >> /usr/share/jitsi-meet/css/all.css && rm /tmp/anuna.css

# Brand interface_config. The entrypoint copies /defaults/interface_config.js to
# /config on boot, so appending here makes the overrides take effect at runtime.
COPY web/branding/interface_overrides.js /tmp/interface_overrides.js
RUN cat /tmp/interface_overrides.js >> /defaults/interface_config.js \
    && rm /tmp/interface_overrides.js

# The welcome-page hero text is baked into the prebuilt JS bundle's default
# English strings. We can't change it via the served lang file without a source
# rebuild, so (a) keep the lang file in sync for non-English/SEO, and (b) ship a
# small runtime script that rewrites the wordmark text in the DOM.
RUN sed -i \
    -e 's#"headerTitle": "Jitsi Meet"#"headerTitle": "Anuna Meet"#' \
    -e 's#"headerSubtitle": "Secure and high quality meetings"#"headerSubtitle": "Anuna Research Co-operative"#' \
    /usr/share/jitsi-meet/lang/main.json
COPY web/branding/anuna-branding.js /usr/share/jitsi-meet/anuna-branding.js
RUN sed -i 's#</body>#<script src="anuna-branding.js"></script></body>#' \
    /usr/share/jitsi-meet/index.html

# Load Anuna brand fonts + favicon by injecting links into <head>.
RUN sed -i 's#</head>#<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500\&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600\&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600\&family=Space+Grotesk:wght@400;500;600;700\&display=swap" rel="stylesheet"><link rel="icon" type="image/png" href="images/anuna-logo.png"></head>#' \
    /usr/share/jitsi-meet/index.html
