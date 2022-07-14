"""
Get system details like cpu usage, gpu usage, temprature etc.
"""
import os
import time
import platform

import psutil
import GPUtil as gputil


class ProcessDetails:
    """get process details like cpu, gpu, and memory
    Args:
        pid(int): process id
    """

    def __init__(self):
        self.pid = os.getpid()
        self.process = psutil.Process(pid=self.pid)
        self.uname = platform.uname()
        self.gpu = gputil.getGPUs()[0]

    def system_info(self) -> dict:
        """return device informations like os, processer
        Return:
            information(dict): os, release, version, processor
                physical_cores, total_cores
        """
        return {
            "os": self.uname.system,
            "release": self.uname.release,
            "version": self.uname.version,
            "processer": self.uname.processor,
            "physical cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
        }

    def get_cpu_usage(self):
        """get cpu usage"""
        cpu_utilization = self.process.cpu_percent()
        return cpu_utilization

    def get_gpu_usage(self):
        """return total gpu usage"""
        return self.gpu.memoryFree

    def get_memory_usage(self):
        """get total memory usage"""

    def get_gpu_temprature(self):
        """return gpu temprature"""

    def running_time(self, func) -> float:
        """running time decorator to caculate running time

        Args:
            func (function): function

        Returns:
            total_time(float): total processing time
        """

        def wrapper(*args, **kwargs):
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            return end_time - start_time

        return wrapper
