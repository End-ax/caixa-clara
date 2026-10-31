// ============================================================
// MOTOR DE VARIAÇÕES — fonte de verdade do protótipo
// Modelo: Produto -> Grupos de opção -> Valores
// Preço = preço base + soma dos adicionais dos valores escolhidos
// Estoque: produção sob demanda (sem controle de estoque de insumos)
// ============================================================

export const GRUPOS = {
  tamanho: {
    id: 'tamanho',
    nome: 'Tamanho da caixa',
    tipo: 'unico',
    obrigatorio: true,
    valores: [
      { id: 'p', nome: 'Pequena', dim: '15 × 15 × 8 cm', adicional: 0 },
      { id: 'm', nome: 'Média', dim: '22 × 22 × 10 cm', adicional: 18 },
      { id: 'g', nome: 'Grande', dim: '30 × 30 × 12 cm', adicional: 42 },
      { id: 'gg', nome: 'Extra grande', dim: '40 × 30 × 15 cm', adicional: 78 },
    ],
  },
  acabamento: {
    id: 'acabamento',
    nome: 'Acabamento externo',
    tipo: 'unico',
    obrigatorio: true,
    valores: [
      { id: 'kraft', nome: 'Kraft natural', nota: 'Papelão cru, rústico', adicional: 0 },
      { id: 'mate', nome: 'Papel matte colorido', nota: 'Fosco, toque suave', adicional: 12 },
      { id: 'perolado', nome: 'Papel perolado', nota: 'Brilho discreto', adicional: 26 },
      { id: 'textura', nome: 'Textura linho', nota: 'Relevo tipo tecido', adicional: 34 },
    ],
  },
  fita: {
    id: 'fita',
    nome: 'Fita e laço',
    tipo: 'unico',
    obrigatorio: true,
    valores: [
      { id: 'nenhuma', nome: 'Sem fita', adicional: 0 },
      { id: 'cetim', nome: 'Cetim', adicional: 8 },
      { id: 'linho', nome: 'Linho natural', adicional: 14 },
      { id: 'veludo', nome: 'Veludo', adicional: 22 },
    ],
  },
  interno: {
    id: 'interno',
    nome: 'Recheio interno',
    tipo: 'multiplo',
    obrigatorio: false,
    valores: [
      { id: 'seda', nome: 'Papel de seda', adicional: 6 },
      { id: 'palha', nome: 'Palha natural', adicional: 12 },
      { id: 'miolo', nome: 'Miolo de papel picado', adicional: 10 },
      { id: 'bolha', nome: 'Proteção bolha', nota: 'Itens frágeis', adicional: 9 },
    ],
  },
  cartao: {
    id: 'cartao',
    nome: 'Cartão impresso',
    tipo: 'unico',
    obrigatorio: false,
    valores: [
      { id: 'sem', nome: 'Sem cartão', adicional: 0 },
      { id: 'simples', nome: 'Cartão simples', adicional: 5 },
      { id: 'caligrafado', nome: 'Cartão com caligrafia', adicional: 16 },
    ],
  },
};

export const PRODUTOS = [
  {
    slug: 'caixa-presente',
    nome: 'Caixa Presente',
    linha: 'Clássica',
    resumo: 'A caixa vazia que faz o presente começar antes de abrir.',
    descricao:
      'Estrutura rígida em papelão cinza com forro, montada à mão. Tamanho, papel externo e fita escolhidos por você. É a base de todo presente que vale a pena dar.',
    grupos: ['tamanho', 'acabamento', 'fita', 'interno', 'cartao'],
    base: 68,
    prazoProducao: 5,
    tags: ['afetivo', 'corporativo'],
    destaque: true,
    tom: 'terracota',
  },
  {
    slug: 'caixa-envelope',
    nome: 'Caixa Envelope',
    linha: 'Envelope',
    resumo: 'Abaixa, chata, feita para joia, perfume ou convite.',
    descricao:
      'Fecho magnético escondido e abertura por aba. Feita para presentes que precisam deslizar para fora com elegância. Ideal para peças pequenas de alto valor.',
    grupos: ['tamanho', 'acabamento', 'fita', 'interno', 'cartao'],
    base: 82,
    prazoProducao: 6,
    tags: ['afetivo', 'joia'],
    destaque: true,
    tom: 'rose',
  },
  {
    slug: 'caixa-gaveta',
    nome: 'Caixa Gaveta',
    linha: 'Gaveta',
    resumo: 'Abre puxando. O presente aparece como cena.',
    descricao:
      'Duas peças que deslizam uma na outra, com fita de puxar. O momento de abertura dura mais, e é disso que a pessoa vai lembrar.',
    grupos: ['tamanho', 'acabamento', 'fita', 'interno', 'cartao'],
    base: 96,
    prazoProducao: 7,
    tags: ['afetivo'],
    destaque: true,
    tom: 'cacau',
  },
  {
    slug: 'kit-corporativo',
    nome: 'Kit Corporativo',
    linha: 'Corporativo',
    resumo: 'Onboarding, brinde de fim de ano, agradecimento a cliente.',
    descricao:
      'Caixa com berço interno cortado sob medida para o seu produto. Aceita de 1 a 6 itens, com etiqueta e cartão com a identidade da sua marca. Pedido mínimo de 10 unidades.',
    grupos: ['tamanho', 'acabamento', 'interno', 'cartao'],
    base: 124,
    prazoProducao: 10,
    tags: ['corporativo'],
    destaque: false,
    minimo: 10,
    tom: 'mostarda',
  },
  {
    slug: 'caixa-livro',
    nome: 'Caixa Livro',
    linha: 'Livro',
    resumo: 'Parece um livro na estante. Abre como presente.',
    descricao:
      'Capa dura forrada com papel texturizado e lombada aparente. Feita para guardar algo que a pessoa vai querer manter guardado depois.',
    grupos: ['tamanho', 'acabamento', 'fita', 'interno', 'cartao'],
    base: 118,
    prazoProducao: 8,
    tags: ['afetivo', 'premium'],
    destaque: false,
    tom: 'cacau',
  },
  {
    slug: 'caixa-kit-cha',
    nome: 'Kit Chá e Bem-estar',
    linha: 'Kit pronto',
    resumo: 'Caixa com produtos curados por nós, já montada.',
    descricao:
      'Seleção fixa de 4 itens: infusão, vela, sabonete e biscoito. Você escolhe só a caixa e o cartão. É a opção mais rápida para quem quer presentear sem pensar muito.',
    grupos: ['tamanho', 'acabamento', 'cartao'],
    base: 186,
    prazoProducao: 4,
    tags: ['afetivo', 'pronto'],
    destaque: false,
    tom: 'rose',
  },
];

