"""Simula um circuito RC ideal e exporta um gráfico HTML e uma tabela CSV."""
import argparse
import csv
import math
from pathlib import Path


def positivo(texto):
    try:
        valor = float(texto.replace(",", "."))
    except ValueError as erro:
        raise argparse.ArgumentTypeError("Informe um número.") from erro
    if not math.isfinite(valor) or not 1e-12 <= valor <= 1e12:
        raise argparse.ArgumentTypeError("Use um valor entre 1e-12 e 1e12.")
    return valor


def simular(resistencia_kohm, capacitancia_uf, tensao, modo):
    resistencia = resistencia_kohm * 1000
    tau = resistencia * capacitancia_uf * 1e-6
    inicio, alvo = (0, tensao) if modo == "carga" else (tensao, 0)
    amostras = []
    for passo in range(201):
        instante = tau * passo / 40
        diferenca = (alvo - inicio) * math.exp(-passo / 40)
        amostras.append((instante, alvo - diferenca, diferenca / resistencia))
    return tau, amostras


def salvar(pasta, tau, amostras, opcoes):
    pasta.mkdir(parents=True, exist_ok=True)
    with (pasta / "amostras.csv").open("w", newline="", encoding="utf-8") as arquivo:
        tabela = csv.writer(arquivo)
        tabela.writerow(["tempo_s", "tensao_capacitor_V", "corrente_A"])
        tabela.writerows(amostras)

    pontos = " ".join(
        f"{64 + 600 * tempo / (5 * tau):.2f},{250 - 210 * volts / opcoes.volts:.2f}"
        for tempo, volts, _ in amostras
    )
    marcas = []
    for indice in range(6):
        x = 64 + 120 * indice
        marcas.append(f'<path d="M{x} 40V250"/><text x="{x}" y="275">{indice}τ</text>')
    pagina = f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Circuito RC</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#101d28;color:#edf4f5;font:18px system-ui}}
main{{max-width:850px;margin:auto;padding:7vh 5vw}}h1{{font-size:clamp(2rem,6vw,4rem);margin:.2em 0}}
small,a{{color:#76e3cc}}figure{{margin:2em 0;background:#192d3b;border-radius:16px;padding:12px}}
svg{{width:100%;height:auto}}svg path{{stroke:#466171}}svg text{{fill:#d8e9ed;text-anchor:middle;font:16px monospace}}
figcaption{{padding:8px}}p{{line-height:1.5}}
</style><main><small>LABORATÓRIO DE ELETRÔNICA</small><h1>Curva de {opcoes.modo}</h1>
<p>Resistência de {opcoes.kohm:g} kΩ · Capacitância de {opcoes.uf:g} µF · Tensão de referência de {opcoes.volts:g} V</p>
<figure><svg viewBox="0 0 710 300" role="img" aria-label="Tensão no capacitor durante cinco constantes de tempo">
<path d="M64 40H664 M64 250H664"/>{''.join(marcas)}
<text x="37" y="34">{opcoes.volts:g} V</text><text x="37" y="250">0 V</text>
<polyline points="{pontos}" stroke="#76e3cc" stroke-width="4" fill="none"/></svg>
<figcaption>Tensão no capacitor em função do tempo. Cada intervalo τ dura {tau:.4g} s.</figcaption></figure>
<p>Em 1τ, a tensão chega a <b>{amostras[40][1]:.4g} V</b>. Em 5τ ({5*tau:.4g} s), chega a <b>{amostras[-1][1]:.4g} V</b>.</p>
<a href="amostras.csv" download>Baixar as 201 amostras em CSV</a></main></html>"""
    (pasta / "curva.html").write_text(pagina, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kohm", type=positivo, default=10, help="resistência em kΩ")
    parser.add_argument("--uf", type=positivo, default=100, help="capacitância em µF")
    parser.add_argument("--volts", type=positivo, default=5, help="tensão de referência em V")
    parser.add_argument("--modo", choices=["carga", "descarga"], default="carga")
    parser.add_argument("--saida", type=Path, default=Path("resultado"))
    opcoes = parser.parse_args()
    tau, amostras = simular(opcoes.kohm, opcoes.uf, opcoes.volts, opcoes.modo)
    salvar(opcoes.saida, tau, amostras, opcoes)
    print(f"Constante de tempo: {tau:.4g} s. Abra {(opcoes.saida / 'curva.html').resolve()}")
