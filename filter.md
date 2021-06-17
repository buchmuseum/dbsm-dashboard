#GND aus Gesamtdaten schneiden
pica filter -s "002@.0 =^ 'T' && \!008@.a? && 007K.a == 'gnd'" DNB_GND_titel-2021-06.dat -o gnd-2021-06.dat

#DBMS Gesamtbestand
7109 beginnt mit DBSM oder 0600 == yy

pica filter -s "(209A/01.f? && 209A/01.f =^ 'DBSM') || 017A.a == 'yy'" DNB_titel_exemplare-2021-06.dat -o dbsm-titel-exemplare-2021-06.dat

#Verteilung der Satzarten
pica frequency "002@.0" dbsm-titel-exemplare-2021-06.dat -o verteilung.csv



zeitliche Einordnung

011@    1100, zeitliche Einordnung
003@.0  IDN

alle Satzarten außer Alxo

pica filter "002@.0 != 'Alxo'" dbsm-titel-exemplare-2021-06.dat | pica select "003@.0, 011@.a" -H "idn,year" -o zeit.csv
pica filter "002@.0 != 'Alxo'" dbsm-titel-exemplare-2021-06.dat | pica frequency "011@.a" -o zeit_frequency.csv

pica filter "002@.0 != 'Alxo'" dbsm-titel-exemplare-2021-06.dat | pica select ""