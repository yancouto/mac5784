# Tarefa 1

## Introdução

O jogo é um simulador de ecossistema, onde seres vivos são agentes independentes que analisam o ambiente e a si mesmos, e decidem o que fazer. O jogador não controla os agentes diretamente, ele pode apenas criar novos agentes, e observar suas interações. O objetivo é criar um ecossistema em equilíbrio, em que não acontece uma extinção mesmo o jogador não criando mais agentes manualmente. O ponto é o jogador perceber como um equilíbrio é complicado, e pequenas mudanças podem causar consequências horriveis num ecossistema (ex. adição de uma espécie).

O jogo se passa em um mapa retangular, cada agente é um sprite no mapa, e pode se mover pelo mapa, e interagir com outros agentes que estejam próximos dele. O jogador clica com o mouse para criar agentes, e pode usar as setas para mudar a velocidade da simulação.

## Agentes
Cada tipo de agente é implementado como uma máquina de estados, o estado atual representa o que o agente "está fazendo" (ex. comendo), e há uma mudança de estado quando ao analisar o ambiente o agente decide fazer outra coisa (ex. se a comida acabar, buscar mais, ou se estiver saciado, parar de comer).

Em comum, todos agentes tem uma quantidade de vida (0-100), e quando essa vida chega a 0, o agente morre, e desaparece.

Temos 4 tipos de agentes:

### Planta (Grass)
Essa é uma "planta" genérica. Ela apenas fica parada, e sua vida se regenera automaticamente, simulando que ela está fazendo fotossíntese e o sol é abundante.

### Herbívoro (Herbivore)
Um herbivoro, que come plantas. Ele tem uma fome que cresce com o tempo, diminui se ele come, e causa dano a ele se está muito grande. Sua vida se regenera se ele está alimentado, mas vagarosamente.

Quando tem pouca fome, ele anda pelo mapa aleatoriamente, e pode se reproduzir, criando uma cópia de si mesmo: não é necessário interação com outros agentes, estamos considerando que cada agente "Herbívoro" é na verdade uma pequena "tribo" de animais.

Quando ele tem muita fome, ele busca uma Planta próxima e anda em direção a ela, e começa a comê-la, tirando vida da planta e diminuindo sua fome.

### Carnívoro (Carnivore)
Um carnívoro, que come outros animais. Tem fome que funciona como no Herbívoro.

O Carnívoro funciona de forma similar ao Herbívoro, mas não se reproduz, e só pode se alimentar de carcaças. Quando tem fome, busca um herbívoro próximo e tenta o ataca, tentando matá-lo. Se algum animal morre, seja por ataque ou por fome, ele vira uma Carcaça.

### Carcaça (Carcass)
Corpo de um animal morto. Sua vida diminui com o tempo, ou ainda mais rápido se um carnívoro está se alimentando dele.

## Conclusão e Futuro
O jogo já está bem funcional, e é um divertido playground para testar agentes. Porém, ainda é fácil conseguir um equilibrio colocando apenas plantas, e dificil colocando os outros agentes. Ainda falta isso virar um "ciclo", onde as plantas dependem dos carnívoros (ou herbívoros), isso será implementado em uma tarefa futura. Talvez as plantas se alimentem de carcaças, ou de alguma forma dependam das mortes dos animais para viver, de forma que se houverem apenas plantas, elas acabam morrendo. Mas ainda não é claro como fazer isso, e como deixar claro pro jogador.

Reprodução é um tópico complicado, pode se tornar muito complicado e eu não quero deixar o jogo super complicado. Atualmente, apenas herbívoros se reproduzem. Carnívoros não se reproduzem por que o mapa é pequeno e é muito raro eles morrerem de fome, então adicionando reprodução no jogo como está, eles provavelmente acabariam matando todos os herbívoros sempre. Pode ser bom implementar reprodução para carnívoros e plantas no futuro também, mas tem que ser feito com cuidado.

E as possibilidades são bem grandes, é fácil adicionar mais tipos de agentes, tipos diferentes de herbívoros/carnívoros, onívoros, outras espécies, ou deixar o comportamento das atuais mais complexos (sede, sexo, tribos, etc etc). Mas não quero adicionar mais agentes ou comportamentos só por que é possível, quero adicionar apenas se estes explorarem novas técnicas de IA relacionadas à disciplina.

## Como jogar
Para rodar, se já tiver Python e Python Arcade instalado, basta rodar:
- `python src/ep1/main.py`

Para instalar Python Arcade, faça:
- `pip install arcade`

Ou, se já você utilizar `pipenv` e não quiser instalar Python Arcade globalmente, faça:
- `pipenv install`

O programa foi verificado usando Python 3.11.9 no Windows (versões mais novas não são compatíveis com Python arcade no Windows, mas no Linux deve funcionar).