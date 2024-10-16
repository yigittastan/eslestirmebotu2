from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import os
import json
import time
import keyboard

def parse_address(address):
    filters = [
        ["No", "Numara", "Nr.", "Numarası", "No."],
        ["Bulvar", "Blv.", "Bul.", "Boulevard", "Blvr."],
        ["Sokak", "Sk.", "Sok.", "Street"],
        ["Mahalle", "Mah.", "Neighborhood"],
        ["Cadde", "Cd.", "Cad.", "Avenue", "Av."]
    ]

    parts = address.split()
    print("Ayrıştırılan kelimeler:", parts)

    # İstenmeyen kelimeleri filtrele
    parts = [part for part in parts if not any(filter_word in part for filter_group in filters for filter_word in filter_group)]

    print("Temizlenmiş adres parçaları:", parts)
    return parts

def is_bot_detected(driver):
    try:
        bot_message_selector = '.bot-detection-message, .robot-detected-message, #bot-warning'
        element = driver.find_element(By.CSS_SELECTOR, bot_message_selector)
        return 'Robot değilim algılandı' in element.text or 'Başka bir işlem yapın' in element.text
    except:
        return False

def compare_addresses(address_text, data_text):
    address_parts = address_text.lower().split()
    data_parts = data_text.lower().split()

    common_words = [word for word in address_parts if word in data_parts]
    print("Ortak kelimeler:", common_words)

    if len(common_words) >= 2:
        print("İki veya daha fazla benzerlik bulundu!")
        return True
    else:
        print("Yeterli benzerlik yok.")
        return False

def find_and_process(driver):
    try:
        if is_bot_detected(driver):
            print("Bot tespit edildi! İşlem durduruluyor.")
            return None, None

        bilgi_button = driver.find_element(By.CSS_SELECTOR, '.main-info__title')
        bilgi_button.click()
        print("Butona Tıklandı, Açılıyor...")

        time.sleep(5)

        title_element = driver.find_element(By.CSS_SELECTOR, 'span.bds-c-modal__header__title--truncate')
        title_text = title_element.text if title_element else None
        print(f"Restoran adı: {title_text}")

        address_element = driver.find_element(By.CSS_SELECTOR, '.box-flex.fd-row.my-sm h1')
        address_text = address_element.text if address_element else None
        print(f"Adres: {address_text}")

        if address_text:
            address_parts = parse_address(address_text)
            print(f"Parçalanmış Adres: {address_parts}")
        else:
            print("Adres bulunamadı.")
            return title_text, address_text

        data_divs = driver.find_elements(By.CSS_SELECTOR, 'div.Io6YTe.fontBodyMedium.kR99db.fdkmkc')
        if data_divs:
            for data_div in data_divs:
                data_text = data_div.text
                print(f"Data: {data_text}")
                compare_addresses(address_text, data_text)
        else:
            print("Data div bulunamadı.")

        return title_text, address_text
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None, None

def after_google_maps_open(driver):
    print("Google Maps açıldı, burada işlemler yapılacak.")
    time.sleep(10)
    
    total_divs = 0
    while True:
        try:
            new_div = driver.find_element(By.CSS_SELECTOR, f'div.Nv2PK.THOPZb.CpccDe:nth-of-type({total_divs + 1})[jsaction]')
            if new_div:
                total_divs += 1
        except:
            break

    print(f"Toplam {total_divs} div bulundu.")

    for i in range(total_divs):
        try:
            new_div = driver.find_element(By.CSS_SELECTOR, f'div.Nv2PK.THOPZb.CpccDe:nth-of-type({i + 1})[jsaction]')
            new_div.click()
            print(f"Yeni div'e geçildi: div.Nv2PK.THOPZb.CpccDe:nth-of-type({i + 1})")

            inner_div = new_div.find_element(By.CSS_SELECTOR, 'div[jsaction]')
            if inner_div:
                inner_div.click()
            else:
                print("Inner div bulunamadı.")
            time.sleep(5)

            data_divs = driver.find_elements(By.CSS_SELECTOR, 'div.Io6YTe.fontBodyMedium.kR99db.fdkmkc')
            for j, data_div in enumerate(data_divs):
                data_text = data_div.text
                print(f"Adres {j + 1}: {data_text}")

                if compare_addresses(data_text, data_text):  # Benzerlik kontrolü
                    print(f"Uyumlu adres bulundu: {data_text}")
                    break
                else:
                    print(f"Uyumsuz adres: {data_text}")
        except Exception as e:
            print(f"İşlem sırasında hata: {str(e)}")

def read_urls_from_folder(folder_path):
    urls = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'url' in data:
                    urls.append(data['url'])
                    print(f"URL eklendi: {data['url']}")
                else:
                    print(f"'url' anahtarı bulunamadı: {file_path}")
    return urls

def open_urls(urls):
    for url in urls:
        print(f"URL'ler Açılıyor: {url}")
        driver = webdriver.Chrome(service=Service('C:\\Users\\LEVEL END\\.cache\\selenium\\chromedriver\\win64\\129.0.6668.100\\chromedriver.exe'))
        driver.get(url)
        time.sleep(5)

        title_text, address_text = find_and_process(driver)
        if title_text:
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={title_text}"
            driver.get(google_maps_url)
            after_google_maps_open(driver)

        driver.quit()

def on_keypress_insert():
    folder_path = './test'
    urls = read_urls_from_folder(folder_path)
    open_urls(urls)

# Klavye işlemleri için
keyboard.add_hotkey('insert', on_keypress_insert)

print("Insert tuşuna basıldığında işlemler başlayacak.")
keyboard.wait('esc')  # Escape tuşuna basılana kadar bekler
