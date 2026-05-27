let todosEquipamentos = [];
let mapTipos = {};
let mapFabricantes = {};
let mapSetores = {};

async function carregarEquipamentos() {
  try {
    const [equipamentos, tipos, fabricantes, setores] = await Promise.all([
      API.get("/equipamentos/"),
      API.get("/tipos"),
      API.get("/fabricantes"),
      API.get("/setores"),
    ]);

    mapTipos = Object.fromEntries(tipos.map(t => [t.id_tipo, t.nome_tipo]));
    mapFabricantes = Object.fromEntries(fabricantes.map(f => [f.id_fabricante, f.nome_fabricante]));
    mapSetores = Object.fromEntries(setores.map(s => [s.id_setor, s.nome_setor]));

    todosEquipamentos = equipamentos;
    renderizarTabela(equipamentos);
  } catch (err) {
    console.error("Erro ao carregar equipamentos:", err);
  }
}

function renderizarTabela(lista) {
  const tbody = document.querySelector(".tabela-equipamentos tbody");
  if (!tbody) return;

  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;">Nenhum equipamento encontrado.</td></tr>`;
    return;
  }

  tbody.innerHTML = lista.map(eq => {
    const tipo = mapTipos[eq.id_tipo] || "-";
    const fab = mapFabricantes[eq.id_fabricante] || "-";
    const setor = mapSetores[eq.id_setor] || "-";
    const crit = eq.grau_criticidade;
    const statusLabel = statusEquipLabel(eq.status_atual);
    const statusCss = statusEquipClass(eq.status_atual);

    return `
      <tr>
        <td><span class="coluna-PATRIM">#${eq.num_patrimonio}</span></td>
        <td><span class="coluna-EQ">${tipo}</span></td>
        <td>${fab} - ${eq.modelo || "-"}</td>
        <td>${setor}</td>
        <td><span class="badge-criticidade ${criticidadeClass(crit)}">${crit}</span></td>
        <td><span class="badge-status ${statusCss}">${statusLabel}</span></td>
        <td class="acoes-manutencao">
          <div class="btns-acao">
            <a href="/pages/preventiva-checklist.html?eq=${eq.id_equipamento}" class="btn-preventiva">Fazer Preventiva</a>
            <a href="/pages/abertura-chamado.html?eq=${eq.id_equipamento}" class="btn-chamado">Abrir Chamado</a>
            <a href="/pages/Cadastro_equipamentos.html?eq=${eq.id_equipamento}" class="btn-editar">Editar</a>
          </div>
          <a href="/pages/detalhes-equipamento.html?eq=${eq.id_equipamento}" class="btn-detalhes">Detalhes</a>
        </td>
      </tr>`;
  }).join("");
}

function filtrarEquipamentos(termo) {
  const t = termo.toLowerCase();
  const filtrados = todosEquipamentos.filter(eq => {
    const tipo = (mapTipos[eq.id_tipo] || "").toLowerCase();
    const fab = (mapFabricantes[eq.id_fabricante] || "").toLowerCase();
    const pat = eq.num_patrimonio.toLowerCase();
    const modelo = (eq.modelo || "").toLowerCase();
    return tipo.includes(t) || fab.includes(t) || pat.includes(t) || modelo.includes(t);
  });
  renderizarTabela(filtrados);
}

document.addEventListener("DOMContentLoaded", () => {
  carregarEquipamentos();

  const busca = document.getElementById("busca-equipamento");
  if (busca) {
    busca.addEventListener("input", e => filtrarEquipamentos(e.target.value));
  }
});
