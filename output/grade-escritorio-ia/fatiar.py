"""Corta a arte 3x2 do escritorio de agentes em 6 quadros 1080x1080.

A arte de origem tem celulas em 3:2. Forcar recorte quadrado cortaria as
tarjas de texto ("1 PESQUISA E OPORTUNIDADES"), entao cada celula entra
centralizada sobre fundo da propria arte. No grid do perfil os 6 aparecem
alinhados e a numeracao mantem a leitura 1 a 6.

Uso:  python3 -I fatiar.py <caminho_da_arte.png>
"""
import os, sys
from PIL import Image

SRC = sys.argv[1]
OUT = os.path.dirname(os.path.abspath(__file__))
LADO = 1080
COLS, LINHAS = 3, 2

NOMES = ["1_pesquisa", "2_anuncios", "3_atendimento",
         "4_rentabilidade", "5_logistica", "6_planejamento"]

im = Image.open(SRC).convert("RGB")
W, H = im.size
cw, ch = W // COLS, H // LINHAS
print(f"origem {W}x{H} -> celula {cw}x{ch}")

# cor de fundo: canto superior esquerdo da arte, que e a area escura
fundo = im.getpixel((4, 4))

for i, nome in enumerate(NOMES):
    cx, cy = i % COLS, i // COLS
    cel = im.crop((cx * cw, cy * ch, (cx + 1) * cw, (cy + 1) * ch))
    # escala para caber na largura, mantendo proporcao
    nh = round(cel.height * LADO / cel.width)
    cel = cel.resize((LADO, nh), Image.LANCZOS)
    tela = Image.new("RGB", (LADO, LADO), fundo)
    tela.paste(cel, (0, (LADO - nh) // 2))
    destino = os.path.join(OUT, f"{nome}.jpg")
    tela.save(destino, "JPEG", quality=92, optimize=True)
    print("ok", destino)

print("\nPublicar no Instagram do 6 para o 1 — o perfil empilha de tras pra frente.")
