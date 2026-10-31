#!/usr/bin/env node
/**
 * Publica o protótipo no GitHub usando só a API REST (sem git nem gh instalados).
 *
 * Uso:
 *   node publicar.cjs                 # cria o repo se não existir e envia tudo
 *   node publicar.cjs "mensagem"      # envia commit com mensagem própria
 *
 * Exige GH_TOKEN no ambiente (já vem do conector GitHub).
 */
const fs = require('fs');
const path = require('path');
const https = require('https');
const crypto = require('crypto');

const TOKEN = process.env.GH_TOKEN;
const DONO = 'End-ax';
const REPO = 'caixa-clara';
const RAIZ = __dirname;
const IGNORAR = new Set(['.git', 'node_modules', 'site', 'dados.json']);
const EXT_OK = new Set([
  '.html', '.css', '.js', '.cjs', '.mjs', '.json', '.md', '.py',
  '.svg', '.png', '.jpg', '.jpeg', '.webp', '.ico', '.txt', '.toml',
]);

if (!TOKEN) {
  console.error('GH_TOKEN ausente no ambiente.');
  process.exit(1);
}

function api(metodo, caminho, corpo) {
  return new Promise((resolve, rejeitar) => {
    const dados = corpo ? JSON.stringify(corpo) : null;
    const req = https.request(
      {
        hostname: 'api.github.com',
        path: caminho,
        method: metodo,
        headers: {
          Authorization: `Bearer ${TOKEN}`,
          'User-Agent': 'caixa-clara-deploy',
          Accept: 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          ...(dados ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(dados) } : {}),
        },
      },
      (res) => {
        let txt = '';
        res.on('data', (c) => (txt += c));
        res.on('end', () => {
          let json = null;
          try {
            json = txt ? JSON.parse(txt) : null;
          } catch {
            json = { bruto: txt };
          }
          resolve({ status: res.statusCode, json });
        });
      }
    );
    req.on('error', rejeitar);
    if (dados) req.write(dados);
    req.end();
  });
}

function listar(dir, base = '') {
  const saida = [];
  for (const nome of fs.readdirSync(dir)) {
    if (IGNORAR.has(nome) || nome.startsWith('.git')) continue;
    const abs = path.join(dir, nome);
    const rel = base ? `${base}/${nome}` : nome;
    const st = fs.statSync(abs);
    if (st.isDirectory()) saida.push(...listar(abs, rel));
    else if (EXT_OK.has(path.extname(nome).toLowerCase()) && st.size < 900_000) {
      saida.push({ rel, abs });
    }
  }
  return saida;
}

async function garantirRepo() {
  const ver = await api('GET', `/repos/${DONO}/${REPO}`);
  if (ver.status === 200) {
    console.log(`repo existe: ${ver.json.html_url}`);
    return;
  }
  const criado = await api('POST', '/user/repos', {
    name: REPO,
    description: 'Loja de caixas e kits personalizados — protótipo (Cloudflare Workers + Supabase)',
    private: false,
    has_issues: true,
    has_wiki: false,
    auto_init: false,
  });
  if (criado.status === 201) {
    console.log(`repo criado: ${criado.json.html_url}`);
  } else {
    throw new Error(`falha ao criar repo: ${criado.status} ${JSON.stringify(criado.json)}`);
  }
}

async function arvoreAtual() {
  const r = await api('GET', `/repos/${DONO}/${REPO}/git/trees/main?recursive=1`);
  const mapa = new Map();
  if (r.status === 200 && Array.isArray(r.json.tree)) {
    for (const t of r.json.tree) if (t.type === 'blob') mapa.set(t.path, t.sha);
  }
  return mapa;
}

async function main() {
  const msg = process.argv[2] || 'prototipo: loja, motor de variacoes, sacola, checkout e painel';
  await garantirRepo();

  const existentes = await arvoreAtual();
  const arquivos = listar(RAIZ);
  const envios = [];

  for (const f of arquivos) {
    const conteudo = fs.readFileSync(f.abs);
    const blob = await api('POST', `/repos/${DONO}/${REPO}/git/blobs`, {
      content: conteudo.toString('base64'),
      encoding: 'base64',
    });
    if (blob.status !== 201) throw new Error(`blob falhou em ${f.rel}: ${blob.status}`);
    envios.push({ path: f.rel, mode: '100644', type: 'blob', sha: blob.json.sha });
  }

  // árvore completa a partir da base (mantém o que já existir de igual)
  const base = existentes.size
    ? (await api('GET', `/repos/${DONO}/${REPO}/git/ref/heads/main`)).json?.object?.sha
    : undefined;

  const arvore = await api('POST', `/repos/${DONO}/${REPO}/git/trees`, {
    ...(base ? { base_tree: base } : {}),
    tree: envios,
  });
  if (arvore.status !== 201) throw new Error(`arvore falhou: ${arvore.status} ${JSON.stringify(arvore.json)}`);

  const commit = await api('POST', `/repos/${DONO}/${REPO}/git/commits`, {
    message: msg,
    tree: arvore.json.sha,
    ...(base ? { parents: [base] } : {}),
  });
  if (commit.status !== 201) throw new Error(`commit falhou: ${commit.status} ${JSON.stringify(commit.json)}`);

  if (base) {
    const ref = await api('PATCH', `/repos/${DONO}/${REPO}/git/refs/heads/main`, {
      sha: commit.json.sha,
      force: false,
    });
    if (ref.status !== 200) throw new Error(`ref falhou: ${ref.status} ${JSON.stringify(ref.json)}`);
  } else {
    const ref = await api('POST', `/repos/${DONO}/${REPO}/git/refs`, {
      ref: 'refs/heads/main',
      sha: commit.json.sha,
    });
    if (ref.status !== 201) throw new Error(`ref falhou: ${ref.status} ${JSON.stringify(ref.json)}`);
  }

  console.log(`ok · ${arquivos.length} arquivos · commit ${commit.json.sha.slice(0, 7)}`);
  console.log(`https://github.com/${DONO}/${REPO}`);
}

main().catch((e) => {
  console.error('ERRO:', e.message);
  process.exit(1);
});
