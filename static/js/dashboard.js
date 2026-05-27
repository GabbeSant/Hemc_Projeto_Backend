async function carregarDashboard() {
  try {
    const [ind, ordens] = await Promise.all([
      API.get("/indicadores"),
      API.get("/ordens-servico/"),
    ]);

    // Cards de indicadores
    document.querySelector(".total-equipamentos .valor-indicador").textContent = ind.total_equipamentos;
    document.querySelector(".criticos .valor-indicador").textContent = ind.criticos;
    document.querySelector(".em-reparo .valor-indicador").textContent = ind.em_reparo;
    document.querySelector(".conformidade .valor-indicador").textContent = ind.conformidade + "%";

    // Cards de resumo
    document.querySelector(".card-resumo.inativo .numero").textContent = ind.fora_de_operacao;
    document.querySelector(".card-resumo.ativo .numero").textContent = ind.operando;
    document.querySelector(".card-resumo.abertos .numero").textContent = ind.chamados_abertos;

    // Barras de progresso
    const totalOS = ind.os_abertas + ind.os_concluidas;
    const pctOS = totalOS > 0 ? Math.round(ind.os_concluidas / totalOS * 100) : 0;
    const pctPrev = ind.total_manutencoes > 0 ? Math.round(ind.preventivas / ind.total_manutencoes * 100) : 0;
    const pctCrit = ind.total_equipamentos > 0 ? Math.round(ind.criticos / ind.total_equipamentos * 100) : 0;

    const barras = document.querySelectorAll(".barra-preenchimento");
    const pcts = document.querySelectorAll(".barra-info span:last-child");

    if (barras[0]) { barras[0].style.width = pctOS + "%"; pcts[0].textContent = pctOS + "%"; }
    if (barras[1]) { barras[1].style.width = pctPrev + "%"; pcts[1].textContent = pctPrev + "%"; }
    if (barras[2]) { barras[2].style.width = pctCrit + "%"; pcts[2].textContent = pctCrit + "%"; }

    // Tabela de ordens de serviço (últimas 5)
    const tbody = document.querySelector(".tabela-ordens tbody");
    if (tbody && ordens.length > 0) {
      const equipamentos = await API.get("/equipamentos/");
      const mapEq = Object.fromEntries(equipamentos.map(e => [e.id_equipamento, e]));
      const setores = await API.get("/setores");
      const mapSet = Object.fromEntries(setores.map(s => [s.id_setor, s.nome_setor]));

      tbody.innerHTML = ordens.slice(0, 5).map(os => {
        const eq = mapEq[os.id_equipamento] || {};
        const setor = mapSet[eq.id_setor] || "-";
        const crit = eq.grau_criticidade || "-";
        return `
          <tr>
            <td><span class="coluna-os">#OS-${String(os.id_os).padStart(4, "0")}</span></td>
            <td><span class="coluna-EQ">${eq.modelo || "Equipamento #" + os.id_equipamento}</span></td>
            <td>${setor}</td>
            <td><span class="badge-criticidade ${criticidadeClass(crit)}">${crit}</span></td>
            <td><span class="badge-status ${statusOSClass(os.status_os)}">${statusOSLabel(os.status_os)}</span></td>
            <td>${formatarData(os.data_geracao)}</td>
            <td><a href="/pages/ordens-servico.html" class="btn-executar">Ver</a></td>
          </tr>`;
      }).join("");
    }

  } catch (err) {
    console.error("Erro ao carregar dashboard:", err);
  }
}

document.addEventListener("DOMContentLoaded", carregarDashboard);
