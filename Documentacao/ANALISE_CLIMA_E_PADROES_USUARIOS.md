#  Análise: Impacto do Clima e Padrões de Uso — BikeAnalytics

## Resumo Executivo

Este documento mapeia as **análises já implementadas** no projeto, identifica os **gaps de dados** em relação ao clima, e propõe uma **estratégia de pesquisa** para as questões levantadas sobre:
- Impacto do clima no uso
- Tempo médio de viagens e influência climática
- Mudanças de trajetos por clima e tipo de usuário
- Horários de pico e padrões de utilização

---

##  Análises EXISTENTES no Projeto

# 1. Sazonalidade e Volume de Viagens (Temperatura Indireta)

**Arquivo:** `analise_resultados_citibike.md` (Análise 1)

**O que foi feito:**
- Análise de volume de viagens de Janeiro a Abril 2026
- Crescimento observado: ~1,8 mi viagens (jan) → ~3,5 mi viagens (abr) — **dobro**
- Correlação indireta com clima: inverno severo (jan-fev) vs. primavera (mar-abr)

**Evidências climáticas encontradas:**
- **Jan 23–27:** Tempestade de neve histórica (~60 cm) → fechamento do serviço em 25 de janeiro
- **Fev 22–23:** Blizzard histórica (~60 cm) → redução severa de viagens
- **Mar-Abr:** Aquecimento gradual → recuperação crescente de uso

**Conclusão:** Clima frio/neve suprime demanda; aquecimento restaura uso.

---

###  2. Duração de Viagens por Tipo de Usuário

**Arquivo:** `analise_resultados_citibike.md` (Análise 2), `analyze_citibike.py`

**O que foi feito:**
- Duração média por tipo de usuário (member vs. casual)
- **Membros:** ~10–11 minutos (utilitário, commute)
- **Casuais:** ~13–17 minutos (recreativo, exploratório)
- Diferença: **30–60% mais tempo para casuais**

**Descoberta importante:**
- Duração **NÃO VARIA** com clima/mês
- Quem pedala no frio, pedala pelo mesmo tempo
- Conclusão: clima afeta **frequência** de uso, não **comportamento** durante a viagem


---

###  3. Distância de Trajetos por Tipo de Usuário

**Arquivo:** `analise_resultados_citibike.md` (Análise 3), `analyze_citibike.py`

**O que foi feito:**
- Distância média por tipo de usuário
- **Membros:** ~1,7–2,0 km (trajetos objetivos)
- **Casuais:** ~2,0–2,2 km (trajetos exploratórios)
- Diferença sutil: **~15%**

**Descoberta importante:**
- Distância **NÃO VARIA** significativamente com mês/clima
- Velocidade média implícita (~10–12 km/h) é similar em ambos grupos
- Quem sai no frio, faz o mesmo tipo de trajeto


---

###  4. Horários de Pico por Tipo de Usuário

**Arquivo:** `analise_resultados_citibike.md` (Análise 4), `analyze_citibike.py`, `explore_data_citibike.ipynb`

**O que foi feito:**
- Pipeline completo de ponta a ponta
- Ingestão histórica + tempo real
- Armazenamento distribuído (HDFS)
- Processamento Spark com 7 análises
- Dashboard interativo com Streamlit
- Dados de 3,8M+ viagens reais
- Infraestrutura containerizada (Docker)
- Código versionado no GitHub


---

## ❌ GAPS IDENTIFICADOS — Dados Não Disponíveis

### 1. **Falta de Dados Climáticos Diretos**

O dataset do CitiBike **NÃO contém** colunas como:
- Temperatura
- Precipitação (chuva, neve)
- Umidade
- Velocidade do vento
- Condição geral do dia (ensolarado, nublado, chuvoso)

**Impacto:** Impossível fazer correlação direta de um valor de temperatura com uma viagem específica.

**Possível solução:**
- Integrar dados de API de clima externa (OpenWeatherMap, NOAA)
- Usar timestamps das viagens para buscar clima no histórico (retroativamente)


---

### 2. **Falta de Informação sobre Condição Pessoal do Ciclista**

O dataset **NÃO contém**:
- Idade / faixa etária
- Gênero
- Experiência (novo vs. veterano)
- Motivo declarado da viagem

**Impacto:** Impossível saber se casuais jovens vs. idosos reagem diferente ao frio.

**Possível solução:**
- Análise de comportamento de rota (inferir padrão)
- Nenhuma solução de dados diretos

---
### 3. **Aumentar quantidade de dados analisados para avaliar por Ano**
Pegamos de um ano apenas, para que o device que utilizamos desse conta de rodar. 
Subir na nuvem para dar maior escalabilidade dos dados


##  O Que PODE SER Explorado com Dados Existentes

### A. **Padrão Temporal Semanal (Já Parcialmente Feito)**

 Implementar análise de **dia da semana**:
- Segunda a sexta (work days) vs. sábado-domingo (weekends)
- Como cambiam padrões de membros vs. casuais
- Picos diferentes em fins de semana?

**Local sugerido:** `analyze_citibike.py` — adicionar coluna `dayofweek`

---

### B. **Diferenças por Tipo de Bicicleta**

 Dataset contém coluna: `rideable_type` (classic vs. electric)

 Análise proposta:
- Eletric bikes são mais usadas em dias frios? (menos esforço)
- Casuais preferem electric? (mais confortável para passeio)
- Diferença de distância por tipo de bike?

**Não foi feito ainda** — seria adicção valiosa

---

##  Recomendações para Próximos Passos

1. *Deploy em cluster ou nuvem (GCP/AWS)*
2. *Spark Streaming para análise em tempo real*
3. *ML: previsão de demanda por estação*
4. *Spark SQL + BI tools (Metabase/Superset)*
5. *Expandir para outros sistemas GBFS*
6. *Alertas automáticos (estações críticas)*
7. *API REST para consumo externo*
8. *Testes de carga com volumes maiores*



---

## 🎓 Conclusão

O projeto **já tem análises sólidas** sobre sazonalidade, duração, distância e padrões horários. A próxima evolução natural é:

1. **Explorar variações dia da semana + hora** (estrutura de dados já permite)
2. **Incorporar dados climáticos externos** (requer nova fonte de dados)
3. **Analisar tipo de bicicleta e sua relação com clima** (dados já existem, análise falta)

Ao fazer isso, você terá uma compreensão muito mais rica de **como o clima, a hora, o tipo de usuário e o tipo de bicicleta interagem** para criar o padrão observado de uso.
