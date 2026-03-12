import subprocess
import time
import signal
import os
from pathlib import Path
import logging
logging.basicConfig(level=logging.DEBUG)

CARLA_DIR = Path('carla')

# --world-port = 20010


class CarlaWrapper():
    def __init__(self) -> None:
        self.carla_process_high: subprocess.Popen = None
        self.carla_process_low: subprocess.Popen = None

    def launch_and_wait(self, high_quality=True):
        self.launch(high_quality)
        
        time.sleep(1)




    def launch(self, high_quality=True, offscreen=True):

        quality = "Epic" if high_quality else "Low"
        wp = 2000 if high_quality else 2010
        display = "DISPLAY=" if offscreen else ""

        logging.info(f"Launching carla in {quality} quality at port {wp}, offscreen: {offscreen}")
        
        
        process_args = {
            "args":  f"{display} {CARLA_DIR}/CarlaUE4.sh -opengl --world-port={wp} -quality-level={quality}",
            "shell": True,
            "stdout": subprocess.PIPE,
            "preexec_fn": os.setsid
        }

        if high_quality:
            self.carla_process_high = subprocess.Popen(**process_args)
        else:
            self.carla_process_low = subprocess.Popen(**process_args)

    def __del__(self):
        #cleanup processes
        self.kill_all()

    def kill_all(self) -> None:
        self._kill_process(self.carla_process_high)
        self._kill_process(self.carla_process_low)

    def is_running(self, high_quality=True):
        if high_quality:
            return self._is_process_running(self.carla_process_high)

        return self._is_process_running(self.carla_process_low)

    @staticmethod
    def _kill_process(process: subprocess.Popen) -> None:
        if process:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

    @staticmethod
    def _is_process_running(process: subprocess.Popen) -> bool:

        poll = process.poll()
        if poll:
            logging.warning(f"Carla exited with code: {poll}")
            return False
        else:
            logging.info("Carla is still running!")
            return True


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    logging.info("Checking if carla wrapper works properly")
    wrapper = CarlaWrapper()
    low_q = True
    wrapper.launch(high_quality=low_q)
    time.sleep(2)
    wrapper.is_running(high_quality=low_q)
    time.sleep(5)
    logging.info("Killing process")
    wrapper.kill_all()
    time.sleep(2)
    wrapper.is_running(high_quality=low_q)
