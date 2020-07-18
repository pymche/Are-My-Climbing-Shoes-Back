import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
import smtplib
import os
from email.message import EmailMessage

# User specification
budget = 100
shoe_size = '6'
pattern = re.compile(shoe_size)

# Conversion between EU and UK size and vice versa

# First exclude child size in script
child_size_key = [n + 0.5 for n in range(27, 35)]
child_size = {}
for x in range(0, len(child_size_key)):
    child_size_key[x] = str(child_size_key[x])
    child_size[child_size_key[x]] = 'NA'

conversion = {
'35':2, '35.5':2.5, '36':3, '36.5':3.5, '37':4, '37.5':4.5, '38':5, '38.5':5.5, '39':6, '39.5':6.5, '40':6.5, '40.5': 7, '41':7, '41.5':7.5, '42':8, '42.5':8.5, '43':9, '43.5': 9, '44':9.5, '44.5': 10, '45':10, '45.5':10.5, '46':11, '46.5':11.5, '47':12, '47.5':12.5, '48':13, '48.5':13.5, '49':14, '50':14.5, '51':15
}
conversion.update(child_size)
conversion_2 = dict([(str(value), float(key)) for key, value in conversion.items()]) # swapping key and values from conversion dictionary

# storing available shoes
links = []  # list of links to shoes to loop through after filtering
name = []
price_display = []

# Starting browser
driver = webdriver.Chrome()
driver.get("https://rockrun.com/collections/climbing-shoes")
products = driver.find_elements_by_class_name("product-wrap")

""" Loop through each pair of available shoes on display"""

for product in products:
    # string with name, after price, before price
    print(product.text)
    text = product.text.split('\n') # splitting string into text[0] name and text[1] prices
    print('Shoe name:', text[0])

    """Split list of string of 2 prices into before and after sale prices"""

    if text[1] == 'Sold Out':
        print('{} is currently unavailable'.format(text[0]))
    else:
        price = text[1].split(' ')  # splitting prices into two, now a list

        for x in range(0, len(price)):

            price[x] = float(price[x].replace("£", ""))

        print('Price before sale:', max(price))
        print('Price after sale:', min(price))

    """If sale price is lower than budget, save product link for later to check for available size, send email to notify if in stock"""

    if min(price) < budget:
        message = '{} is now under £{}!'.format(text[0], budget)
        print(message)

        price_display.append(min(price))
        name.append(text[0])

        link = driver.find_element_by_link_text(text[0])    # Find link by title of link
        link = link.get_attribute('href')   # Access link from <a href> tag with get_attribute
        links.append(link)

        # print(price_display)
        # print(name)
        # print(link)

    print('\n')

"""Check for available sizes and save results as message to send as email later"""

with open('email_message', 'w') as f:

    for x in range(0, len(links)):

        driver.get(links[x])

        available_shoe_sizes = driver.find_elements_by_xpath("//div[@tabindex='0']")

        for shoe in available_shoe_sizes:

            label = shoe.text

            if '-' in label:
                label_temp = label.split(' ')
                label_temp = label_temp[1].split('-')
                store = {}
                for x in range (0, len(label_temp)):
                    label_temp[x] = float(label_temp[x])
                    store[x] = label_temp[x]
                label_temp_2 = (store[0] + store[1])/2
                label = str(label_temp_2)

            if 'EU' in label:
                label = label.replace("EU ", "")
                label = str(conversion[label])
            elif 'UK' in label:
                label = label.replace("UK ", "")

            matches = pattern.finditer(label)
            for match in matches:
                availability = shoe.get_attribute('class')
                availability = availability.split(' ')[-1:]
                availability = str(availability[0])

                if availability == 'soldout':

                    print('{} in UK size {} / EU size {} is currently {}, click here to check for other sizes: {}'.format(name[x], shoe_size, conversion_2[shoe_size], availability, links[x]))

                elif availability == 'available':

                    msg = '{} in UK size {} / EU size {} is currently {} at £{}, click here to buy: {} \n'.format(name[x], shoe_size, conversion_2[shoe_size], availability, price_display[x], links[x])
                    f.write(msg)

"""Send email to notify"""

with open('email_message', 'r') as f:
    content = f.read()
    if content != "":

        EMAIL_ADDRESS = os.environ.get('GMAIL_USER')
        EMAIL_PASSWORD = os.environ.get('GMAIL_PASS')

        msg = EmailMessage()
        msg['Subject'] = 'CLIMBING SHOES IN YOUR SIZE AND BUDGET BOOOMMMM'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = 'cpy.melanie@gmail.com'

        msg.set_content(content)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print('Check email for available shoes!')

    else:
        print('No shoes available!')


driver.quit()