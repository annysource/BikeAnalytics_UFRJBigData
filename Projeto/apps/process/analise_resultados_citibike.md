# Análise de Exploração — CitiBike NYC 2026
### Resultados, Observações e Conclusões por Hipótese

---

## Análise 1 — Volume de Viagens Mensais e Sazonalidade

### Gráfico: Total de Viagens por Mês

O volume de viagens apresenta crescimento consistente ao longo do período analisado (Janeiro a Abril de 2026). Janeiro registra aproximadamente **1,8 milhão de viagens**, enquanto Abril alcança cerca de **3,5 milhões** — praticamente o dobro.

**Observação:**
Observa-se um aumento expressivo das corridas a partir do mês de fevereiro, com aceleração mais acentuada em março e abril. Esse padrão pode ser correlacionado diretamente com as condições climáticas da cidade: janeiro e fevereiro são os meses de inverno mais intenso em Nova York, com temperaturas médias entre **-3°C e 6°C** e ocorrência frequente de nevascas.

Em janeiro de 2026, uma tempestade de neve histórica (23–27 de janeiro) levou ao **fechamento temporário do serviço CitiBike** em 25 de janeiro, com acúmulo de neve superior a 60 cm em partes da cidade. Em fevereiro, uma blizzard histórica em 22–23 de fevereiro depositou mais de 60 cm de neve, afetando diretamente as ciclovias e a mobilidade urbana. A recuperação do volume de viagens a partir do final de fevereiro e ao longo de março coincide com a elevação gradual das temperaturas e a redução das ocorrências de neve.

**Hipótese confirmada:** existe correlação entre temperatura/clima e o volume de uso do CitiBike. O inverno severo suprime a demanda e o aquecimento progressivo da primavera a recupera.

> **Dado de suporte:** Temperatura média histórica de Nova York em janeiro: ~0°C (32°F); em abril: ~13°C (55°F). A variação de ~13°C entre os extremos do período analisado é consistente com a variação de ~2× no volume de viagens.

---

### Gráfico: % Member vs Casual por Mês

A distribuição entre **membros** (assinantes) e **casuais** (usuários avulsos) se mantém praticamente constante ao longo de todos os meses analisados, com membros representando aproximadamente **85–90%** das viagens em todos os períodos.

**Observação:**
A estabilidade dessa proporção, mesmo durante os meses de inverno severo, é um resultado relevante. Indica que **o clima frio não afasta proporcionalmente mais os usuários casuais do que os membros** — ambos os segmentos reduzem o uso na mesma proporção. Isso sugere que os membros não são necessariamente ciclistas utilitários mais resilientes ao frio do que os casuais, mas sim que o perfil de uso de ambos os grupos é igualmente sensível (ou igualmente insensível) às condições climáticas adversas.

Uma possível explicação é que o **ciclista casual de inverno** é também um usuário frequente (não turístico), pois turistas dificilmente visitam Nova York em janeiro. A fatia casual que permanece ativa no inverno tende a ser residente que usa o serviço esporadicamente — perfil próximo ao membro em termos de propósito de viagem (commuting, errands).

**Conclusão:** A proporção member/casual é uma característica estrutural do serviço, não sazonal. O volume absoluto varia com o clima, mas a composição dos usuários permanece estável.

---

*Próximas análises: duração das viagens, distância percorrida, horários de pico, estações mais movimentadas e mapa de rotas.*

---

## Análise 2 — Duração das Viagens por Tipo de Usuário e Mês

### Gráfico: Duração Média das Viagens por Mês e Tipo de Usuário (Q1–Q3)

Os dados mostram que a **duração média das viagens é consistentemente maior para usuários casuais** em todos os meses analisados. Membros registram média entre **~10 e ~11 minutos**, enquanto casuais ficam entre **~13 e ~17 minutos** — uma diferença de aproximadamente 30–60% em todos os períodos.

**Observação:**
As durações permanecem notavelmente estáveis ao longo dos quatro meses, tanto para membros quanto para casuais. Não há sazonalidade na duração: o inverno severo de janeiro e fevereiro não encurta as viagens — quem pedala no frio, pedala pelo mesmo tempo. Isso reforça a interpretação de que o clima afeta a **decisão de usar ou não** o serviço, mas não o **comportamento durante o uso**.

