import requests
import json
import csv
from collections import defaultdict
import time  
# URL e chave da API (substitua com suas próprias credenciais)
url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key="

# Função para enviar a requisição e retornar apenas o texto gerado
def send_request(descricao):
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Monta o prompt com a instrução adicional
    full_prompt = f"Haja como um perito criminal para analisar usando apenas uma palavra entre as categorias (Homicídio, Feminicídio, Assalto, Roubo, Extorsão, Vandalismo, Agressão, Abuso, Assédio, Indetectado) o caso de acordo com o input: {descricao}"
    
    data = {
        "contents": [
            {
                "parts": [{"text": full_prompt}]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result_json = response.json()

        # Verifica se há uma resposta válida na estrutura
        if 'candidates' in result_json and len(result_json['candidates']) > 0:
            content = result_json['candidates'][0].get('content', {})
            if 'parts' in content and len(content['parts']) > 0:
                return content['parts'][0]['text']
        
    except Exception as e:
        print(f"Erro ao processar a requisição para '{descricao}': {e}")
    
    return None

# Função para processar o arquivo CSV e gerar o relatório
def process_csv(file_path):
    crimes_por_bairro = defaultdict(int)
    homicidio_feminicidio_por_bairro = defaultdict(int)
    casos_sem_resposta = []

    # Leitura do arquivo CSV
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            descricao = row['Descrição']
            local = row['Local']
            
            # Envia a descrição do crime para a API e obtém a análise gerada
            analise = send_request(descricao)
            
            # Adiciona um intervalo de 1 segundo entre as requisições
            time.sleep(1)
            
            # Exibir detalhes da requisição
            print(f"Descrição: {descricao}")
            print(f"Local: {local}")
            
            if analise:
                print(f"Resposta da análise: {analise}")
                print("----------------------------------------")
                
                # Atualiza as estatísticas com base na análise gerada
                crimes_por_bairro[local] += 1
                
                # Verifica se a análise menciona homicídio ou feminicídio
                if 'homicídio' in analise.lower() or 'feminicídio' in analise.lower():
                    homicidio_feminicidio_por_bairro[local] += 1
            else:
                print("Não foi possível obter uma resposta válida.")
                print("----------------------------------------")
                
                # Salva casos sem resposta
                casos_sem_resposta.append({'Descrição': descricao, 'Local': local})
    
    # Identifica o bairro com mais homicídios e feminicídios
    if homicidio_feminicidio_por_bairro:
        bairro_mais_crimes = max(homicidio_feminicidio_por_bairro, key=homicidio_feminicidio_por_bairro.get)
        total_homicidio_feminicidio = homicidio_feminicidio_por_bairro[bairro_mais_crimes]
    else:
        bairro_mais_crimes = "Nenhum bairro com homicídio ou feminicídio registrado"
        total_homicidio_feminicidio = 0
    
    # Gera o relatório final
    relatorio = f"Relatório de Crimes por Bairro:\n\n"
    for bairro, total_crimes in crimes_por_bairro.items():
        relatorio += f"Bairro: {bairro}\n"
        relatorio += f"Total de Crimes: {total_crimes}\n"
        relatorio += "\n"
    
    relatorio += f"Bairro com mais casos de Homicídio e Feminicídio: {bairro_mais_crimes}\n"
    relatorio += f"Total de Homicídios e Feminicídios: {total_homicidio_feminicidio}\n"
    
    return relatorio, casos_sem_resposta

# Arquivo CSV de exemplo
csv_file = 'exemplo_crimes.csv'

# Processamento do arquivo CSV e geração do relatório
relatorio, casos_sem_resposta = process_csv(csv_file)

# Salvando o relatório final em um arquivo
with open('relatorio_final.txt', 'w', encoding='utf-8') as file:
    file.write(relatorio)

# Salvando casos sem resposta em um arquivo CSV
if casos_sem_resposta:
    with open('casos_sem_resposta.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Descrição', 'Local']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(casos_sem_resposta)

# Exibe o relatório gerado
print(relatorio)
print("\nRelatório final e casos sem resposta foram salvos nos arquivos 'relatorio_final.txt' e 'casos_sem_resposta.csv'.")
