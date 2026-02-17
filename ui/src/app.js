import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open, save } from "@tauri-apps/plugin-dialog";

// --- Theme ---
const stored = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
if (stored === "dark" || (!stored && prefersDark)) document.documentElement.dataset.theme = "dark";

let files = [];
let processing = false;

const $ = (s) => document.querySelector(s);
const $drop = $("#drop-zone");
const $fileSection = $("#file-section");
const $list = $("#file-list");
const $count = $("#file-count");
const $start = $("#btn-start");
const $progress = $("#progress-section");
const $fill = $("#progress-fill");
const $ptext = $("#progress-text");
const $pct = $("#progress-pct");
const $status = $("#status-msg");
const $settingsBody = $("#settings-body");
const $settingsArrow = $("#settings-arrow");

// --- Theme toggle ---
$("#btn-theme").addEventListener("click", () => {
  const isDark = document.documentElement.dataset.theme === "dark";
  document.documentElement.dataset.theme = isDark ? "" : "dark";
  localStorage.setItem("theme", isDark ? "light" : "dark");
});

// --- File rendering ---
function renderFiles() {
  if (files.length) {
    $drop.style.display = "none";
    $fileSection.style.display = "";
    $count.textContent = `${files.length} 个文件`;
    $list.innerHTML = files
      .map(
        (f, i) =>
          `<li class="file-item" style="animation-delay:${i * 30}ms">
            <div class="name"><span class="file-icon">🎬</span><span>${f.split(/[\\/]/).pop()}</span></div>
            <button class="remove" data-i="${i}">✕</button>
          </li>`
      )
      .join("");
  } else {
    $drop.style.display = "";
    $fileSection.style.display = "none";
    $list.innerHTML = "";
  }
}

// --- File actions ---
$list.addEventListener("click", (e) => {
  const btn = e.target.closest(".remove");
  if (btn) {
    files.splice(+btn.dataset.i, 1);
    renderFiles();
  }
});

$("#btn-clear").addEventListener("click", () => {
  if (processing) return;
  files = [];
  renderFiles();
  $status.className = "status-msg";
  $progress.classList.remove("active");
});

async function browseDir() {
  const selected = await open({ directory: true, title: "选择视频目录" });
  if (selected) {
    files = [selected];
    renderFiles();
  }
}

$("#btn-browse").addEventListener("click", (e) => { e.stopPropagation(); browseDir(); });
$("#btn-add-more").addEventListener("click", browseDir);
$drop.addEventListener("click", browseDir);

// --- Drag & drop ---
$drop.addEventListener("dragover", (e) => { e.preventDefault(); $drop.classList.add("dragover"); });
$drop.addEventListener("dragleave", () => $drop.classList.remove("dragover"));
$drop.addEventListener("drop", (e) => { e.preventDefault(); $drop.classList.remove("dragover"); });

// --- Settings toggle with smooth animation ---
$("#settings-toggle").addEventListener("click", () => {
  $settingsBody.classList.toggle("open");
  $settingsArrow.classList.toggle("open");
});

// --- Range ↔ number sync ---
const threshRange = $("#threshold-range");
const threshNum = $("#threshold");
const durRange = $("#duration-range");
const durNum = $("#min-duration");

threshRange.addEventListener("input", () => { threshNum.value = threshRange.value; });
threshNum.addEventListener("input", () => { threshRange.value = threshNum.value; });
durRange.addEventListener("input", () => { durNum.value = durRange.value; });
durNum.addEventListener("input", () => { durRange.value = durNum.value; });

// --- Output file picker ---
$("#btn-output").addEventListener("click", async () => {
  const path = await save({
    defaultPath: $("#output").value,
    filters: [{ name: "Video", extensions: ["mp4"] }],
  });
  if (path) $("#output").value = path;
});

// --- Progress listener ---
listen("progress", (event) => {
  const { current, total, name } = event.payload;
  const pctVal = Math.round((current / total) * 100);
  $fill.style.width = pctVal + "%";
  $pct.textContent = pctVal + "%";
  $ptext.textContent = `处理: ${name}`;
});

// --- Start processing ---
$start.addEventListener("click", async () => {
  if (processing) return;
  if (files.length === 0) {
    $("#card-files").classList.add("shake");
    setTimeout(() => $("#card-files").classList.remove("shake"), 400);
    return;
  }

  processing = true;
  $start.disabled = true;
  $start.querySelector("span").textContent = "处理中...";
  $start.classList.add("processing");
  $progress.classList.add("active");
  $fill.style.width = "0%";
  $pct.textContent = "";
  $ptext.textContent = "准备中...";
  $status.className = "status-msg";

  try {
    const result = await invoke("process_videos", {
      inputDir: files[0],
      output: $("#output").value,
      threshold: parseFloat(threshNum.value),
      minDuration: parseFloat(durNum.value),
      codec: $("#codec").value,
      preset: $("#preset").value,
    });
    $fill.style.width = "100%";
    $pct.textContent = "100%";
    $status.textContent = "✅ " + result;
    $status.className = "status-msg visible success";
  } catch (err) {
    $status.textContent = "❌ " + err;
    $status.className = "status-msg visible error";
  } finally {
    processing = false;
    $start.disabled = false;
    $start.querySelector("span").textContent = "开始处理";
    $start.classList.remove("processing");
  }
});