**Por que casuais pedalam mais tempo?**
A diferença estrutural de duração entre os grupos reflete padrões de uso distintos:

- **Membros** tendem a usar o CitiBike como meio de transporte utilitário — trajetos predefinidos, commuting, percursos otimizados. O objetivo é chegar ao destino com eficiência.
- **Casuais** incluem um perfil mais exploratório — passeios, lazer, turismo (mesmo que reduzido no inverno) e deslocamentos menos rotineiros. Sem uma rota memorizada, a viagem naturalmente dura mais.

As barras de erro (Q1–Q3) mostram dispersão maior nos casuais, especialmente em fevereiro e março, o que é consistente com essa heterogeneidade de propósito: dentro dos casuais coexistem tanto viagens curtíssimas quanto passeios longos.

**Conclusão:** A duração da viagem é uma característica do **perfil do usuário**, não do **clima ou do mês**. Casuais usam o serviço de forma mais prolongada e variada; membros são mais consistentes e objetivos nos seus trajetos.


---

## Análise 3 — Distância dos Trajetos por Tipo de Usuário e Mês

### Gráfico: Distância Média dos Trajetos por Mês e Tipo de Usuário (Q1–Q3)

As distâncias médias percorridas são muito próximas entre os dois grupos: **membros percorrem entre ~1,7 e ~2,0 km** por viagem, enquanto **casuais ficam entre ~2,0 e ~2,2 km** — uma diferença sutil de aproximadamente 0,2–0,3 km. Ambos os grupos apresentam leve tendência de crescimento de janeiro a março, mas sem variação expressiva.

**Observação:**
O mesmo padrão identificado na duração se repete na distância: **o inverno severo não reduz significativamente o trajeto percorrido**. Quem opta por usar a bicicleta no frio mantém o mesmo comportamento espacial de quem pedala no clima mais ameno — as viagens não ficam mais curtas para "sair logo do frio".

Combinando este resultado com a análise de duração, emerge uma conclusão importante: **duração e distância são coerentes entre si**. Casuais pedalam um pouco mais longe *e* por mais tempo, o que é matematicamente consistente. A velocidade média implícita em ambos os grupos é similar (~10–12 km/h), sugerindo que o estilo de pedalada não difere radicalmente — o que muda é o **quanto** cada grupo se desloca, não o **ritmo**.

**As barras de erro (Q1–Q3)** mostram dispersão semelhante à observada na duração: casuais têm maior variabilidade, confirmando que esse grupo abrange perfis mais heterogêneos de uso — de deslocamentos curtos e pontuais até trajetos mais longos e exploratórios.

**Conclusão:** Assim como a duração, a distância percorrida é uma característica do perfil do usuário, não do clima. A diferença entre membros e casuais é real mas sutil (~15%), e ambos os grupos mantêm comportamento espacial estável ao longo dos meses de inverno. O clima impacta a **frequência** de uso do serviço, não a **natureza** das viagens realizadas.


---

## Análise 4 — Distribuição de Viagens por Hora do Dia

### Gráfico: Distribuição de Viagens por Hora do Dia — Member vs Casual (Jan–Abr 2026)

Esta é a análise mais reveladora do conjunto. Os dois grupos exibem padrões temporais **completamente distintos**, e essa diferença se mantém consistente em todos os quatro meses analisados.

**Membros — perfil de commuter:**
A curva dos membros apresenta dois picos nítidos e recorrentes: **às 8h da manhã** e **às 17h (5 da tarde)** — exatamente os horários de entrada e saída do expediente de trabalho na cidade de Nova York. Entre os picos, o volume cai de forma acentuada durante o horário comercial (9h–16h) e praticamente zera a partir das 21h. Esse padrão de "M invertido" é o comportamento típico de transporte utilitário urbano, e se replica fielmente mês a mês, independentemente do clima. Em abril, os volumes absolutos são muito maiores (chegando a ~325k viagens na hora de pico), mas a **forma da curva é idêntica** à de janeiro — o que confirma que o padrão de uso do membro é estrutural.

