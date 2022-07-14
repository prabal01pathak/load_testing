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
        self.gpu: list = gputil.getGPUs()
        if len(self.gpu) > 0:
            self.gpu = self.gpu[0]

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

    def get_size(self, size: int, suffix="B") -> str:
        """
        Scale bytes to its proper format- KB, MB, GB, TB and PB
        Args:
            size(int): size in bytes

        Return:
            str: return size of given bytes
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if size < factor:
                return f"{size:.2f}{unit}{suffix}"
            size /= factor
        return size

    def get_cpu_usage(self) -> float:
        """get cpu usage
        Return:
            float: return total cpu utilization
        """
        cpu_utilization = self.process.cpu_percent()
        return cpu_utilization

    def get_gpu_usage(self) -> str:
        """return total gpu usage
        Return:
            str: return total gpu usage in mb
        """
        if not isinstance(self.gpu, list):
            return f"{self.gpu.memoryFree}MB"
        return "0MB"

    def get_memory_usage(self) -> str:
        """get total memory usage
        Return:
            str: get total memory used
        """
        svmem = psutil.virtual_memory()
        return self.get_size(svmem.used)

    def gpu_memory_free(self) -> str:
        """get total memory free

        Returns:
            str: total memory in mb
        """
        if not isinstance(self.gpu, list):
            return f"{self.gpu.memoryFree}MB"
        return "0MB"

    def get_gpu_temprature(self) -> str:
        """return gpu temprature
        Return:
            str: temprature of gpu
        """
        if not isinstance(self.gpu, list):
            return f"{self.gpu.temperature}*C"
        return "0*C"

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
