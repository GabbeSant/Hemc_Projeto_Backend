let pecasDisponiveis = [];

async function carregarPagina() {
  const params = new URLSearchParams(window.location.search);
  const idOs = params.get("os");

  if (!idOs) {
    document.getElementById("os-numero").textContent = "OS não informada";
    return;
  }

  try {
    const [os, usuarios, pecas] = await Promise.all([
      API.get("/ordens-servico/" + idOs),
      API.get("/usuarios/"),
      API.get("/manutencoes/pecas"),
    ]);

    document.getElementById("os-numero").textContent = "#OS-" + String(os.id_os).padStart(4, "0");

    const equipamentos = await API.get("/equipamentos/");
    const eq = equipamentos.find(e => e.id_equipamento === os.id_equipamento);
    document.getElementById("os-equipamento").textContent = eq ? (eq.modelo || "Equipamento #" + eq.id_equipamento) : "-";

    // Técnicos
    const selResp = document.getElementById("responsavel");
    usuarios.filter(u => u.perfil === "tecnico").forEach(u => {
      selResp.innerHTML += `<option value="${u.id_usuario}">${u.nome}</option>`;
    });

    // Peças
    pecasDisponiveis = pecas;
    document.getElementById("btn-add-peca").addEventListener("click", adicionarLinhaPeca);

    // Submit
    document.getElementById("form-corretiva").addEventListener("submit", e => submeter(e, os));

  } catch (err) {
    alert("Erro ao carregar página: " + err.message);
  }
}

function adicionarLinhaPeca() {
  const lista = document.getElementById("lista-pecas");
  const idx = lista.children.length;
  const opts = pecasDisponiveis.map(p => `<option value="${p.id_peca}">${p.nome_peca}</option>`).join("");
  lista.innerHTML += `
    <div class="linha-peca">
      <select class="select-peca">${opts}</select>
      <input type="number" class="qtd-peca" value="1" min="1" style="width:70px" />
      <button type="button" onclick="this.parentElement.remove()">✕</button>
    </div>`;
}

async function submeter(e, os) {
  e.preventDefault();
  const idResp = parseInt(document.getElementById("responsavel").value);
  if (!idResp) { alert("Selecione o técnico responsável."); return; }

  const pecas = [];
  document.querySelectorAll(".linha-peca").forEach(linha => {
    pecas.push({
      id_peca: parseInt(linha.querySelector(".select-peca").value),
      quantidade: parseInt(linha.querySelector(".qtd-peca").value),
    });
  });

  try {
    await API.post("/manutencoes/corretiva", {
      id_os: os.id_os,
      id_equipamento: os.id_equipamento,
      id_responsavel: idResp,
      descricao_reparo: document.getElementById("descricao-reparo").value,
      testes_finais: document.getElementById("testes-finais").value,
      status_resultante: document.getElementById("status-resultante").value,
      pecas,
    });
    alert("Manutenção corretiva registrada com sucesso!");
    window.location.href = "/pages/ordens-servico.html";
  } catch (err) {
    alert("Erro ao registrar: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", carregarPagina);
