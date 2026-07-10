const API = "";

function switchTab(id, el) {
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  el.classList.add("active");
  if (id === "tabCompare" && !window._compareLoaded) loadComparison();
}

function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2200);
}

function setGauge(gaugeEl, value, vmin, vmax) {
  const frac = Math.max(0, Math.min(1, (value - vmin) / (vmax - vmin)));
  const deg = 45 + frac * 270; // 45deg..315deg sweep matches the CSS gauge geometry
  gaugeEl.style.transform = `rotate(${deg}deg)`;
}

async function predict24(track = true) {
  const btn = document.getElementById("btn24");
  btn.disabled = true;
  btn.innerHTML = '<span class="material-symbols-outlined animate-spin">autorenew</span> Computing...';
  try {
    const body = {
      pH: parseFloat(document.getElementById("f_pH").value),
      C0: parseFloat(document.getElementById("f_C0").value),
      Time: parseFloat(document.getElementById("f_Time").value),
      Dose: parseFloat(document.getElementById("f_Dose").value),
      Temp: parseFloat(document.getElementById("f_Temp").value),
      Flow: parseFloat(document.getElementById("f_Flow").value),
      Chloride: parseFloat(document.getElementById("f_Chloride").value),
      Hardness: parseFloat(document.getElementById("f_Hardness").value),
      Carbonate: parseFloat(document.getElementById("f_Carbonate").value),
      NOM: parseFloat(document.getElementById("f_NOM").value),
    };
    const res = await fetch(`${API}/api/predict24?track=${track}`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    const d = await res.json();

    document.getElementById("val24").textContent = d.q_hybrid.toFixed(2);
    setGauge(document.getElementById("gauge24"), d.q_hybrid, d.range[0], d.range[1]);

    document.getElementById("b24_base").textContent = `${d.q_langmuir.toFixed(3)} mg/g`;
    document.getElementById("b24_res").textContent = `${d.residual >= 0 ? "+" : ""}${d.residual.toFixed(3)} mg/g`;
    document.getElementById("b24_final").textContent = `${d.q_hybrid.toFixed(3)} mg/g`;

    const maxAbs = Math.max(Math.abs(d.q_langmuir), Math.abs(d.residual), Math.abs(d.q_hybrid), 0.001);
    document.getElementById("bar24_base").style.width = `${Math.min(100, Math.abs(d.q_langmuir) / maxAbs * 100)}%`;
    document.getElementById("bar24_res").style.width = `${Math.min(100, Math.abs(d.residual) / maxAbs * 100)}%`;
    document.getElementById("bar24_final").style.width = `${Math.min(100, Math.abs(d.q_hybrid) / maxAbs * 100)}%`;

    toast("Prediction updated");
  } catch (e) {
    toast("Error: " + e.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined">bolt</span> Predict Hybrid Performance';
  }
}

async function predict4(track = true) {
  const btn = document.getElementById("btn4");
  btn.disabled = true;
  btn.innerHTML = '<span class="material-symbols-outlined animate-spin">autorenew</span> Computing...';
  try {
    const body = {
      pH: parseFloat(document.getElementById("g_pH").value),
      Dose: parseFloat(document.getElementById("g_Dose").value),
      C0: parseFloat(document.getElementById("g_C0").value),
      Time: parseFloat(document.getElementById("g_Time").value),
    };
    const res = await fetch(`${API}/api/predict4?track=${track}`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    const d = await res.json();

    document.getElementById("val4").textContent = d.final.toFixed(1);
    setGauge(document.getElementById("gauge4"), d.final, d.range[0], d.range[1]);

    document.getElementById("b4_base").textContent = `${d.q_baseline.toFixed(2)}%`;
    document.getElementById("b4_res").textContent = `${d.residual >= 0 ? "+" : ""}${d.residual.toFixed(2)}%`;
    document.getElementById("bar4_base").style.width = `100%`;
    document.getElementById("bar4_res").style.width = `${Math.min(100, Math.abs(d.residual) / Math.max(Math.abs(d.q_baseline), 0.001) * 100)}%`;

    toast("Prediction updated");
  } catch (e) {
    toast("Error: " + e.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined">bolt</span> Predict Fluoride Removal';
  }
}

async function loadComparison() {
  window._compareLoaded = true;
  const res = await fetch(`${API}/api/comparison`);
  const d = await res.json();

  const tbody = document.getElementById("compareTable");
  tbody.innerHTML = d.models.map(m => `
    <tr class="border-t border-outline">
      <td class="px-4 py-3 font-sans font-semibold text-on-surface">${m.name}</td>
      <td class="px-4 py-3 font-sans text-on-surface-variant">${m.dataset}</td>
      <td class="px-4 py-3 font-sans text-on-surface-variant">${m.response}</td>
      <td class="px-4 py-3 text-right">${m.baseline_r2.toFixed(3)}</td>
      <td class="px-4 py-3 text-right">${m.residual_r2.toFixed(3)}</td>
      <td class="px-4 py-3 text-right font-semibold">${m.final_r2.toFixed(3)}</td>
      <td class="px-4 py-3 text-right">${m.final_rmse}</td>
    </tr>`).join("");

  new Chart(document.getElementById("compareChart"), {
    type: "bar",
    data: {
      labels: d.models.map(m => m.name),
      datasets: [{
        label: "Final R²",
        data: d.models.map(m => m.final_r2),
        backgroundColor: ["#1E40AF", "#2A9D8F"],
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: { display: true, text: "Model R² Comparison (cross-validated OOF)", color: "#E2E8F0", font: { size: 14 } },
      },
      scales: {
        y: { beginAtZero: true, max: 1.05, grid: { color: "#1E293B" }, ticks: { color: "#94A3B8" } },
        x: { grid: { color: "#1E293B" }, ticks: { color: "#94A3B8" } }
      }
    }
  });
}

// Initial predictions on load
window.addEventListener("DOMContentLoaded", () => {
  predict24(false);
  predict4(false);
});
