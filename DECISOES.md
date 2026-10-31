# Decisões de arquitetura — caixa clara

**Data:** 30/10/2026 · **Autor:** engenharia + gestão de decisão
**Status:** protótipo aprovado para validação visual

---

## 1. Contexto

Loja de caixas e kits personalizados. Produção sob demanda, sem estoque de produto final.
Venda para pessoa física, regime MEI. Objetivo declarado do site: **gerar tráfego orgânico**
e converter em pedidos aprovados manualmente pela dona.

## 2. Restrições que governam tudo

| Restrição | Consequência técnica |
|---|---|
| MEI (teto R$ 81.000/ano) | Painel precisa medir faturamento e avisar em 80% do limite |
| Venda só para CPF | Sem emissão obrigatória de NF-e; módulo fiscal = controle + exportação, não integração |
| Produção sob demanda | Sem tabela de estoque de produto; prazo de produção entra no cálculo de entrega |
| Sem CNPJ de gateway ainda | Mercado Pago com CNPJ é bloqueante para produção, não para protótipo |
| SEO orgânico é o canal | **HTML estático** obrigatório. SPA é a escolha errada aqui |
| Mobile + desktop | Layout mobile-first; grade de produto quebra em 2 colunas a partir de 760px |
| Assets (logo, foto) ainda não existem | Nada pode depender de imagem. Identidade toda em CSS |

## 3. Decisões

### D1 · Renderização estática (não SPA)
**Escolha:** HTML gerado, zero JavaScript de framework.
**Por quê:** tráfego orgânico vive de HTML indexável e rápido no celular. React em SPA
custa ~100kb de JS para renderizar uma lista de seis caixas.
**Custo:** menos interatividade instantânea — aceitável neste catálogo.
**Revisar quando:** houver filtros dinâmicos, conta de cliente, ou mais de 30 produtos.

### D2 · Catálogo em arquivo, não em banco (por enquanto)
**Escolha:** `src/data/catalogo.js` é a fonte única; Python lê e gera HTML.
**Por quê:** você define os produtos hoje. Editar um arquivo e rodar um comando é mais
rápido que abrir painel — e não há risco de corromper dados em produção.
**Revisar quando:** o painel precisar editar produto (fase 2, com Supabase).

### D3 · Motor de variações relacional, não matriz de SKUs
**Escolha:** Produto → Grupos → Valores, com preço = base + adicionais.
**Por quê:** 6 produtos × 4 tamanhos × 4 acabamentos × 4 fitas já são 384 combinações.
Cadastrar SKU a SKU é inviável e vira fonte de erro de preço. A soma de adicionais
é auditável e o cliente entende o que pagou.
**Custo:** não permite preço "exceção" por combinação específica. Se isso for
necessário depois, adiciona-se uma tabela de override — sem migrar o modelo.
**Chave de SKU** é determinística e ordenada, o que impede duplicação na sacola
e serve de chave primária no pedido.

### D4 · Mercado Pago Checkout Pro, não transparente
**Escolha:** redirect para o Mercado Pago.
**Por quê:** checkout transparente exige tokenização de cartão e escopo PCI, e o
webhook é o ponto onde iniciantes furam (pedido pago sem pagamento ou vice-versa).
Checkout Pro entrega a mesma conversão com uma fração do risco.
**Revisar quando:** houver volume que justifique pagar a taxa extra e a equipe para
sustentar o fluxo.

### D5 · Frete atrás de uma função só
**Escolha:** `cotarFrete(cep, itens)` é a única porta de entrada do frete.
**Por quê:** hoje simula; amanhã chama o Worker que fala com o Melhor Envio.
A assinatura não muda, então nenhuma tela precisa ser tocada.

### D6 · Módulo fiscal = controle, não declaração
**Escolha:** painel mede faturamento, alerta o teto MEI, exporta CSV para o contador.
**Por quê:** não existe API pública da Receita para "declarar IR automaticamente".
O que existe (eSocial, DCTFWeb, PGDAS-D, NF-e estadual) é integração contábil que
exige contador responsável. Escrever software que declara imposto sem responsável
técnico cria responsabilidade solidária sobre multas.
**Revisar quando:** você virar ME. Aí entra emissão de NF-e via provedor
(Focus NFe, eNotas), nunca integração direta com o governo.

### D7 · Cloudflare Workers + Supabase
**Escolha:** site estático e API no Worker; Postgres e Auth no Supabase.
**Por quê:** Workers não rodam processo Node tradicional nem banco local — por isso
o banco fica fora. Supabase dá Postgres real, o que o motor de variações precisa,
e Auth com Google sem escrever senha.

## 4. Riscos abertos

| Risco | Impacto | Mitigação |
|---|---|---|
| Teto do MEI estourar sem perceber | Desenquadramento retroativo, multa | Alerta em 80% no painel; exportação mensal |
| Webhook do MP falhar em silêncio | Pedido pago marcado como pendente | Reconsulta periódica de pagamentos pendentes |
| Sem contrato de frete | Não cota no checkout | Começar com tabela própria por CEP, migrar para Melhor Envio |
| Estética pastel virar genérica | Perde diferenciação | Serifada expressiva + cacau como "preto" + aba da caixa como assinatura |
| Sem foto de produto | Site parece incompleto | Mini-caixa em CSS até a produção das fotos |

## 5. O que foi construído agora

- Home com catálogo, "como funciona", ocasiões e bloco corporativo
- Página de produto com motor de variações funcional (preço ao vivo, validação)
- Sacola lateral com chave de SKU, frete simulado por CEP, total
- Checkout em protótipo com aviso LGPD
- Painel com pedidos, fila de produção, medidor de teto MEI e bloco fiscal
- Design system em tokens, mobile-first, sem dependência de imagem

## 6. Próxima decisão pendente

**Modelo de preço do kit corporativo.** Hoje é "base + adicionais" igual aos outros,
mas pedido de 24 unidades costuma ter desconto por volume. Isso é uma regra de
negócio que precisa de definição sua antes de virar código.
