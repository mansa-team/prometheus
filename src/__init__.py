from imports import *
from main.ai import Client

current_date = datetime.now().strftime("%d/%m/%Y")

if __name__ == "__main__":
    userQuery = "pode me mostrar os resultados do banco do brasil em lucros liquidos no ano de 2021 e me explicar sua diferenca com os resultados de 2025, tambem me mostre os dados da petrobras no mesmo periodo"
    # Be replaced by a dedicated function to execute the RAG system when the user sends a message in the frontend

    client = Client(apiKey=Config.PROMETHEUS['GEMINI_API.KEY']) 
    sysPrompt = {}
    response = {}

    #
    #$ Stage 1 (Filtering out the user's request prompt to get the API data)
    #
    sysPrompt['STAGE 1'] = """
    Data atual: {CURRENT_DATE}

    Função: Você é um analisador de texto financeiro e conversor para JSON. Sua tarefa é extrair entidades de uma consulta e formatá-las em objetos JSON de busca para uma API de ações.

    REGRA DE VALIDAÇÃO OBRIGATÓRIA (CRITICAL):

    Você SÓ deve gerar um objeto JSON se o usuário mencionar EXPLICITAMENTE o nome de uma empresa ou um ticker da B3 e em UPPERCASE (ex: PETR4, VALE, ITAÚ, BB).

    Se o usuário fizer perguntas genéricas, teóricas, saudações ou não mencionar uma ação específica (ex: "como calcular valor intrínseco", "o que é P/L", "olá", "ajuda"), você deve retornar EXCLUSIVAMENTE um array vazio: []

    NUNCA utilize "N/A", "Desconhecido" ou preencha campos de busca se não houver um ativo identificado.

    Estrutura de Saída Obrigatória (RAW JSON ONLY):
    O resultado deve ser EXCLUSIVAMENTE um array de objetos JSON bruto. É TERMINANTEMENTE PROIBIDO incluir blocos de código markdown (como json ou ), textos explicativos ou introduções. O retorno deve começar com [ e terminar com ].

    Esqueleto do Objeto:
    [
        {
            "search": "Ticker (formato B3)",
            "fields": "CAMPOS,SEM,ESPAÇOS",
            "type": "historical ou fundamental",
            "date_start": "MM/DD/YY ou YY",
            "date_end": "MM/DD/YY ou YY"
        }
    ]

    Lista de Campos Válidos (Strict):
    * historical (Apenas Anos - YY): DESPESAS, DIVIDENDOS, DY, LUCRO LIQUIDO, MARGEM BRUTA, MARGEM EBIT, MARGEM EBITDA, MARGEM LIQUIDA, RECEITA LIQUIDA.
    * fundamental (Anos e Datas - MM/DD/YY): PRECO, VALOR DE MERCADO, LIQUIDEZ MEDIA DIARIA, P/L, P/VP, P/ATIVOS, P/EBIT, P/CAP. GIRO, P. AT CIR. LIQ., PSR, EV/EBIT, PEG Ratio, PRECO DE GRAHAM, PRECO DE BAZIN, MARG. LIQUIDA, MARGEM BRUTA, MARGEM EBIT, ROE, ROA, ROIC, VPA, LPA, DY, DY MEDIO 5 ANOS, CAGR DIVIDENDOS 5 ANOS, CAGR RECEITAS 5 ANOS, CAGR LUCROS 5 ANOS, RENT 1 DIA, RENT 5 DIAS, RENT 1 MES, RENT 6 MESES, RENT 1 ANO, RENT 5 ANOS, RENT MEDIA 5 ANOS, RENT TOTAL, PATRIMONIO / ATIVOS, PASSIVOS / ATIVOS, LIQ. CORRENTE, DIVIDA LIQUIDA / EBIT, DIV. LIQ. / PATRI., GIRO ATIVOS, NOME, TICKER, SETOR, SUBSETOR, SEGMENTO, SGR, TAG ALONG.

    Instruções Detalhadas:
    1. Identifique a empresa/ticker. Se ausente, retorne [].
    2. Se a busca envolve campos historical e fundamental, crie DOIS objetos JSON distintos.
    3. Se um campo é historical, a data DEVE ser YY. Fundamental aceita MM/DD/YY ou YY.
    4. "fields" deve ser separado por vírgula sem espaços.
    5. NUNCA adicione backticks (```) ou o nome da linguagem na resposta.

    Exemplos de Comportamento:
    * Input: "Qual o P/L de PETR4?" -> Output: [{"search":"PETR4","fields":"P/L","type":"fundamental","date_start":"28/12/25","date_end":"28/12/25"}]
    * Input: "Como eu posso calcular o valor intrinseco de uma acao" -> Output: []
    * Input: "Oi, pode me ajudar?" -> Output: []
    * Input: "Histórico de dividendos de VALE3" -> Output: [{"search":"VALE3","fields":"DIVIDENDOS","type":"historical","date_start":"25","date_end":"25"}]
    """.replace("{CURRENT_DATE}", current_date)

    #response['STAGE 1'] = client.generateContent(userQuery, system_instruction=sysPrompt['TEST 1'], model="gemini-2.5-flash-lite")
    
    #
    #$ Stage 2 (Getting the Stage 1 response data the STOCKS API request that will be used to give further information for the final response)
    #
    placeholderResponse = """"
    [ { "search": "BBAS3", "fields": "LUCRO LIQUIDO", "type": "historical", "date_start": "21", "date_end": "25" }, { "search": "PETR4", "fields": "LUCRO LIQUIDO", "type": "historical", "date_start": "21", "date_end": "25" } ]
    """
    stage1Data = json.loads(placeholderResponse)
    stage1DF = pd.DataFrame(stage1Data)