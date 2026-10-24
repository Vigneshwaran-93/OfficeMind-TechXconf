(function () {
  const transcript = document.getElementById("transcript");
  const statusLine = document.getElementById("statusLine");
  const crisisBanner = document.getElementById("crisisBanner");
  const voiceControls = document.getElementById("voiceControls");
  const textControls = document.getElementById("textControls");
  const micBtn = document.getElementById("micBtn");
  const muteBtn = document.getElementById("muteBtn");
  const stopSpeakingBtn = document.getElementById("stopSpeakingBtn");
  const switchToTextBtn = document.getElementById("switchToTextBtn");
  const switchToVoiceBtn = document.getElementById("switchToVoiceBtn");
  const textInput = document.getElementById("textInput");
  const sendBtn = document.getElementById("sendBtn");
  const endBtn = document.getElementById("endBtn");
  const endModal = document.getElementById("endModal");
  const confirmEndBtn = document.getElementById("confirmEndBtn");
  const cancelEndBtn = document.getElementById("cancelEndBtn");

  let mode = window.OM.preferredInteraction === "voice" ? "voice" : "text";
  let muted = false;
  let mediaRecorder = null;
  let audioChunks = [];
  let recordTimer = null;
  let currentAudio = null;
  let busy = false;

  function addBubble(role, text) {
    if (!text) return;
    const div = document.createElement("div");
    div.className = "bubble " + role;
    div.textContent = text;
    transcript.appendChild(div);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function addSystemNote(text) {
    const div = document.createElement("div");
    div.className = "bubble system-note";
    div.textContent = text;
    transcript.appendChild(div);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function setMode(m) {
    mode = m;
    voiceControls.style.display = m === "voice" ? "flex" : "none";
    textControls.style.display = m === "text" ? "flex" : "none";
  }

  function stopSpeaking() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }

  function speak(text, audioB64) {
    if (mode !== "voice") return;
    stopSpeaking();
    if (audioB64) {
      currentAudio = new Audio("data:audio/wav;base64," + audioB64);
      currentAudio.play().catch(() => {});
    } else if (window.speechSynthesis) {
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 1.0;
      window.speechSynthesis.speak(utter);
    }
  }

  function handleChatResponse(data) {
    if (data.user_text_display) addBubble("user", data.user_text_display);
    if (data.crisis) {
      crisisBanner.style.display = "block";
      crisisBanner.innerHTML =
        "You're not alone, and this matters. Please consider reaching out to a crisis helpline — " +
        "Tele-MANAS (India): 14416 — or see <a href=\"" + window.OM.helpUrl + "\">Help & Safety</a> for more options.";
    } else if (data.harassment) {
      crisisBanner.style.display = "block";
      crisisBanner.innerHTML =
        "This sounds serious. You may want to document what happened and consider talking to HR or a trusted person. " +
        "See <a href=\"" + window.OM.helpUrl + "\">Help & Safety</a> for more options.";
    }
    addBubble("model", data.reply_display);
    speak(data.reply_display, data.reply_audio_b64);
    statusLine.textContent = "";
    busy = false;
  }

  function sendText(message) {
    if (!message.trim() || busy) return;
    busy = true;
    statusLine.textContent = "Thinking...";
    fetch("/chat/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          addSystemNote(data.error);
          statusLine.textContent = "";
          busy = false;
          return;
        }
        handleChatResponse(data);
      })
      .catch(() => {
        addSystemNote("Could not reach the server. Please try again.");
        statusLine.textContent = "";
        busy = false;
      });
  }

  sendBtn.addEventListener("click", () => {
    const val = textInput.value;
    textInput.value = "";
    sendText(val);
  });
  textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendBtn.click();
    }
  });

  function sendAudio(blob) {
    if (busy) return;
    busy = true;
    statusLine.textContent = "Thinking...";
    const form = new FormData();
    form.append("audio", blob, "recording.webm");
    fetch("/chat/voice", { method: "POST", body: form })
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          addSystemNote(data.error);
          statusLine.textContent = "";
          busy = false;
          return;
        }
        handleChatResponse(data);
      })
      .catch(() => {
        addSystemNote("Could not reach the server. Please try again.");
        statusLine.textContent = "";
        busy = false;
      });
  }

  function fallbackToText(reason) {
    setMode("text");
    addSystemNote(reason);
  }

  micBtn.addEventListener("click", () => {
    if (muted || busy) return;
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      fallbackToText("Voice input isn't supported in this browser. Switched to text.");
      return;
    }
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        audioChunks = [];
        let mimeType = "audio/webm";
        if (!MediaRecorder.isTypeSupported(mimeType)) mimeType = "";
        mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
          micBtn.classList.remove("recording");
          statusLine.textContent = "";
          clearTimeout(recordTimer);
          stream.getTracks().forEach((t) => t.stop());
          const blob = new Blob(audioChunks, { type: mediaRecorder.mimeType || "audio/webm" });
          if (blob.size > 0) sendAudio(blob);
        };
        mediaRecorder.start();
        micBtn.classList.add("recording");
        statusLine.textContent = "Listening... tap again to stop";
        recordTimer = setTimeout(() => {
          if (mediaRecorder && mediaRecorder.state === "recording") mediaRecorder.stop();
        }, window.OM.maxAudioSeconds * 1000);
      })
      .catch(() => {
        fallbackToText("Microphone access was denied. Switched to text — you can still talk this through.");
      });
  });

  muteBtn.addEventListener("click", () => {
    muted = !muted;
    muteBtn.classList.toggle("active", muted);
    if (muted && mediaRecorder && mediaRecorder.state === "recording") mediaRecorder.stop();
  });

  stopSpeakingBtn.addEventListener("click", stopSpeaking);
  switchToTextBtn.addEventListener("click", () => setMode("text"));
  switchToVoiceBtn.addEventListener("click", () => setMode("voice"));

  endBtn.addEventListener("click", () => (endModal.style.display = "block"));
  cancelEndBtn.addEventListener("click", () => (endModal.style.display = "none"));
  confirmEndBtn.addEventListener("click", () => {
    confirmEndBtn.disabled = true;
    stopSpeaking();
    fetch("/session/end", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.redirect) window.location.href = data.redirect;
        else confirmEndBtn.disabled = false;
      })
      .catch(() => (confirmEndBtn.disabled = false));
  });

  setMode(mode);
  addBubble("model", window.OM.openingMessage);
  if (mode === "voice") {
    fetch("/chat/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: window.OM.openingMessage }),
    })
      .then((r) => r.json())
      .then((data) => speak(window.OM.openingMessage, data.audio_b64))
      .catch(() => speak(window.OM.openingMessage, null));
  }
})();
