(function () {
  const catData = JSON.parse(document.getElementById("catData").textContent);

  const state = {
    stage: 1,
    situationId: null,
    answers: {
      specific_situation: null,
      situation_details: null,
      main_worry: null,
      desired_support: null,
    },
    feelings: [],
    stress: null,
  };

  const stageContainer = document.getElementById("stageContainer");
  const freeTextContainer = document.getElementById("freeTextContainer");
  const checkinContainer = document.getElementById("checkinContainer");
  const skipBtn = document.getElementById("skipBtn");
  const backBtn = document.getElementById("backBtn");
  const progress = document.getElementById("progress");
  const stageLabel = document.getElementById("stageLabel");

  function stageOptions(n) {
    if (n === 1) return catData.stage1 || [];
    const branch = catData.branches && catData.branches[state.situationId];
    if (n === 2) return (branch && branch.stage2) || catData.generic_stage2 || [];
    return (branch && branch.stage3) || catData.generic_stage3 || [];
  }

  function updateProgress() {
    const dots = progress.querySelectorAll(".dot");
    dots.forEach((d, i) => d.classList.toggle("done", i < state.stage));
    stageLabel.textContent = `Step ${state.stage} of 3`;
  }

  function renderStage(n) {
    state.stage = n;
    freeTextContainer.style.display = "none";
    checkinContainer.style.display = "none";
    stageContainer.style.display = "flex";
    progress.style.display = "flex";
    skipBtn.style.display = "block";
    stageLabel.style.display = "block";
    updateProgress();

    stageContainer.innerHTML = "";
    const options = stageOptions(n);
    options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.className = "option-btn";
      btn.textContent = opt.label;
      btn.addEventListener("click", () => selectOption(n, opt));
      stageContainer.appendChild(btn);
    });
    if (!options.some((o) => o.free_text)) {
      const btn = document.createElement("button");
      btn.className = "option-btn";
      btn.textContent = "Something else";
      btn.addEventListener("click", () => showFreeText(n));
      stageContainer.appendChild(btn);
    }
  }

  function selectOption(n, opt) {
    if (opt.free_text) {
      showFreeText(n);
      return;
    }
    if (n === 1) {
      state.situationId = opt.id;
      state.answers.specific_situation = opt.label;
    } else if (n === 2) {
      state.answers.main_worry = opt.label;
    } else {
      state.answers.desired_support = opt.label;
    }
    advance(n);
  }

  function showFreeText(n) {
    stageContainer.style.display = "none";
    freeTextContainer.style.display = "flex";
    document.getElementById("freeTextInput").value = "";
    document.getElementById("freeTextSubmit").onclick = () => {
      const text = document.getElementById("freeTextInput").value.trim();
      if (n === 1) {
        state.situationId = "something_else";
        state.answers.specific_situation = "Something else";
        state.answers.situation_details = text;
      } else if (n === 2) {
        state.answers.main_worry = text;
      } else {
        state.answers.desired_support = text;
      }
      advance(n);
    };
  }

  function advance(n) {
    if (n < 3) {
      renderStage(n + 1);
    } else {
      showCheckin();
    }
  }

  function showCheckin() {
    stageContainer.style.display = "none";
    freeTextContainer.style.display = "none";
    progress.style.display = "none";
    skipBtn.style.display = "none";
    stageLabel.style.display = "none";
    checkinContainer.style.display = "flex";
  }

  skipBtn.addEventListener("click", () => advance(state.stage));

  backBtn.addEventListener("click", () => {
    if (checkinContainer.style.display === "flex") {
      renderStage(3);
    } else if (state.stage > 1) {
      renderStage(state.stage - 1);
    } else {
      window.history.back();
    }
  });

  const stressSlider = document.getElementById("stressSlider");
  const stressValue = document.getElementById("stressValue");
  stressSlider.addEventListener("input", () => {
    stressValue.textContent = stressSlider.value;
    state.stress = parseInt(stressSlider.value, 10);
  });

  document.querySelectorAll("#feelingChips .chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      chip.classList.toggle("selected");
      const f = chip.dataset.feeling;
      if (state.feelings.includes(f)) {
        state.feelings = state.feelings.filter((x) => x !== f);
      } else {
        state.feelings.push(f);
      }
    });
  });

  function buildContext(preferred_interaction) {
    let details = state.answers.situation_details || "";
    if (state.feelings.length) {
      details += (details ? " " : "") + `Feelings noted: ${state.feelings.join(", ")}.`;
    }
    return {
      category: CATEGORY,
      specific_situation: state.answers.specific_situation,
      situation_details: details || null,
      main_worry: state.answers.main_worry,
      desired_support: state.answers.desired_support,
      initial_stress_level: state.stress,
      preferred_interaction: preferred_interaction,
      conversation_stage: "acknowledge",
    };
  }

  function startSession(preferred_interaction) {
    const btns = checkinContainer.querySelectorAll("button");
    btns.forEach((b) => (b.disabled = true));
    fetch("/session/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildContext(preferred_interaction)),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.redirect) {
          window.location.href = data.redirect;
        } else {
          alert(data.error || "Could not start the conversation. Please try again.");
          btns.forEach((b) => (b.disabled = false));
        }
      })
      .catch(() => {
        alert("Could not reach the server. Please try again.");
        btns.forEach((b) => (b.disabled = false));
      });
  }

  document.getElementById("checkinContinue").addEventListener("click", () => startSession("voice"));
  document.getElementById("checkinContinueText").addEventListener("click", () => startSession("text"));

  renderStage(1);
})();
