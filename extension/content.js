function cleanText(text) {
  return text
    .replace(/\s+/g, ' ')         
    .replace(/[^\x20-\x7E\n]/g, ' ') 
    .trim();
}

function getGmailText() {
  // Try to get subject
  const subjectEl = document.querySelector('h2.hP');
  const subject = subjectEl ? subjectEl.innerText.trim() : '';

  // Get sender info
  const senderEl = document.querySelector('.gD');
  const sender = senderEl ? senderEl.getAttribute('email') || senderEl.innerText : '';

  // Get ONLY the email body, not the entire thread/UI
  const bodyEls = document.querySelectorAll('.a3s.aiL, .a3s');
  let body = '';
  if (bodyEls.length > 0) {
    body = bodyEls[0].innerText;
  }

  body = body.split('\n')
    .filter(line => !line.trim().startsWith('>'))
    .join('\n');

  const combined = `Subject: ${subject}\nFrom: ${sender}\n\n${body}`;
  return cleanText(combined).substring(0, 3000);
}

function getOutlookText() {
  const subject = document.querySelector('[data-testid="subject"]');
  const body = document.querySelector('[role="main"] .ReadingPaneContent');
  const subjectText = subject ? subject.innerText : '';
  const bodyText = body ? body.innerText : '';
  return cleanText(`Subject: ${subjectText}\n\n${bodyText}`).substring(0, 3000);
}

function getWhatsAppText() {
  const msgs = document.querySelectorAll('[data-testid="conversation-panel-body"] .copyable-text');
  const last20 = Array.from(msgs).slice(-20).map(m => m.innerText).join('\n');
  return cleanText(last20).substring(0, 3000);
}

function getPageText() {
  const url = window.location.href;

  if (url.includes('mail.google.com')) {
    return getGmailText();
  }

  if (url.includes('outlook.live.com') || url.includes('outlook.office.com')) {
    return getOutlookText();
  }

  if (url.includes('web.whatsapp.com')) {
    return getWhatsAppText();
  }

  // Generic fallback - get main content only
  const main = document.querySelector('main, article, [role="main"], .main-content');
  if (main) return cleanText(main.innerText).substring(0, 3000);

  return cleanText(document.body.innerText).substring(0, 3000);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getText") {
    sendResponse({ text: getPageText() });
  }
});