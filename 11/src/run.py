import logging
from wordpress.wp_uploader import make_post


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    query = """
    Мы IT компания, которая работает с искусственным интеллектом. Напиши интересную статью про искусственный интеллект.
    Не повторяй уже существующие статьи. Выбери какую-нибудь другую тему.
    
    Вот опубликованные статьи:
    - Искусственный интеллект в медицине: новые горизонты и возможности
    - Искусственный интеллект: Как ИИ меняет бизнес-процессы 
    - Искусственный интеллект в логистике: Как ИИ меняет правила игры 
    - Искусственный Интеллект: Революция в Мире Продаж 
    - Искусственный интеллект в HR: Перспективы и вызовы на рынке труда 
    - В чем польза ИИ для бизнеса: Революция в управлении и операционной деятельности 
    - Искусственный интеллект в образовании: преимущества, вызовы и будущее
    - Искусственный Интеллект: Революция в SEO для Бизнеса
    - Искусственный Интеллект: На Пороге Новой Эры 
    - Выбрать Как ИИ трансформирует HR: повышение эффективности и вовлечённости
    """
    make_post(query=query)