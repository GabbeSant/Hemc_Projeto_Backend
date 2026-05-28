document.addEventListener("DOMContentLoaded", function () {
    // Se já está logado, redireciona direto para o dashboard
    if (localStorage.getItem("hemc_token")) {
        window.location.href = "/pages/dashboard.html";
        return;
    }

    const form = document.getElementById("form-login");
    const inputNome = document.getElementById("input-nome");
    const inputSenha = document.getElementById("input-senha");
    const msgErro = document.getElementById("msg-erro");
    const btnSubmit = form.querySelector(".btn-submit");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const nome = inputNome.value.trim();
        const senha = inputSenha.value;

        if (!nome || !senha) {
            mostrarErro("Preencha o nome e a senha.");
            return;
        }

        btnSubmit.disabled = true;
        btnSubmit.textContent = "Entrando...";
        msgErro.style.display = "none";

        try {
            const res = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nome, senha }),
            });

            const data = await res.json();

            if (!res.ok) {
                mostrarErro(data.detail || "Credenciais inválidas.");
                return;
            }

            localStorage.setItem("hemc_token", data.token);
            localStorage.setItem("hemc_usuario", JSON.stringify(data.usuario));
            window.location.href = "/pages/dashboard.html";

        } catch (err) {
            mostrarErro("Erro ao conectar com o servidor.");
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.textContent = "Entrar no sistema";
        }
    });

    function mostrarErro(msg) {
        msgErro.textContent = msg;
        msgErro.style.display = "block";
    }
});
