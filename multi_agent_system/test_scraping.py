#!/usr/bin/env python3
"""
Test script for scraping tools
"""

from tools.scraping_tools import fetch_html_content, extract_clean_text, WebScrapingTool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_fetch_html_content():
    """Test fetch_html_content function"""
    print('🔍 Тестирую fetch_html_content...')
    try:
        html = fetch_html_content('https://httpbin.org/html', timeout=10)
        print(f'✅ HTML получен: {len(html)} символов')
        return html
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        return None

def test_extract_clean_text(html=None):
    """Test extract_clean_text function"""
    print('\n🧹 Тестирую extract_clean_text...')
    try:
        test_html = html[:1000] if html else '<html><body><h1>Test</h1><p>Sample text</p></body></html>'
        clean_text = extract_clean_text(test_html)
        print(f'✅ Чистый текст: {len(clean_text)} символов')
        print(f'Превью: {clean_text[:100]}...')
        return clean_text
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        return None

def test_web_scraping_tool():
    """Test WebScrapingTool class"""
    print('\n🛠️ Тестирую WebScrapingTool...')
    try:
        scraper = WebScrapingTool(timeout=10)
        data = scraper.scrape_website('https://httpbin.org/html')
        print(f'✅ Данные получены: {len(data)} полей')
        print(f'Заголовок: {data.get("title", "N/A")}')
        print(f'Контент: {len(data.get("content", ""))} символов')
        print(f'Ссылки: {len(data.get("links", []))}')
        print(f'Изображения: {len(data.get("images", []))}')
        return data
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        return None

def test_error_handling():
    """Test error handling"""
    print('\n🚨 Тестирую обработку ошибок...')
    
    # Test invalid URL
    try:
        fetch_html_content('invalid-url')
        print('❌ Должна была быть ошибка для неверного URL')
    except Exception as e:
        print(f'✅ Корректно обработана ошибка: {type(e).__name__}')
    
    # Test timeout
    try:
        fetch_html_content('https://httpbin.org/delay/5', timeout=1)
        print('❌ Должна была быть ошибка таймаута')
    except Exception as e:
        print(f'✅ Корректно обработана ошибка таймаута: {type(e).__name__}')

if __name__ == '__main__':
    print('🚀 Запуск тестов модуля scraping_tools\n')
    
    # Run tests
    html = test_fetch_html_content()
    clean_text = test_extract_clean_text(html)
    data = test_web_scraping_tool()
    test_error_handling()
    
    print('\n✅ Все тесты завершены!')

