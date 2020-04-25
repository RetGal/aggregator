# aggregator

## Funktion

Mit Hilfe von *aggregator* lassen sich von *[MAverage](https://github.com/RetGal/MAverage)*, *[holdntrade](https://github.com/RetGal/holdntrade)* oder *[BalanceR](https://github.com/RetGal/BalanceR)* Instanzen generierte CSV-Dateien zu einer gemeinsamen CSV-Datei zusammenfassen und als Tagesrapport per E-Mail versenden.
Zum Jahreswechsel wird jeweils eine neue Datei erstellt, die alte(n) werden umbenannt.

## Voraussetzungen

*aggregator* setzt *Python* Version 3 oder grösser voraus.

## Inbetriebnahme

Vor dem Start ist die Konfigurationsdatei 'aggregator.txt' mit den gewünschten Einstellungen zu ergänzen.

Der absolute Pfad zu den zu aggregierenden CSV-Dateien wird als Parameter übergeben.
Der Name der aggregierten CSV-Datei kann optional als zweiter Parameter übergeben, standardmässig wird *allbots.csv* verwendet.

Für einen täglichen Versand wird ein oder mehrere *Cronjobs* benötigt:

```
20  14   *   *   *   /home/bot/aggregator.py /home/bot/holdntrade
30  14   *   *   *   /home/bot/aggregator.py /home/bot/maverage allMAverage.csv
40  14   *   *   *   /home/bot/aggregator.py /home/bot/balancer allBalancer.csv
```

Die Datei *aggregator.py* muss vor dem ersten Start mittels `chmod +x` ausführbar gemacht werden.
