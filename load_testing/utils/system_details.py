"""
Get system details like cpu usage, gpu usage, temprature etc.
"""
import os
import time
import platform
import datetime as dt

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
        return cpu_utilization/psutil.cpu_count()

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
        return self.process.memory_percent() #self.get_size(svmem.used)

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

    @staticmethod
    def running_time(func) -> dict:
        """running time decorator to caculate running time

        Args:
            func (function): function

        Returns:
            dict
            total_time(float): total processing time
            func_return(): function return values
        """

        def wrapper(*args, **kwargs):
            start_time = time.time()
            values = func(*args, **kwargs)
            process_util: ProcessDetails = kwargs["process_util"]
            cpu_usage = process_util.get_cpu_usage()
            gpu_usage = process_util.get_gpu_usage()
            gpu_temp = process_util.get_gpu_temprature()
            memory_usage = process_util.get_memory_usage()
            current_time = dt.datetime.now().strftime("%H:%M:%S")
            end_time = time.time()
            return {
                "func_return": values,
                "processing_time": end_time - start_time,
                "time": current_time,
                "cpu_usage": cpu_usage,
                "gpu_usage": gpu_usage,
                "gpu_temprateure": gpu_temp,
                "memory_usage": memory_usage,
            }

        return wrapper
