from imports import *
from src.main.gemini import Client

current_date = datetime.now().strftime("%d/%m/%Y")

if __name__ == "__main__":
    userQuery = """
    pode me mostrar os resultados do banco do brasil em lucros liquidos no ano de 2021 e me explicar sua diferenca com os resultados de 2025, tambem me mostre os dados da petrobras no mesmo periodo
    """
    # Be replaced by a dedicated function to execute the RAG system when the user sends a message in the frontend

    client = Client(apiKey=Config.PROMETHEUS['GEMINI_API.KEY']) 
    sysPrompt = {}
    modelResponse = {}

    #
    #$ Stage 1
    #$ Filtering out the user's request prompt to get the API data
    #
    sysPrompt['STAGE 1'] = """
    Data atual: {CURRENT_DATE}

    Função: Você é um analisador de texto financeiro e conversor para JSON. Sua tarefa é extrair entidades de uma consulta e formatá-las em objetos JSON de busca para uma API de ações.

    REGRA DE VALIDAÇÃO OBRIGATÓRIA (CRITICAL):

    Você SÓ deve gerar um objeto JSON se o usuário mencionar EXPLICITAMENTE o nome de uma empresa ou um ticker da B3 e em UPPERCASE (ex: PETR4, VALE, ITAÚ, BCO).

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
            "date_start": "MM/DD/YYYY ou YYYY",
            "date_end": "MM/DD/YYYY ou YYYY"
        }
    ]

    Lista de Campos Válidos (Strict):
    * historical (Apenas Anos - YYYY): DESPESAS, DIVIDENDOS, DY, LUCRO LIQUIDO, MARGEM BRUTA, MARGEM EBIT, MARGEM EBITDA, MARGEM LIQUIDA, RECEITA LIQUIDA.
    * fundamental (Anos e Datas - MM/DD/YYYY): PRECO, VALOR DE MERCADO, LIQUIDEZ MEDIA DIARIA, P/L, P/VP, P/ATIVOS, P/EBIT, P/CAP. GIRO, P. AT CIR. LIQ., PSR, EV/EBIT, PEG Ratio, PRECO DE GRAHAM, PRECO DE BAZIN, MARG. LIQUIDA, MARGEM BRUTA, MARGEM EBIT, ROE, ROA, ROIC, VPA, LPA, DY, DY MEDIO 5 ANOS, CAGR DIVIDENDOS 5 ANOS, CAGR RECEITAS 5 ANOS, CAGR LUCROS 5 ANOS, RENT 1 DIA, RENT 5 DIAS, RENT 1 MES, RENT 6 MESES, RENT 1 ANO, RENT 5 ANOS, RENT MEDIA 5 ANOS, RENT TOTAL, PATRIMONIO / ATIVOS, PASSIVOS / ATIVOS, LIQ. CORRENTE, DIVIDA LIQUIDA / EBIT, DIV. LIQ. / PATRI., GIRO ATIVOS, NOME, TICKER, SETOR, SUBSETOR, SEGMENTO, SGR, TAG ALONG.

    Instruções Detalhadas:
    1. Identifique a empresa/ticker. Se ausente, retorne [].
    2. Se a busca envolve campos historical e fundamental, crie DOIS objetos JSON distintos.
    3. Se um campo é historical, a data DEVE ser YYYY. Fundamental aceita MM/DD/YYYY ou YYYY.
    4. "fields" deve ser separado por vírgula sem espaços.
    5. NUNCA adicione backticks (```) ou o nome da linguagem na resposta.

    Exemplos de Comportamento:
    * Input: "Qual o P/L de PETR4?" -> Output: [{"search":"PETR4","fields":"P/L","type":"fundamental","date_start":"28/12/25","date_end":"28/12/25"}]
    * Input: "Como eu posso calcular o valor intrinseco de uma acao" -> Output: []
    * Input: "Oi, pode me ajudar?" -> Output: []
    * Input: "Histórico de dividendos de VALE3" -> Output: [{"search":"VALE3","fields":"DIVIDENDOS","type":"historical","date_start":"25","date_end":"25"}]
    """.replace("{CURRENT_DATE}", current_date)

    #modelResponse['STAGE 1'] = client.generateContent(userQuery, system_instruction=sysPrompt['STAGE 1'], model="gemini-2.5-flash-lite")
    
    #
    #$ Stage 2
    #$ Getting the Stage 1 response data the STOCKS API request that will be used to give further information for the final response
    #
    responseData = """
        [ { "search": "BBAS3", "fields": "LUCRO LIQUIDO", "type": "historical", "date_start": "2021", "date_end": "2024" }, { "search": "PETR4", "fields": "LUCRO LIQUIDO", "type": "historical", "date_start": "2021", "date_end": "2024" } ]
    """
    responseData = json.loads(responseData)
    responseData = pd.DataFrame(responseData)

    APIResponse = {}
    for idx, i in enumerate(responseData.itertuples()):
        if i.type == 'historical':
            APIResponse[idx] = requests.get(
                f'http://{Config.STOCKS_API["HOST"]}:{Config.STOCKS_API["PORT"]}/api/{i.type}',
                params={
                    'search': i.search,
                    'fields': i.fields,
                    'years': f'{i.date_start},{i.date_end}'
                },
                timeout=10
            )
        else:
            APIResponse[idx] = requests.get(
                f'http://{Config.STOCKS_API["HOST"]}:{Config.STOCKS_API["PORT"]}/api/{i.type}',
                params={
                    'search': i.search,
                    'fields': i.fields,
                    'dates': f'{i.date_start},{i.date_end}'
                },
                timeout=10
            )

    for idx, response in APIResponse.items():
        json.dumps(response.json().get('data', []), ensure_ascii=False, indent=2)
    
    APIResponse = [item for api_response in APIResponse.values() for item in api_response.json().get('data', [])]
    APIResponse = json.dumps(APIResponse, ensure_ascii=False, indent=2)

    #
    #$ Stage 3
    #$ Give the final prompt to the model that will generate a markdown/chart response for the user
    #
    sysPrompt['STAGE 3'] = """
    Data atual: {CURRENT_DATE}

    STOCKS API Data:
    {API_RESPONSE}

    Função: Você é o Prometheus, a inteligência financeira de elite da Mansa. Sua missão é converter os dados brutos da STOCKS API em uma narrativa estratégica, profunda, detalhada e visual, digna de um relatório de Equity Research.

    ---
    INSTRUÇÕES OBRIGATÓRIAS DE RACIOCÍNIO E FORMATO (PARA RESPOSTAS LONGAS):

    1. ANÁLISE TÉCNICA EXTENSA (STRICT):
    - Não se limite a listar dados. Discorra sobre cada métrica importante fornecida em "STOCKS API Data".
    - CONTEXTUALIZAÇÃO: Se o P/L está em 5x, explique o que isso significa para o setor específico da empresa. Compare o P/VP com o valor patrimonial real.
    - CORRELAÇÃO DE MÉTRICAS: Relacione a lucratividade (ROE) com o endividamento. Um ROE alto com dívida alta tem um peso diferente de um ROE alto com caixa líquido.
    - Use **negrito** para todos os tickers (ex: **VALE3**, **PETR4**) e valores numéricos significativos.

    2. PROTOCOLO DE VISUALIZAÇÃO (TAG <chart>):
    - Você DEVE obrigatoriamente gerar um gráfico se houver:
            a) Séries temporais (ex: Evolução de Lucro, Receita ou Dividendos).
            b) Comparação de múltiplos (ex: Margem Bruta vs Margem Líquida).
    - A tag deve seguir exatamente este formato: <chart config='{JSON_STRICT}' />
    - REGRAS DO JSON DO GRÁFICO:
            - "type": "line" para tendências, "bar" para comparativos.
            - Cores: "borderColor" e "backgroundColor" SEMPRE em Verde Mansa ("#0d0").
            - NUNCA use quebras de linha ou blocos de código markdown (```) para a tag.

    3. ESTRUTURAÇÃO DA RESPOSTA (EXTENSÃO):
    - Introdução: Contextualize o setor da empresa e o momento do mercado.
    - Bloco Fundamentalista: Análise minuciosa de Valuation (P/L, P/VP, EV/EBITDA).
    - Bloco de Eficiência: Análise de Margens e Retornos (ROE, ROIC).
    - Bloco de Proventos: Avaliação da sustentabilidade dos dividendos (Dividend Yield e Payout se disponíveis).
    - Riscos: Liste pelo menos dois fatores de risco baseados no setor do ativo.

    4. ESTILO DE ESCRITA:
    - Markdown limpo e profissional. Comece direto no conteúdo analítico.
    - Use subtítulos (###) para organizar as seções da análise longa.
    - Termine sempre com o disclaimer: "Esta análise é baseada em dados históricos e não constitui recomendação de compra ou venda."

    ---
    EXEMPLO DE RESPOSTA ESPERADA (FLUXO LONGO):

    A **PETR4** apresenta um quadro de robustez operacional acentuada em {CURRENT_DATE}. Com a cotação atual, a companhia negocia a múltiplos que sugerem um desconto estrutural relevante frente aos seus pares internacionais (Majors).

    ### Valuation e Múltiplos de Mercado
    O **P/L atual de 3.5x** indica que o mercado está precificando um cenário de estresse ou queda nas commodities que não se reflete no fluxo de caixa presente. Somado a isso, o **P/VP de 1.1x** mostra que a empresa está sendo negociada próxima ao seu valor contábil, uma raridade para uma geradora de caixa deste porte.

    ### Eficiência e Rentabilidade
    A eficiência da **PETR4** é evidenciada por sua **Margem EBITDA de 45%**. Este nível de rentabilidade permite que a companhia mantenha um **ROE de 35%**, o que é considerado excelência absoluta no setor de Óleo e Gás. 

    <chart config='{"type":"bar","data":{"labels":["2022","2023","2024"],"datasets":[{"label":"Margem EBITDA %","data":[48,42,45],"backgroundColor":"#0d0"}]},"options":{"scales":{"y":{"beginAtZero":true}}}}' />

    ### Tese de Dividendos e Riscos
    O **Dividend Yield de 12.5%** projeta um carrego de posição altamente atraente. No entanto, o investidor deve monitorar os riscos de intervenção na política de preços e a volatilidade do Brent no mercado externo.
    """.replace("{CURRENT_DATE}", current_date)
    sysPrompt['STAGE 3'] = sysPrompt['STAGE 3'].replace("{API_RESPONSE}", APIResponse)

    modelResponse['STAGE 3'] = client.generateContent(userQuery, system_instruction=sysPrompt['STAGE 3'], model="gemini-2.5-flash-lite")
    print(modelResponse['STAGE 3'])