
from PIL import Image
import os

def eh_cinza_ou_escuro(pixel, limiar=195):
    """Retorna True se o pixel fizer parte da barra cinza/escura do cabeçalho."""
    r, g, b = pixel[:3]
    return r < limiar and g < limiar and b < limiar

def encontrar_cabecalhos_enem_digital(imagem):
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Região horizontal da barra cinza (de 35% até 92% da largura da imagem)
    x_inicio = int(largura * 0.35)
    x_fim = int(largura * 0.92)
    largura_regiao = x_fim - x_inicio
    
    posicoes_corte = []
    y = 5
    
    while y < altura - 15:
        # Verifica 3 linhas seguidas da espessura da barra (y, y+2 e y+4)
        escuros_y0 = sum(1 for x in range(x_inicio, x_fim) if eh_cinza_ou_escuro(pixels[x, y]))
        
        if escuros_y0 > largura_regiao * 0.78:
            escuros_y2 = sum(1 for x in range(x_inicio, x_fim) if eh_cinza_ou_escuro(pixels[x, y + 2]))
            escuros_y4 = sum(1 for x in range(x_inicio, x_fim) if eh_cinza_ou_escuro(pixels[x, y + 4]))
            
            # Checa bem rente acima (y-4) e logo abaixo da barra (y+11)
            escuros_acima = sum(1 for x in range(x_inicio, x_fim) if eh_cinza_ou_escuro(pixels[x, y - 4]))
            escuros_abaixo = sum(1 for x in range(x_inicio, x_fim) if eh_cinza_ou_escuro(pixels[x, y + 11]))
            
            if (escuros_y2 > largura_regiao * 0.78 and 
                escuros_y4 > largura_regiao * 0.78 and
                escuros_acima < largura_regiao * 0.10 and 
                escuros_abaixo < largura_regiao * 0.10):
                
                # Corta 5 pixels acima da barra para ficar abaixo da linha fina do cabeçalho
                posicao_corte = max(0, y - 5)
                posicoes_corte.append(posicao_corte)
                print(f"Questão encontrada! Topo da barra em y={y} -> Cortando em y={posicao_corte}")
                
                # Pula 200 pixels para baixo para não cortar a mesma questão duas vezes
                y += 200
                continue
        y += 1
        
    return posicoes_corte

def dividir_imagem_enem(caminho_imagem, pasta_saida):
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_cabecalhos_enem_digital(imagem)
    
    if not posicoes_corte:
        print("Nenhuma questão encontrada! Tente aumentar o 'limiar' de 195 para 210.")
        return
    
    print(f"\nTotal de cortes encontrados: {len(posicoes_corte)}")
    os.makedirs(pasta_saida, exist_ok=True)
    
    pontos = list((0,)) + posicoes_corte + list((altura,))
    contador = 1
    
    for i in range(len(pontos) - 1):
        y_inicio = pontos[i]
        y_fim = pontos[i + 1]
        
        # Ignora sobras muito pequenas antes da primeira questão
        if y_fim - y_inicio < 100:
            continue
            
        secao = imagem.crop((0, y_inicio, largura, y_fim))
        nome_arquivo = f"questao_{contador:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        contador += 1

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes"
    
    dividir_imagem_enem(caminho_imagem, pasta_saida)
    print("\nDivisão concluída!")
