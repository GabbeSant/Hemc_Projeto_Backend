const API = {
  base: "/api",

  async get(path) {
    const res = await fetch(this.base + path);
    if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
    return res.json();
  },

  async post(path, body) {
    const res = await fetch(this.base + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
    return res.json();
  },

  async patch(path, body) {
    const res = await fetch(this.base + path, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
    return res.json();
  },

  async put(path, body) {
    const res = await fetch(this.base + path, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
    return res.json();
  },

  async delete(path) {
    const res = await fetch(this.base + path, { method: "DELETE" });
    if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
    return res.status === 204 ? null : res.json();
  },
};

function formatarData(isoStr) {
  if (!isoStr) return "-";
  const d = new Date(isoStr);
  return d.toLocaleDateString("pt-BR");
}

function criticidadeClass(grau) {
  return { A: "vermelho", B: "amarelo", C: "azul" }[grau] || "";
}

function statusEquipLabel(status) {
  const map = {
    em_funcionamento:  "Operando",
    em_manutencao:     "Em manutenção",
    aguardando_reparo: "Corrigir",
    fora_de_operacao:  "Inativo",
  };
  return map[status] || status;
}

function statusEquipClass(status) {
  const map = {
    em_funcionamento:  "verde",
    em_manutencao:     "amarelo",
    aguardando_reparo: "vermelho",
    fora_de_operacao:  "vermelho",
  };
  return map[status] || "";
}

function statusOSLabel(status) {
  const map = {
    aberta:      "Aberta",
    em_execucao: "Em execução",
    concluida:   "Concluída",
    cancelada:   "Cancelada",
  };
  return map[status] || status;
}

function statusOSClass(status) {
  const map = {
    aberta:      "vermelho",
    em_execucao: "amarelo",
    concluida:   "verde",
    cancelada:   "vermelho",
  };
  return map[status] || "";
}

function fazerLogout(e) {
  e.preventDefault();
  window.location.href = "/pages/login.html";
}
