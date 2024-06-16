## Video-encoder
video-encoder - это сервис для извлечения признаков из коротких видео. Используется text-image модель CLIP, дообученная для более точного поиска - [jina-clip-v1](https://huggingface.co/jinaai/jina-clip-v1).
Алгоритм получения векторов:
  - Видео делится на сцены с помощью [PySceneDetect](https://www.scenedetect.com/)
  - Из каждой сцены берется несколько случайных кадров.
  - Кадры преобразуются в векторы, которые затем усредняются.

