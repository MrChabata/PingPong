from logging.handlers import RotatingFileHandler
import threading
import time
import logging
from pathlib import Path

import kivy
kivy.require("2.3.1")

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

# Важно: ставим python-OBD
# pip install kivy python-OBD
try:
    import obd
except Exception as e:
    obd = None

APP_LOGGER_NAME = "obd_app"

class KivyUIHandler(logging.Handler):
    """Пихает логи прямо в TextInput через app.ui_append."""
    def __init__(self, ui_callback):
        super().__init__()
        self.ui_callback = ui_callback

    def emit(self, record):
        try:
            msg = self.format(record)
            self.ui_callback(msg)
        except Exception:
            # глотаем, чтобы логгер не убил приложение
            pass

def build_logger(log_dir: Path, ui_callback) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "obd_app.log"

    logger = logging.getLogger(APP_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False  # иначе пойдёт наверх к root и будет дубль

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # 1) Файл с ротацией
    fh = RotatingFileHandler(
        log_path,
        mode="a",
        maxBytes=1_000_000,  # ~1 МБ
        backupCount=3,
        encoding="utf-8",
        delay=True,
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # 2) Консоль (полезно на десктопе)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # 3) В UI
    uh = KivyUIHandler(ui_callback)
    uh.setLevel(logging.INFO)
    uh.setFormatter(fmt)
    logger.addHandler(uh)

    # Подцепим логгер python-OBD к тем же хэндлерам
    pyobd_logger = logging.getLogger("obd")
    pyobd_logger.setLevel(logging.INFO)
    pyobd_logger.handlers.clear()
    pyobd_logger.propagate = False
    pyobd_logger.addHandler(fh)
    pyobd_logger.addHandler(sh)
    pyobd_logger.addHandler(uh)

    logger.info(f"Логи пишутся сюда: {log_path}")
    return logger   


class Root(BoxLayout):
    pass


class OBDApp(App):
    title = "OBD Tester"

    def build(self):
        self.root = Root()

        try:
            log_dir = Path(self.user_data_dir)  # Android/десктоп внутренняя папка
        except Exception:
            log_dir = Path.cwd() / "logs"

        # ВАЖНО: передаём ui_append как колбэк логгеру
        self.logger = build_logger(log_dir, self.ui_append)

        self._conn = None
        self._poll_thread = None
        self._stop_flag = threading.Event()

        if obd is None:
            self.logger.error("python-OBD не установлен. pip install python-OBD")
        else:
            self.logger.info("Готово. Жми «Подключиться».")
        return self.root

    # Безопасные апдейты UI из любых потоков
    def ui_append(self, msg: str):
        def _append(_dt):
            ti = self.root.ids.output
            ti.readonly = False
            ti.text += (msg.rstrip() + "\n")
            ti.cursor = (0, len(ti.text))   # прокрутить в конец
            ti.readonly = True
        Clock.schedule_once(_append, 0)

    def on_connect_press(self):
        if obd is None:
            self.ui_append("python-OBD не найден. Установите пакет.")
            return

        if self._poll_thread and self._poll_thread.is_alive():
            self.ui_append("Уже подключаюсь, не мешай процессу...")
            return

        self._stop_flag.clear()
        self._poll_thread = threading.Thread(target=self._connect_and_poll, daemon=True)
        self._poll_thread.start()

    def on_stop(self):
        self._stop_flag.set()
        try:
            if self._conn:
                self._conn.close()
        except Exception:
            pass

    # Фоновая логика подключения и опроса
    def _connect_and_poll(self):
        self.logger.info("Запуск подключения к OBD")
        self.ui_append("Подключаюсь к OBD...")

        try:
            # Автопоиск порта. Если знаете порт, передайте portstr="COM5" или "/dev/rfcomm0".
            conn = obd.OBD(fast=False, timeout=5.0)  # blocking, автоскан портов
        except Exception as e:
            self.logger.exception("Ошибка при создании подключения")
            self.ui_append(f"Ошибка подключения: {e}")
            return

        self._conn = conn

        if not conn.is_connected():
            self.ui_append("Не удалось подключиться. Проверь ELM327, порт и питание.")
            self.logger.warning("OBD не подключен")
            return

        self.ui_append(f"Успех. Протокол: {conn.protocol_name()}")
        self.logger.info(f"Подключено. Протокол: {conn.protocol_name()}")

        # Какие команды вообще доступны на этом ECU:
        try:
            supported = conn.supported_commands
            # Отфильтруем только «интересные»
            wanted = [
                obd.commands.RPM,
                obd.commands.SPEED,
                obd.commands.COOLANT_TEMP,
                obd.commands.INTAKE_TEMP if hasattr(obd.commands, "INTAKE_TEMP") else None,
                obd.commands.MAF if hasattr(obd.commands, "MAF") else None,
                obd.commands.MAP if hasattr(obd.commands, "MAP") else None,
                obd.commands.THROTTLE_POS,
                obd.commands.FUEL_LEVEL if hasattr(obd.commands, "FUEL_LEVEL") else None,
            ]
            wanted = [w for w in wanted if w is not None]
            available = [c for c in wanted if c in supported]
            missing = [c for c in wanted if c not in supported]

            self.ui_append("Доступные команды:")
            for c in available:
                self.ui_append(f"  ✓ {c.name}")

            if missing:
                self.ui_append("Недоступные команды (нормально, не все ECU всё умеют):")
                for c in missing:
                    self.ui_append(f"  – {c.name}")
        except Exception as e:
            self.logger.exception("Ошибка при определении поддерживаемых команд")
            self.ui_append(f"Не удалось получить список поддерживаемых команд: {e}")
            available = [obd.commands.RPM, obd.commands.SPEED, obd.commands.COOLANT_TEMP]

        # Пробуем прочитать ошибки DTC сразу
        try:
            r = conn.query(obd.commands.GET_DTC)
            if r and r.value:
                dtcs = r.value  # список кортежей (код, описание)
                if len(dtcs) == 0:
                    self.ui_append("Ошибки DTC: не найдены")
                else:
                    self.ui_append("Ошибки DTC:")
                    for code, desc in dtcs:
                        self.ui_append(f"  {code}: {desc}")
            else:
                self.ui_append("Ошибки DTC: ответ пустой")
        except Exception as e:
            self.logger.exception("Ошибка чтения DTC")
            self.ui_append(f"Ошибка при чтении DTC: {e}")

        # Циклический опрос доступных параметров
        self.ui_append("Начинаю опрос датчиков каждые ~1.0 сек. Остановить — закрой приложение.")
        while not self._stop_flag.is_set():
            try:
                for cmd in available:
                    resp = self._conn.query(cmd)
                    if resp and not resp.is_null():
                        self.ui_append(f"{cmd.name}: {resp.value}")  # value уже с единицами
                        self.logger.info(f"{cmd.name}: {resp.value}")
                    else:
                        self.ui_append(f"{cmd.name}: нет данных")
                time.sleep(1.0)
            except Exception as e:
                self.logger.exception("Ошибка в цикле опроса")
                self.ui_append(f"Ошибка опроса: {e}")
                time.sleep(2.0)
                # можно не рвать цикл, ECU любит капризничать

        self.ui_append("Опрос остановлен.")
        try:
            self._conn.close()
        except Exception:
            pass
        self.logger.info("Подключение закрыто.")

if __name__ == "__main__":
    OBDApp().run()