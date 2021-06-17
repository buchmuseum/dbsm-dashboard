#GND aus Gesamtdaten schneiden
pica filter -s "002@.0 =^ 'T' && \!008@.a? && 007K.a == 'gnd'" DNB_GND_titel-2021-06.dat -o gnd-2021-06.dat

#DBMS Gesamtbestand
7109 beginnt mit DBSM oder 0600 == yy

pica filter -s "(209A/01.f? && 209A/01.f =^ 'DBSM') || 017A.a == 'yy'" DNB_titel_exemplare-2021-06.dat -o dbsm-titel-exemplare-2021-06.dat

#Verteilung der Satzarten
pica frequency "002@.0" dbsm-titel-exemplare-2021-06.dat -o verteilung.csv



#zeitliche Einordnung

011@    1100, zeitliche Einordnung
003@.0  IDN

alle Satzarten außer Alxo

pica filter "002@.0 != 'Alxo'" dbsm-titel-exemplare-2021-06.dat | pica select "003@.0, 011@.a" -H "idn,year" -o zeit.csv
pica filter "002@.0 != 'Alxo'" dbsm-titel-exemplare-2021-06.dat | pica frequency "011@.a" -o zeit_frequency.csv

#Geschäftsrundschreiben
IDN 103243757X
245Y/01 9103243757XhDBSM.StSlgaArchiv/Boe-GRjSammlung der Geschäftsrundschreiben der Börsenvereinsbibliotheksdbsm-stsl-arch.boe0.gr00l1

044P 912270169217Tg1VgikAgnd01227016921aBerum

pica filter "245Y/01.9 == '103243757X'" dbsm-titel-exemplare-2021-06.dat | pica select "003@.0, 011@.a, 044P{7 =^ 'Tg',9,a}" -H "idn, year, ort_idn, ort_name" -o rundschreiben.csv