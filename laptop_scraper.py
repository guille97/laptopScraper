# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 16:19:57 2020

@author: Guillermo Camps Pons
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import date
from os.path import exists

def extract_comp(comp, specs):
    '''Checks for the given component in specs.
            -comp can be ['cpu','ram','display','disk','gpu']'''
    
#   Contains the different names every component can appear with   
    components = {'cpu': ['Procesador','CPU'],
                  'ram': ['Memoria','RAM'],
                  'display': ['Display','Pantalla'],
                  'disk': ['Disco duro','Almacenamiento(?!.?ópti)','Capacidad'],
                  'gpu': ['Controlador gráfico','Gráfica','Gráficos','GPU',
                          'Tarjeta Gráfica']}
    
#   Looks for strings starting (^) with any of the component's name
    regex = '^'+'|^'.join(components[comp])
    txt = specs.find(lambda tag: tag.name == 'li' and re.search(regex, tag.text,re.IGNORECASE))
    
    if txt:
#       Removes the components name from the result
        regex = '(?<='+').+|(?<='.join(components[comp])+').+'
        return re.findall(regex, txt.get_text(),re.IGNORECASE)[0]

file = 'laptop_data.csv'
if exists(file):
#   Load dataframe
    df = pd.read_csv(file)
else:
#   Empty DataFrame where all data is stored
    df = pd.DataFrame(columns=['name', 'brand', 'p/n', 'code',
                               'p_current', 'p_base', 'discount', 'tax',  
                               'rating', 'opinions',
                               'cpu', 'cpu_ghz_min', 'cpu_ghz_max', 
                               'ram', 'ram_mhz', 'ram_gb', 
                               'gpu',
                               'disk1', 'disk1_gb', 'disk1_type', 
                               'disk2', 'disk2_gb', 'disk2_type',
                               'display', 'display_inch', 'display_width', 'display_height',
                               'date', 'url'])

# Desired number of laptops
numpcs = 100

# 24 per page. If numpcs mod 24 is not 0, add 1 page
numpages = int(numpcs/24)+(numpcs % 24 > 0) 

coreurl= 'https://www.pccomponentes.com'
dfshape = df.shape[0]
counter = dfshape

# Loop for pages
for j in range(numpages):

    url = coreurl + '/portatiles?page='+str(j)
    page = requests.get(url)    
    bigsoup = BeautifulSoup(page.content, features="lxml")
    
#   Loop for each article in the page
    for article in bigsoup.find_all('article'):
        url = coreurl + article.find('a')['href']
        page = requests.get(url)
        soup = BeautifulSoup(page.content, features="lxml")        
                  
# =============================================================================
#       Article name and codes           
# =============================================================================
#       The full article name is contained in h1
        df.loc[counter,'name'] = soup.find('h1').text     
        
#       Brand, P/N and code are in a div that contains a text with P/N
        regex = 'P/N:'
        art = soup.find_all(lambda tag: tag.name == 'div' and re.search(regex, tag.text,re.IGNORECASE))[-1]
        df.loc[counter,'brand'] = art.a.get_text()
        df.loc[counter,'p/n']   = art.find_all('span')[0].get_text()
        df.loc[counter,'code']  = art.find_all('span')[1].get_text()        

# =============================================================================
#       Prices        
# =============================================================================
#       Prices, discount and tax are in the attributes of an element with class 'precioMain h1'
        prices = soup.find(attrs = {'class':'precioMain h1'})
        df.loc[counter,'p_base'] = float(prices['data-baseprice'])
        df.loc[counter,'p_current'] =float(prices['data-price'])
        df.loc[counter,'discount'] = float(prices['data-discount'])
        df.loc[counter,'tax']= round((float(prices['data-tax'])-1.00)*100.00,2)            
            
# =============================================================================
#       Opinions and ratings        
# =============================================================================
#       Ratings are in the attribute 'style' of a <div> with class 'rating-stars'
#           regex: checks for numbers that may have a .
        ratings = soup.find('div', attrs = {'class':'rating-stars'})['style']
        regex = '\d+\\.?\d*'
        df.loc[counter,'rating'] = float(re.findall(regex, ratings, re.IGNORECASE)[0])
        
#       Opinions are in the text of a <a> with id 'article-hlink-comments'
#           regex: checks for numbers       
        opinions = soup.find('a', attrs = {'id':'article-hlink-comments'}).get_text()
        regex ='\d+'
        opinion = re.findall(regex, opinions, re.IGNORECASE)
        if opinion:
            df.loc[counter,'opinions'] = int(opinion[0])
        else:
            df.loc[counter,'opinions'] = 0
               
# =============================================================================
#       Specs    
# =============================================================================
        specs = soup.find('h2',text = re.compile('Especificacio')).find_next_sibling()

# ----- GPU -------------------------------------------------------------------
#       Extract GPU using extract_comp
        gpu = extract_comp('gpu', specs)
        if gpu:
            df.loc[counter,'gpu'] = gpu
        
# ----- CPU -------------------------------------------------------------------
#       Extract CPU using extract_comp
        cpu = extract_comp('cpu', specs)
        if cpu:
            df.loc[counter,'cpu'] = cpu
            
#           Look for the GHz of the CPU
#               regex: looks for float numbers with , (Spanish) or . (English)
            regex = '\d+[.,]\d+'   
            cpughz = [float(ghz.replace(',','.')) for ghz in re.findall(regex, cpu, re.IGNORECASE)]       
            if len(cpughz)==1:
