# Lista de APIs Omie Disponíveis

## 📋 APIs que Você Pode Adicionar

Baseado na documentação da Omie (https://developer.omie.com.br/service-list/), aqui estão as APIs mais comuns:

### Cadastros Gerais

| API | Endpoint | Método | Status |
|-----|----------|--------|--------|
| Clientes | `geral/clientes/` | `ListarClientes` | ✅ Implementado |
| Produtos | `geral/produtos/` | `ListarProdutos` | ✅ Implementado |
| Serviços | `servicos/servico/` | `ListarCadastroServico` | ✅ Implementado |
| Categorias | `geral/categorias/` | `ListarCategorias` | ✅ Implementado |
| Fornecedores | `geral/fornecedores/` | `ListarFornecedores` | ❌ Não implementado |
| Vendedores | `geral/vendedores/` | `ListarVendedores` | ❌ Não implementado |
| Transportadoras | `geral/transportadoras/` | `ListarTransportadoras` | ❌ Não implementado |
| Contas DRE | `financas/contadre/` | `ListarCadastroDRE` | ✅ Implementado |

### Financeiro

| API | Endpoint | Método | Status |
|-----|----------|--------|--------|
| Contas a Receber | `financas/contareceber/` | `ListarContasReceber` | ✅ Implementado |
| Contas a Pagar | `financas/contapagar/` | `ListarContasPagar` | ✅ Implementado |
| Extrato | `financas/extrato/` | `ListarExtrato` | ✅ Implementado |
| Extrato Diário | `financas/extrato/` | `ListarExtratoDiario` | ❌ Não implementado |
| Conta Corrente | `financas/conta_corrente/` | `ListarContasCorrentes` | ❌ Não implementado |
| Movimentos CP | `financas/movimentos/` | `ListarMovimentosCP` | ❌ Não implementado |
| Movimentos CR | `financas/movimentos/` | `ListarMovimentosCR` | ❌ Não implementado |
| Movimentos CP/CR | `financas/movimentos/` | `ListarMovimentosCPCR` | ❌ Não implementado |
| Movimentos Baixa | `financas/movimentos/` | `ListarMovimentosBaixa` | ❌ Não implementado |
| Movimentos Conta Corrente | `financas/movimentos/` | `ListarMovimentosCC` | ❌ Não implementado |

### Movimentos e Operações

| API | Endpoint | Método | Status |
|-----|----------|--------|--------|
| Ordens de Serviço | `servicos/os/` | `ListarOS` | ✅ Implementado |
| Pedidos | `produtos/pedido/` | `ListarPedidos` | ❌ Não implementado |
| Contratos | `geral/contratos/` | `ListarContratos` | ❌ Não implementado |
| Projetos | `geral/projetos/` | `ListarProjetos` | ❌ Não implementado |
| Tipo Faturamento | `geral/tipo_faturamento/` | `ListarTipoFatContrato` | ❌ Não implementado |
| Movimentos por Contrato | `financas/movimentos/` | `ListarMovimentosContrato` | ❌ Não implementado |
| Status Movimentos CP/CR | `financas/movimentos/` | `ListarMovimentosCPCRStatus` | ❌ Não implementado |

---

## 🎯 Prioridade de Implementação

### Alta Prioridade (Dados Financeiros Essenciais)
1. ✅ Contas a Receber
2. ✅ Contas a Pagar
3. ✅ Extrato
4. ❌ Conta Corrente
5. ❌ Movimentos CP/CR

### Média Prioridade (Cadastros Importantes)
1. ✅ Clientes
2. ✅ Produtos
3. ✅ Serviços
4. ❌ Fornecedores
5. ❌ Vendedores

### Baixa Prioridade (Complementares)
1. ✅ Categorias
2. ✅ Ordens de Serviço
3. ❌ Pedidos
4. ❌ Contratos
5. ❌ Projetos

---

## 📝 Como Escolher Quais APIs Adicionar

1. **Consulte sua necessidade**: Quais dados você precisa para o dashboard?
2. **Verifique a documentação**: https://developer.omie.com.br/service-list/
3. **Teste o endpoint**: Use Postman ou curl para ver a estrutura dos dados
4. **Siga o template**: Use `TEMPLATE_COLETOR.py` como base
5. **Adicione ao sistema**: Siga o guia em `GUIA_APIS.md`

---

## 🔗 Links Úteis

- **Documentação Omie**: https://developer.omie.com.br/service-list/
- **Portal do Desenvolvedor**: https://developer.omie.com.br/
- **Guia de APIs**: Veja `GUIA_APIS.md` neste projeto
- **Template**: Veja `TEMPLATE_COLETOR.py` neste projeto
