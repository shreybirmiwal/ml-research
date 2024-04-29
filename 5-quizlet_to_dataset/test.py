import nodriver as uc
import time
import random
import jsonlines

quizlet_urls = [
    'https://quizlet.com/748183543/ap-environmental-science-flash-cards/',
    'https://quizlet.com/204426778/ap-environmental-science-review-flash-cards/',
    'https://quizlet.com/904782900/ap-environmental-science-flash-cards/',
    'https://quizlet.com/507844728/ap-environmental-science-flash-cards/',
    'https://quizlet.com/565189431/unit-1-ap-environmental-science-flash-cards/',
    'https://quizlet.com/395328278/ap-environmental-science-review-flash-cards/',
    'https://quizlet.com/281899442/ap-environmental-science-review-flash-cards/',
    'https://quizlet.com/293345572/ap-environmental-science-review-flash-cards/',
    'https://quizlet.com/282329185/ap-environmental-science-flash-cards/',
    'https://quizlet.com/84674637/ap-environmental-science-32-flash-cards/',
    'https://quizlet.com/45223659/apes-ap-environmental-science-flash-cards/',
    'https://quizlet.com/59814533/ap-environmental-science-flash-cards/',
    'https://quizlet.com/691812124/ap-environmental-science-review-flash-cards/',
    'https://quizlet.com/4933824/ap-environmental-science-exam-review-flash-cards/',
    'https://quizlet.com/203209444/ap-environmental-science-environmental-laws-flash-cards/',
    'https://quizlet.com/204310948/ap-environmental-science-review-flash-cards/',
]



output_file = 'output.jsonl'

async def main():
    driver = await uc.start()

    for url in quizlet_urls:
        await driver.get(url)
        time.sleep(random.uniform(30, 70))

        while True:
            try:
                button = driver.find_element(By.CLASS_NAME, 'AssemblyButtonBase')
                button.click()
                time.sleep(random.uniform(10, 20)) 
                print("Clicked on Load More button")
            except Exception as e:
                print(e)
                break  

        terms = []
        definitions = []

        term_elements = driver.find_elements(By.CLASS_NAME, 'SetPageTerms-term')

        for term_elem in term_elements:
            term_x = term_elem.find_element(By.XPATH, ".//div[@data-testid='set-page-card-side'][1]/div/span/span")
            term = term_x.text.strip()

            def_x = term_elem.find_element(By.XPATH, ".//div[@data-testid='set-page-card-side'][2]/div/span/span")
            definition = def_x.text.strip()

            terms.append(term)
            definitions.append(definition)

        with jsonlines.open(output_file, mode='a') as writer:
            for term, definition in zip(terms, definitions):
                data = {'input': term, 'output': definition}
                writer.write(data)

        print(f"Scraping completed for {url}. Data appended to {output_file}")
        time.sleep(random.uniform(200, 800))

if __name__ == '__main__':
    uc.loop().run_until_complete(main())