(() => {
  'use strict';

  const code = document.querySelector('#embed-code');
  const button = document.querySelector('#copy-code');
  const label = button.querySelector('span');
  const status = document.querySelector('#copy-status');
  let resetTimer;
  button.hidden = false;

  button.addEventListener('click', async () => {
    button.disabled = true;
    clearTimeout(resetTimer);
    let copied = false;

    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(code.value);
        copied = true;
      } catch { /* Use selection copying if clipboard access is denied. */ }
    }

    if (!copied) {
      code.focus({ preventScroll: true });
      code.select();
      try { copied = document.execCommand('copy'); } catch { /* Keep the code selected for manual copying. */ }
    }

    button.disabled = false;
    if (copied) {
      button.focus({ preventScroll: true });
      label.textContent = 'Copied';
      status.textContent = 'HTML copied to clipboard.';
      resetTimer = setTimeout(() => { label.textContent = 'Copy HTML'; }, 2500);
    } else {
      label.textContent = 'Copy HTML';
      status.textContent = 'Code selected. Press Ctrl+C or ⌘C, or use your device’s Copy command.';
    }
  });
})();
