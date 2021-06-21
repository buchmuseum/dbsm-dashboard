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

#Objektgattungen
044P bObjektgattung
044P 90400908097Ts1VsazAgnd04009080-2aBuntpapier

pica filter "002@.0 != 'Alxo' && 044P.7 =^ 'Ts'" dbsm-titel-exemplare-2021-06.dat | pica frequency "044P.a" -o objektgattung.csv

pica filter "002@.0 != 'Alxo' && 044P.7 =^ 'Ts'" dbsm-titel-exemplare-2021-06.dat | pica select "003@.0, 044P{b?,b}, 044P{7 =^ 'Ts',a}" -H "idn,verknuepfungstyp,gattung" -o objektgattung.csv

#neueste datensätze
001A

pica select "003@.0, 001A.0, 021A{a,h}" dbsm-titel-exemplare-2021-06.dat -H "idn, erfassungsdatum, titel, person" -o erfassung.csv

#GND-Verknüpfungen

029F 99537793357Tb1Agnd05280008-8aSteirischer HeimatbundbFührungsamtn1BHerausgebendes Organ4isb

pica select "003@.0, 013D{A == 'gnd', 7, 9, a}" dbsm-titel-exemplare-2021-06.dat -H "idn, inhalt_satzart, inhalt_idn, inhalt_name, 