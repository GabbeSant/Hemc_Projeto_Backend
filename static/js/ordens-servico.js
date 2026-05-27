async function carregarOrdens() {
  try {
    const [ordens, ind, equipamentos, setores] = await Promise.all([
      API.get("/ordens-servico/"),
      API.get("/indicadores"),
      API.get("/equipamentos/"),
      API.get("/setores"),
    ]);

    const mapEq = Object.fromEntries(equipamentos.map(e => [e.id_equipamento, e]));
    const mapSet = Object.fromEntries(setores.map(s => [s.id_setor, s.nome_setor]));

    // Indicadores
    const elTotal = document.querySelector(".total-chamados .valor-indicador");
    const elCrit = document.querySelector(".criticos .valor-indicador");
    const elConc = document.querySelector(".chamados-concluidos .valor-indicador");

    if (elTotal) elTotal.textContent = ind.chamados_abertos + ind.chamados_fechados;
    if (elCrit) elCrit.textContent = ind.criticos;
    if (elConc) elConc.textContent = ind.os_concluidas;

    // Tabela
    const tbody = document.querySelector(".tabela-ordens tbody");
    if (!tbody) return;

    if (ordens.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;">Nenhuma ordem de serviço encontrada.</td></tr>`;
      return;
    }

    tbody.innerHTML = ordens.map(os => {
      const eq = mapEq[os.id_equipamento] || {};
      const setor = mapSet[eq.id_setor] || "-";
      const crit = eq.grau_criticidade || "-";
      const destino = os.tipo === "corretiva"
        ? `/pages/manutencao-corretiva.html?os=${os.id_os}`
        : `/pages/manutencao-preventiva.html?os=${os.id_os}`;
      const podExecutar = os.status_os !== "concluida" && os.status_os !== "cancelada";

      return `
        <tr>
          <td><span class="coluna-os">#OS-${String(os.id_os).padStart(4, "0")}</span></td>
          <td><span class="coluna-EQ">${eq.modelo || "Equipamento #" + os.id_equipamento}</span></td>
          <td>${setor}</td>
          <td><span class="badge-criticidade ${criticidadeClass(crit)}">${crit}</span></td>
          <td><span class="badge-status ${statusOSClass(os.status_os)}">${statusOSLabel(os.status_os)}</span></td>
          <td>${formatarData(os.data_geracao)}</td>
          <td>${podExecutar
            ? `<a href="${destino}" class="btn-executar">Executar</a>`
            : `<span class="badge-status verde">Concluída</span>`
          }</td>
        </tr>`;
    }).join("");

  } catch (err) {
    console.error("Erro ao carregar ordens:", err);
  }
}

document.addEventListener("DOMContentLoaded", carregarOrdens);
