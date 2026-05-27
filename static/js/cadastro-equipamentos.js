let modoEdicao = false;
let equipId = null;

async function carregarSelects() {
  try {
    const [tipos, fabricantes, setores] = await Promise.all([
      API.get("/tipos"),
      API.get("/fabricantes"),
      API.get("/setores"),
    ]);

    preencherSelect("id_tipo", tipos, "id_tipo", "nome_tipo", "o tipo");
    preencherSelect("id_fabricante", fabricantes, "id_fabricante", "nome_fabricante", "o fabricante");
    preencherSelect("id_setor", setores, "id_setor", "nome_setor", "o setor");
  } catch (err) {
    console.error("Erro ao carregar selects:", err);
  }
}

function preencherSelect(id, lista, campoValor, campoLabel, placeholder) {
  const sel = document.getElementById(id);
  if (!sel) return;
  sel.innerHTML =
    `<option value="">Selecione ${placeholder}</option>` +
    lista.map(item => `<option value="${item[campoValor]}">${item[campoLabel]}</option>`).join("");
}

async function carregarEquipamento(id) {
  try {
    const eq = await API.get(`/equipamentos/${id}`);

    document.getElementById("num_patrimonio").value = eq.num_patrimonio || "";
    document.getElementById("modelo").value = eq.modelo || "";
    document.getElementById("num_serie").value = eq.num_serie || "";
    document.getElementById("data_aquisicao").value = eq.data_aquisicao || "";
    document.getElementById("valor_aquisicao").value = eq.valor_aquisicao || "";
    document.getElementById("id_tipo").value = eq.id_tipo;
    document.getElementById("id_fabricante").value = eq.id_fabricante;
    document.getElementById("id_setor").value = eq.id_setor;

    const radioCrit = document.querySelector(`input[name="criticidade"][value="${eq.grau_criticidade}"]`);
    if (radioCrit) radioCrit.checked = true;

    const radioFreq = document.querySelector(`input[name="frequencia"][value="${eq.frequencia_preventiva}"]`);
    if (radioFreq) radioFreq.checked = true;

    const titulo = document.getElementById("titulo-pagina");
    if (titulo) titulo.textContent = "Editar Equipamento";
  } catch (err) {
    alert("Erro ao carregar equipamento: " + err.message);
  }
}

async function salvarEquipamento(e) {
  e.preventDefault();

  const numPatrimonio = document.getElementById("num_patrimonio").value.trim();
  const criticidade = document.querySelector('input[name="criticidade"]:checked');
  const frequencia = document.querySelector('input[name="frequencia"]:checked');
  const idTipo = parseInt(document.getElementById("id_tipo").value);
  const idFabricante = parseInt(document.getElementById("id_fabricante").value);
  const idSetor = parseInt(document.getElementById("id_setor").value);

  if (!numPatrimonio || !criticidade || !frequencia || !idTipo || !idFabricante || !idSetor) {
    alert("Preencha todos os campos obrigatórios: número patrimonial, tipo, fabricante, setor, criticidade e frequência.");
    return;
  }

  const dados = {
    num_patrimonio: numPatrimonio,
    modelo: document.getElementById("modelo").value.trim() || null,
    num_serie: document.getElementById("num_serie").value.trim() || null,
    data_aquisicao: document.getElementById("data_aquisicao").value || null,
    valor_aquisicao: parseFloat(document.getElementById("valor_aquisicao").value) || null,
    grau_criticidade: criticidade.value,
    frequencia_preventiva: frequencia.value,
    id_tipo: idTipo,
    id_fabricante: idFabricante,
    id_setor: idSetor,
  };

  try {
    if (modoEdicao) {
      await API.put(`/equipamentos/${equipId}`, dados);
      alert("Equipamento atualizado com sucesso!");
    } else {
      await API.post("/equipamentos/", dados);
      alert("Equipamento cadastrado com sucesso!");
    }
    window.location.href = "/pages/equipamentos.html";
  } catch (err) {
    alert("Erro ao salvar equipamento: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await carregarSelects();

  const params = new URLSearchParams(window.location.search);
  equipId = params.get("eq");
  if (equipId) {
    modoEdicao = true;
    await carregarEquipamento(equipId);
  }

  const form = document.getElementById("form-equipamento");
  if (form) form.addEventListener("submit", salvarEquipamento);
});