export const OCASIOES = [
  { id: 'aniversario', nome: 'Aniversário' },
  { id: 'casamento', nome: 'Casamento e noivado' },
  { id: 'nascimento', nome: 'Nascimento e chá de bebê' },
  { id: 'corporativo', nome: 'Corporativo' },
  { id: 'autocuidado', nome: 'Autocuidado' },
  { id: 'outro', nome: 'Outra ocasião' },
];

// ---------- funções do motor ----------

export function getProduto(slug) {
  return PRODUTOS.find((p) => p.slug === slug);
}

export function gruposDoProduto(produto) {
  return produto.grupos.map((g) => GRUPOS[g]).filter(Boolean);
}

/** Soma dos adicionais de uma seleção { grupoId: valorId | [valorId] } */
export function calcularAdicionais(produto, selecao = {}) {
  let total = 0;
  const detalhe = [];
  for (const grupo of gruposDoProduto(produto)) {
    const escolha = selecao[grupo.id];
    const ids = Array.isArray(escolha) ? escolha : escolha ? [escolha] : [];
    for (const id of ids) {
      const valor = grupo.valores.find((v) => v.id === id);
      if (valor && valor.adicional) {
        total += valor.adicional;
        detalhe.push({ grupo: grupo.nome, valor: valor.nome, adicional: valor.adicional });
      }
    }
  }
  return { total, detalhe };
}

/** Preço unitário = base + adicionais. Quantidade não entra aqui. */
export function precoUnitario(produto, selecao) {
  return produto.base + calcularAdicionais(produto, selecao).total;
}

/** Validação: obrigatórios preenchidos, múltiplos dentro do permitido */
export function validarSelecao(produto, selecao) {
  const erros = [];
  for (const grupo of gruposDoProduto(produto)) {
    const escolha = selecao[grupo.id];
    const vazio = Array.isArray(escolha) ? escolha.length === 0 : !escolha;
    if (grupo.obrigatorio && vazio) {
      erros.push(`${grupo.nome} é obrigatório.`);
      continue;
    }
    const ids = Array.isArray(escolha) ? escolha : escolha ? [escolha] : [];
    if (grupo.tipo === 'unico' && ids.length > 1) {
      erros.push(`${grupo.nome} aceita apenas uma opção.`);
    }
    for (const id of ids) {
      if (!grupo.valores.some((v) => v.id === id)) {
        erros.push(`Opção inválida em ${grupo.nome}.`);
      }
    }
  }
  return erros;
}

/**
 * Chave do SKU — determinística e ordenada, para que a mesma
 * combinação gere sempre a mesma chave no carrinho e no pedido.
 */
export function chaveSku(produto, selecao) {
  const partes = gruposDoProduto(produto).map((grupo) => {
    const escolha = selecao[grupo.id];
    const ids = (Array.isArray(escolha) ? [...escolha] : escolha ? [escolha] : []).sort();
    return `${grupo.id}:${ids.join('+') || '-'}`;
  });
  return `${produto.slug}|${partes.join('|')}`;
}

export function formatarBRL(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
