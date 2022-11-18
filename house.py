class House:
  def __init__(self, json):
    # returns all in str
    self.display = json['display']
    try:
      self.street_number = json['metaData']['streetNumber']
    except KeyError: self.street_number = None
    try:
      self.street_name = json['metaData']['streetName']
    except KeyError: self.street_number = None

    try:
      self.city = json['metaData']['city']
    except KeyError: self.city = None
      
    self.state = json['metaData']['state']
    self.country = json['metaData']['country']

    try:
      self.zip = json['metaData']['zipCode']
    except KeyError: self.zip = None
    try:
      self.zpid = json['metaData']['zpid']
    except KeyError: self.zpid = None

# /search?s={{item.street_name}}&n={{item.street_number}}&c={{item.city}}&st={{item.state}}&cn={{item.country}}
