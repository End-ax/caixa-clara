# caixa clara — protótipo

Site de caixas e kits personalizados. Produção sob demanda, venda para pessoa física,
MEI, pagamento via Mercado Pago, frete via Melhor Envio, painel em subdomínio.

> **Isto é um protótipo navegável.** Nada está conectado a serviço real ainda:
> frete é simulado, pagamento é um alerta, painel usa dados fictícios.
> A estrutura foi desenhada para que cada peça vire produção trocando **um** arquivo.

---

## Rodar

```bash
python construir.py      # gera ./site (HTML estático)
```

O resultado em `./site` é o que o Cloudflare Worker serve. Não há dependências
para instalar — o gerador usa só a biblioteca padrão do Python e o Node que já existe
na máquina para ler o catálogo.

Para ver no navegador, sirva a pasta `site` por qualquer servidor estático.

---

## Estrutura

```
caixas/
├── construir.py           gerador do HTML (Python, sem deps)
├── src/data/catalogo.js   ★ fonte única: produtos, grupos de opção, preços
├── public/
│   ├── estilo.css         design system (cores, tipografia, componentes)
│   ├── paginas.css        estilos por página
│   └── loja.js            carrinho, sacola lateral, frete, formatação
└── site/                  saída gerada (não editar)
```

### Por que gerador e não Astro ainda

Zero instalação, resultado imediato. A migração para Astro é mecânica:
cada função de página vira um `.astro`, e `catalogo.js` continua igual.
Faça isso quando for adicionar autenticação e rotas dinâmicas.

---

## Motor de variações

Modelo: **Produto → Grupos de opção → Valores**.

- `tipo: 'unico'` → o cliente escolhe uma opção (tamanho, acabamento, fita)
- `tipo: 'multiplo'` → pode marcar várias (recheio interno)
- `obrigatorio: true` → bloqueia a compra até preencher
- `adicional` → soma no preço unitário

Preço unitário = `base + soma dos adicionais`. Quantidade multiplica no total.

**Chave de SKU** (`chaveSku`) é determinística e ordenada:
`caixa-presente|tamanho:m|acabamento:mate|fita:cetim|interno:palha+seda|cartao:-`

Isso garante que a mesma combinação nunca apareça duas vezes na sacola —
e é a chave primária que o pedido vai usar no banco.

Funções puras em `src/data/catalogo.js`: `calcularAdicionais`, `precoUnitario`,
`validarSelecao`, `chaveSku`. Todas testáveis sem navegador.

---

## Design system

| Token | Valor | Uso |
|---|---|---|
| `--manteiga` | `#FAF6F0` | fundo (nunca branco puro) |
| `--creme` | `#FFFDFA` | cartões |
| `--rose` | `#E8C4B8` | superfícies de destaque |
| `--terracota` | `#B76E5E` | ação primária |
| `--cacau` | `#4A2E28` | **texto e "preto"** |
| `--mostarda` | `#C9A227` | detalhe, fita |

Tipografia: **Fraunces** (títulos, serifada expressiva) + **Inter** (corpo).

**Assinatura gráfica:** a "aba da caixa" — canto dobrado em `.aba::after`,
divisória `.divisor-aba`, e a mini-caixa em CSS (`.mini-caixa`) usada em todos
os cards. Substitui logo e banner por enquanto, e continua funcionando quando
o logo chegar.

---

## O que trocar para ir a produção

| Hoje | Produção | Onde |
|---|---|---|
| `cotarFrete()` simulada | `POST /api/frete` → Melhor Envio | `public/loja.js` |
| botão "Ir para o pagamento" | `POST /api/pagamento` → Mercado Pago Checkout Pro | `construir.py` → `pedido()` |
| `localStorage` | tabela `pedidos` no Supabase | `public/loja.js` |
| dados fictícios | Supabase Auth + RLS | `construir.py` → `painel()` |

**Webhook do Mercado Pago:** o pedido só muda para "pago" quando o webhook
`payment.updated` chega e é validado (assinatura + reconsulta do pagamento na API).
Nunca confie no retorno do navegador.

---

## Próximos passos (ordem de valor)

1. Supabase: schema `produtos`, `variacoes`, `pedidos`, `pedido_itens`
2. Worker com `/api/frete` (Melhor Envio) — o token fica como secret, nunca no front
3. `/api/pagamento` + webhook
4. Cloudflare: worker + domínio + `painel.seudominio.com`
5. Astro, quando as rotas dinâmicas pedirem