**Casuais — perfil difuso com tendência vespertina:**
Os casuais apresentam uma distribuição significativamente mais homogênea ao longo do dia. O volume cresce gradualmente a partir das 10h da manhã, atinge um platô suave entre 12h e 18h, e declina à noite — sem o pico matutino pronunciado dos membros. Em alguns meses, especialmente março e abril, os casuais coincidem levemente com o pico vespertino (~17h), mas de forma muito menos acentuada. Esse comportamento é consistente com uso recreativo, de lazer ou errands (recados, compras) — atividades que não seguem a lógica do horário comercial.

**A evolução sazonal reforça a análise:**
Nos meses de inverno mais intenso (janeiro e fevereiro), os casuais praticamente desaparecem do gráfico — sua linha quase não sai do zero. Isso conecta diretamente com a Análise 1: os casuais são o grupo mais sensível ao clima, pois seu uso é majoritariamente opcional (lazer, passeio). Em março e abril, à medida que o clima melhora, os casuais ganham visibilidade crescente, especialmente no período vespertino.

**Conclusão:** O horário de uso é o indicador mais forte do propósito da viagem. Membros são trabalhadores urbanos que incorporaram a bicicleta à rotina de commuting; casuais são usuários oportunistas, cujo padrão temporal reflete escolha e disponibilidade, não obrigação. Essa distinção comportamental, aliada às análises de duração e distância, consolida dois perfis de usuário bem definidos: o **ciclista utilitário (membro)** e o **ciclista situacional (casual)**.


---

## Conclusão Geral

A análise exploratória dos dados do CitiBike NYC no período de janeiro a abril de 2026 revelou padrões consistentes e complementares que permitem traçar um retrato claro do serviço e de seus usuários.

O principal achado transversal é a **existência de dois perfis de usuário bem definidos**, cujos comportamentos diferem em todas as dimensões analisadas:

| Dimensão | Membro | Casual |
|---|---|---|
| Volume | ~85–90% das viagens | ~10–15% das viagens |
| Sensibilidade ao clima | Baixa — usa o serviço consistentemente | Alta — reduz drasticamente no inverno |
| Horário de uso | Picos em 8h e 17h (commuting) | Distribuição homogênea ao longo do dia |
| Duração média | ~10–11 min (estável) | ~13–17 min (maior variabilidade) |
| Distância média | ~1,7–2,0 km (estável) | ~2,0–2,2 km (levemente maior) |
| Propósito inferido | Transporte utilitário / commuting | Lazer, errands, uso situacional |

O **clima** emerge como variável que afeta a **frequência** de uso — especialmente dos casuais —, mas não a **natureza** das viagens. Independentemente do mês, quem usa o CitiBike percorre distâncias e durações similares, indicando que a decisão de pedalar ou não é influenciada pelo tempo, mas o trajeto escolhido não é.

A **sazonalidade crescente** de janeiro a abril (quase 2× no volume de viagens) é explicada pela transição do inverno severo para o início da primavera em Nova York, com temperaturas saindo de ~0°C em janeiro para ~13°C em abril. Esse crescimento é puxado especialmente pelos casuais, cuja participação relativa aumenta com a melhora do clima.

Por fim, a **estabilidade da proporção member/casual** ao longo dos meses reforça que a base de assinantes é sólida e resiliente às condições climáticas — um indicativo importante sobre a maturidade e a dependência funcional que os moradores de Nova York desenvolveram com o serviço de bike-sharing.

---



---

## Análise 5 — Estações Mais Movimentadas (Partida e Chegada)

### Gráfico: Top 10 Estações de Partida e Chegada — Janeiro 2026

A análise das estações mais movimentadas revelou um resultado à primeira vista surpreendente: **as top 10 estações de partida e de chegada são praticamente idênticas**, com os mesmos nomes e volumes semelhantes. As estações de maior fluxo incluem W 21 St & 6 Ave, Pier 61 at Chelsea Piers, Lafayette St & E 8 St, W 31 St & 7 Ave, entre outras.

**Por que isso acontece?**

Esse resultado é, na verdade, **matematicamente esperado** e está diretamente conectado ao perfil de uso identificado na Análise 4. Como a grande maioria das viagens é realizada por membros em regime de commuting diário, os trajetos são **fixos e pendulares**: a mesma estação que serve como ponto de partida pela manhã (saída de casa para o trabalho) torna-se ponto de chegada à tarde (retorno ao lar). Ao agregar os dados do mês inteiro, esse movimento de ida e volta equilibra os volumes de entrada e saída de cada estação, fazendo com que as mais populares apareçam no topo de ambos os rankings.