#               If this condition is given the number read must be the maximum
                if 'hasta' in cpu:
                    df.loc[counter,'cpu_ghz_max'] = cpughz[0]
                else:
                    df.loc[counter,'cpu_ghz_min'] = cpughz[0]
            elif len(cpughz) == 2:            
                [df.loc[counter,'cpu_ghz_min'], df.loc[counter,'cpu_ghz_max']] = cpughz
             
# ----- RAM -------------------------------------------------------------------      
#       Extract RAM using extract_comp
        ram = extract_comp('ram', specs)
        if ram:
            df.loc[counter,'ram'] = ram
            
#           Look for the MHz of the RAM
#               regex: looks for 4 numbers that may be separated by . (Spanish thousand separator)
            regex = '\d{4}|\d\\.\d{3}'
            rammhz= [int(mhz.replace('.','')) for mhz in re.findall(regex, ram, re.IGNORECASE)]        
#           Just in case different values are found
            if len(set(rammhz))>1:
                print('More than 1 different values for RAM MHz found {}, first is taken'.format(rammhz))
            if rammhz: 
                df.loc[counter,'ram_mhz'] = rammhz[0]
                
#           Look for the GB of the RAM
#               regex: looks for numbers with GB behind. Also adds if there's any x2 
#                      and the characters in front           
            regex = '.{0,3}\d+.?GB[*x×]?2?'
            ramgb = re.findall(regex, ram, re.IGNORECASE)
            
#               regex: this one takes the numbers from the other           
            regex = '\d+(?=.?GB)'
            gb = [int(re.findall(regex, r, re.IGNORECASE)[0]) for r in ramgb]
    
            for i,g in enumerate(ramgb):
#               If there's a plus (in front of the number) then the value 
#               is added to the previous number
                if '+' in g:
                    gb[i-1] += gb[i]
#               If there's a x2 multiply the value
                elif re.search('[*x×]2', g, re.IGNORECASE):
                    gb[i] = gb[i]*2
    
#           Only take the first value, since it will carry the previous operations
            if gb:
                df.loc[counter,'ram_gb'] = gb[0]

# ----- Display --------------------------------------------------------------- 
#       Extract Display using extract_comp
        display = extract_comp('display', specs)
        if display:
            df.loc[counter,'display'] = display
            
#           Looks for the inches of the display
#               regex: looks for floats that end with ", ” or pulgadas
            regex = '\d+[.,]?\d?(?=.?"|.?”|.?pulgadas)'
            inch = [float(i.replace(',','.')) for i in re.findall(regex, display,re.IGNORECASE)]
            if inch:
                df.loc[counter,'display_inch'] = inch[0]
            
#           Looks for the display width
#               regex: looks for 3 or 4 integers that may have a . (Spanish thousand 
#                      separator) that end with an x (width x height)
            regex = '(?:\d{3,4}|\d\\.\d{3}) ?(?=[*x×])'
            width = [int(h.replace('.','')) for h in re.findall(regex, display, re.IGNORECASE)]
            if width:
                df.loc[counter,'display_width'] = width[0]
    
#           Looks for the display height
#               regex: looks for 3 or 4 integers that may have a . (Spanish thousand 
#                      separator) that start with an x (width x height)         
            regex = '(?<=[*x×]) ?(?:\d{3,4}|\d\\.\d{3})'
            height= [int(w.replace('.','')) for w in re.findall(regex, display, re.IGNORECASE)]
            if height:
                df.loc[counter,'display_height'] = height[0]        


# ----- Disk ------------------------------------------------------------------             
#       Extract Disk using extract_comp        
        disk2 = float('nan')
        disk = extract_comp('disk', specs)
        if disk:                       
#           If there's a x or a + there are 2 disks        
            regex = '[*x×]2'
            if re.search(regex, disk, re.IGNORECASE):
                disk1 = re.sub(regex,'',disk)
                disk2 = disk1
            elif '+' in disk:
                regex = '.+(?=\\+)'
                disk1 = re.findall(regex, disk, re.IGNORECASE)[0]
                regex = '(?<=\\+).+'
                disk2 = re.findall(regex, disk, re.IGNORECASE)[0]
            else:
                disk1 = disk        
            df.loc[counter,'disk1'] = disk1
            df.loc[counter,'disk2'] = disk2
                    
    
            for vardisk, strdisk in zip([disk1,disk2],['disk1','disk2']):
                if not pd.isnull(vardisk):  
#                   Looks for the disk capacity for every disk
#                       regex: looks for integers ending in GB or TB
                    regex = '\d+.?GB|\d+.?TB'
                    diskgb = re.findall(regex, disk1, re.IGNORECASE)
                    if diskgb:
                        regex = '\d+'
                        df.loc[counter,strdisk+'_gb'] =  int(re.findall(regex, diskgb[0], re.IGNORECASE)[0])
#                       Multiplies those with TB by 1000
                        if 'TB' in diskgb[0]:
                            df.loc[counter,strdisk+'_gb'] = df.loc[counter,strdisk+'_gb'] * 1000  
                            
#                   Looks for the disk type for every disk
#                       regex: looks for SSD, HDD or SATA              
                    regex = 'SSD|HDD|SATA'
                    disktype = re.findall(regex,vardisk, re.IGNORECASE)
                    if disktype:
                        df.loc[counter,strdisk+'_type'] = disktype[0] 

# =============================================================================
#       Other        
# =============================================================================
#       Not extracted from the web
        df.loc[counter,'url'] = url
        df.loc[counter,'date'] = date.today()       

        
        counter += 1
    print('Progress: {} out of {} ({:.2f}%)'.format(counter-dfshape,numpages*24, (j+1)/numpages*100))

df = df.drop_duplicates()

df.to_csv(file, index = False)
    
    