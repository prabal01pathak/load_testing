"""
Run every possible combinations from max_process and max_thread arguments
"""
import os
import time


from typer import Typer

from load_testing.main import (
    VIDEO_PATH,
    DEFAULT_RUN_TIME,
    RUN_DETECTIONS,
    SAVE_LOG,
)

app = Typer()


@app.command()
def run(
    max_process: int = 1,
    max_thread: int = 1,
    run_time: int = DEFAULT_RUN_TIME,
    video_path: str = VIDEO_PATH,
    run_detections: bool = RUN_DETECTIONS,
    create_log: bool = SAVE_LOG,
    wait_time: int = 1,
) -> None:
    """run number of combinations from combinations value

    Args:
        run_time (int, optional): _description_. Defaults to DEFAULT_RUN_TIME.
        video_path (str, optional): _description_. Defaults to VIDEO_PATH.
        run_detections (bool, optional): _description_. Defaults to RUN_DETECTIONS.
        create_log (bool, optional): _description_. Defaults to SAVE_LOG.
    """
    log_file = " >> logs/logs.json" if create_log else ""
    create_log = "--create-log" if create_log else "--no-create-log"
    run_detections = "--run-detections" if run_detections else "--no-run-detections"
    for process_count in range(1, max_process + 1):
        for thread_count in range(1, max_thread + 1):
            script = f"""\\
                python3 runapp.py \\
                --process-count {process_count} \\
                --thread-count {thread_count} \\
                --run-time {run_time} \\
                --video-path {video_path} \\
                {create_log} \\
                {run_detections} \\
                {log_file}"""
            print(script)
            os.system(script)
            time.sleep(wait_time)
    print("Completed all combinations")


if __name__ == "__main__":
    app()
