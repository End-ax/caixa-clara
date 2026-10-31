#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gerador do protótipo — HTML estático, sem dependências.
Rode:  python construir.py
Saída: ./site/  (é essa pasta que o Cloudflare Worker serve)

Por que gerador e não Astro ainda: zero instalação, você vê o resultado
agora. A migração para Astro é mecânica e está documentada no README.
"""
import json
import os
import shutil

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "site")
PUBLICO = os.path.join(RAIZ, "public")

# ---------------------------------------------------------------- dados
# Fonte única de verdade: src/data/catalogo.js (o mesmo arquivo que roda
# no navegador). O Node lê o módulo e serializa para JSON; o Python só
# formata HTML. Nenhuma regra de negócio é reimplementada aqui.
import subprocess

RAIZ_JS = os.path.join(RAIZ, "src", "data", "catalogo.js")
_json_tmp = os.path.join(RAIZ, "dados.json")

_node = os.environ.get("ABACUSAI_BOT_NODE", "node")
_cmd = (
    "import('file:///' + process.argv[1].replace(/\\\\/g,'/')).then(m => {"
    " require('fs').writeFileSync(process.argv[2], JSON.stringify("
    "{ PRODUTOS: m.PRODUTOS, GRUPOS: m.GRUPOS, OCASIOES: m.OCASIOES })); });"
)
subprocess.run([_node, "-e", _cmd, RAIZ_JS, _json_tmp], check=True)

with open(_json_tmp, encoding="utf-8") as _f:
    _d = json.load(_f)

PRODUTOS = _d["PRODUTOS"]
GRUPOS = _d["GRUPOS"]
OCASIOES = _d["OCASIOES"]


def brl(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def data_producao(dias_uteis):
    """Mesma regra do loja.js: prazo em dias úteis a partir de hoje."""
    import datetime

    d = datetime.date.today()
    add = 0
    while add < dias_uteis:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            add += 1
    return d.strftime("%d/%m/%Y")

# ---------------------------------------------------------------- html base
def pagina(titulo, descricao, corpo, script="", nav_ativo="", css_extra=""):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descricao}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#faf6f0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/estilo.css">
<link rel="stylesheet" href="/paginas.css">
{css_extra}
</head>
<body>
<a href="#conteudo" class="pular">Pular para o conteúdo</a>
{corpo}
<script type="module">
import {{ iniciarLoja, abrirGaveta, lerCarrinho, adicionar, remover, alterarQtd, totalItens, qtdTotal, brl, cotarFrete, salvarFrete, lerFrete, prazoTexto, dataProducao }} from '/loja.js';
{script}
</script>
</body>
</html>"""


def topo(ativo=""):
    def cls(k):
        return ' aria-current="page"' if ativo == k else ""
    return f"""
<header class="topo" data-topo>
  <div class="wrap topo__in">
    <a href="/" class="marca">
      <span class="marca__aba" aria-hidden="true"></span>
      <span>caixa&nbsp;clara</span>
    </a>
    <nav class="nav" aria-label="Principal">
      <a href="/#caixas"{cls('caixas')}>Caixas</a>
      <a href="/#kits"{cls('kits')}>Kits prontos</a>
      <a href="/#como"{cls('como')}>Como funciona</a>
      <a href="/#corporativo"{cls('corporativo')}>Corporativo</a>
    </nav>
    <div class="topo__acoes">
      <button class="carrinho-btn" data-abrir-gaveta aria-label="Abrir sacola">
        <span class="carrinho-btn__txt">Sacola</span>
        <span class="carrinho-btn__n" data-contador-carrinho style="display:none">0</span>
      </button>
    </div>
  </div>
</header>"""


def rodape():
    return """
<footer class="rodape">
  <div class="wrap">
    <div class="rodape__grade">
      <div>
        <a href="/" class="marca" style="margin-bottom:12px">
          <span class="marca__aba" aria-hidden="true"></span>
          <span>caixa clara</span>
        </a>
        <p class="sutil" style="max-width:34ch">
          Caixas e kits personalizados, montados à mão sob demanda.
          Cada peça é feita para uma pessoa específica — inclusive quando essa pessoa é uma empresa.
        </p>
      </div>
      <div>
        <h4>Comprar</h4>
        <ul>
          <li><a href="/#caixas">Todas as caixas</a></li>
          <li><a href="/#kits">Kits prontos</a></li>
          <li><a href="/#corporativo">Pedidos corporativos</a></li>
        </ul>
      </div>
      <div>
        <h4>Ajuda</h4>
        <ul>
          <li><a href="#">Prazos e produção</a></li>
          <li><a href="#">Frete e entrega</a></li>
          <li><a href="#">Trocas e devolução</a></li>
          <li><a href="/painel">Painel da loja</a></li>
        </ul>
      </div>
    </div>
    <div class="rodape__fim">
      <span>© 2026 caixa clara · CNPJ MEI · São Paulo, SP</span>
      <span>Protótipo · pagamento via Mercado Pago</span>
    </div>
  </div>
</footer>"""


