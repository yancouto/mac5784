# Tarefa 4

## Introdução

O jogo é um simulador de ecossistema, onde seres vivos são agentes independentes que analisam o ambiente e a si mesmos, e decidem o que fazer. O jogador não controla os agentes diretamente, ele pode apenas criar novos agentes, e observar suas interações. O objetivo é criar um ecossistema em equilíbrio, em que não acontece uma extinção mesmo o jogador não criando mais agentes manualmente. O ponto é o jogador perceber como um equilíbrio é complicado, e pequenas mudanças podem causar consequências horriveis num ecossistema (ex. adição de uma espécie).

O jogo se passa em um mapa retangular, cada agente é um sprite no mapa, e pode se mover pelo mapa, e interagir com outros agentes que estejam próximos dele. O jogador clica com o mouse para criar agentes, e pode usar as setas para mudar a velocidade da simulação.

## Entrega final

Como exemplo de comportamento de agente com escala de valores adicionado, Herbívoros param de comer plantas se elas estão próximas de morrer e eles não estão morrendo de fome, pois isso, apesar de dificultar sua vida em curto termo, prolonga em longo já que evita a redução do número de plantas, que pode causar a extinção dos herbívoros.

Foi implementada a modificação de paramêtros: Jogadores podem modificar parâmentros como o dano de ataque de carnívoros, fome dos herbívoros, e muitos outros parâmetros. Isso dá muito mais agência ao jogador em como criar seu equilíbrio, enquanto antes ele podia apenas criar ou remover agentes.

Também foi implementada a mecânica de idade, em que animais velhos morrem.

## Como jogar
Para rodar, se já tiver Python e Python Arcade instalado, basta rodar:
- `python src/main.py`

Para instalar Python Arcade, faça:
- `pip install arcade`

Ou, se já você utilizar `pipenv` e não quiser instalar Python Arcade globalmente, faça:
- `pipenv install`

O programa foi verificado usando Python 3.11.9 no Windows (versões mais novas não são compatíveis com Python arcade no Windows, mas no Linux deve funcionar).