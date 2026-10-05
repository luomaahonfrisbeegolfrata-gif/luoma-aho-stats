# V18 FINAL KAIKKI KORTIT - 44010 44763 43119 udisc saa vaylatilasto

Analysoitu Actions run 37337583432 - korjattu:
- Node.js 20 warning -> ubuntu-24.04 + actions v4 (toimii Node 24)
- ubuntu-latest migration warning -> vaihdettu ubuntu-24.04
- Puuttuva 43119 lisätty
- Kaikki kortit nyt dynaaminen + automaatio + laskenta

## Korjatut
- Väylätilasto B [8,5,9,10,6,2,4,11,7,1,3,12] Tot 78
- Metrix 44010 42-49 Par 41
- Metrix 44763 82-93 Par 82
- Metrix 43119 26-33 Par 27 (UUSI)
- UDisc top10
- Sää V16.2 live 15min
- Kierrokset 1164

## Automaatio
- vaylatilasto.yml 6h ubuntu-24.04
- metrix.yml 6h kaikki 3 rataa
- kierrokset.yml 12h
- udisc.yml 8h
- saa.yml 15min

Header/layout/kortit lukittu.