# ---------------------------------------------------------------- home
def card_produto(p):
    tags = {
        "afetivo": "Presente",
        "corporativo": "Corporativo",
        "pronto": "Pronto",
        "premium": "Premium",
        "joia": "Joia",
    }
    etiqueta = tags.get(p["tags"][0], p["linha"])
    minimo = f" · mín. {p['minimo']}un" if p.get("minimo") else ""
    return f"""
    <a class="card-prod aba" href="/produto/{p['slug']}">
      <div class="card-prod__vis tom-{p['tom']}">
        <span class="card-prod__etiqueta">{etiqueta}</span>
        <div class="mini-caixa" aria-hidden="true"></div>
      </div>
      <div class="card-prod__corpo">
        <div class="card-prod__linha">
          <h3>{p['nome']}</h3>
          <span class="card-prod__preco">{brl(p['base'])}<small>a partir{minimo}</small></span>
        </div>
        <p class="card-prod__resumo">{p['resumo']}</p>
        <span class="card-prod__pe">Personalizar</span>
      </div>
    </a>"""


def home():
    cards = "".join(card_produto(p) for p in PRODUTOS)
    ocas = "".join(f'<button class="ocasiao">{o["nome"]}</button>' for o in OCASIOES)

    corpo = topo() + f"""
<main id="conteudo">

  <section class="heroi">
    <div class="wrap heroi__grade">
      <div>
        <span class="heroi__selo surge"><i></i> Produção sob demanda · feito em São Paulo</span>
        <h1 class="surge-2">A caixa é a <em>primeira</em> parte do presente.</h1>
        <p class="lead surge-3" style="margin-top:18px">
          Caixas rígidas em quatro tamanhos, papel, fita e recheio escolhidos por você.
          Montadas uma a uma depois do pedido — nada de estoque parado, nada de presente igual ao do vizinho.
        </p>
        <div class="heroi__acoes surge-3">
          <a href="#caixas" class="btn btn--primario">Ver as caixas</a>
          <a href="#como" class="btn btn--fantasma">Como funciona</a>
        </div>
      </div>
      <div class="cena surge-2" aria-hidden="true">
        <div class="cena__caixa">
          <div class="cena__tampa"></div>
        </div>
        <div class="cena__selo">
          <strong>22 × 22 × 10</strong>
          papel matte<br>fita de cetim
        </div>
        <div class="cena__etiqueta">montada à mão</div>
      </div>
    </div>
  </section>

  <div class="faixa">
    <div class="wrap faixa__in">
      <div class="faixa__item"><strong>4 tamanhos</strong><span>De 15 cm a 40 cm</span></div>
      <div class="faixa__item"><strong>Sem mínimo</strong><span>1 unidade já é pedido</span></div>
      <div class="faixa__item"><strong>5 a 10 dias</strong><span>Produção antes do envio</span></div>
      <div class="faixa__item"><strong>Pix ou cartão</strong><span>Mercado Pago, em até 3×</span></div>
    </div>
  </div>

  <section class="secao" id="caixas">
    <div class="wrap">
      <div class="secao__cabeca">
        <div>
          <p class="olho">Catálogo</p>
          <h2>Escolha a estrutura.<br>O resto você monta.</h2>
        </div>
        <p class="sutil" style="max-width:32ch">
          Todos os modelos aceitam os mesmos tamanhos, papéis e acabamentos.
          O que muda é a forma de abrir.
        </p>
      </div>
      <div class="grade-produtos">{cards}</div>
    </div>
  </section>

  <div class="wrap"><div class="divisor-aba"><span></span></div></div>

  <section class="secao" id="kits" style="padding-top:0">
    <div class="wrap">
      <div class="secao__cabeca">
        <div>
          <p class="olho">Para quem tem pressa</p>
          <h2>Kits prontos, já com produto dentro.</h2>
          <p class="lead" style="margin-top:12px">
            Quando você não quer pensar em recheio: a gente escolhe os itens, você escolhe só a caixa e o cartão.
          </p>
        </div>
        <a href="/produto/caixa-kit-cha" class="btn btn--fantasma">Ver o kit</a>
      </div>
      <div class="grade-produtos">
        {card_produto([p for p in PRODUTOS if p['slug']=='caixa-kit-cha'][0])}
        {card_produto([p for p in PRODUTOS if p['slug']=='kit-corporativo'][0])}
        {card_produto([p for p in PRODUTOS if p['slug']=='caixa-livro'][0])}
      </div>
    </div>
  </section>

  <section class="secao" id="como">
    <div class="wrap">
      <div class="secao__cabeca">
        <div>
          <p class="olho">Como funciona</p>
          <h2>Três passos, nenhuma dúvida.</h2>
        </div>
      </div>
      <div class="passos">
        <div class="passo aba">
          <h3>Você monta</h3>
          <p>Escolhe tamanho, papel, fita e recheio na página do produto. O preço se atualiza na hora, sem surpresa no checkout.</p>
        </div>
        <div class="passo aba">
          <h3>A gente produz</h3>
          <p>O pedido entra na fila no mesmo dia. Entre 5 e 10 dias úteis a caixa está montada, conferida e embalada para viagem.</p>
        </div>
        <div class="passo aba">
          <h3>Chega pronta</h3>
          <p>Vai embalada para chegar inteira. Se for presente direto para outra pessoa, o cartão escrito à mão já vai dentro.</p>
        </div>
      </div>
    </div>
  </section>

  <div class="wrap"><div class="divisor-aba"><span></span></div></div>

  <section class="secao" id="ocasioes" style="padding-top:0">
    <div class="wrap">
      <div class="secao__cabeca">
        <div>
          <p class="olho">Ocasiões</p>
          <h2>Para qual momento é?</h2>
        </div>
      </div>
      <div class="ocasioes">{ocas}</div>
    </div>
  </section>

  <section class="secao" id="corporativo" style="padding-top:0">
    <div class="wrap">
      <div class="cta">
        <div>
          <p class="olho" style="color:var(--rose)">Corporativo</p>
          <h2>Brinde de empresa que ninguém joga fora.</h2>
          <p>
            Onboarding, fim de ano, agradecimento a cliente. Berço interno cortado sob medida
            para o seu produto, etiqueta com a sua marca e cartão impresso. A partir de 10 unidades,
            com prazo combinado antes de fechar.
          </p>
        </div>
        <a href="/produto/kit-corporativo" class="btn">Ver o kit corporativo</a>
      </div>
    </div>
  </section>

</main>
""" + rodape()

    return pagina(
        "caixa clara · caixas e kits personalizados, feitos sob demanda",
        "Caixas rígidas personalizadas em 4 tamanhos, com papel, fita e recheio à escolha. Kits prontos e pedidos corporativos. Produção sob demanda em São Paulo.",
        corpo,
        """
iniciarLoja();
// sombra do topo ao rolar
const topo = document.querySelector('[data-topo]');
addEventListener('scroll', () => topo.classList.toggle('topo--rolado', scrollY > 8), { passive: true });
""",
    )


