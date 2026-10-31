/* ============================================================
   LOJA — carrinho em localStorage + gaveta + cotação de frete
   Protótipo: frete SIMULADO (troque por Melhor Envio depois)
   ============================================================ */

const CHAVE = 'caixas:carrinho:v1';
const CHAVE_FRETE = 'caixas:frete:v1';

/* ---------- carrinho ---------- */

export function lerCarrinho() {
  try {
    const cru = localStorage.getItem(CHAVE);
    const dados = cru ? JSON.parse(cru) : [];
    return Array.isArray(dados) ? dados : [];
  } catch {
    return [];
  }
}

function gravar(itens) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(itens));
  } catch {
    /* modo privado: segue sem persistir */
  }
  atualizarContadores();
  document.dispatchEvent(new CustomEvent('carrinho:mudou', { detail: itens }));
}

/**
 * Item do carrinho. A chave do SKU garante que a mesma
 * combinação de opções some na mesma linha, e não duplique.
 */
export function adicionar(item) {
  const itens = lerCarrinho();
  const existente = itens.find((i) => i.sku === item.sku);
  if (existente) {
    existente.qtd += item.qtd;
  } else {
    itens.push(item);
  }
  gravar(itens);
}

export function remover(sku) {
  gravar(lerCarrinho().filter((i) => i.sku !== sku));
}

export function alterarQtd(sku, qtd) {
  const itens = lerCarrinho();
  const alvo = itens.find((i) => i.sku === sku);
  if (!alvo) return;
  alvo.qtd = Math.max(1, Math.min(999, qtd));
  gravar(itens);
}

export function limpar() {
  gravar([]);
  sessionStorage.removeItem(CHAVE_FRETE);
}

export function contarItens() {
  return lerCarrinho().reduce((s, i) => s + i.qtd, 0);
}

export function totalItens() {
  return lerCarrinho().reduce((s, i) => s + i.preco * i.qtd, 0);
}

export function qtdTotal(itens = lerCarrinho()) {
  return itens.reduce((s, i) => s + i.qtd, 0);
}

/* ---------- frete (SIMULADO) ---------- */

/**
 * PONTO DE INTEGRAÇÃO REAL
 * Trocar esta função pela chamada ao Worker /api/frete, que por sua vez
 * chama o Melhor Envio. A assinatura não muda: entra CEP + itens,
 * sai lista de opções. Assim o resto da loja não precisa ser tocado.
 */
export function cotarFrete(cep, itens) {
  const limpo = String(cep).replace(/\D/g, '');
  if (limpo.length !== 8) {
    return { erro: 'Digite um CEP com 8 dígitos.' };
  }

  // faixas regionais por 1º dígito do CEP — apenas para o protótipo
  const regiao = Number(limpo[0]);
  const base = [0, 18.9, 21.9, 24.9, 27.9, 31.9, 34.9, 38.9, 42.9, 46.9][regiao] ?? 27.9;

  const unidades = itens.reduce((s, i) => s + i.qtd, 0);
  const pesoExtra = Math.max(0, unidades - 1) * 6.5;
  const prazoExtra = Math.max(0, unidades - 1) * 1;

  return {
    cep: limpo,
    opcoes: [
      {
        id: 'pac',
        nome: 'PAC',
        transportadora: 'Correios',
        preco: Math.round((base + pesoExtra) * 100) / 100,
        prazo: 8 + prazoExtra,
      },
      {
        id: 'sedex',
        nome: 'SEDEX',
        transportadora: 'Correios',
        preco: Math.round((base * 1.72 + pesoExtra * 1.4) * 100) / 100,
        prazo: 3 + prazoExtra,
      },
      {
        id: 'melhor-envio',
        nome: 'Melhor Envio · Jadlog',
        transportadora: 'Jadlog .Package',
        preco: Math.round((base * 1.28 + pesoExtra * 1.1) * 100) / 100,
        prazo: 5 + prazoExtra,
      },
    ],
  };
}

export function salvarFrete(escolha) {
  try {
    sessionStorage.setItem(CHAVE_FRETE, JSON.stringify(escolha));
  } catch {
    /* ignora */
  }
}

export function lerFrete() {
  try {
    const cru = sessionStorage.getItem(CHAVE_FRETE);
    return cru ? JSON.parse(cru) : null;
  } catch {
    return null;
  }
}

/* ---------- formatação ---------- */

