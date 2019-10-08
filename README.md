# aggregator

## Funktion

Mit Hilfe von *aggregator* lassen sich von *[MAverage](https://github.com/RetGal/MAverage)* oder *[holdntrade](https://github.com/RetGal/holdntrade)* Instanzen generierte CSV-Dateien zu einer gemeinsamen CSV-Datei zusammenfassen und als Tagesrapport per E-Mail versenden.

## Voraussetzungen

*aggregator* setzt *Python* Version 3 oder grösser voraus.

## Inbetriebnahme

Vor dem Start ist die Konfigurationsdatei 'aggregator.txt' mit den gewünschten Einstellungen zu ergänzen.

Der absolute Pfad zu den zu aggregierenden CSV-Dateien wird als Parameter übergeben.

Für einen täglichen Versand wird ein oder mehrere *Cronjobs* benötigt:

```
20  14   *   *   *   /home/bot/aggregator.py /home/bot/holdntrade
30  14   *   *   *   /home/bot/aggregator.py /home/bot/maverage
```

Die Datei *aggregator.py* muss vor dem ersten Start mittels `chmod +x` ausführbar gemacht werden.
