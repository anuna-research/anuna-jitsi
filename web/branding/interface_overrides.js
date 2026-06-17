// Anuna branding overrides for Jitsi Meet.
// Appended (at image build) to /defaults/interface_config.js, which the web
// container copies to /config/interface_config.js on boot. These reassign the
// already-declared global `interfaceConfig`.
interfaceConfig.APP_NAME = 'Anuna Meet';
interfaceConfig.NATIVE_APP_NAME = 'Anuna Meet';
interfaceConfig.PROVIDER_NAME = 'Anuna';

// Replace the Jitsi watermark with the Anuna mark, linking back to anuna.io.
interfaceConfig.SHOW_JITSI_WATERMARK = false;
interfaceConfig.SHOW_WATERMARK_FOR_GUESTS = false;
interfaceConfig.SHOW_BRAND_WATERMARK = true;
interfaceConfig.BRAND_WATERMARK_LINK = 'https://anuna.io';
interfaceConfig.JITSI_WATERMARK_LINK = 'https://anuna.io';
interfaceConfig.DEFAULT_LOGO_URL = 'images/anuna-logo.png';
interfaceConfig.DEFAULT_WELCOME_PAGE_LOGO_URL = 'images/anuna-logo.png';

// Friendlier room-name suggestions on the welcome page.
interfaceConfig.GENERATE_ROOMNAMES_ON_WELCOME_PAGE = true;