export function brl(v) {
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

export function prazoTexto(dias) {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  return `chega até ${d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })}`;
}

export function dataProducao(diasUteis) {
  const d = new Date();
  let add = 0;
  while (add < diasUteis) {
    d.setDate(d.getDate() + 1);
    if (d.getDay() !== 0 && d.getDay() !== 6) add++;
  }
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long' });
}

/* ---------- contador do topo ---------- */

export function atualizarContadores() {
  const n = contarItens();
  document.querySelectorAll('[data-contador-carrinho]').forEach((el) => {
    el.textContent = n;
    el.style.display = n > 0 ? '' : 'none';
  });
}

/* ---------- gaveta ---------- */

let gavetaPronta = false;

export function montarGaveta() {
  if (gavetaPronta) return;
  gavetaPronta = true;

  const veu = document.createElement('div');
  veu.className = 'veu';
  veu.setAttribute('data-veu', '');

  const gaveta = document.createElement('aside');
  gaveta.className = 'gaveta';
  gaveta.setAttribute('role', 'dialog');
  gaveta.setAttribute('aria-modal', 'true');
  gaveta.setAttribute('aria-label', 'Sacola de compras');
  gaveta.setAttribute('data-gaveta', '');
  gaveta.innerHTML = `
    <div class="gaveta__topo">
      <h3>Sua sacola</h3>
      <button class="gaveta__fechar" data-fechar-gaveta aria-label="Fechar sacola">×</button>
    </div>
    <div class="gaveta__corpo" data-gaveta-corpo></div>
    <div class="gaveta__pe" data-gaveta-pe></div>
  `;

  document.body.append(veu, gaveta);

  veu.addEventListener('click', fecharGaveta);
  gaveta.querySelector('[data-fechar-gaveta]').addEventListener('click', fecharGaveta);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') fecharGaveta();
  });
  document.addEventListener('carrinho:mudou', renderizarGaveta);
  document.addEventListener('frete:escolhido', renderizarGaveta);

  renderizarGaveta();
}

export function abrirGaveta() {
  montarGaveta();
  document.querySelector('[data-veu]')?.classList.add('veu--on');
  document.querySelector('[data-gaveta]')?.classList.add('gaveta--on');
  document.body.style.overflow = 'hidden';
  renderizarGaveta();
}

export function fecharGaveta() {
  document.querySelector('[data-veu]')?.classList.remove('veu--on');
  document.querySelector('[data-gaveta]')?.classList.remove('gaveta--on');
  document.body.style.overflow = '';
}

function renderizarGaveta() {
  const corpo = document.querySelector('[data-gaveta-corpo]');
  const pe = document.querySelector('[data-gaveta-pe]');
  if (!corpo || !pe) return;

  const itens = lerCarrinho();

  if (itens.length === 0) {
    corpo.innerHTML = `
      <div class="vazio">
        <div class="vazio__icone"></div>
        <p style="margin:0 0 4px"><strong>Sua sacola está vazia.</strong></p>
        <p class="sutil" style="margin:0">Escolha uma caixa e monte do seu jeito.</p>
      </div>`;
    pe.innerHTML = `<a href="/" class="btn btn--fantasma btn--bloco">Ver caixas</a>`;
    return;
  }

  corpo.innerHTML = itens
    .map(
      (i) => `
    <div class="item-carrinho">
      <div class="item-carrinho__vis tom-${i.tom || 'rose'}"><div class="mini-caixa"></div></div>
      <div>
        <div class="item-carrinho__nome">${i.nome} <span class="sutil">× ${i.qtd}</span></div>
        <div class="item-carrinho__opts">${i.opcoesResumo}</div>
        <button class="item-carrinho__remover" data-remover="${i.sku}">remover</button>
      </div>
      <div class="item-carrinho__preco">${brl(i.preco * i.qtd)}</div>
    </div>`
    )
    .join('');

  corpo.querySelectorAll('[data-remover]').forEach((b) => {
    b.addEventListener('click', () => remover(b.dataset.remover));
  });

  const sub = totalItens();
  const frete = lerFrete();
  const freteValor = frete ? frete.preco : null;

  pe.innerHTML = `
    <div class="linha-total"><span>Subtotal</span><span>${brl(sub)}</span></div>
    <div class="linha-total">
      <span>Frete</span>
      <span>${freteValor !== null ? brl(freteValor) : '<span class="sutil">calculado no pedido</span>'}</span>
    </div>
    <div class="linha-total linha-total--forte"><span>Total</span><strong>${brl(sub + (freteValor || 0))}</strong></div>
    <a href="/pedido" class="btn btn--primario btn--bloco">Finalizar pedido</a>
    <p class="sutil" style="text-align:center;margin:0;font-size:0.78rem">
      Produção sob demanda · pagamento via Mercado Pago
    </p>
  `;
}

/* ---------- ligação automática ---------- */

export function iniciarLoja() {
  montarGaveta();
  atualizarContadores();
  document.querySelectorAll('[data-abrir-gaveta]').forEach((b) => {
    b.addEventListener('click', abrirGaveta);
  });
  // adicionar direto da vitrine
  document.querySelectorAll('[data-add-rapido]').forEach((b) => {
    b.addEventListener('click', () => {
      const item = JSON.parse(b.dataset.addRapido);
      adicionar(item);
      abrirGaveta();
    });
  });
}
