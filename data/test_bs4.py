from bs4 import BeautifulSoup

with open('demo.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'lxml')
tag = soup.find(class_='total fl')
print(tag.text.strip().split(' ')[1])


house_name = [i.text for i in soup.find_all(class_='VIEWDATA CLICKDATA maidian-detail')]
location_href = [a.get('href') for a in soup.select('.positionInfo a')]
location_name = [i.text.strip('\n') for i in soup.find_all(class_='positionInfo')]
price = [i.text.strip('\n')  for i in soup.find_all(class_='priceInfo')]


print(house_name)
# print(location_href)
# print(location_name)
# print(price)

sellListContent = soup.find_all(class_='clear')
data = []
print(len(sellListContent))
for item in sellListContent:
    try:
        house_name = item.find(class_='VIEWDATA CLICKDATA maidian-detail').text
        location_href = item.select('.positionInfo a')[0].get('href')
        location_name = item.find(class_='positionInfo').text.strip('\n')
        price = item.find(class_='priceInfo').text.replace('\n','').strip(' ')
        data.append(
            {
                'house_name': house_name,
                'location_href': location_href,
                'location_name': location_name,
                'price': price
            }
        )
    except Exception as e:
        print(e)
result = list({tuple(d.items()) for d in data})
result = [dict(item) for item in result]
print(result)


