"use strict";
const $ = (selector) => document.querySelector(selector);
let tasks = [];
let filter = "all";
let loaded = false;
let toastTimer;
const pending = new Set();

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    let message = `Something went wrong (${response.status}). Please try again.`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (response.status === 422) message = "Check your task details and try again.";
    } catch (_) { /* Keep the HTTP error if the server did not return JSON. */ }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

function showError(message) {
  $("#error").textContent = message;
  $("#error").hidden = !message;
}

function toast(message) {
  clearTimeout(toastTimer);
  $("#toast").textContent = message;
  $("#toast").hidden = false;
  toastTimer = setTimeout(() => { $("#toast").hidden = true; }, 3000);
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function openForm() {
  $("#task-form").reset();
  $("#form-error").hidden = true;
  $("#task-dialog").showModal();
  $("#title").focus();
}

function render() {
  const done = tasks.filter((task) => task.completed).length;
  const percent = tasks.length ? Math.round(done / tasks.length * 100) : 0;
  $("#total").textContent = tasks.length;
  $("#active").textContent = tasks.length - done;
  $("#done").textContent = done;
  $("#percent").textContent = `${percent}%`;
  $("#progress").value = percent;
  $("#nav-count").textContent = tasks.length;
  $("#all-count").textContent = tasks.length;
  $("#momentum").textContent = tasks.length ? `${done} of ${tasks.length} tasks complete. Keep going.` : "A fresh start. Make it yours.";
  const query = $("#search").value.trim().toLowerCase();
  const visible = tasks.filter((task) => (filter === "all" || task.completed === (filter === "completed")) && `${task.title} ${task.notes}`.toLowerCase().includes(query));
  document.querySelectorAll("[data-filter]").forEach((button) => {
    const selected = button.dataset.filter === filter;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", selected);
  });
  document.querySelectorAll("[data-view]").forEach((button) => {
    const selected = button.dataset.view === (filter === "completed" ? "completed" : "all");
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", selected);
  });
  $("#shown-count").textContent = `${visible.length} ${visible.length === 1 ? "task" : "tasks"} shown`;
  const list = $("#task-list");
  list.replaceChildren();
  if (!visible.length) {
    const empty = element("div", "empty");
    empty.append(element("div", "empty-icon", "↗"));
    empty.append(element("h3", "", tasks.length ? "A little breathing room." : "Start with one small thing."));
    empty.append(element("p", "", tasks.length ? "No tasks match this view. Try another filter or search." : "Add your first task and give your next idea a place to land."));
    const button = element("button", "", tasks.length ? "Show all tasks →" : "+ Create your first task");
    button.addEventListener("click", () => {
      if (!tasks.length) openForm();
      else { filter = "all"; $("#search").value = ""; render(); }
    });
    empty.append(button);
    list.append(empty);
    return;
  }
  for (const task of visible) {
    const row = element("article", `task${task.completed ? " completed" : ""}`);
    const checkbox = element("input", "task-check");
    checkbox.type = "checkbox";
    checkbox.checked = task.completed;
    checkbox.disabled = pending.has(task.id);
    checkbox.setAttribute("aria-label", `${task.completed ? "Reopen" : "Complete"} ${task.title}`);
    checkbox.addEventListener("change", () => changeStatus(task));
    const body = element("div", "task-body");
    body.append(element("div", "task-title", task.title));
    if (task.notes) body.append(element("p", "task-notes", task.notes));
    const meta = element("div", "task-meta");
    meta.append(element("span", `badge ${task.priority}`, `${task.priority[0].toUpperCase()}${task.priority.slice(1)} priority`));
    const date = new Date(task.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" });
    meta.append(element("span", "", `Added ${date}`));
    body.append(meta);
    const remove = element("button", "task-delete", "×");
    remove.disabled = pending.has(task.id);
    remove.setAttribute("aria-label", `Delete ${task.title}`);
    remove.addEventListener("click", () => deleteTask(task));
    row.append(checkbox, body, remove);
    list.append(row);
  }
}

async function changeStatus(task) {
  if (pending.has(task.id)) return;
  pending.add(task.id);
  render();
  try {
    const updated = await api(`/api/tasks/${task.id}`, { method: "PATCH", body: JSON.stringify({ completed: !task.completed }) });
    tasks = tasks.map((item) => item.id === updated.id ? updated : item);
    showError("");
    toast(updated.completed ? "One more thing done. Nice work." : "Task moved back to in progress.");
  } catch (error) { showError(error.message); }
  finally { pending.delete(task.id); render(); }
}

async function deleteTask(task) {
  if (pending.has(task.id) || !window.confirm(`Delete “${task.title}”? This cannot be undone.`)) return;
  pending.add(task.id);
  render();
  try {
    await api(`/api/tasks/${task.id}`, { method: "DELETE" });
    tasks = tasks.filter((item) => item.id !== task.id);
    showError("");
    toast("Task deleted.");
  } catch (error) { showError(error.message); }
  finally { pending.delete(task.id); render(); }
}

$("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = $("#title").value.trim();
  if (!title) { $("#title").setCustomValidity("Please give your task a name."); $("#title").reportValidity(); return; }
  $("#submit-task").disabled = true;
  $("#form-error").hidden = true;
  try {
    const task = await api("/api/tasks", { method: "POST", body: JSON.stringify({ title, notes: $("#notes").value.trim(), priority: $("#priority").value }) });
    tasks.unshift(task);
    filter = "all";
    $("#search").value = "";
    $("#task-dialog").close();
    showError("");
    if (!loaded) await load();
    else render();
    toast("A new step, ready when you are.");
  } catch (error) { $("#form-error").textContent = error.message; $("#form-error").hidden = false; }
  finally { $("#submit-task").disabled = false; }
});
$("#title").addEventListener("input", () => $("#title").setCustomValidity(""));
$("#close-dialog").addEventListener("click", () => $("#task-dialog").close());
$("#cancel-task").addEventListener("click", () => $("#task-dialog").close());
document.querySelectorAll(".new-task").forEach((button) => button.addEventListener("click", openForm));
document.querySelectorAll("[data-filter], [data-view]").forEach((button) => button.addEventListener("click", () => { filter = button.dataset.filter || button.dataset.view; render(); }));
$("#search").addEventListener("input", render);

async function load() {
  try {
    tasks = await api("/api/tasks");
    loaded = true;
    $("#connection").textContent = "Connected to your board";
    $("#connection").classList.add("online");
    showError("");
    render();
  } catch (_) {
    $("#connection").textContent = "Connection unavailable";
    $("#connection").classList.remove("online");
    showError("We couldn’t load your tasks. Check the server connection and refresh to try again.");
    $("#task-list").replaceChildren(element("div", "empty", "Your saved tasks will appear when the connection is restored."));
  }
}
load();
