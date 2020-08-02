
import requests
import json
from datetime import date
import urllib.parse
import pprint
import os

accuweatherAPIKey = os.environ.get('accuweatherAPIKey')
mapboxToken = os.environ.get('mapboxToken')
dias_semana = ["Domingo","Segunda-feira","Terça-feira","Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"];

def pegarCoordenadas():
    r = requests.get('http://www.geoplugin.net/json.gp')

    if (r.status_code != 200):
        print('Não foi possível obter a localização.')
        return None
    else:
        try:
            localizacao = json.loads(r.text)
            coordenadas = {}
            coordenadas['lat'] = localizacao['geoplugin_latitude']
            coordenadas['long'] = localizacao['geoplugin_longitude']
            return coordenadas
        except:
            return None
    
def pegarCodigoLocal(lat,long):
    LocationAPIUrl = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/" \
    + "search?apikey=" +  accuweatherAPIKey \
    + "&q=" + lat + "%2C"+ long +"&language=pt-br"

    r = requests.get(LocationAPIUrl)
    if (r.status_code != 200):
        print('Não foi possível obter o código do local.')
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {}
            infoLocal['nomeLocal'] = locationResponse['LocalizedName'] + ", " \
                        + locationResponse['AdministrativeArea']['LocalizedName'] + ". " \
                        + locationResponse['Country']['LocalizedName']
            infoLocal['codigoLocal'] = locationResponse['Key']
            return infoLocal
        except:
            return None

def pegarTempoAgora(codigoLocal, nomeLocal):

    CurrentConditionsAPIUrl = "http://dataservice.accuweather.com/currentconditions/v1/" \
                              + codigoLocal + "?apikey=" + accuweatherAPIKey \
                              + "&language=pt-br"
    r = requests.get(CurrentConditionsAPIUrl)
    if (r.status_code != 200):
        print('Não foi possível obter o clima atual.')
        return None
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            infoClima = {}
            infoClima['textoClima'] = CurrentConditionsResponse[0]['WeatherText']
            infoClima['temperatura'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value']
            infoClima['nomeLocal'] = nomeLocal
            return infoClima
        except:
            return None

def pegarPrevisao5Dias(codigoLocal):
    DailyAPIUrl = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" \
                              + codigoLocal + "?apikey=" + accuweatherAPIKey \
                              + "&metric=true&language=pt-br&details=true&getphotos=false"
    r = requests.get(DailyAPIUrl)
    if (r.status_code != 200):
        print('Não foi possível obter a previsão para os próximos dias.')
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            infoClima5Dias = []
            for dia in DailyResponse['DailyForecasts']:
                climaDia = {}
                climaDia['max'] = dia['Temperature']['Maximum']['Value']
                climaDia['min'] = dia['Temperature']['Minimum']['Value']
                climaDia['clima'] = dia['Day']['IconPhrase']
                diaSemana = date.fromtimestamp(dia['EpochDate']).strftime("%w")
                climaDia['dia'] = dias_semana[int(diaSemana)]
                infoClima5Dias.append(climaDia)
            return infoClima5Dias
        except:
            return None

def mostrarPrevisaoTempo(lat, long):
    try:
        local = pegarCodigoLocal(lat,long)
        climaAtual = pegarTempoAgora(local['codigoLocal'], local['nomeLocal'])  
        print('Clima atual em: ' + climaAtual['nomeLocal'])
        print(climaAtual['textoClima'])
        print('Temperatura: ' + str(climaAtual['temperatura']) + "\xb0" + "C")
    except:
        print("Erro ao obter o clima atual")
    
    opcao = input('\nDeseja ver a previsão do tempo para os próximos dias ? (S ou N): ').lower()
    
    if opcao == "s":
        print('Clima para hoje e para os próximos dias: \n')
        
        previsao5Dias = pegarPrevisao5Dias(local['codigoLocal'])
        try:
            for dia in previsao5Dias:
                print(dia['dia'])
                print('Mínima: ' + str(dia['min']) + "\xb0" + "C")
                print('Máxima: ' + str(dia['max']) + "\xb0" + "C")
                print('Clima: ' + dia['clima'])
                print('\n--------------------------')
        except:
            print('Erro ao obter a previsão do tempo')

def pesquisarLocal(local):
    _local = urllib.parse.quote(local)
    mapboxGeocodeUrl = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + _local + ".json?access_token=" + mapboxToken
    r = requests.get(mapboxGeocodeUrl)
    if (r.status_code != 200):
        print('Não foi possível obter o clima atual')
    else:
        try:
            MapboxResponse = json.loads(r.text)
            coordenadas = {}
            coordenadas['long'] = str( MapboxResponse['features'][0]['geometry']['coordinates'][0] )
            coordenadas['lat'] = str( MapboxResponse['features'][0]['geometry']['coordinates'][1] )
            return coordenadas
        except:
            print("Erro ao obter a previsão do tempo")
  
try:
    coordenadas = pegarCoordenadas()
    mostrarPrevisaoTempo(coordenadas['lat'], coordenadas['long'])
    
    continuar = "s"
    while continuar == "s":
        continuar = input("Deseja consultar a previsão de outro local ? (S ou N): ").lower()
        if continuar != "s":
            break
        local = input('Digite a cidade e o estado: ')
        try:
            coordenadas = pesquisarLocal(local)
            mostrarPrevisaoTempo(coordenadas['lat'],coordenadas['long'])
        except:
            print('Não foi possível obter a previsão para este local')
    
except:
    print('Erro ao processar a solicitação. Entre em contato com o suporte.')