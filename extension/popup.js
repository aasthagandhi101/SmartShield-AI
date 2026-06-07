document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = '<div class="placeholder">Analyzing...</div>';

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // Inject content script
  chrome.scripting.executeScript(
    { target: { tabId: tab.id }, files: ["content.js"] },
    () => {
      chrome.tabs.sendMessage(tab.id, { action: "getText" }, async (response) => {

        if (chrome.runtime.lastError || !response || !response.text) {
          resultDiv.innerHTML = '<div class="placeholder">Could not read page content.</div>';
          return;
        }

        const pageText = response.text;
        console.log("Extracted text length:", pageText.length);
        console.log("First 300 chars:", pageText.substring(0, 300));

        try {
          const apiResponse = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: pageText })
          });

          const data = await apiResponse.json();

          const isSpam = data.prediction === 1;
          const statusColor = isSpam ? "#ef4444" : "#22c55e";
          const statusText = isSpam ? "🚨 SPAM DETECTED" : "✅ SAFE";
          const barColor = data.confidence >= 80 ? "#ef4444"
                         : data.confidence >= 50 ? "#f97316"
                         : "#22c55e";

          let badges = '';
          if (data.trusted_sender) {
            badges += '<span style="background:#1e3a5f;color:#38bdf8;padding:3px 8px;border-radius:6px;font-size:11px;margin-right:5px;">✓ Trusted Sender</span>';
          }
          if (data.transactional_signals > 0) {
            badges += '<span style="background:#14532d;color:#86efac;padding:3px 8px;border-radius:6px;font-size:11px;">✓ Transactional Email</span>';
          }

          resultDiv.innerHTML = `
            <div class="status" style="color:${statusColor}">${statusText}</div>

            ${badges ? `<div style="text-align:center;margin-bottom:12px">${badges}</div>` : ''}

            <div class="label">Confidence</div>
            <div class="progress-container">
              <div class="progress-bar" style="width:${data.confidence}%;background:${barColor}"></div>
            </div>
            <div style="text-align:center;margin-top:4px;font-size:14px">${data.confidence}%</div>

            <div class="label">Risk Level</div>
            <div class="risk-level" style="color:${barColor}">${data.risk}</div>

            <div class="recommendation">
              ${isSpam
                ? '⚠️ Do not click links or share personal info. Verify sender directly.'
                : '✓ Message appears safe. Always stay cautious with unexpected emails.'}
            </div>
          `;

        } catch (error) {
          console.error(error);
          resultDiv.innerHTML = '<div class="placeholder">⚠️ API connection failed.<br>Make sure the server is running.</div>';
        }
      });
    }
  );
});