const $ = (s) => document.querySelector(s);
const audio = $("#audio"), player = $("#player"), seek = $("#seek"), toggle = $("#toggle");
const beats = [...document.querySelectorAll(".beat")];
let cur = -1;

const fmt = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

function load(i) {
  if (i < 0 || i >= beats.length) return;
  if (i === cur) return audio.paused ? audio.play() : audio.pause();
  cur = i;
  audio.src = beats[i].dataset.src;
  $("#now").textContent = beats[i].dataset.title;
  player.hidden = false;
  audio.play();
  sync();
}

function sync() {
  beats.forEach((b, i) => b.classList.toggle("on", i === cur && !audio.paused));
  toggle.innerHTML = audio.paused ? "&#9654;" : "&#10074;&#10074;";
}

beats.forEach((b, i) => b.querySelector(".cover").addEventListener("click", () => load(i)));
toggle.onclick = () => (audio.paused ? audio.play() : audio.pause());
$("#next").onclick = () => load((cur + 1) % beats.length);
$("#prev").onclick = () => load((cur - 1 + beats.length) % beats.length);
audio.onplay = audio.onpause = sync;
audio.onended = () => $("#next").click();
audio.ontimeupdate = () => {
  if (audio.duration) seek.value = (audio.currentTime / audio.duration) * 1000;
  $("#time").textContent = fmt(audio.currentTime);
};
seek.oninput = () => audio.duration && (audio.currentTime = (seek.value / 1000) * audio.duration);

document.addEventListener("contextmenu", (e) => e.target.closest(".beat,.player") && e.preventDefault());

document.querySelectorAll(".inquire").forEach((a) =>
  a.addEventListener("click", async () => {
    const title = a.closest(".beat").dataset.title;
    try { await navigator.clipboard.writeText(`Hola, consulta por el beat "${title}" (BEATS OCTUBRE / shelovesttute©)`); } catch {}
    const t = $("#toast");
    t.textContent = "Mensaje copiado. Pegalo en el DM.";
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 2800);
  })
);

document.addEventListener("keydown", (e) => {
  if (e.code === "Space" && cur >= 0 && e.target === document.body) { e.preventDefault(); toggle.click(); }
});
