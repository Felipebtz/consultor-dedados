# ⚡ Início Rápido - 5 Minutos

## 🚀 Execução Rápida

### 1️⃣ Instalar Dependências (Primeira vez)

```bash
install_venv.bat
```

### 2️⃣ Configurar Credenciais

Edite o arquivo `.env` com suas credenciais da API Omie.

### 3️⃣ Executar Coleta de Dados

```bash
executar.bat
```

OU manualmente:
```bash
venv\Scripts\activate.bat
python -m src.main
```

### 4️⃣ Iniciar Dashboard Web

```bash
iniciar_dashboard.bat
```

OU manualmente:
```bash
venv\Scripts\activate.bat
python -m src.web.app
```

### 5️⃣ Acessar Dashboard

Abra seu navegador em:
```
http://localhost:5000
```

---

## 📋 Checklist Rápido

- [ ] Python instalado
- [ ] MySQL rodando
- [ ] Dependências instaladas (`install_venv.bat`)
- [ ] Arquivo `.env` configurado
- [ ] Coleta executada (`executar.bat`)
- [ ] Dashboard iniciado (`iniciar_dashboard.bat`)
- [ ] Acessar `http://localhost:5000`

---

## 🎯 Próximos Passos

1. Veja `GUIA_EXECUCAO.md` para instruções detalhadas
2. Veja `VISAO_GERAL_PROJETO.md` para entender a arquitetura
3. Veja `GUIA_APIS.md` para adicionar novas APIs

---

## ❓ Problemas?

- **Erro de encoding**: Use ambiente virtual (`install_venv.bat`)
- **MySQL não conecta**: Verifique credenciais no `.env`
- **API retorna erro**: Verifique APP_KEY e APP_SECRET
- **Dashboard não abre**: Verifique se Flask está instalado

Veja `SOLUCAO_PIP.md` para mais soluções.
