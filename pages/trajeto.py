import xml.etree.ElementTree as ET

def calcular_frete(cep_origem, cep_destino, peso=1, altura=2, largura=11, comprimento=16, servico='04014'):
    """Consulta o frete usando a API dos Correios (SOAP via HTTP GET)"""
    url = (
        f"http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx?"
        f"nCdServico={servico}&sCepOrigem={cep_origem}&sCepDestino={cep_destino}"
        f"&nVlPeso={peso}&nCdFormato=1&nVlComprimento={comprimento}&nVlAltura={altura}"
        f"&nVlLargura={largura}&nVlDiametro=0&sCdMaoPropria=n&nVlValorDeclarado=0"
        f"&sCdAvisoRecebimento=n&nIndicaCalculo=3&StrRetorno=xml"
    )

    try:
        response = requests.get(url)
        tree = ET.fromstring(response.content)
        valor = tree.find(".//Valor").text
        prazo = tree.find(".//PrazoEntrega").text
        erro = tree.find(".//Erro").text
        msg_erro = tree.find(".//MsgErro").text

        if erro != '0':
            return f"Erro: {msg_erro}"
        return f"Valor: R$ {valor}, Prazo: {prazo} dias úteis"
    except Exception as e:
        return f"Erro ao calcular frete: {e}"
