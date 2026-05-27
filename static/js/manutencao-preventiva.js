let pecasDisponiveis = [];
let pecasSelecionadas = [];

async function carregarPagina() {
  const params = new URLSearchParams(window.location.search);
  const idOs = params.get("os");

  if (!idOs) {
    document.getElementById("info-os").innerHTML = '<span style="color:red">OS não informada na URL (?os=ID)</span>';
    return;
  }

  try {
    const [os, usuarios, pecas, checklist] = await Promise.all([
      API.get("/ordens-servico/" + idOs),
      API.get("/usuarios/"),
      API.get("/manutencoes/pecas"),
      API.get("/manutencoes/checklist-itens"),
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

    // Checklist
    const container = document.getElementById("checklist-itens");
    checklist.forEach(item => {
      container.innerHTML += `
        <div class="checklist-item" data-id="${item.id_item}">
          <span class="tipo-badge">${item.tipo_teste === "seguranca" ? "🔒" : "📐"}</span>
          <span class="descricao-teste">${item.descricao_teste}</span>
          <select class="resultado-select" data-id="${item.id_item}">
            <option value="aprovado">Aprovado</option>
            <option value="reprovado">Reprovado</option>
            <option value="nao_aplicavel">N/A</option>
          </select>
        </div>`;
    });

    // Mostrar/ocultar seção de peças
    document.querySelectorAll('input[name="substituicao"]').forEach(radio => {
      radio.addEventListener("change", e => {
        document.getElementById("secao-pecas").style.display =
          e.target.value === "sim" ? "block" : "none";
      });
    });

    // Submit
    document.getElementById("form-preventiva").addEventListener("submit", e => submeter(e, os, eq));

  } catch (err) {
    alert("Erro ao carregar página: " + err.message);
  }
}

function adicionarLinhaPeca() {
  const lista = document.getElementById("lista-pecas");
  const idx = lista.children.length;
  const opts = pecasDisponiveis.map(p => `<option value="${p.id_peca}">${p.nome_peca}</option>`).join("");
  lista.innerHTML += `
    <div class="linha-peca" id="peca-${idx}">
      <select class="select-peca" data-idx="${idx}">${opts}</select>
      <input type="number" class="qtd-peca" value="1" min="1" style="width:70px" />
      <button type="button" onclick="this.parentElement.remove()">✕</button>
    </div>`;
}

async function submeter(e, os, eq) {
  e.preventDefault();
  const idResp = parseInt(document.getElementById("responsavel").value);
  if (!idResp) { alert("Selecione o técnico responsável."); return; }

  const houve = document.querySelector('input[name="substituicao"]:checked').value === "sim";

  const pecas = [];
  document.querySelectorAll(".linha-peca").forEach(linha => {
    const idPeca = parseInt(linha.querySelector(".select-peca").value);
    const qtd = parseInt(linha.querySelector(".qtd-peca").value);
    pecas.push({ id_peca: idPeca, quantidade: qtd });
  });

  const checklist = [];
  document.querySelectorAll(".resultado-select").forEach(sel => {
    checklist.push({ id_item: parseInt(sel.dataset.id), resultado: sel.value });
  });

  try {
    await API.post("/manutencoes/preventiva", {
      id_os: os.id_os,
      id_equipamento: os.id_equipamento,
      id_responsavel: idResp,
      houve_substituicao: houve,
      pecas,
      checklist,
    });
    alert("Manutenção preventiva registrada com sucesso!");
    window.location.href = "/pages/ordens-servico.html";
  } catch (err) {
    alert("Erro ao registrar: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", carregarPagina);
