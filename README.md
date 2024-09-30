# Tarefa 2

## Introdução

O jogo é um simulador de ecossistema, onde seres vivos são agentes independentes que analisam o ambiente e a si mesmos, e decidem o que fazer. O jogador não controla os agentes diretamente, ele pode apenas criar novos agentes, e observar suas interações. O objetivo é criar um ecossistema em equilíbrio, em que não acontece uma extinção mesmo o jogador não criando mais agentes manualmente. O ponto é o jogador perceber como um equilíbrio é complicado, e pequenas mudanças podem causar consequências horriveis num ecossistema (ex. adição de uma espécie).

O jogo se passa em um mapa retangular, cada agente é um sprite no mapa, e pode se mover pelo mapa, e interagir com outros agentes que estejam próximos dele. O jogador clica com o mouse para criar agentes, e pode usar as setas para mudar a velocidade da simulação.

## Agentes estratégicos e equilíbrios

De acordo com a aula de agentes estratégicos, foi interessante explorar agentes terem consciência da existência dos outros agentes. Previamente, carnívoros já perseguiam e comiam herbívoros, mas estes simplesmente ignoravam a existência dos carnívoros. Nessa entrega, os herbívoros sabem da existência de carnívoros e atacam os carnívoros de volta quando atacados. Dessa forma, fica mais dificil para um carnívoro atacar um grupo de herbívoros próximos, o que faz estas "comunidades" ficarem mais fortes, uma interação interessante.

Como o jogo é sobre atingir um equilíbrio, também adicionei um gráfico que mostra a porcentagem de plantas, herbívoros e carnívoros. Além disso, o gráfico mostra (com linhas verticais) todos os momentos que o jogador artificialmente adicionou algum agente ao mapa. Isso permite ao jogador analisar como suas mudanças afetam o equilíbrio do ecossistema.

Além disso, outras mudanças foram feitas. Além de balanceamentos entre a força, velocidade e outros parâmetros dos agentes, agora herbívoros e carnívoros podem se reproduzir, e além disso quando um animal morre e decompõe, tem a chance de uma planta surgir em seu lugar, fazendo a ecologia ser realmente um ciclo onde cada ser depende do outro.

## Como jogar
Para rodar, se já tiver Python e Python Arcade instalado, basta rodar:
- `python src/ep1/main.py`

Para instalar Python Arcade, faça:
- `pip install arcade`

Ou, se já você utilizar `pipenv` e não quiser instalar Python Arcade globalmente, faça:
- `pipenv install`

O programa foi verificado usando Python 3.11.9 no Windows (versões mais novas não são compatíveis com Python arcade no Windows, mas no Linux deve funcionar).