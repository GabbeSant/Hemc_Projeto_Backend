async function carregarDetalhes() {
  const params = new URLSearchParams(window.location.search);
  const idEq = params.get("eq");

  if (!idEq) {
    document.getElementById("card-detalhes").innerHTML = '<p style="color:red">Equipamento não informado.</p>';
    return;
  }

  try {
    const [eq, tipos, fabricantes, setores, historico] = await Promise.all([
      API.get("/equipamentos/" + idEq),
      API.get("/tipos"),
      API.get("/fabricantes"),
      API.get("/setores"),
      API.get("/manutencoes/equipamento/" + idEq),
    ]);

    const mapTipos = Object.fromEntries(tipos.map(t => [t.id_tipo, t.nome_tipo]));
    const mapFab = Object.fromEntries(fabricantes.map(f => [f.id_fabricante, f.nome_fabricante]));
    const mapSet = Object.fromEntries(setores.map(s => [s.id_setor, s.nome_setor]));

    document.getElementById("d-patrimonio").textContent = "#" + eq.num_patrimonio;
    document.getElementById("d-modelo").textContent = eq.modelo || "-";
    document.getElementById("d-serie").textContent = eq.num_serie || "-";
    document.getElementById("d-tipo").textContent = mapTipos[eq.id_tipo] || "-";
    document.getElementById("d-fabricante").textContent = mapFab[eq.id_fabricante] || "-";
    document.getElementById("d-setor").textContent = mapSet[eq.id_setor] || "-";
    document.getElementById("d-criticidade").textContent = eq.grau_criticidade;
    document.getElementById("d-frequencia").textContent = eq.frequencia_preventiva;
    document.getElementById("d-status").textContent = statusEquipLabel(eq.status_atual);
    document.getElementById("d-aquisicao").textContent = formatarData(eq.data_aquisicao) || "-";
    document.getElementById("d-valor").textContent = eq.valor_aquisicao
      ? "R$ " + eq.valor_aquisicao.toLocaleString("pt-BR", { minimumFractionDigits: 2 })
      : "-";

    document.getElementById("btn-preventiva").href = "/pages/manutencao-preventiva.html?eq=" + idEq;
    document.getElementById("btn-chamado").href = "/pages/abertura-chamado.html?eq=" + idEq;

    const tbody = document.getElementById("tbody-historico");
    if (historico.length === 0) {
      tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:1rem;">Nenhuma manutenção registrada.</td></tr>';
    } else {
      tbody.innerHTML = historico.map(m => `
        <tr>
          <td>${formatarData(m.data_execucao)}</td>
          <td><span class="badge-status ${m.tipo === 'preventiva' ? 'verde' : 'amarelo'}">${m.tipo}</span></td>
          <td>#OS-${String(m.id_os).padStart(4, "0")}</td>
        </tr>`).join("");
    }

    document.title = "Hemec | " + (eq.modelo || "Equipamento #" + idEq);

  } catch (err) {
    document.getElementById("card-detalhes").innerHTML = '<p style="color:red">Erro ao carregar: ' + err.message + '</p>';
  }
}

document.addEventListener("DOMContentLoaded", carregarDetalhes);
