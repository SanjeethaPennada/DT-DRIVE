from itertools import product
import sys
import time
import traceback

from lib.carla_wrapper import CarlaWrapper
from lib.fidelity_evaluator import FidelityEvaluator
from pprint import pprint
import logging
import os
import debugpy
from multiprocessing import Process


HOUR = 60*60  # seconds of an hour


class ExperimentRunner():

    # this needs to be run in separate process due to threading issues in leaderboard 1.0
    @staticmethod
    def run_experiment(fps=20, high_quality=True):
        q = "high" if high_quality else "low"
        logging.info(f"Running experiment for: {fps} FPS and {q} quality!")
        try:

            print("Starting the client")
            fidelity_evaluator = FidelityEvaluator(fps, high_quality)
            fidelity_evaluator.run()
            print("Experiments finished")

        except BaseException as e:
            traceback.print_exc()
        finally:

            # Delete fidelity evaluator if exists
            try:
                del fidelity_evaluator
            except NameError:
                pass

            time.sleep(5)
            # give time to exit the process
        print("Run experiment bye")

    @staticmethod
    def run_all_experiments(fps_choices=[20, 18, 15, 12, 10], high_quality=True, offscreen=True):

        # spin carla server
        logging.info("Spinning up carla server")
        carlaWrapper = CarlaWrapper()
        carlaWrapper.launch(high_quality, offscreen)
        time.sleep(5)

        logging.info(
            f"All experiments are with high_quality={high_quality} and fps choices: ", str(fps_choices))

        for fps in fps_choices:
            logging.info("Starting a child process!")
            p = Process(target=ExperimentRunner.run_experiment,
                        args=(fps, high_quality))
            p.start()
            # 32 hours time out
            p.join(32*HOUR)

            if p.is_alive():
                logging.warning(f"Time out reached for: {fps},{high_quality}")
                logging.warning(f"Terminating the process: ", p.name)
                p.terminate()
                logging.warning(f"Waiting to terminate the process: ")
                time.sleep(10)

                if p.is_alive():
                    logging.warning(
                        f"Termination was not success need to kill.")
                    p.kill()
                    time.sleep(5)

                logging.warning(f"Realising the resources.")
                p.close()

            logging.info("Hello from experiment runner again!")
            time.sleep(1)

        carlaWrapper.kill_all()
        print("All experiments finished!!!")


def parse_args(args):
    q = True if args[1] == "True" else False

    fps_str = args[2:]
    fps_int = [int(v) for v in fps_str]
    logging.info(f"High quality: {q}")
    logging.info(f"Fps choices: {fps_int}")
    
    return fps_int, q


if __name__ == "__main__":

    logging.basicConfig(encoding='utf-8', format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

    fps_list, q = parse_args(sys.argv)
    ExperimentRunner.run_all_experiments(fps_choices=fps_list, high_quality=q)
    logging.info("Bye from main")