# ---------------------------------------------------------------- produto
def grupo_html(g):
    req = '<span class="req" aria-hidden="true">*</span>' if g["obrigatorio"] else ""
    tipo = "multiplo" if g["tipo"] == "multiplo" else "unico"
    chips = []
    for v in g["valores"]:
        mais = f'<span class="chip__mais">+{brl(v["adicional"])[3:]}</span>' if v["adicional"] else ""
        dim = f'<span class="chip__dim">{v["dim"]}</span>' if v.get("dim") else ""
        nota = f'<span class="chip__dim">{v["nota"]}</span>' if v.get("nota") else ""
        chips.append(
            f'<button type="button" class="chip" data-grupo="{g["id"]}" data-valor="{v["id"]}" '
            f'data-extra="{v["adicional"]}" data-tipo="{tipo}" aria-pressed="false">{v["nome"]}{dim}{nota}{mais}</button>'
        )
    return f"""
    <div class="grupo-opcao" data-grupo-bloco="{g['id']}">
      <div class="grupo-opcao__cabeca">
        <span class="grupo-opcao__nome">{g['nome']}{req}</span>
        <span class="grupo-opcao__atual" data-atual="{g['id']}"></span>
      </div>
      <div class="grupo-opcao__valores">{''.join(chips)}</div>
    </div>"""


