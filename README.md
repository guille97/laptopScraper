
# Pràctica 1: Web Scraping (laptopScraper)

## Descripció

Aquesta pràctica de Web Scraping ha estat realitzada pel Guillermo Camps Pons (individual) per a l'assignatura de _Tipologia i cicle de vida de les dades_ del Màster de Ciència de Dades de la Universitat Oberta de Catalunya (UOC). El programa _laptop_scraper.py_ (escrit en Python 3.7) realitza un procés de Web Scraping per a extreure dades sobre els diferents portàtils disponibles al web de [PcComponentes](https://www.pccomponentes.com/portatiles) i genera (o actualitza) un arxiu csv anomenat _laptop_data.csv_ on s'emmagatzemen dades com les especificacions del portàtil, el preu, la marca, la valoració, etc. 

## Requisits d'execució

El codi present a _laptop_scraper.py_ fa ús dels següents mòduls:

* _requests_: s'utilitza per a obtenir els HTML de la web.

* _pandas_: s'utilitza per a crear i gestionar DataFrames.

* _bs4_: es fa ús de la classe o objecte _BeautifulSoup_ per a extreure dades del HTML.

* _re_: s'utilitza per a crear expresions regulars per a la búsqueda de patrons de caràcters.

* _date_: es fa ús de _datetime_ per a obtenir la data actual.

* _os_: es fa ús de la funció _exists_ de _os.path_ per a mirar si existeix el dataset al directori.

Si no es tenen alguns d'aquests mòduls instal·lats conjuntament amb Python, s'haurà d'utilitzar l'instal·lador de paquets de Python (pip) de la següent manera:

```
pip install [nom_modul]
```

on el [nom_mòdul] és l'utilitzat a la llista anterior.

## Fitxers

* _laptop_scraper.py_: codi que genera el dataset.

* _laptop_data.csv_: dataset resultant.

* _README.md_: aquest arxiu.

* _PRA1.pdf_: pdf amb les respostes de la pràctica.

* _LICENSE_: arxiu de la licència generat automàticament.

