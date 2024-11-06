# Tarefa 3

## Introdução

O jogo é um simulador de ecossistema, onde seres vivos são agentes independentes que analisam o ambiente e a si mesmos, e decidem o que fazer. O jogador não controla os agentes diretamente, ele pode apenas criar novos agentes, e observar suas interações. O objetivo é criar um ecossistema em equilíbrio, em que não acontece uma extinção mesmo o jogador não criando mais agentes manualmente. O ponto é o jogador perceber como um equilíbrio é complicado, e pequenas mudanças podem causar consequências horriveis num ecossistema (ex. adição de uma espécie).

O jogo se passa em um mapa retangular, cada agente é um sprite no mapa, e pode se mover pelo mapa, e interagir com outros agentes que estejam próximos dele. O jogador clica com o mouse para criar agentes, e pode usar as setas para mudar a velocidade da simulação.

## Agentes sociais e pontuação

Nessa entregas, explorei tanto interações sociais, quanto uma gamificação maior do jogo.

Para interações sociais, foram adicionadas mecânicas de inteligência de grupo, onde ações locais podem causar um comportamento mais inteligente quando se olha um conjunto grande de indivíduos. Os herbívoros agora formam grupos e manadas ao se locomover, isso é feito adicionando forças entre herbivoros próximos, onde eles tentam ficar à uma distância ideal um do outro. Isso naturalmente faz grupos se formarem, sem ser necessário manualmente tratar isso no código, e os ajuda se proteger dos carnívoros, já que um carnívoro atacando um grupo grande tem mais chance de morrer.

Para carnívoros, o comportamento oposto foi adicionado, onde os carnívoros se repelem, o que naturalmente simula animais territorialistas e faz cada um dominar uma "área", o que garante que eles tenham a comida da região pra si mesmos.

Além disso, foi implementado uma pontuação que diz quão bem o jogador está indo. O jogador é penalizado ao modificar o ambiente, ou quando alguma extinção ocorre, o que torna o jogo mais divertido, e mais claro o objetivo de conseguir um equilíbrio sem influência externa.

Por fim, várias mudanças de gameplay e interface foram implementadas:
- Com o botão direito do mouse agora é possível excluir agentes, facilitando o encontro de um equilíbrio.
- Uma lista dos últimos acontecimentos agora aparece na direita, falando quando o jogador criou algum agente, ou quando alguma extinção ocorreu.
- Barras de vida e fome não aparecem mais por padrão, que deixa o visual mais limpo, mas ainda podem ser vistas apertando TAB.

## Como jogar
Para rodar, se já tiver Python e Python Arcade instalado, basta rodar:
- `python src/main.py`

Para instalar Python Arcade, faça:
- `pip install arcade`

Ou, se já você utilizar `pipenv` e não quiser instalar Python Arcade globalmente, faça:
- `pipenv install`

O programa foi verificado usando Python 3.11.9 no Windows (versões mais novas não são compatíveis com Python arcade no Windows, mas no Linux deve funcionar).