def produto(p):
    grupos = "".join(grupo_html(GRUPOS[g]) for g in p["grupos"])
    minimo = p.get("minimo")
    aviso_min = (
        f'<p class="aviso"><svg width="15" height="15" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.4"/><path d="M8 4.5v4M8 11h.01" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
        f'Pedido mínimo de {minimo} unidades para este modelo.</p>'
        if minimo
        else ""
    )

    dados_js = json.dumps(
        {
            "slug": p["slug"],
            "nome": p["nome"],
            "base": p["base"],
            "tom": p["tom"],
            "prazo": p["prazoProducao"],
            "grupos": {
                g: {
                    "nome": GRUPOS[g]["nome"],
                    "tipo": GRUPOS[g]["tipo"],
                    "obrigatorio": GRUPOS[g]["obrigatorio"],
                    "valores": {v["id"]: v["nome"] for v in GRUPOS[g]["valores"]},
                }
                for g in p["grupos"]
            },
        },
        ensure_ascii=False,
    )

    corpo = topo() + f"""
<main id="conteudo">
  <div class="wrap migalha">
    <a href="/">Início</a> <span aria-hidden="true">/</span>
    <a href="/#caixas">Caixas</a> <span aria-hidden="true">/</span>
    <span>{p['nome']}</span>
  </div>

  <div class="wrap produto">
    <div class="produto__midia">
      <div class="produto__palco tom-{p['tom']}">
        <div class="mini-caixa" aria-hidden="true"></div>
      </div>
      <div class="produto__miniaturas" role="tablist" aria-label="Vistas do produto">
        <div class="produto__mini tom-{p['tom']}" role="tab" aria-selected="true"><div class="mini-caixa"></div></div>
        <div class="produto__mini tom-cacau" role="tab" aria-selected="false"><div class="mini-caixa"></div></div>
        <div class="produto__mini tom-mostarda" role="tab" aria-selected="false"><div class="mini-caixa"></div></div>
        <div class="produto__mini tom-rose" role="tab" aria-selected="false"><div class="mini-caixa"></div></div>
      </div>
      <p class="sutil" style="margin-top:12px;font-size:0.78rem">
        Imagens ilustrativas. A cor final depende do papel escolhido.
      </p>
    </div>

    <div class="produto__info">
      <p class="olho">{p['linha']}</p>
      <h1>{p['nome']}</h1>
      <p class="produto__desc">{p['descricao']}</p>

      <div class="produto__preco-linha">
        <span class="produto__preco" data-preco>{brl(p['base'])}</span>
        <span class="produto__un">por unidade · <span data-adicionais>sem adicionais</span></span>
      </div>

      <div class="opcoes">{grupos}</div>
      {aviso_min}

      <div class="compra">
        <div class="linha-compra">
          <div class="quantidade">
            <button type="button" data-menos aria-label="Diminuir quantidade">−</button>
            <input type="number" value="{minimo or 1}" min="{minimo or 1}" max="999" inputmode="numeric" data-qtd aria-label="Quantidade">
            <button type="button" data-mais aria-label="Aumentar quantidade">+</button>
          </div>
          <button class="btn btn--primario" data-comprar>Adicionar à sacola</button>
        </div>

        <div class="resumo-preco">
          <span>Total <span class="sutil" data-qtd-rotulo></span></span>
          <strong data-total>{brl(p['base'] * (minimo or 1))}</strong>
        </div>

        <div>
          <div class="grupo-opcao__cabeca" style="margin-bottom:8px">
            <span class="grupo-opcao__nome">Calcular frete</span>
          </div>
          <div class="cep-caixa">
            <input type="text" inputmode="numeric" maxlength="9" placeholder="Seu CEP" data-cep aria-label="CEP de entrega">
            <button class="btn btn--fantasma" data-calcular>Calcular</button>
          </div>
          <div class="frete-lista" data-fretes></div>
        </div>

        <p class="aviso">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M8 1.5 2 4v4.2c0 3.2 2.4 5.6 6 6.3 3.6-.7 6-3.1 6-6.3V4L8 1.5Z" stroke="currentColor" stroke-width="1.3"/><path d="m5.8 8 1.6 1.6L10.4 6.6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
          <span>Produção sob demanda: sai daqui em até <strong>{p['prazoProducao']} dias úteis</strong> — previsão <span data-producao>{data_producao(p['prazoProducao'])}</span>. O prazo do frete soma a isso.</span>
        </p>
      </div>

      <div class="detalhes">
        <details>
          <summary>O que vem em cada tamanho</summary>
          <div class="detalhes__corpo">
            <ul>
              <li><strong>Pequena 15×15×8</strong> — joia, perfume, chocolate, convite</li>
              <li><strong>Média 22×22×10</strong> — o tamanho mais pedido; caneca, livro, kit de skincare</li>
              <li><strong>Grande 30×30×12</strong> — kit de 3 a 4 itens, cesta pequena</li>
              <li><strong>Extra grande 40×30×15</strong> — kit corporativo, cesta completa, roupa dobrada</li>
            </ul>
          </div>
        </details>
        <details>
          <summary>Papéis e acabamentos</summary>
          <div class="detalhes__corpo">
            <ul>
              <li><strong>Kraft natural</strong> — papelão cru, aparência rústica, o mais barato</li>
              <li><strong>Papel matte</strong> — fosco, toque suave, cores sólidas e vivas</li>
              <li><strong>Papel perolado</strong> — brilho discreto, muda com a luz</li>
              <li><strong>Textura linho</strong> — relevo tipo tecido, o mais sofisticado</li>
            </ul>
          </div>
        </details>
        <details>
          <summary>Prazos, frete e devolução</summary>
          <div class="detalhes__corpo">
            <p>Produção de {p['prazoProducao']} dias úteis antes do envio. Frete calculado por CEP com Correios e Jadlog.
            Como cada peça é feita sob demanda, não aceitamos devolução por desistência — só por defeito de fabricação
            ou avaria no transporte, com foto em até 7 dias do recebimento.</p>
          </div>
        </details>
      </div>
    </div>
  </div>
</main>
""" + rodape()

    script = f"""
iniciarLoja();
const P = {dados_js};
const selecao = {{}};
const extras = {{}};
const precoEl = document.querySelector('[data-preco]');
const adicEl = document.querySelector('[data-adicionais]');
const totalEl = document.querySelector('[data-total]');
const qtdEl = document.querySelector('[data-qtd]');
const rotuloEl = document.querySelector('[data-qtd-rotulo]');
const minimo = {p.get('minimo') or 1};

function lerQtd() {{ return Math.max(minimo, Math.min(999, parseInt(qtdEl.value || '1', 10) || 1)); }}

function render() {{
  const qtd = lerQtd();
  const somaExtras = Object.values(extras).reduce((a, b) => a + b, 0);
  const unit = P.base + somaExtras;
  precoEl.textContent = brl(unit);
  adicEl.textContent = somaExtras ? `+${{brl(somaExtras)}} em adicionais` : 'sem adicionais';
  totalEl.textContent = brl(unit * qtd);
  rotuloEl.textContent = `· ${{qtd}} un`;
  qtdEl.value = qtd;

  for (const [gid, g] of Object.entries(P.grupos)) {{
    const alvo = document.querySelector(`[data-atual="${{gid}}"]`);
    const s = selecao[gid];
    const nomes = Array.isArray(s) ? s.map(v => g.valores[v]) : (s ? [g.valores[s]] : []);
    alvo.textContent = nomes.length ? nomes.join(' + ') : (g.obrigatorio ? 'obrigatório' : 'opcional');
    alvo.style.color = (!nomes.length && g.obrigatorio) ? 'var(--terracota)' : '';
  }}
  document.querySelector('[data-comprar]').disabled = !podeComprar();
}}

function podeComprar() {{
  return Object.entries(P.grupos).every(([gid, g]) => {{
    const s = selecao[gid];
    const vazio = Array.isArray(s) ? s.length === 0 : !s;
    return !g.obrigatorio || !vazio;
  }});
}}

document.querySelectorAll('.chip').forEach(chip => {{
  chip.addEventListener('click', () => {{
    const gid = chip.dataset.grupo;
    const vid = chip.dataset.valor;
    const extra = Number(chip.dataset.extra || 0);
    const g = P.grupos[gid];

    if (g.tipo === 'multiplo') {{
      const atual = Array.isArray(selecao[gid]) ? selecao[gid] : [];
      const tem = atual.includes(vid);
      const nova = tem ? atual.filter(x => x !== vid) : [...atual, vid];
      if (nova.length) selecao[gid] = nova; else delete selecao[gid];
      chip.setAttribute('aria-pressed', String(!tem));
      const soma = nova.reduce((a, id) => {{
        const c = document.querySelector(`.chip[data-grupo="${{gid}}"][data-valor="${{id}}"]`);
        return a + Number(c.dataset.extra || 0);
      }}, 0);
      if (soma) extras[gid] = soma; else delete extras[gid];
    }} else {{
      const anterior = selecao[gid];
      document.querySelectorAll(`.chip[data-grupo="${{gid}}"]`).forEach(c => c.setAttribute('aria-pressed', 'false'));
      if (anterior === vid) {{
        delete selecao[gid];
        delete extras[gid];
      }} else {{
        selecao[gid] = vid;
        chip.setAttribute('aria-pressed', 'true');
        if (extra) extras[gid] = extra; else delete extras[gid];
      }}
    }}
    render();
  }});
}});

qtdEl.addEventListener('change', render);
document.querySelector('[data-mais]').addEventListener('click', () => {{ qtdEl.value = lerQtd() + 1; render(); }});
document.querySelector('[data-menos]').addEventListener('click', () => {{ qtdEl.value = Math.max(minimo, lerQtd() - 1); render(); }});

// monta a linha do carrinho com a chave de SKU determinística
document.querySelector('[data-comprar]').addEventListener('click', () => {{
  if (!podeComprar()) return;
  const partes = Object.entries(P.grupos).map(([gid]) => {{
    const s = selecao[gid];
    const ids = (Array.isArray(s) ? [...s] : s ? [s] : []).sort();
    return `${{gid}}:${{ids.join('+') || '-'}}`;
  }});
  const resumo = Object.entries(P.grupos).map(([gid, g]) => {{
    const s = selecao[gid];
    const nomes = Array.isArray(s) ? s.map(v => g.valores[v]) : (s ? [g.valores[s]] : []);
    return nomes.length ? `${{nomes.join(' + ')}}` : null;
  }}).filter(Boolean).join(' · ');

  adicionar({{
    sku: `${{P.slug}}|${{partes.join('|')}}`,
    nome: P.nome,
    preco: P.base + Object.values(extras).reduce((a, b) => a + b, 0),
    qtd: lerQtd(),
    tom: P.tom,
    opcoesResumo: resumo || 'padrão',
  }});
  abrirGaveta();
}});

// frete simulado (troque cotarFrete por chamada ao Worker)
document.querySelector('[data-calcular]').addEventListener('click', () => {{
  const cep = document.querySelector('[data-cep]').value;
  const r = cotarFrete(cep, lerCarrinho().length ? lerCarrinho() : [{{ qtd: lerQtd() }}]);
  const alvo = document.querySelector('[data-fretes]');
  if (r.erro) {{ alvo.innerHTML = `<p class="sutil" style="margin-top:10px">${{r.erro}}</p>`; return; }}
  alvo.innerHTML = r.opcoes.map(o => `
    <button class="frete-item" data-frete='${{JSON.stringify({{ ...o, cep: r.cep }})}}'>
      <span><strong>${{o.nome}}</strong><br>${{o.transportadora}} · ${{o.prazo}} dias úteis</span>
      <strong>${{brl(o.preco)}}</strong>
    </button>`).join('');
  alvo.querySelectorAll('[data-frete]').forEach(b => {{
    b.addEventListener('click', () => {{
      alvo.querySelectorAll('[data-frete]').forEach(x => x.setAttribute('aria-pressed', 'false'));
      b.setAttribute('aria-pressed', 'true');
      salvarFrete(JSON.parse(b.dataset.frete));
      document.dispatchEvent(new CustomEvent('frete:escolhido'));
    }});
  }});
}});

render();
"""

    return pagina(
        f"{p['nome']} · caixa clara",
        p["resumo"],
        corpo,
        script,
    )