Trata-se de um fenômeno bem documentado em sistemas de transporte urbano: estações de alta demanda em redes de commuting tendem a apresentar **simetria de fluxo ao longo do dia** — o que Fruin (1987) denomina de "movimentos pendulares em estações de alta capacidade". O ranking único reflete, portanto, a maturidade e a rotina consolidada dos membros do CitiBike, não uma limitação da análise.

**Estações em destaque:**
- **W 21 St & 6 Ave** (Chelsea) — bairro residencial denso com forte commuting para o Midtown
- **Pier 61 at Chelsea Piers** — ponto de convergência entre lazer e commuting à beira do Hudson River
- **Lafayette St & E 8 St** (NoHo/SoHo) — área de alta densidade comercial e residencial
- **W 31 St & 7 Ave** — próxima ao Penn Station, um dos maiores hubs de transporte de NYC

**Conclusão:** O ranking idêntico entre partidas e chegadas não é um resultado insatisfatório — é uma **confirmação quantitativa** do perfil pendular dos membros descrito na Análise 4. As estações mais movimentadas são os nós da rede de commuting ciclístico de Nova York, e seu equilíbrio de fluxo reflete a regularidade e previsibilidade do uso diário do serviço.


---

## Conclusão Geral

A análise exploratória dos dados do CitiBike NYC no período de janeiro a abril de 2026 revelou padrões consistentes e complementares que permitem traçar um retrato claro do serviço e de seus usuários.

O principal achado transversal é a **existência de dois perfis de usuário bem definidos**, cujos comportamentos diferem em todas as dimensões analisadas:

| Dimensão | Membro | Casual |
|---|---|---|
| Volume | ~85–90% das viagens | ~10–15% das viagens |
| Sensibilidade ao clima | Baixa — usa o serviço consistentemente | Alta — reduz drasticamente no inverno |
| Horário de uso | Picos em 8h e 17h (commuting) | Distribuição homogênea ao longo do dia |
| Duração média | ~10–11 min (estável) | ~13–17 min (maior variabilidade) |
| Distância média | ~1,7–2,0 km (estável) | ~2,0–2,2 km (levemente maior) |
| Rotas dominantes | Curtas, fixas, pendulares (<1 km) | Mais longas, exploratórias, sazonais |
| Propósito inferido | Transporte utilitário / commuting | Lazer, errands, uso situacional |

O **clima** emerge como variável que afeta a **frequência** de uso — especialmente dos casuais —, mas não a **natureza** das viagens. Independentemente do mês, quem usa o CitiBike percorre distâncias e durações similares, indicando que a decisão de pedalar ou não é influenciada pelo tempo, mas o trajeto escolhido não é. Essa conclusão é reforçada pela análise de rotas: as top 10 rotas mais populares são as **mesmas em todos os meses**, com distâncias inferiores a 1 km, e mantêm sua posição no ranking mesmo durante as nevascas de janeiro e fevereiro.

A **sazonalidade crescente** de janeiro a abril (quase 2× no volume total de viagens) é explicada pela transição do inverno severo para o início da primavera em Nova York. Esse crescimento é puxado especialmente pelos casuais, cuja participação relativa aumenta com a melhora do clima — evidenciada pela queda do % member médio nas top 300 rotas de 94,3% (janeiro) para 85,2% (abril), e pelo aumento de 58% na duração média das rotas no mesmo período.

A **estabilidade da proporção member/casual** ao longo dos meses e a consistência das rotas dominantes reforçam que a base de assinantes é sólida e resiliente às condições climáticas. O CitiBike consolidou-se como infraestrutura de transporte urbano cotidiano para uma parcela significativa dos moradores de Nova York — não como serviço de lazer, mas como alternativa real ao metrô e ao ônibus para trajetos de última milha.

Em síntese: **o núcleo duro do uso do CitiBike é estrutural e imune ao clima; a camada recreativa e casual é sazonal.** Toda a evidência coletada — volume, duração, distância, horário, rotas — aponta para a mesma direção e se reforça mutuamente, conferindo robustez às conclusões desta análise exploratória.
