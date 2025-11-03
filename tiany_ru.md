# Структура программы libirsample и руководство пользователя

---

## 1. Структура программы

![Структура программы](./irsample_structure.png)

Пример включает следующие модули: **sample**, **camera**, **display**, **temperature** и **cmd**.  
Назначение каждого модуля:

### sample module
После настройки соответствующих параметров в `sample.cpp` модуль вызывает **camera**, чтобы установить соединение с инфракрасной камерой и начать потоковую передачу изображения.  
Далее создаются четыре потока: **stream**, **display**, **temperature** и **cmd**, которые обрабатывают соответствующие данные.

### camera module
Используется для получения данных от инфракрасной камеры.  
Поток **stream** получает исходные кадры и разделяет их на два потока — изображения (**image frame**) и температуры (**temp frame**).  
После обработки модуль возвращает сигнал в поток камеры для продолжения работы.

### display module
После получения кадра изображения выполняет обработку в соответствии с параметрами `frame_info`:  
форматирование данных, отражение, зеркалирование, поворот и т. д.  
Затем отображает результат с помощью **OpenCV**.

### temperature module
После получения температурного кадра обрабатывает его аналогично — выполняет преобразование формата, отражение и поворот.

### cmd module
Отправляет команды в инфракрасную камеру.

---

## 2. Метод компиляции программы

### Windows
В папке `libir_sample` предоставлен проект для **Visual Studio 2019**.  
Для работы примера требуются библиотеки **OpenCV** и **pthreadVC2.dll** (уже включены).

### Linux
В `libir_sample` есть файлы `Makefile` и `CMakeLists.txt`.  
Перед компиляцией необходимо удалить каталог `opencv2` (OpenCV устанавливается отдельно).  
Если OpenCV не используется, закомментируйте строку:

```c
#define OPENCV_ENABLE
```

в `display.h`, а также все связанные строки в `Makefile` или `CMakeLists.txt`.

---

## 3. Руководство пользователя

### 3.1 Подключение камеры

В `main()` файла `sample.cpp` камера выбирается вызовом:

```c
ir_camera_open();
```

После получения параметров камеры вызывается:

```c
load_stream_frame_info();
```

для настройки параметров отображения и измерения температуры — ширины, высоты, поворота, зеркалирования, псевдоцвета, форматов входных и выходных кадров и выделения памяти.

Пример настройки:

```c
stream_frame_info->image_info.width = stream_frame_info->camera_param.width;
stream_frame_info->image_info.height = stream_frame_info->camera_param.height / 2;
stream_frame_info->image_info.rotate_side = LEFT_90D;
stream_frame_info->image_info.mirror_flip_status = STATUS_MIRROR_FLIP;
stream_frame_info->image_info.pseudo_color_status = PSUEDO_COLOR_ON;
stream_frame_info->image_info.img_enhance_status = IMG_ENHANCE_OFF;
stream_frame_info->image_info.input_format = INPUT_FMT_YUV422;
stream_frame_info->image_info.output_format = OUTPUT_FMT_BGR888;

stream_frame_info->temp_info.width = stream_frame_info->camera_param.width;
stream_frame_info->temp_info.height = stream_frame_info->camera_param.height / 2;
stream_frame_info->temp_info.rotate_side = NO_ROTATE;
stream_frame_info->temp_info.mirror_flip_status = STATUS_NO_MIRROR_FLIP;
stream_frame_info->image_byte_size = stream_frame_info->image_info.width * stream_frame_info->image_info.height * 2;
stream_frame_info->temp_byte_size = stream_frame_info->temp_info.width * stream_frame_info->temp_info.height * 2;
```

**Основные поля структуры `StreamFrameInfo_t`:**

- `width` / `height` — размеры кадра.  
- `byte_size` — размер кадра в байтах.  
- `rotate_side`, `mirror_flip_status` — параметры поворота и зеркалирования.  
- `input_format`, `output_format` — форматы входных и выходных данных.  
- `pseudo_color_status` — включение псевдоцвета.  
- `img_enhance_status` — включение растяжения контраста.  
- `image_byte_size` / `temp_byte_size` — размеры буферов данных.

---

### 3.2 Потоковая передача (Streaming)

После открытия устройства и настройки параметров можно вызвать:

```c
ir_camera_stream_on();
```

или

```c
ir_camera_stream_on_with_callback();
```

(если используется пользовательская функция обратного вызова).

В процессе отображения вызывается `display_one_frame()`, которая обрабатывает данные, выполняет поворот, зеркалирование и вывод изображения через `cv::imshow()`.

---

### 3.3 Отправка команд

В `cmd.cpp` реализована функция:

```c
void* cmd_function(void* threadarg);
```

которая считывает число с клавиатуры и вызывает соответствующую команду:

```c
command_sel(cmd);
```

---

### 3.4 Измерение температуры

Функция `temperature_function()` каждые 25 кадров выполняет измерение температуры в одном из трёх режимов:
- точечный,
- линейный,
- площадной.

```c
if (timer % 25 == 0) {
    line_temp_demo((uint16_t*)stream_frame_info->temp_frame, temp_res);
}
```

> ⚠️ В многопоточном режиме необходимо использовать **mutex**, чтобы избежать конфликтов при отправке команд.

---

### 3.5 Завершение работы

Для завершения программы вызовите:

```c
destroy_pthread_sem();
uvc_camera_close();
```

---

### 3.6 Обновление прошивки

Для обновления микропрограммы используется функция `update_fw_cmd()` в `cmd.cpp`.  
Шаги обновления:

1. Проверить текущий режим устройства (**ROM** или **Cache**) и при необходимости переключить в **ROM mode**.  
2. Проверить и сбросить состояние SPI.  
3. Стереть область flash-памяти (256 КБ = 64 сектора по 4 КБ).  
4. Записать новый файл прошивки и проверить данные.  
5. Записать метку **cache tag** (подтверждение успешной записи).  
6. Перезапустить устройство (автоматическое переключение в **Cache Mode**).

---

### 3.7 Вторичная калибровка измерения температуры

В `cmd.cpp` (кейсы 16 и 17):

- `read_nuc_parameter()` — считывает параметры NUC.  
- `calculate_org_env_cali_parameter()` — вычисляет коэффициенты коррекции температуры.  
- `calculate_new_env_cali_parameter()` — пересчитывает параметры с учётом эмиссивности, расстояния, температуры и влажности.  
- `tpd_get_point_temp_info()` — считывает исходную температуру точки.  
- `temp_calc_with_new_env_calibration()` — вычисляет скорректированную температуру.

---

### 3.8 Предотвращение пересвета и автоматическое усиление

В `camera.cpp` реализованы две независимые функции:  
**avoid_overexposure()** и **auto_gain_switch()**.  
Обе работают с температурными данными (`stream_frame_info->temp_frame`).

```c
avoid_overexposure((uint16_t*)stream_frame_info->temp_frame, &stream_frame_info->temp_info, 10 * fps);
auto_gain_switch((uint16_t*)stream_frame_info->temp_frame, &stream_frame_info->temp_info, &auto_gain_switch_info);
```

---

© 2025 — libir SDK Documentation
