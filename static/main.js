let editId = null;
let chartTotal, chartClientes;

document.addEventListener("DOMContentLoaded", () => {
  cargarCreditos();
  configurarFormulario();
});

function configurarFormulario() {
  const form = document.getElementById("form-credito");
  const btnCancelar = document.getElementById("btn-cancelar");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    limpiarError();

    const data = leerFormulario();
    const error = validarFront(data);
    if (error) return mostrarError(error);

    try {
      const resp = await fetch(editId ? `/api/creditos/${editId}` : "/api/creditos", {
        method: editId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const json = await resp.json();
      if (!resp.ok) throw new Error(json.error || "Error en el servidor");

      form.reset();
      editId = null;
      btnCancelar.hidden = true;
      document.getElementById("btn-guardar").textContent = "Guardar";
      await cargarCreditos();
    } catch (err) {
      mostrarError(err.message);
    }
  });

  btnCancelar.addEventListener("click", () => {
    editId = null;
    form.reset();
    btnCancelar.hidden = true;
    document.getElementById("btn-guardar").textContent = "Guardar";
    limpiarError();
  });
}

function leerFormulario() {
  return {
    cliente: document.getElementById("cliente").value.trim(),
    monto: document.getElementById("monto").value,
    tasa_interes: document.getElementById("tasa_interes").value,
    plazo: document.getElementById("plazo").value,
    fecha_otorgamiento: document.getElementById("fecha_otorgamiento").value,
  };
}

function validarFront(d) {
  if (!d.cliente) return "El campo 'Cliente' es obligatorio.";
  if (d.monto === "" || Number(d.monto) < 0) return "Monto inválido.";
  if (d.tasa_interes === "" || Number(d.tasa_interes) < 0) return "Tasa inválida.";
  if (!Number.isInteger(Number(d.plazo)) || Number(d.plazo) <= 0) return "Plazo inválido.";
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d.fecha_otorgamiento)) return "Fecha con formato YYYY-MM-DD.";
  return null;
}

function mostrarError(msg) {
  const p = document.getElementById("form-error");
  p.textContent = msg;
  p.hidden = false;
}
function limpiarError() {
  const p = document.getElementById("form-error");
  p.hidden = true;
  p.textContent = "";
}

async function cargarCreditos() {
  const tbody = document.querySelector("#tabla-creditos tbody");
  tbody.innerHTML = "";

  const resp = await fetch("/api/creditos");
  const data = await resp.json();

  data.forEach((c) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.id}</td>
      <td>${esc(c.cliente)}</td>
      <td>${Number(c.monto).toFixed(2)}</td>
      <td>${Number(c.tasa_interes).toFixed(2)}</td>
      <td>${c.plazo}</td>
      <td>${c.fecha_otorgamiento}</td>
      <td>
        <div class="row-actions">
          <button onclick="editar(${c.id})">Editar</button>
          <button class="secondary" onclick="eliminarCredito(${c.id})">Eliminar</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  actualizarGraficos(data);
}

function esc(str) {
  const div = document.createElement("div");
  div.innerText = str;
  return div.innerHTML;
}

async function editar(id) {
  const resp = await fetch("/api/creditos");
  const data = await resp.json();
  const c = data.find(x => x.id === id);
  if (!c) return;

  editId = id;
  document.getElementById("cliente").value = c.cliente;
  document.getElementById("monto").value = c.monto;
  document.getElementById("tasa_interes").value = c.tasa_interes;
  document.getElementById("plazo").value = c.plazo;
  document.getElementById("fecha_otorgamiento").value = c.fecha_otorgamiento;

  document.getElementById("btn-guardar").textContent = "Actualizar";
  document.getElementById("btn-cancelar").hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function eliminarCredito(id) {
  if (!confirm("¿Eliminar este crédito?")) return;
  const resp = await fetch(`/api/creditos/${id}`, { method: "DELETE" });
  const json = await resp.json();
  if (!resp.ok) return alert(json.error || "Error al eliminar");
  cargarCreditos();
}

// ---------- Gráficos ----------
function actualizarGraficos(creditos) {
  const total = creditos.reduce((acc, c) => acc + Number(c.monto), 0);

  // Gráfico 1: Total 
  const ctx1 = document.getElementById("chartTotal").getContext("2d");
  if (chartTotal) chartTotal.destroy();
  chartTotal = new Chart(ctx1, {
    type: "bar",
    data: {
      labels: ["Total otorgado"],
      datasets: [{ label: "MXN", data: [total] }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: { y: { beginAtZero: true } }
    }
  });

  // Gráfico 2: Distribución por cliente
  const porCliente = {};
  creditos.forEach(c => {
    porCliente[c.cliente] = (porCliente[c.cliente] || 0) + Number(c.monto);
  });
  const labels = Object.keys(porCliente);
  const valores = Object.values(porCliente);

  const ctx2 = document.getElementById("chartClientes").getContext("2d");
  if (chartClientes) chartClientes.destroy();
  chartClientes = new Chart(ctx2, {
    type: "pie",
    data: {
      labels,
      datasets: [{ data: valores }]
    },
    options: { responsive: true }
  });
}
