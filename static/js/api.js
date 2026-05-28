// ---- Autenticação ----
const Auth = {
    getToken()   { return localStorage.getItem("hemc_token"); },
    getUsuario() {
        const u = localStorage.getItem("hemc_usuario");
        return u ? JSON.parse(u) : null;
    },
    salvar(token, usuario) {
        localStorage.setItem("hemc_token", token);
        localStorage.setItem("hemc_usuario", JSON.stringify(usuario));
    },
    limpar() {
        localStorage.removeItem("hemc_token");
        localStorage.removeItem("hemc_usuario");
    },
    isLogado() { return !!this.getToken(); },
    async logout() {
        const token = this.getToken();
        if (token) {
            try {
                await fetch("/api/logout", {
                    method: "POST",
                    headers: { "Authorization": "Bearer " + token },
                });
            } catch (_) { /* ignora erros de rede no logout */ }
        }
        this.limpar();
        window.location.href = "/pages/login.html";
    },
};

// ---- Cliente HTTP ----
const API = {
    base: "/api",

    _headers() {
        const h = { "Content-Type": "application/json" };
        const token = Auth.getToken();
        if (token) h["Authorization"] = "Bearer " + token;
        return h;
    },

    _tratar401(res) {
        if (res.status === 401) {
            Auth.limpar();
            window.location.href = "/pages/login.html";
            throw new Error("Não autorizado");
        }
    },

    async get(path) {
        const res = await fetch(this.base + path, { headers: this._headers() });
        this._tratar401(res);
        if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
        return res.json();
    },

    async post(path, body) {
        const res = await fetch(this.base + path, {
            method: "POST",
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        this._tratar401(res);
        if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
        return res.json();
    },

    async patch(path, body) {
        const res = await fetch(this.base + path, {
            method: "PATCH",
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        this._tratar401(res);
        if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
        return res.json();
    },

    async put(path, body) {
        const res = await fetch(this.base + path, {
            method: "PUT",
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        this._tratar401(res);
        if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
        return res.json();
    },

    async delete(path) {
        const res = await fetch(this.base + path, {
            method: "DELETE",
            headers: this._headers(),
        });
        this._tratar401(res);
        if (!res.ok) throw new Error(`Erro ${res.status}: ${await res.text()}`);
        return res.status === 204 ? null : res.json();
    },
};

// ---- Utilitários de formatação ----
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

async function fazerLogout(e) {
    e.preventDefault();
    await Auth.logout();
}

function carregarNomeUsuario() {
    const usuario = Auth.getUsuario();
    if (usuario) {
        const el = document.querySelector(".nome-paciente");
        if (el) el.textContent = usuario.nome;
    }
}

document.addEventListener("DOMContentLoaded", carregarNomeUsuario);
