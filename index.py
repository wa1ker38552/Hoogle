from flask import render_template
from flask import redirect
from flask import request
from flask import Flask

from bs4 import BeautifulSoup
from house import House
import requests
import time


headers = {}
for ln in open('headers.txt','r').read().split('\n'):
  headers[ln.split(':')[0]] = ':'.join(ln.split(':')[1:])[1:]

def query_address(location):
  request = requests.get(
    f'https://www.zillowstatic.com/autocomplete/v3/suggestions?q={location}&userLat=37.38000&userLon=-122.08000&abKey=39d7d6f0-e6da-4578-a7b9-78bc9285cd21&clientId=homepage-render', 
    headers=headers
  )
  return [House(res) for res in request.json()['results']]

def get_data(display, zpid):
  display = ''.join(display.split(',')).split(' ')
  request = requests.get(
    f'https://www.zillow.com/homedetails/{"-".join(display)}/{zpid}_zpid/', headers=headers
  )

  data = {}
  soup = BeautifulSoup(request.text, 'html.parser')
  rhousedata = soup.find('span', attrs={'data-testid': 'bed-bath-beyond'}).get_text()

  data['size'] = {
    'bedrooms': rhousedata.split('bd')[0][:-1],
    'bathrooms': rhousedata.split('bd')[1].split('ba')[0][:-1],
    'sqft': rhousedata.split('bd')[1].split('ba')[1].split('sqft')[0][:-1]
  }

  data['images'] = []
  for e in soup.find_all('source', attrs={'type': 'image/jpeg'}):
    try:
      data['images'].append(e.get('srcset').split()[2])
    except IndexError:
      if 'zillow' in e.get('srcset').split()[0]:
        data['images'].append(e.get('srcset').split()[0])
      
  data['images'] = list(set(data['images']))
  data['zestimate'] = soup.find('span', attrs={'class': 'Text-c11n-8-73-0__sc-aiai24-0 xGfxD'}).get_text().replace('$', '')
  data['features'] = {}
  
  rfeatures = soup.find('div', attrs={'class': 'Spacer-c11n-8-73-0__sc-17suqs2-0 bRwHmw'})
  s = BeautifulSoup(str(rfeatures), 'html.parser')
  for spcer in s.find_all('div', attrs={'class': 'Spacer-c11n-8-73-0__sc-17suqs2-0 jCOrgb'}):
    search = BeautifulSoup(str(spcer), 'html.parser')
    title = search.find('h5', attrs={'class': 'Text-c11n-8-73-0__sc-aiai24-0 dpf__sc-1qwb4yr-0 drWVBo gFHTdP'}).get_text()
    data['features'][title] = {}
    
    rsubcat = search.find_all('div', attrs={'class': 'dpf__sc-1j9xcg4-0 gjalta'})
    for item in rsubcat:
      search = BeautifulSoup(str(item), 'html.parser')
      subtitle = search.find('h6', attrs={'class': 'Text-c11n-8-73-0__sc-aiai24-0 StyledHeading-c11n-8-73-0__sc-ktujwe-0 xGfxD'}).get_text()
      data['features'][title][subtitle] = []

      for item in search.find_all('span', attrs={'class': 'Text-c11n-8-73-0__sc-aiai24-0 kHeRng'}):
        data['features'][title][subtitle].append(item.get_text())

  return data


app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/results')
def results():
  start = time.time()
    
  address = request.args.get('q')
  results = query_address(address)
  data = {
    'query': address,
    'time': round(time.time()-start, 2),
    'num': len(results),
    'results': results
  }
  return render_template('search.html', data=data)

@app.route('/search', methods=['GET', 'POST'])
def search():
  if request.args.get('d') is None:
    return redirect(f'/results?q={request.form["address"]}', code=302)
  else:
    display = request.args.get('d')
    zpid = request.args.get('zpid')

    if zpid is None:
      display = display.split(' ')
      return redirect(f'https://www.zillow.com/homes/{"-".join(display)}_rb/', code=302)

    try:
      data = {
        'meta': query_address(display),
        'display': display,
        'query': request.args.get('query'),
        'data': get_data(display, zpid),
        'zpid': zpid
      }
    except AttributeError:
      # not a residential building
      display = display.split(' ')
      return redirect(f'https://www.zillow.com/homes/{"-".join(display)}_rb/', code=302)
    except IndexError:
      # not a residential building
      display = ''.join(display.split(',')).split(' ')
      return redirect(f'https://www.zillow.com/homedetails/{"-".join(display)}/{zpid}_zpid/', code=302)
    
    return render_template('search_result.html', data=data)


# app.run(host='0.0.0.0', port=8080)
