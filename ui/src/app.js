import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open, save } from "@tauri-apps/plugin-dialog";

let files = [];
let processing = false;

const $ = (s) => document.querySelector(s);
const $list = $("#file-list");
const $count = $("#file-count");
const $drop = $("#drop-zone");
const $start = $("#btn-start");
const $progress = $("#progress-section");
const $fill = $("#progress-fill");
const $ptext = $("#progress-text");
const $status = $("#status-msg");
const $settingsBody = $("#settings-body");
const $settingsArrow = $("#settings-arrow");

function renderFiles() {
  $list.innerHTML = files
    .map(
      (f, i) =>
        `<li class="file-item"><span>${f.split(/[\\/]/).pop()}</span><button class="remove" data-i="${i}">✕</button></li>`
    )
    .join("");
  if (files.length) {
    $count.textContent = `${files.length} 个文件`;
    $count.style.display = "block";
    $drop.style.display = "none";
  } else {
    $count.style.display = "none";
    $drop.style.display = "";
  }
}

$list.addEventListener("click", (e) => {
  if (e.target.classList.contains("remove")) {
    files.splice(+e.target.dataset.i, 1);
    renderFiles();
  }
});

$("#btn-clear").addEventListener("click", () => {
  files = [];
  renderFiles();
});

$drop.addEventListener("click", async () => {
  const selected = await open({
    directory: true,
    title: "选择视频目录",
  });
  if (selected) {
    files = [selected];
    renderFiles();
  }
});

$drop.addEventListener("dragover", (e) => {
  e.preventDefault();
  $drop.classList.add("dragover");
});
$drop.addEventListener("dragleave", () => $drop.classList.remove("dragover"));
$drop.addEventListener("drop", (e) => {
  e.preventDefault();
  $drop.classList.remove("dragover");
});

// Settings toggle
$("#settings-toggle").addEventListener("click", () => {
  $settingsBody.classList.toggle("open");
  $settingsArrow.classList.toggle("open");
});

// Progress listener
listen("progress", (event) => {
  const { current, total, name } = event.payload;
  const pct = Math.round((current / total) * 100);
  $fill.style.width = pct + "%";
  $ptext.textContent = `处理中 (${current}/${total}): ${name}`;
});

// Start processing
$start.addEventListener("click", async () => {
  if (processing || files.length === 0) return;
  processing = true;
  $start.disabled = true;
  $start.textContent = "处理中...";
  $progress.classList.add("active");
  $fill.style.width = "0%";
  $ptext.textContent = "准备中...";
  $status.classList.remove("visible");

  try {
    const result = await invoke("process_videos", {
      inputDir: files[0],
      output: $("#output").value,
      threshold: parseFloat($("#threshold").value),
      minDuration: parseFloat($("#min-duration").value),
      codec: $("#codec").value,
      preset: $("#preset").value,
    });
    $fill.style.width = "100%";
    $status.textContent = "✅ " + result;
    $status.classList.add("visible");
  } catch (err) {
    $status.textContent = "❌ " + err;
    $status.classList.add("visible");
  } finally {
    processing = false;
    $start.disabled = false;
    $start.textContent = "开始处理";
  }
});

export { files };
