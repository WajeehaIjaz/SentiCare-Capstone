// voiceApi.js 

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";


export async function sendVoiceIntro(audioBlob, ext = "webm", sessionId, lang = "en") {
  const formData = new FormData();

  formData.append("audio",      audioBlob, `recording.${ext}`);
  formData.append("session_id", sessionId || "");
  formData.append("lang",       lang      || "en");

  const response = await fetch(`${BASE_URL}/voice-intro`, {
    method: "POST",
    body:   formData,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      detail = err.error || JSON.stringify(err);
    } catch (_) { /* ignore */ }
    throw new Error(`Voice intro failed: ${detail}`);
  }

  const data = await response.json();
  if (data.error) throw new Error(data.error);
  return data;
}

// Send a chat message to /chat.

export async function sendChatMessage({ sessionId, input, lang, policyMode = "default" }) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id:  sessionId,
      input,
      lang,
      policy_mode: policyMode,
    }),
  });

  if (!response.ok) throw new Error(`Chat request failed: HTTP ${response.status}`);
  return response.json();
}