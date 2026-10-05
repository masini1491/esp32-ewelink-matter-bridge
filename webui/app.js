"use strict";

const channelCards = [...document.querySelectorAll(".channel-card")];
const availabilityValue = document.getElementById("availability-value");
const availabilityHelp = document.getElementById("availability-help");
const feedback = document.getElementById("action-feedback");
const activityList = document.getElementById("activity-list");
const transportResult = document.getElementById("transport-result");

const observedLabels = { on: "ON", off: "OFF", unknown: "Unknown" };
const convergenceLabels = {
  none: "No outcome",
  matched: "Matched observation",
  conflicted: "Conflicting observation",
  rejected: "Rejected by simulator",
};

function setField(card, name, value) {
  const field = card.querySelector(`[data-field="${name}"]`);
  if (field) field.textContent = value;
}

function renderState(state) {
  const available = state.availability === "available";
  availabilityValue.textContent = available ? "Available · simulated" : "Unavailable · simulated";
  availabilityHelp.textContent = available
    ? "Commands are synthetic intents. Only an explicit observation changes observed state."
    : "Connect the simulator before submitting command intents. Synthetic observations remain available for deterministic state setup.";

  for (const channel of state.channels) {
    const card = channelCards.find((item) => Number(item.dataset.channel) === channel.index);
    if (!card) continue;
    const observed = observedLabels[channel.observed_state] || "Unknown";
    const pill = card.querySelector('[data-field="observed-state"]');
    pill.textContent = observed;
    pill.dataset.state = channel.observed_state;
    setField(card, "observed-detail", observed);
    setField(card, "freshness", channel.fresh ? "Fresh observation" : channel.observed_state === "unknown" ? "No observation yet" : "Stale observation");
    setField(card, "pending", channel.pending_state ? `Request ${channel.pending_state.toUpperCase()}` : "None");

    let disposition = "No command submitted";
    if (channel.transport_disposition === "accepted") disposition = "Accepted by simulator";
    if (channel.transport_disposition === "rejected") disposition = "Rejected by simulator";
    if (channel.pending_state && channel.transport_disposition === "accepted") disposition += " · awaiting observation";
    setField(card, "transport", disposition);
    setField(card, "convergence", convergenceLabels[channel.convergence] || "Unknown");

    for (const button of card.querySelectorAll("[data-command]")) button.disabled = !available;
  }

  activityList.replaceChildren();
  const events = [...(state.events || [])].reverse();
  if (events.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty-event";
    empty.textContent = "No synthetic actions yet.";
    activityList.append(empty);
  } else {
    for (const event of events) {
      const item = document.createElement("li");
      item.textContent = event;
      activityList.append(item);
    }
  }
}

async function refresh() {
  const response = await fetch("/api/state", { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error("Simulator state is unavailable.");
  renderState(await response.json());
}

async function dispatch(action) {
  feedback.textContent = "Applying synthetic action…";
  try {
    const response = await fetch("/api/actions", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(action),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Action was not accepted.");
    renderState(result);
    if (action.action === "submit") {
      const channel = result.channels[action.channel];
      feedback.textContent = channel.transport_disposition === "accepted"
        ? "Synthetic transport accepted. Observed state waits for an observation."
        : "Synthetic transport rejected. Observed state was not changed.";
    } else {
      feedback.textContent = "Synthetic simulator updated. No hardware operation occurred.";
    }
  } catch (error) {
    feedback.textContent = error instanceof Error ? error.message : "Simulator action failed.";
  }
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button || button.disabled) return;
  const card = button.closest(".channel-card");
  if (button.dataset.action === "set-transport") {
    dispatch({ action: "set_transport", result: transportResult.value });
  } else if (button.dataset.action) {
    dispatch({ action: button.dataset.action });
  } else if (card && button.dataset.command) {
    dispatch({ action: "submit", channel: Number(card.dataset.channel), state: button.dataset.command });
  } else if (card && button.dataset.observe) {
    dispatch({ action: "observe", channel: Number(card.dataset.channel), state: button.dataset.observe });
  }
});

refresh().catch((error) => {
  availabilityValue.textContent = "Unavailable · simulator did not start";
  feedback.textContent = error instanceof Error ? error.message : "Simulator state is unavailable.";
});
