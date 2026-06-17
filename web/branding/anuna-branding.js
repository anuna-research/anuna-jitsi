/* Anuna front-end rebranding for Jitsi Meet.
 *
 * The welcome-page hero text ("Jitsi Meet" / "Secure and high quality meetings")
 * is baked into the prebuilt jitsi-meet JS bundle as the default English i18n
 * strings, so it can't be changed by editing the served lang/*.json without
 * rebuilding from source. Instead we rewrite the rendered text in the DOM and
 * keep it rewritten across re-renders via a MutationObserver. Original styling
 * (Fraunces serif, sizing, layout) is untouched — only the words change.
 */
(function () {
  var MAP = [
    ['Jitsi Meet', 'Anuna Meet'],
    ['Secure and high quality meetings', 'Anuna Research Co-operative']
  ];

  function rewriteTextNode(node) {
    var v = node.nodeValue;
    if (!v) return;
    var out = v;
    for (var i = 0; i < MAP.length; i++) {
      if (out.indexOf(MAP[i][0]) !== -1) {
        out = out.split(MAP[i][0]).join(MAP[i][1]);
      }
    }
    if (out !== v) node.nodeValue = out;
  }

  function walk(node) {
    if (node.nodeType === 3) {
      rewriteTextNode(node);
    } else if (node.nodeType === 1 && node.childNodes && node.tagName !== 'SCRIPT'
               && node.tagName !== 'STYLE') {
      for (var i = 0; i < node.childNodes.length; i++) walk(node.childNodes[i]);
    }
  }

  var scheduled = false;
  function apply() {
    scheduled = false;
    if (document.body) walk(document.body);
    if (document.title && document.title.indexOf('Jitsi Meet') !== -1) {
      document.title = document.title.split('Jitsi Meet').join('Anuna Meet');
    }
  }
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    (window.requestAnimationFrame || window.setTimeout)(apply, 0);
  }

  function start() {
    apply();
    try {
      new MutationObserver(schedule).observe(document.body, {
        childList: true, subtree: true, characterData: true
      });
    } catch (e) { /* no-op */ }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
