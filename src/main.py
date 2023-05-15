import json
from pathlib import Path    
from bs4 import BeautifulSoup
from mail_utils.gmail_extractor import get_email_ids, get_email_info

ids = get_email_ids('news@theshift.info')

for id_ in ids:
    result_set = get_email_info(id_)
    body_html = result_set['body']
    soup = BeautifulSoup(body_html, 'html.parser')

    result_set['subject'] = soup.title.string
    result_set['body'] = soup.get_text()
    result_set['date'] = result_set['date'].isoformat()

    file_name = str(result_set['subject'])

    output_dir = Path('src', 'outputs', f'{file_name}.json')

    
    print(f'Extraindo email {file_name}')

    with open(f'src/outputs/{file_name}.json', 'w') as json_file:
        json.dump(result_set, json_file, ensure_ascii=False)
    
    print('Feito.')