# ---------------------------------------------------------------- pedido
def pedido():
    corpo = topo() + """
<main id="conteudo">
  <div class="wrap migalha"><a href="/">Início</a> <span aria-hidden="true">/</span> <span>Finalizar pedido</span></div>
  <div class="wrap" style="padding-bottom:40px">
    <h1 style="max-width:18ch">Falta pouco.</h1>
    <p class="lead" style="margin-top:12px">Este é o protótipo do checkout. O passo de pagamento vai para o Mercado Pago.</p>

    <div style="display:grid;grid-template-columns:1.4fr 0.9fr;gap:26px;margin-top:34px;align-items:start" class="pedido-grade">
      <div class="bloco" style="padding:24px">
        <h2 style="font-size:1.1rem;margin-bottom:16px">Seus dados</h2>
        <div style="display:grid;gap:12px">
          <label style="display:grid;gap:6px;font-size:0.85rem">Nome completo
            <input type="text" placeholder="Como no documento" style="height:44px;border:1px solid var(--linha);border-radius:100px;padding:0 16px;background:var(--manteiga)">
          </label>
          <label style="display:grid;gap:6px;font-size:0.85rem">E-mail
            <input type="email" placeholder="voce@email.com" style="height:44px;border:1px solid var(--linha);border-radius:100px;padding:0 16px;background:var(--manteiga)">
          </label>
          <label style="display:grid;gap:6px;font-size:0.85rem">CEP de entrega
            <input type="text" data-cep-pedido placeholder="00000-000" style="height:44px;border:1px solid var(--linha);border-radius:100px;padding:0 16px;background:var(--manteiga)">
          </label>
          <div class="aviso-fiscal" style="margin-top:6px">
            <strong>Proteção de dados (LGPD)</strong>
            Coletamos nome, e-mail e endereço apenas para produzir e entregar o pedido. Nada é vendido ou compartilhado.
          </div>
        </div>
        <div style="display:flex;gap:10px;margin-top:20px;flex-wrap:wrap">
          <button class="btn btn--primario" data-pagar>Ir para o pagamento</button>
          <a href="/" class="btn btn--fantasma">Continuar comprando</a>
        </div>
        <p class="sutil" style="font-size:0.78rem;margin-top:14px">
          Ao avançar você será levado ao Mercado Pago (Checkout Pro). Não guardamos dados de cartão em nenhum momento.
        </p>
      </div>

      <div class="bloco" style="padding:24px">
        <h2 style="font-size:1.1rem;margin-bottom:16px">Resumo</h2>
        <div data-resumo-pedido></div>
      </div>
    </div>
  </div>
</main>
""" + rodape()

    script = """
iniciarLoja();
const itens = lerCarrinho();
const alvo = document.querySelector('[data-resumo-pedido]');
const frete = lerFrete();

if (!itens.length) {
  alvo.innerHTML = `<p class="sutil">Sua sacola está vazia. <a href="/" style="text-decoration:underline">Escolher uma caixa</a>.</p>`;
} else {
  const sub = totalItens();
  const freteValor = frete ? frete.preco : 0;
  alvo.innerHTML = `
    ${itens.map(i => `
      <div style="display:flex;justify-content:space-between;gap:10px;padding:9px 0;border-bottom:1px solid var(--manteiga-2);font-size:0.88rem">
        <span>${i.nome} <span class="sutil">× ${i.qtd}</span><br><span class="sutil" style="font-size:0.75rem">${i.opcoesResumo}</span></span>
        <strong style="white-space:nowrap">${brl(i.preco * i.qtd)}</strong>
      </div>`).join('')}
    <div class="linha-total" style="margin-top:14px"><span>Subtotal</span><span>${brl(sub)}</span></div>
    <div class="linha-total"><span>Frete${frete ? ` · ${frete.nome}` : ''}</span><span>${frete ? brl(freteValor) : 'a calcular'}</span></div>
    <div class="linha-total linha-total--forte" style="margin-top:10px"><span>Total</span><strong>${brl(sub + freteValor)}</strong></div>
    <p class="sutil" style="font-size:0.76rem;margin-top:12px">Produção de 5 a 10 dias úteis antes do envio.</p>
  `;
}

document.querySelector('[data-pagar]').addEventListener('click', () => {
  alert('Protótipo: aqui o cliente seria redirecionado ao Mercado Pago (Checkout Pro).\\n\\nEm produção, este botão chama POST /api/pagamento no Worker, que cria a preferência e devolve o init_point.');
});
"""

    return pagina(
        "Finalizar pedido · caixa clara",
        "Finalize seu pedido de caixas personalizadas.",
        corpo,
        script,
    )


