let urgenciaSelecionada = null;

async function carregarFormulario() {
  try {
    const [equipamentos, setores] = await Promise.all([
      API.get("/equipamentos/"),
      API.get("/setores"),
    ]);

    const selEq = document.getElementById("equipamento");
    const selSetor = document.getElementById("setor");

    if (selEq) {
      selEq.innerHTML = '<option value="">Selecione o equipamento</option>' +
        equipamentos.map(e => `<option value="${e.id_equipamento}">${e.num_patrimonio} – ${e.modelo || "sem modelo"}</option>`).join("");
    }

    if (selSetor) {
      selSetor.innerHTML = '<option value="">Selecione o setor</option>' +
        setores.map(s => `<option value="${s.id_setor}">${s.nome_setor}</option>`).join("");
    }

    // Pré-seleciona equipamento se veio por query string
    const params = new URLSearchParams(window.location.search);
    const eqId = params.get("eq");
    if (eqId && selEq) {
      selEq.value = eqId;
      // Preenche setor automaticamente
      const eq = equipamentos.find(e => e.id_equipamento == eqId);
      if (eq && selSetor) selSetor.value = eq.id_setor;
    }
  } catch (err) {
    console.error("Erro ao carregar formulário:", err);
  }
}

function configurarCriticidade() {
  document.querySelectorAll(".criticidade-option").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".criticidade-option").forEach(b => b.classList.remove("selecionado"));
      btn.classList.add("selecionado");
      urgenciaSelecionada = btn.dataset.valor;
    });
  });
}

async function submeterChamado(e) {
  e.preventDefault();

  const idEquip = parseInt(document.getElementById("equipamento").value);
  const idSetor = parseInt(document.getElementById("setor").value);
  const descricao = document.getElementById("descricao").value.trim();

  if (!idEquip || !idSetor || !descricao || !urgenciaSelecionada) {
    alert("Preencha todos os campos e selecione a criticidade.");
    return;
  }

  try {
    await API.post("/chamados/", {
      descricao_problema: descricao,
      nivel_urgencia: urgenciaSelecionada,
      id_equipamento: idEquip,
      id_usuario_abertura: 1,  // usuário fixo por enquanto (sem login real)
      id_setor: idSetor,
    });
    alert("Chamado aberto com sucesso! Uma OS corretiva foi gerada automaticamente.");
    window.location.href = "/pages/ordens-servico.html";
  } catch (err) {
    alert("Erro ao abrir chamado: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  carregarFormulario();
  configurarCriticidade();

  const form = document.querySelector("form.conteiner-abertura");
  if (form) form.addEventListener("submit", submeterChamado);
});
