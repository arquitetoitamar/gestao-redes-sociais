"""Gera versoes 1080x1920 dos quadros da grade, para story e capa de destaque."""
import os
from PIL import Image, ImageFilter

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
NOMES = ["1_pesquisa", "2_anuncios", "3_atendimento",
         "4_rentabilidade", "5_logistica", "6_planejamento"]

for nome in NOMES:
    q = Image.open(os.path.join(OUT, nome + ".jpg")).convert("RGB")
    # fundo: o proprio quadro ampliado e desfocado, para preencher sem tarja
    bg = q.resize((W, W), Image.LANCZOS)
    bg = bg.resize((int(W * 1.6), int(W * 1.6)), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(42))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2,
                  (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = Image.eval(bg, lambda p: int(p * 0.45))
    tela = bg
    # quadro nitido, centralizado e um pouco acima do meio
    nq = q.resize((W, W), Image.LANCZOS)
    tela.paste(nq, (0, (H - W) // 2 - 60))
    destino = os.path.join(OUT, f"story_{nome}.jpg")
    tela.save(destino, "JPEG", quality=92, optimize=True)
    print("ok", os.path.basename(destino))