# ---------------------------------------------------------------- painel
def painel():
    linhas = [
        ("#1042", "Caixa Presente · Média · matte · cetim", "Marina A.", "189,00", "pago", "Pago"),
        ("#1041", "Caixa Gaveta · Grande · perolado · veludo", "Studio Lima", "412,00", "producao", "Em produção"),
        ("#1040", "Kit Corporativo · 24un", "Grupo Norte", "3.480,00", "producao", "Em produção"),
        ("#1039", "Caixa Envelope · Pequena · kraft", "Rafael T.", "82,00", "enviado", "Enviado"),
        ("#1038", "Kit Chá · Média · matte", "Camila R.", "186,00", "enviado", "Enviado"),
        ("#1037", "Caixa Livro · Média · linho", "Beatriz M.", "118,00", "pendente", "Aguardando pgto"),
    ]
    tabela = "".join(
        f"<tr><td><strong>{n}</strong></td><td>{d}</td><td>{c}</td><td>{v}</td>"
        f"<td><span class='etiqueta etiqueta--{s}'>{r}</span></td></tr>"
        for n, d, c, v, s, r in linhas
    )

    corpo = f"""
<div class="painel">
  <aside class="painel__lado">
    <a href="/" class="marca"><span class="marca__aba" aria-hidden="true"></span><span>caixa clara</span></a>
    <nav class="painel__menu" aria-label="Painel">
      <a href="/painel" aria-current="page">Visão geral</a>
      <a href="/painel">Pedidos <span class="sutil" style="font-size:0.75rem">6</span></a>
      <a href="/painel">Produtos</a>
      <a href="/painel">Variações</a>
      <a href="/painel">Frete</a>
      <a href="/painel">Fiscal</a>
      <a href="/">← Ver a loja</a>
    </nav>
    <div class="painel__rodape">
      Protótipo · dados fictícios<br>
      Logado como dono da loja
    </div>
  </aside>

  <main class="painel__principal">
    <div class="painel__topo">
      <div>
        <p class="olho">Visão geral · outubro 2026</p>
        <h1>Bom dia, Agda.</h1>
      </div>
      <span class="sutil">Última atualização agora</span>
    </div>

    <div class="cartoes">
      <div class="cartao-metrica">
        <div class="cartao-metrica__rotulo">Faturamento no mês</div>
        <div class="cartao-metrica__valor">R$ 6.240</div>
        <div class="cartao-metrica__nota">+18% vs. setembro · 6 pedidos</div>
      </div>
      <div class="cartao-metrica">
        <div class="cartao-metrica__rotulo">Ticket médio</div>
        <div class="cartao-metrica__valor">R$ 1.040</div>
        <div class="cartao-metrica__nota">Corporativo puxa a média</div>
      </div>
      <div class="cartao-metrica">
        <div class="cartao-metrica__rotulo">Na fila de produção</div>
        <div class="cartao-metrica__valor">2</div>
        <div class="cartao-metrica__nota">Prazo médio: 7 dias úteis</div>
      </div>
      <div class="cartao-metrica">
        <div class="cartao-metrica__rotulo">Limite MEI usado</div>
        <div class="cartao-metrica__valor">62%</div>
        <div class="cartao-metrica__nota">R$ 50.400 de R$ 81.000</div>
        <div class="barra-limite"><span style="width:62%"></span></div>
      </div>
    </div>

    <div class="aviso-fiscal" style="margin-bottom:16px">
      <strong>Atenção ao teto do MEI</strong>
      Faltam R$ 30.600 para o limite anual. Nesse ritmo você chega lá em cerca de 5 meses.
      Ao passar de R$ 64.800 (80%), o painel vai te avisar com antecedência para você planejar a mudança para ME — o desenquadramento é retroativo e não pode ser desfeito.
    </div>

    <div class="painel__grade">
      <div class="bloco">
        <h2>Pedidos recentes</h2>
        <div style="overflow-x:auto">
          <table class="tabela">
            <thead><tr><th>Pedido</th><th>Item</th><th>Cliente</th><th>Total</th><th>Status</th></tr></thead>
            <tbody>{tabela}</tbody>
          </table>
        </div>
      </div>

      <div style="display:grid;gap:16px">
        <div class="bloco">
          <h2>Para hoje</h2>
          <div class="tarefa"><span class="tarefa__marca tarefa__marca--ok"></span><span>Conferir arte do cartão do pedido #1042</span></div>
          <div class="tarefa"><span class="tarefa__marca"></span><span>Emitir etiqueta do #1039 no Melhor Envio</span></div>
          <div class="tarefa"><span class="tarefa__marca"></span><span>Responder orçamento corporativo (24un)</span></div>
          <div class="tarefa"><span class="tarefa__marca"></span><span>Comprar fita de veludo — estoque baixo</span></div>
        </div>

        <div class="bloco">
          <h2>Fiscal · MEI</h2>
          <p class="sutil" style="font-size:0.85rem;margin-bottom:12px">
            DAS de outubro vence em <strong>20/11</strong>. Situação: em dia.
          </p>
          <div style="display:grid;gap:8px">
            <a href="#" class="btn btn--fantasma btn--bloco" style="font-size:0.85rem">Baixar DAS do mês</a>
            <a href="#" class="btn btn--fantasma btn--bloco" style="font-size:0.85rem">Exportar faturamento (CSV)</a>
          </div>
          <p class="sutil" style="font-size:0.76rem;margin-top:12px;margin-bottom:0">
            A declaração anual do MEI (DASN-SIMEI) é feita no portal do governo até 31 de maio.
            O painel te lembra e organiza os números — a entrega continua sendo sua.
          </p>
        </div>
      </div>
    </div>
  </main>
</div>"""

    return pagina("Painel · caixa clara", "Painel de gestão da loja.", corpo, "")


# ---------------------------------------------------------------- escrever
def escrever(caminho_rel, html):
    destino = os.path.join(SAIDA, caminho_rel)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    if os.path.isdir(SAIDA):
        shutil.rmtree(SAIDA)
    os.makedirs(SAIDA, exist_ok=True)

    # estáticos
    for nome in os.listdir(PUBLICO):
        shutil.copy2(os.path.join(PUBLICO, nome), os.path.join(SAIDA, nome))

    escrever("index.html", home())
    escrever(os.path.join("pedido", "index.html"), pedido())
    escrever(os.path.join("painel", "index.html"), painel())
    for p in PRODUTOS:
        escrever(os.path.join("produto", p["slug"], "index.html"), produto(p))

    total = sum(len(f) for _, _, f in os.walk(SAIDA))
    print(f"ok · {total} arquivos em {SAIDA}")


if __name__ == "__main__":
    main()
