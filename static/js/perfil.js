const USUARIO_FIXO = 1; // mesmo ID usado no resto do sistema

const PERFIL_LABEL = {
  admin:      "Administrador",
  enfermeira: "Enfermeira",
  tecnico:    "Técnico",
};

function iniciais(nome) {
  return nome
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map(p => p[0].toUpperCase())
    .join("");
}

async function carregarPerfil() {
  try {
    const [usuario, setores] = await Promise.all([
      API.get(`/usuarios/${USUARIO_FIXO}`),
      API.get("/setores"),
    ]);

    const mapSetores = Object.fromEntries(setores.map(s => [s.id_setor, s.nome_setor]));
    const nomeSetor = mapSetores[usuario.id_setor] || "–";
    const perfilLabel = PERFIL_LABEL[usuario.perfil] || usuario.perfil;

    // Sidebar
    const sidebarNome = document.getElementById("sidebar-nome");
    if (sidebarNome) sidebarNome.textContent = usuario.nome;

    // Avatar com iniciais
    document.getElementById("perfil-iniciais").textContent = iniciais(usuario.nome);

    // Card principal
    document.getElementById("perfil-nome").textContent = usuario.nome;
    document.getElementById("perfil-badge").textContent = perfilLabel;

    // Detalhes
    document.getElementById("detalhe-nome").textContent = usuario.nome;
    document.getElementById("detalhe-perfil").textContent = perfilLabel;
    document.getElementById("detalhe-setor").textContent = nomeSetor;
    document.getElementById("detalhe-id").textContent = `#${usuario.id_usuario}`;
  } catch (err) {
    console.error("Erro ao carregar perfil:", err);
  }
}

document.addEventListener("DOMContentLoaded", carregarPerfil);
