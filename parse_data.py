import json
from mdutils.mdutils import MdUtils

file_path = './raw_data/osorio.json'
with open(file_path, 'r') as f:
  data = json.load(f)

parsed_items = []
for item in data['Items']:
  if item['Price'] or item['FullPrice']:
    new_item = {}
    new_item['title'] = item['Title']
    new_item['description'] = item['Description']
    new_item['type'] = item['CurrentRealtyTypeTitle']
    new_item['negotiation_type'] = item['CurrentNegotiationTypeTitle']
    new_item['state'] = item['CurrentSpot']['CurrentStateName']
    new_item['city'] = item['CurrentSpot']['City']
    new_item['neighborhood'] = item['CurrentSpot']['Neighborhood']
    new_item['street'] = item['CurrentSpot']['CurrentAddress']
    new_item['price'] = item['FullPrice'] or item['Price']
    # new_item['build_name'] = item['Development']    # new_item['street_number'] = item['CurrentSpot']['Number']
    # new_item['build_name'] = item['Development']
    parsed_items.append(new_item)

general_instruction = 'Você é um assistente de inteligência artificial criado para vender imóveis. Você precisa ajudar a vender propriedades que estão localizadas na matriz de itens neste contexto. Os itens estão escritos em português brasileiro e você precisa traduzi-los.'

real_estate_agent = 'Sergio Madalena'

new_data = {
  'instructions': general_instruction,
  'real estate agent': real_estate_agent,
  'real state properties': parsed_items
}

def makeJson(): 
  with open('context.json' , 'w') as write: 
    json.dump(new_data , write)

def makeMD():
  mdFile = MdUtils(file_name='context')
  mdFile.new_header(level=1, title='# Informações gerais') 
  mdFile.new_paragraph(general_instruction)
  mdFile.new_paragraph('O nome da imobiliária é Imobiliária ' + real_estate_agent + '.')
  mdFile.new_paragraph()

  mdFile.new_header(level=1, title='# Lista de imóveis à venda')
  
  for idx, item in enumerate(parsed_items):
    mdFile.new_header(level=2, title="## Propriedade " + str(idx))
    for key in item.keys():
      mdFile.new_paragraph(key + '=' + str(item[key]))
  
  # mdFile.new_table_of_contents(table_title='Sumário', depth=2)
  mdFile.create_md_file()

makeJson()
makeMD()
