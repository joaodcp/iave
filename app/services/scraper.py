# it works! now account for guides and replace empty values with null
import requests, json
from bs4 import BeautifulSoup
from flask import jsonify, escape
from datetime import datetime


# epocic pode ser época ou ciclo, dependendo do tipo. é feita validação para determinar qual.
def scrapeIAVE(tipo, ano, epocic):
    tipo = escape(str(tipo))
    ano = escape(str(ano))
    epocic = escape(str(epocic))
    # lista de tipos permitidos e parte do url correspondente
    tipos = {
        'pAfericaoEB': 'arquivo-provas-de-afericao-eb',
        'pFinaisEB': 'arquivo-provas-finais-de-ciclo-eb',
        'peFinaisES': 'arquivo-provas-e-exames-finais-nacionais-es',
    }
    # se o tipo indicado nao estiver na lista de tipos
    if tipo not in [*tipos]:
        return 'Indique um tipo válido.'
    # se a string ano contiver carateres não numéricos
    if not ano.isnumeric():
        return 'Indique um ano válido.'
    currentYear = datetime.now().year
    currentMonth = datetime.now().month
    # recusar anos não disponiveis em iave.pt
    if int(ano) not in range(1997, currentYear):
        return 'Indique um ano entre 1997 e ' + str(currentYear)
    # definir sufixo para uso em classes html (são diferentes dependendo do tipo)
    suffix = ''
    if tipo == 'pFinaisEB':
        suffix = '-final-ciclo-eb'
    elif tipo == 'peFinaisES':
        suffix = '-exame-nacional'
    # lista de épocas permitidas e ids html correspondentes
    epocas = {
        '1fase': 'fase-1'+suffix,
        '2fase': 'fase-2'+suffix,
        'especial': 'epoca-especial'+suffix
    }
    # lista de ciclos permitidos e ids html correspondentes
    ciclos = {
        '1ciclo': 'ciclo-1',
        '2ciclo': 'ciclo-2',
        '3ciclo': 'ciclo-3'
    }
    # se o tipo for pFinaisEB ou peFinaisES, e se a epoca não estiver na lista de épocas
    if tipo == 'pFinaisEB' or tipo == 'peFinaisES':
        if epocic not in [*epocas]:
            return 'Indique uma época válida.'
    # se o tipo for pAfericaoEB, e se o ciclo não estiver na lista de ciclos
    elif tipo == 'pAfericaoEB':
        if epocic not in [*ciclos]:
            return 'Indique um ciclo válido.'
    url = 'https://iave.pt/provas-e-exames/arquivo/' + tipos[tipo] + '/?ano=' + ano
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    # se as provas forem de afericao e do eb, procurar por ciclo
    if tipo == 'pAfericaoEB':
        epoca = soup.find(id=ciclos[epocic])
    # se as provas forem finais do eb ou provas e exames do es, procurar por epoca
    elif tipo == 'pFinaisEB' or tipo == 'peFinaisES':
        epoca = soup.find(id=epocas[epocic])
    # encontrar o acordeao correspondente a cada disciplina
    disciplinas = epoca.find_all(class_='each-acordeao')
    # lista que vai conter todos os dados
    arr = []
    # lista de uso temporário que muda a cada disciplina
    filesArr = []
    audioArr = []

    for disciplina in disciplinas:
        # encontrar e "tratar" nome da disciplina
        nome = disciplina.find(class_='uk-accordion-title').getText()
        nome = str(nome).strip()
        # encontrar ficheiros
        conteudos = disciplina.find(class_='uk-accordion-content')
        documentos = conteudos.find(class_='docs-container')
        ficheiros = documentos.find_all(class_='each-doc')
        for ficheiro in ficheiros:
            # encontrar e "tratar" nome do ficheiro
            filetitle = ficheiro.find(class_='title')
            fileversion = filetitle.find(class_='doc-version')
            if fileversion: fileversion = fileversion.getText()
            filename = ficheiro.find(class_='title').getText()
            filename = str(filename).strip()
            # print(fileversion)
            fileversion = str(fileversion).strip()
            filename = filename.replace(fileversion, '')
            # print(filename)
            audioscontainer = ficheiro.find(class_='links-container')
            if audioscontainer:
                audios = audioscontainer.find_all(class_='audios-links')
                # filename = audios
                for audio in audios:
                    audioname = audio.getText()
                    audioname = str(audioname).strip()
                    # print(audioname)
                    audiopath = audio['href']
                    # print(audiopath)
                    audioArr.append({
                        'nome': audioname,
                        'url': audiopath
                    })
                # print(filename+"\nend")
                # não é a melhor solução
                if "Guiões" in filename:
                    filename = "Guiões"
                filesArr.append({
                    'nome': filename,
                    'subcontent': audioArr
                })
                audioArr = []
            elif not audioscontainer:
                # encontrar url para o ficheiro
                filepath = ficheiro.find(class_='title')['href']
                # criar dict com os dados do ficheiro
                if fileversion == "None":
                    filesArr.append({
                        'nome': filename,
                        'url': filepath,
                    })
                else:
                    filesArr.append({
                        'nome': filename,
                        'url': filepath,
                        'versao': fileversion,
                    })
        # por cada disciplina, adicionar à lista final os seus dados
        arr.append({
            'disciplina': nome,
            'ficheiros': filesArr
        })
        # apagar os conteudos temporários que estavam nesta lista
        filesArr = []
    # se nenhum dado for adicionado à lista final (não existem no site do iave)
    if arr == []:
        return 'Não existem dados disponíveis para os parâmetros que indicou.'
    else:
        return jsonify(arr)